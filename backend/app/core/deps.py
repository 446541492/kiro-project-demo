"""
FastAPI 依赖注入模块
提供数据库会话、当前用户等通用依赖
"""

import jwt
from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User

settings = get_settings()


async def get_current_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    从 Authorization 头提取并验证 JWT Token，返回当前用户
    @param authorization: Authorization 请求头
    @param db: 数据库会话
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

    # 验证 Token 类型
    if payload.get("token_type") != "access":
        raise AuthenticationError(detail="Token 类型无效", code="INVALID_TOKEN")

    user_id = payload.get("user_id")
    if not user_id:
        raise AuthenticationError(detail="Token 无效或已过期", code="INVALID_TOKEN")

    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError(detail="用户不存在", code="INVALID_TOKEN")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户，检查账户是否被禁用
    @param current_user: 当前用户
    @return: 活跃用户对象
    @raises AuthorizationError: 账户已被禁用
    """
    if not current_user.is_active:
        raise AuthorizationError(detail="账户已被禁用", code="ACCOUNT_DISABLED")
    return current_user
