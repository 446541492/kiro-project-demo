"""
认证相关 Pydantic 请求/响应模型
包含注册、登录、Token、用户信息、2FA、密码修改、设备等
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


# ==================== 注册 ====================

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """用户名: 3-50 字符，字母/数字/下划线，不能以数字开头"""
        if len(v) < 3 or len(v) > 50:
            raise ValueError("用户名长度必须在 3-50 个字符之间")
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", v):
            raise ValueError("用户名只能包含字母、数字和下划线，且不能以数字开头")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """邮箱格式验证"""
        if v is not None and v.strip():
            # 简单邮箱格式验证
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
                raise ValueError("邮箱格式不正确")
            return v.lower().strip()
        return None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """手机号: 11 位数字，以 1 开头"""
        if v is not None and v.strip():
            if not re.match(r"^1\d{10}$", v):
                raise ValueError("手机号格式不正确，需要 11 位数字且以 1 开头")
            return v.strip()
        return None


# ==================== 登录 ====================

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str
    device_id: Optional[str] = None
    captcha_token: Optional[str] = None


class TwoFactorVerifyRequest(BaseModel):
    """2FA 验证请求（登录第二步）"""
    temp_token: str
    code: str


# ==================== Token ====================

class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Token 刷新请求"""
    refresh_token: str


class LoginResponse(BaseModel):
    """登录响应（可能需要 2FA）"""
    requires_2fa: bool = False
    temp_token: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None


# ==================== 用户信息 ====================

class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_2fa_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 密码修改 ====================

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str


# ==================== 2FA ====================

class TwoFactorSetupResponse(BaseModel):
    """2FA 设置响应（返回密钥和二维码）"""
    secret: str
    qr_code_base64: str
    provisioning_uri: str


class TwoFactorEnableRequest(BaseModel):
    """确认启用 2FA 请求（验证首次 TOTP 码）"""
    secret: str
    code: str


class TwoFactorEnableResponse(BaseModel):
    """启用 2FA 响应（返回恢复码）"""
    recovery_codes: list[str]


class TwoFactorDisableRequest(BaseModel):
    """禁用 2FA 请求"""
    code: str


class RecoveryCodesResponse(BaseModel):
    """恢复码响应"""
    recovery_codes: list[str]


# ==================== 设备 ====================

class DeviceResponse(BaseModel):
    """设备信息响应"""
    id: int
    device_id: str
    device_name: str
    ip_address: Optional[str] = None
    last_login_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
