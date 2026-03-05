"""
用户服务
处理用户信息查询、密码修改、设备管理等
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import hash_password, validate_password, verify_password
from app.models.device import Device
from app.models.user import User
from app.schemas.auth import DeviceResponse, UserResponse

logger = logging.getLogger(__name__)


class UserService:
    """用户服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_info(self, user: User) -> UserResponse:
        """
        获取用户信息
        @param user: 用户对象
        @return: 用户信息响应
        """
        return UserResponse.model_validate(user)

    async def change_password(
        self, user: User, old_password: str, new_password: str
    ) -> None:
        """
        修改密码
        @param user: 当前用户
        @param old_password: 旧密码
        @param new_password: 新密码
        """
        # 验证旧密码
        if not verify_password(old_password, user.password_hash):
            raise AuthenticationError(detail="当前密码错误", code="WRONG_PASSWORD")

        # 验证新密码策略
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            raise ConflictError(detail=error_msg, code="WEAK_PASSWORD")

        # 检查新旧密码是否相同
        if verify_password(new_password, user.password_hash):
            raise ConflictError(detail="新密码不能与当前密码相同", code="SAME_PASSWORD")

        # 更新密码
        user.password_hash = hash_password(new_password)
        await self.db.flush()

        logger.info(f"用户修改密码成功 user_id={user.id}")

    async def get_devices(self, user_id: int) -> list[DeviceResponse]:
        """
        获取用户设备列表
        @param user_id: 用户 ID
        @return: 设备列表
        """
        result = await self.db.execute(
            select(Device)
            .where(Device.user_id == user_id)
            .order_by(Device.last_login_at.desc())
        )
        devices = result.scalars().all()
        return [DeviceResponse.model_validate(d) for d in devices]
