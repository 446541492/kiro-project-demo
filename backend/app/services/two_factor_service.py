"""
两步验证服务
处理 TOTP 密钥生成、二维码生成、验证码验证、恢复码管理
"""

from __future__ import annotations

import io
import base64
import logging
import secrets
import string
from datetime import datetime, timezone

import pyotp
import segno
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, ConflictError
from app.models.recovery_code import RecoveryCode
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()


class TwoFactorService:
    """两步验证服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def generate_secret(self) -> str:
        """
        生成 TOTP 密钥
        @return: Base32 编码的密钥
        """
        return pyotp.random_base32()

    def generate_provisioning_uri(self, secret: str, username: str) -> str:
        """
        生成 TOTP 配置 URI
        @param secret: TOTP 密钥
        @param username: 用户名
        @return: otpauth:// URI
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=username, issuer_name=settings.TWO_FA_ISSUER
        )

    def generate_qr_code(self, provisioning_uri: str) -> str:
        """
        生成二维码图片（Base64 SVG）
        @param provisioning_uri: otpauth:// URI
        @return: Base64 编码的 SVG 图片
        """
        qr = segno.make(provisioning_uri)
        buffer = io.BytesIO()
        qr.save(buffer, kind="svg", scale=4, border=4)
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def verify_totp(self, secret: str, code: str) -> bool:
        """
        验证 TOTP 验证码
        @param secret: TOTP 密钥
        @param code: 用户输入的验证码
        @return: 是否验证通过
        """
        totp = pyotp.TOTP(secret)
        # 允许前后 1 个时间窗口的偏差（±30 秒）
        return totp.verify(code, valid_window=1)

    def generate_recovery_codes(self, count: int = 8) -> list[str]:
        """
        生成恢复码
        @param count: 恢复码数量，默认 8 个
        @return: 恢复码列表（8 位大写字母数字）
        """
        chars = string.ascii_uppercase + string.digits
        codes = []
        for _ in range(count):
            code = "".join(secrets.choice(chars) for _ in range(8))
            codes.append(code)
        return codes

    async def setup_2fa(self, user: User) -> dict:
        """
        设置 2FA（第一步：生成密钥和二维码）
        @param user: 当前用户
        @return: 包含 secret、qr_code_base64、provisioning_uri 的字典
        """
        if user.is_2fa_enabled:
            raise ConflictError(detail="两步验证已启用", code="2FA_ALREADY_ENABLED")

        secret = self.generate_secret()
        uri = self.generate_provisioning_uri(secret, user.username)
        qr_code = self.generate_qr_code(uri)

        return {
            "secret": secret,
            "qr_code_base64": qr_code,
            "provisioning_uri": uri,
        }

    async def enable_2fa(self, user: User, secret: str, code: str) -> list[str]:
        """
        确认启用 2FA（第二步：验证首次 TOTP 码并保存）
        @param user: 当前用户
        @param secret: TOTP 密钥
        @param code: 用户输入的验证码
        @return: 恢复码列表
        """
        if user.is_2fa_enabled:
            raise ConflictError(detail="两步验证已启用", code="2FA_ALREADY_ENABLED")

        # 验证首次 TOTP 码
        if not self.verify_totp(secret, code):
            raise AuthenticationError(detail="验证码错误，请重试", code="INVALID_2FA_CODE")

        # 保存 2FA 设置
        user.totp_secret = secret
        user.is_2fa_enabled = True

        # 生成恢复码
        recovery_codes = self.generate_recovery_codes()

        # 删除旧恢复码
        await self.db.execute(
            delete(RecoveryCode).where(RecoveryCode.user_id == user.id)
        )

        # 保存新恢复码
        for code_str in recovery_codes:
            rc = RecoveryCode(user_id=user.id, code=code_str)
            self.db.add(rc)

        await self.db.flush()
        logger.info(f"用户启用 2FA user_id={user.id}")

        return recovery_codes

    async def disable_2fa(self, user: User, code: str) -> None:
        """
        禁用 2FA
        @param user: 当前用户
        @param code: TOTP 验证码
        """
        if not user.is_2fa_enabled:
            raise ConflictError(detail="两步验证未启用", code="2FA_NOT_ENABLED")

        # 验证 TOTP 码
        if not self.verify_totp(user.totp_secret, code):
            raise AuthenticationError(detail="验证码错误", code="INVALID_2FA_CODE")

        # 禁用 2FA
        user.is_2fa_enabled = False
        user.totp_secret = None

        # 删除所有恢复码
        await self.db.execute(
            delete(RecoveryCode).where(RecoveryCode.user_id == user.id)
        )

        await self.db.flush()
        logger.info(f"用户禁用 2FA user_id={user.id}")

    async def verify_code(self, user: User, code: str) -> bool:
        """
        验证 2FA 码（TOTP 或恢复码）
        @param user: 用户对象
        @param code: 验证码或恢复码
        @return: 是否验证通过
        """
        # 先尝试 TOTP 验证
        if user.totp_secret and self.verify_totp(user.totp_secret, code):
            return True

        # 再尝试恢复码验证
        result = await self.db.execute(
            select(RecoveryCode).where(
                RecoveryCode.user_id == user.id,
                RecoveryCode.code == code.upper(),
                RecoveryCode.is_used == False,
            )
        )
        recovery_code = result.scalar_one_or_none()
        if recovery_code:
            recovery_code.is_used = True
            recovery_code.used_at = datetime.now(timezone.utc)
            await self.db.flush()
            logger.info(f"用户使用恢复码 user_id={user.id}")
            return True

        return False

    async def get_recovery_codes(self, user: User) -> list[str]:
        """
        获取未使用的恢复码
        @param user: 当前用户
        @return: 恢复码列表
        """
        if not user.is_2fa_enabled:
            raise ConflictError(detail="两步验证未启用", code="2FA_NOT_ENABLED")

        result = await self.db.execute(
            select(RecoveryCode).where(
                RecoveryCode.user_id == user.id,
                RecoveryCode.is_used == False,
            )
        )
        codes = result.scalars().all()
        return [c.code for c in codes]

    async def regenerate_recovery_codes(self, user: User) -> list[str]:
        """
        重新生成恢复码（旧的全部失效）
        @param user: 当前用户
        @return: 新的恢复码列表
        """
        if not user.is_2fa_enabled:
            raise ConflictError(detail="两步验证未启用", code="2FA_NOT_ENABLED")

        # 删除旧恢复码
        await self.db.execute(
            delete(RecoveryCode).where(RecoveryCode.user_id == user.id)
        )

        # 生成新恢复码
        recovery_codes = self.generate_recovery_codes()
        for code_str in recovery_codes:
            rc = RecoveryCode(user_id=user.id, code=code_str)
            self.db.add(rc)

        await self.db.flush()
        logger.info(f"用户重新生成恢复码 user_id={user.id}")

        return recovery_codes
