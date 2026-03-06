"""
用户服务
处理用户信息查询、密码修改、设备管理等
"""

from __future__ import annotations

import logging

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import hash_password, validate_password, verify_password
from app.core.memory_store import store, UserData
from app.schemas.auth import DeviceResponse, UserResponse

logger = logging.getLogger(__name__)


class UserService:
    """用户服务类"""

    async def get_user_info(self, user: UserData) -> UserResponse:
        """获取用户信息"""
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            is_2fa_enabled=user.is_2fa_enabled,
            created_at=user.created_at,
        )

    async def change_password(
        self, user: UserData, old_password: str, new_password: str
    ) -> None:
        """修改密码"""
        if not verify_password(old_password, user.password_hash):
            raise AuthenticationError(detail="当前密码错误", code="WRONG_PASSWORD")

        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            raise ConflictError(detail=error_msg, code="WEAK_PASSWORD")

        if verify_password(new_password, user.password_hash):
            raise ConflictError(detail="新密码不能与当前密码相同", code="SAME_PASSWORD")

        user.password_hash = hash_password(new_password)
        logger.info(f"用户修改密码成功 user_id={user.id}")

    async def get_devices(self, user_id: int) -> list[DeviceResponse]:
        """获取用户设备列表"""
        devices = store.get_user_devices(user_id)
        return [
            DeviceResponse(
                id=d.id,
                device_id=d.device_id,
                device_name=d.device_name,
                ip_address=d.ip_address,
                last_login_at=d.last_login_at,
                created_at=d.created_at,
            )
            for d in devices
        ]
