"""
FastAPI 依赖注入模块
提供当前用户等通用依赖
"""

import logging

import jwt
from fastapi import Depends, Header

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.memory_store import store, UserData

logger = logging.getLogger(__name__)
settings = get_settings()


def _restore_user_from_token(payload: dict) -> UserData:
    """
    当内存中找不到用户时，从 JWT 载荷恢复用户（幽灵用户恢复）
    适用于 Vercel serverless 环境：不同 Lambda 实例间 /tmp 数据不共享，
    但 JWT 本身携带了用户身份信息，可以据此重建用户记录。
    """
    user_id = payload["user_id"]
    username = payload.get("username", f"user_{user_id}")

    # 直接写入内存存储（绕过 add_user 的自增 ID 逻辑）
    user = UserData(
        id=user_id,
        username=username,
        password_hash="",  # 无法恢复密码哈希，用户需重新登录才能修改密码
    )
    store.users[user_id] = user
    # 更新自增计数器，避免 ID 冲突
    if user_id >= store._next_user_id:
        store._next_user_id = user_id + 1

    # 创建默认自选组合
    store.add_portfolio(user_id=user_id, name="我的自选", sort_order=0, is_default=True)

    logger.info(f"从 Token 恢复用户 user_id={user_id} username={username}")
    return user


async def get_current_user(
    authorization: str = Header(None),
) -> UserData:
    """
    从 Authorization 头提取并验证 JWT Token，返回当前用户
    如果用户不在内存中（Vercel 冷启动/实例切换），自动从 Token 恢复
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
        # Vercel 冷启动或实例切换导致内存数据丢失，从 Token 恢复用户
        user = _restore_user_from_token(payload)

    return user


async def get_current_active_user(
    current_user: UserData = Depends(get_current_user),
) -> UserData:
    """获取当前活跃用户，检查账户是否被禁用"""
    if not current_user.is_active:
        raise AuthorizationError(detail="账户已被禁用", code="ACCOUNT_DISABLED")
    return current_user
