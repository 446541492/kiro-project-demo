"""
安全工具模块
JWT Token 生成/验证和 bcrypt 密码加密/验证
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings

settings = get_settings()


# ==================== 密码工具 ====================

def hash_password(password: str) -> str:
    """
    使用 bcrypt 加密密码
    @param password: 明文密码
    @return: 加密后的密码哈希
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    验证密码是否匹配
    @param password: 明文密码
    @param hashed: 加密后的密码哈希
    @return: 是否匹配
    """
    return bcrypt.checkpw(
        password.encode("utf-8"), hashed.encode("utf-8")
    )


def validate_password(password: str) -> tuple[bool, str]:
    """
    验证密码是否符合安全策略
    规则: 最少8位，包含大写、小写、数字、特殊字符
    @param password: 待验证的密码
    @return: (是否合法, 错误信息)
    """
    if len(password) < 8:
        return False, "密码最少需要 8 个字符"
    if len(password) > 128:
        return False, "密码最多 128 个字符"
    if not re.search(r"[A-Z]", password):
        return False, "密码必须包含至少 1 个大写字母"
    if not re.search(r"[a-z]", password):
        return False, "密码必须包含至少 1 个小写字母"
    if not re.search(r"\d", password):
        return False, "密码必须包含至少 1 个数字"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        return False, "密码必须包含至少 1 个特殊字符"
    return True, ""


# ==================== JWT Token 工具 ====================

def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """
    创建 JWT Access Token
    @param data: Token 载荷数据
    @param expires_delta: 自定义过期时间
    @return: 编码后的 JWT Token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "token_type": "access",
    })
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(data: dict) -> str:
    """
    创建 JWT Refresh Token
    @param data: Token 载荷数据
    @return: 编码后的 JWT Token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "token_type": "refresh",
    })
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_2fa_temp_token(data: dict) -> str:
    """
    创建 2FA 临时 Token（有效期 5 分钟）
    @param data: Token 载荷数据
    @return: 编码后的 JWT Token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "token_type": "2fa_temp",
    })
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> dict:
    """
    解码 JWT Token
    @param token: JWT Token 字符串
    @return: Token 载荷数据
    @raises jwt.ExpiredSignatureError: Token 已过期
    @raises jwt.InvalidTokenError: Token 无效
    """
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
