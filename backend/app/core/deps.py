"""
FastAPI 依赖注入模块
提供当前用户等通用依赖
"""

import jwt
from fastapi import Depends, Header

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.memory_store import store, UserData

settings = get_settings()


async def get_current_user(
    authorization: str = Header(None),
) -> UserData:
    """
    从 Authorization 头提取并验证 JWT Token，返回当前用户
    @param authorization: Authorization 请求头
    @return: 当前用户对象
    @raises AuthenticationError: Token 无效或用户不存在
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError(detail="请先登录", code="UNAUTHORIZED")

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise AuthenticationError(detail="Token 已过期", code="TOKEN_EXPIRED")
    except jwt.InvalidTokenError:
        raise AuthenticationError(detail="Token 无效或已过期", code="INVALID_TOKEN")

    if payload.get("token_type") != "access":
        raise AuthenticationError(detail="Token 类型无效", code="INVALID_TOKEN")

    user_id = payload.get("user_id")
    if not user_id:
        raise AuthenticationError(detail="Token 无效或已过期", code="INVALID_TOKEN")

    user = store.get_user_by_id(user_id)
    if not user:
        raise AuthenticationError(detail="用户不存在", code="INVALID_TOKEN")

    return user


async def get_current_active_user(
    current_user: UserData = Depends(get_current_user),
) -> UserData:
    """获取当前活跃用户，检查账户是否被禁用"""
    if not current_user.is_active:
        raise AuthorizationError(detail="账户已被禁用", code="ACCOUNT_DISABLED")
    return current_user
