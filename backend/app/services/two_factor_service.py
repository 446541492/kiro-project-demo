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

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, ConflictError
from app.core.memory_store import store, UserData

logger = logging.getLogger(__name__)
settings = get_settings()


class TwoFactorService:
    """两步验证服务类"""

    def generate_secret(self) -> str:
        """生成 TOTP 密钥"""
        return pyotp.random_base32()

    def generate_provisioning_uri(self, secret: str, username: str) -> str:
        """生成 TOTP 配置 URI"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=username, issuer_name=settings.TWO_FA_ISSUER
        )

    def generate_qr_code(self, provisioning_uri: str) -> str:
        """生成二维码图片（Base64 SVG）"""
        qr = segno.make(provisioning_uri)
        buffer = io.BytesIO()
        qr.save(buffer, kind="svg", scale=4, border=4)
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def verify_totp(self, secret: str, code: str) -> bool:
        """验证 TOTP 验证码"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    def generate_recovery_codes(self, count: int = 8) -> list[str]:
        """生成恢复码"""
        chars = string.ascii_uppercase + string.digits
        return ["".join(secrets.choice(chars) for _ in range(8)) for _ in range(count)]

    async def setup_2fa(self, user: UserData) -> dict:
        """设置 2FA（第一步：生成密钥和二维码）"""
        if user.is_2fa_enabled:
            raise ConflictError(detail="两步验证已启用", code="2FA_ALREADY_ENABLED")

        secret = self.generate_secret()
        uri = self.generate_provisioning_uri(secret, user.username)
        qr_code = self.generate_qr_code(uri)

        return {"secret": secret, "qr_code_base64": qr_code, "provisioning_uri": uri}

    async def enable_2fa(self, user: UserData, secret: str, code: str) -> list[str]:
        """确认启用 2FA（第二步）"""
        if user.is_2fa_enabled:
            raise ConflictError(detail="两步验证已启用", code="2FA_ALREADY_ENABLED")

        if not self.verify_totp(secret, code):
            raise AuthenticationError(detail="验证码错误，请重试", code="INVALID_2FA_CODE")

        user.totp_secret = secret
        user.is_2fa_enabled = True

        # 删除旧恢复码，生成新恢复码
        store.delete_user_recovery_codes(user.id)
        recovery_codes = self.generate_recovery_codes()
        for code_str in recovery_codes:
            store.add_recovery_code(user_id=user.id, code=code_str)

        logger.info(f"用户启用 2FA user_id={user.id}")
        return recovery_codes

    async def disable_2fa(self, user: UserData, code: str) -> None:
        """禁用 2FA"""
        if not user.is_2fa_enabled:
            raise ConflictError(detail="两步验证未启用", code="2FA_NOT_ENABLED")

        if not self.verify_totp(user.totp_secret, code):
            raise AuthenticationError(detail="验证码错误", code="INVALID_2FA_CODE")

        user.is_2fa_enabled = False
        user.totp_secret = None
        store.delete_user_recovery_codes(user.id)
        logger.info(f"用户禁用 2FA user_id={user.id}")

    def verify_code(self, user: UserData, code: str) -> bool:
        """验证 2FA 码（TOTP 或恢复码）"""
        if user.totp_secret and self.verify_totp(user.totp_secret, code):
            return True

        rc = store.get_valid_recovery_code(user.id, code)
        if rc:
            rc.is_used = True
            rc.used_at = datetime.now(timezone.utc)
            logger.info(f"用户使用恢复码 user_id={user.id}")
            return True

        return False

    async def get_recovery_codes(self, user: UserData) -> list[str]:
        """获取未使用的恢复码"""
        if not user.is_2fa_enabled:
            raise ConflictError(detail="两步验证未启用", code="2FA_NOT_ENABLED")
        return store.get_unused_recovery_codes(user.id)

    async def regenerate_recovery_codes(self, user: UserData) -> list[str]:
        """重新生成恢复码"""
        if not user.is_2fa_enabled:
            raise ConflictError(detail="两步验证未启用", code="2FA_NOT_ENABLED")

        store.delete_user_recovery_codes(user.id)
        recovery_codes = self.generate_recovery_codes()
        for code_str in recovery_codes:
            store.add_recovery_code(user_id=user.id, code=code_str)

        logger.info(f"用户重新生成恢复码 user_id={user.id}")
        return recovery_codes
