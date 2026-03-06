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
    当内存中找不到用户时，从 JWT 载荷恢复用户和自选数据
    适用于 Vercel serverless 环境：不同 Lambda 实例间数据不共享，
    但 JWT 携带了用户身份和自选快照，可以据此完整重建。
    """
    user_id = payload["user_id"]
    username = payload.get("username", f"user_{user_id}")

    # 恢复用户（如果已存在则复用）
    user = store.get_user_by_id(user_id)
    if not user:
        user = UserData(id=user_id, username=username, password_hash="")
        store.users[user_id] = user
        if user_id >= store._next_user_id:
            store._next_user_id = user_id + 1

    # 检查该用户是否已有组合数据，有则跳过恢复
    existing_portfolios = store.get_user_portfolios(user_id)
    if existing_portfolios:
        logger.info(f"用户 user_id={user_id} 已有 {len(existing_portfolios)} 个组合，跳过恢复")
        return user

    # 从 token 恢复自选数据
    watchlist_data = payload.get("wl", [])
    if watchlist_data:
        for p_data in watchlist_data:
            # 使用 token 中记录的原始 id，保持前后端 id 一致
            original_id = p_data.get("id")
            portfolio = store.add_portfolio(
                user_id=user_id,
                name=p_data.get("n", "我的自选"),
                sort_order=p_data.get("o", 0),
                is_default=p_data.get("d", False),
                restore_id=original_id,
            )
            for item_data in p_data.get("items", []):
                store.add_watchlist_item(
                    portfolio_id=portfolio.id,
                    symbol=item_data.get("s", ""),
                    name=item_data.get("n", ""),
                    market=item_data.get("m", ""),
                    sort_order=0,
                )
    else:
        # 没有自选快照，创建默认组合
        store.add_portfolio(
            user_id=user_id, name="我的自选", sort_order=0, is_default=True
        )

    logger.info(f"从 Token 恢复用户及自选 user_id={user_id} username={username}")
    return user


async def get_current_user(
    authorization: str = Header(None),
) -> UserData:
    """
    从 Authorization 头提取并验证 JWT Token，返回当前用户
    如果用户不在内存中（Vercel 冷启动/实例切换），自动从 Token 恢复
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
        user = _restore_user_from_token(payload)
    else:
        # 用户存在但组合可能丢失（同实例内其他请求只恢复了用户），补充恢复
        _restore_user_from_token(payload)

    return user


async def get_current_active_user(
    current_user: UserData = Depends(get_current_user),
) -> UserData:
    """获取当前活跃用户，检查账户是否被禁用"""
    if not current_user.is_active:
        raise AuthorizationError(detail="账户已被禁用", code="ACCOUNT_DISABLED")
    return current_user
