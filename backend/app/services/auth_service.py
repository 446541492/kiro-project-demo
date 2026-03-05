"""
认证服务
处理用户注册、登录、登出、Token 刷新等核心认证逻辑
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    LockedError,
    PreconditionError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_2fa_temp_token,
    decode_token,
    hash_password,
    validate_password,
    verify_password,
)
from app.models.device import Device
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:
    """认证服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(
        self,
        data: RegisterRequest,
        device_id: Optional[str] = None,
        device_name: str = "未知设备",
        ip_address: Optional[str] = None,
    ) -> TokenResponse:
        """
        用户注册
        @param data: 注册请求数据
        @param device_id: 设备标识
        @param device_name: 设备名称
        @param ip_address: IP 地址
        @return: Token 响应
        """
        # 验证密码策略
        is_valid, error_msg = validate_password(data.password)
        if not is_valid:
            raise ConflictError(detail=error_msg, code="WEAK_PASSWORD")

        # 验证联系方式至少填一个
        if not data.email and not data.phone:
            raise ConflictError(detail="邮箱和手机号至少填写一个", code="VALIDATION_ERROR")

        # 检查用户名唯一性（不区分大小写）
        result = await self.db.execute(
            select(User).where(func.lower(User.username) == data.username.lower())
        )
        if result.scalar_one_or_none():
            raise ConflictError(detail="用户名已被注册", code="USERNAME_EXISTS")

        # 检查邮箱唯一性
        if data.email:
            result = await self.db.execute(
                select(User).where(func.lower(User.email) == data.email.lower())
            )
            if result.scalar_one_or_none():
                raise ConflictError(detail="邮箱已被注册", code="EMAIL_EXISTS")

        # 检查手机号唯一性
        if data.phone:
            result = await self.db.execute(
                select(User).where(User.phone == data.phone)
            )
            if result.scalar_one_or_none():
                raise ConflictError(detail="手机号已被注册", code="PHONE_EXISTS")

        # 创建用户
        user = User(
            username=data.username,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
        )
        self.db.add(user)
        await self.db.flush()

        # 记录设备信息
        if not device_id:
            device_id = str(uuid.uuid4())
        device = Device(
            user_id=user.id,
            device_id=device_id,
            device_name=device_name,
            ip_address=ip_address,
        )
        self.db.add(device)

        # 生成 Token
        token_data = {"user_id": user.id, "username": user.username}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        logger.info(f"用户注册成功 user_id={user.id} username={user.username}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def login(
        self,
        data: LoginRequest,
        device_name: str = "未知设备",
        ip_address: Optional[str] = None,
    ) -> LoginResponse:
        """
        用户登录
        @param data: 登录请求数据
        @param device_name: 设备名称
        @param ip_address: IP 地址
        @return: 登录响应（可能需要 2FA）
        """
        # 查找用户
        result = await self.db.execute(
            select(User).where(func.lower(User.username) == data.username.lower())
        )
        user = result.scalar_one_or_none()
        if not user:
            raise AuthenticationError(detail="用户名或密码错误", code="INVALID_CREDENTIALS")

        # 检查账户状态
        if not user.is_active:
            raise AuthenticationError(detail="账户已被禁用", code="ACCOUNT_DISABLED")

        # 检查锁定状态（SQLite 不保留时区信息，统一使用 naive UTC）
        now = datetime.utcnow()
        if user.locked_until and user.locked_until > now:
            remaining = int((user.locked_until - now).total_seconds() / 60) + 1
            raise LockedError(
                detail=f"账户已锁定，请 {remaining} 分钟后重试",
                code="ACCOUNT_LOCKED",
            )
        elif user.locked_until and user.locked_until <= now:
            # 锁定已过期，重置
            user.failed_login_count = 0
            user.locked_until = None

        # 检查是否需要验证码（连续失败 3 次以上）
        if user.failed_login_count >= 3 and not data.captcha_token:
            raise PreconditionError(
                detail="请完成验证码验证", code="CAPTCHA_REQUIRED"
            )

        # 验证密码
        if not verify_password(data.password, user.password_hash):
            user.failed_login_count += 1

            if user.failed_login_count >= 5:
                # 锁定账户 15 分钟
                user.locked_until = now + timedelta(minutes=15)
                await self.db.commit()
                raise LockedError(
                    detail="连续登录失败过多，账户已锁定 15 分钟",
                    code="ACCOUNT_LOCKED",
                )
            elif user.failed_login_count >= 3:
                await self.db.commit()
                raise PreconditionError(
                    detail="用户名或密码错误，请完成验证码验证",
                    code="CAPTCHA_REQUIRED",
                )
            else:
                await self.db.commit()
                raise AuthenticationError(
                    detail="用户名或密码错误", code="INVALID_CREDENTIALS"
                )

        # 密码验证成功，重置失败计数
        user.failed_login_count = 0
        user.locked_until = None

        # 检查 2FA 状态
        if user.is_2fa_enabled:
            temp_token = create_2fa_temp_token(
                {"user_id": user.id, "username": user.username}
            )
            await self.db.flush()
            return LoginResponse(requires_2fa=True, temp_token=temp_token)

        # 生成正式 Token
        token_data = {"user_id": user.id, "username": user.username}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # 记录设备信息
        await self._record_device(
            user.id, data.device_id, device_name, ip_address
        )

        logger.info(f"用户登录成功 user_id={user.id}")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def verify_2fa_login(
        self,
        temp_token: str,
        code: str,
        device_id: Optional[str] = None,
        device_name: str = "未知设备",
        ip_address: Optional[str] = None,
    ) -> TokenResponse:
        """
        2FA 验证（登录第二步）
        @param temp_token: 临时 Token
        @param code: TOTP 验证码或恢复码
        @param device_id: 设备标识
        @param device_name: 设备名称
        @param ip_address: IP 地址
        @return: Token 响应
        """
        # 验证临时 Token
        try:
            payload = decode_token(temp_token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(detail="验证已过期，请重新登录", code="TOKEN_EXPIRED")
        except jwt.InvalidTokenError:
            raise AuthenticationError(detail="Token 无效", code="INVALID_TOKEN")

        if payload.get("token_type") != "2fa_temp":
            raise AuthenticationError(detail="Token 类型无效", code="INVALID_TOKEN")

        user_id = payload.get("user_id")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise AuthenticationError(detail="用户不存在", code="INVALID_TOKEN")

        # 验证 TOTP 码（延迟导入避免循环依赖）
        from app.services.two_factor_service import TwoFactorService
        two_factor_service = TwoFactorService(self.db)

        is_valid = await two_factor_service.verify_code(user, code)
        if not is_valid:
            raise AuthenticationError(detail="验证码错误", code="INVALID_2FA_CODE")

        # 生成正式 Token
        token_data = {"user_id": user.id, "username": user.username}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # 记录设备信息
        await self._record_device(user.id, device_id, device_name, ip_address)

        logger.info(f"用户 2FA 验证成功 user_id={user.id}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        """
        刷新 Access Token
        @param refresh_token_str: Refresh Token
        @return: 新的 Token 响应
        """
        try:
            payload = decode_token(refresh_token_str)
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(detail="Token 已过期，请重新登录", code="TOKEN_EXPIRED")
        except jwt.InvalidTokenError:
            raise AuthenticationError(detail="Token 无效", code="INVALID_TOKEN")

        if payload.get("token_type") != "refresh":
            raise AuthenticationError(detail="Token 类型无效", code="INVALID_TOKEN")

        user_id = payload.get("user_id")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise AuthenticationError(detail="用户不存在或已被禁用", code="INVALID_TOKEN")

        # 生成新的 Access Token
        token_data = {"user_id": user.id, "username": user.username}
        new_access_token = create_access_token(token_data)

        # 检查 Refresh Token 是否即将过期（剩余 < 1 天），如果是则同时刷新
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        remaining = exp - datetime.now(timezone.utc)
        new_refresh_token = refresh_token_str
        if remaining < timedelta(days=1):
            new_refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def _record_device(
        self,
        user_id: int,
        device_id: Optional[str],
        device_name: str,
        ip_address: Optional[str],
    ) -> None:
        """
        记录或更新设备信息
        @param user_id: 用户 ID
        @param device_id: 设备标识
        @param device_name: 设备名称
        @param ip_address: IP 地址
        """
        if not device_id:
            device_id = str(uuid.uuid4())

        # 查找已有设备记录
        result = await self.db.execute(
            select(Device).where(
                Device.user_id == user_id, Device.device_id == device_id
            )
        )
        device = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if device:
            # 更新已有设备
            device.last_login_at = now
            device.ip_address = ip_address
            device.device_name = device_name
        else:
            # 创建新设备记录
            device = Device(
                user_id=user_id,
                device_id=device_id,
                device_name=device_name,
                ip_address=ip_address,
                last_login_at=now,
            )
            self.db.add(device)
