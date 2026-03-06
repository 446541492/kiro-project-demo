"""
自选组合服务
处理组合的增删改查、排序、默认组合管理
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.core.exceptions import AppException, ConflictError
from app.core.memory_store import store
from app.schemas.portfolio import CreatePortfolioRequest, PortfolioResponse, UpdatePortfolioRequest

logger = logging.getLogger(__name__)

# 每个用户最多创建的组合数
MAX_PORTFOLIOS_PER_USER = 20


class PortfolioService:
    """自选组合服务类"""

    async def get_portfolios(self, user_id: int) -> list[PortfolioResponse]:
        """获取用户所有组合（含标的数量）"""
        portfolios = store.get_user_portfolios(user_id)
        return [
            PortfolioResponse(
                id=p.id,
                name=p.name,
                sort_order=p.sort_order,
                is_default=p.is_default,
                item_count=store.get_portfolio_item_count(p.id),
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in portfolios
        ]

    async def create_portfolio(
        self, user_id: int, data: CreatePortfolioRequest
    ) -> PortfolioResponse:
        """创建新组合"""
        portfolios = store.get_user_portfolios(user_id)
        if len(portfolios) >= MAX_PORTFOLIOS_PER_USER:
            raise AppException(
                detail=f"最多创建 {MAX_PORTFOLIOS_PER_USER} 个组合",
                code="PORTFOLIO_LIMIT_EXCEEDED",
                status_code=400,
            )

        # 检查同名组合
        for p in portfolios:
            if p.name == data.name:
                raise ConflictError(detail="组合名称已存在", code="PORTFOLIO_NAME_EXISTS")

        next_order = max((p.sort_order for p in portfolios), default=-1) + 1
        portfolio = store.add_portfolio(
            user_id=user_id, name=data.name, sort_order=next_order, is_default=False
        )

        return PortfolioResponse(
            id=portfolio.id, name=portfolio.name, sort_order=portfolio.sort_order,
            is_default=portfolio.is_default, item_count=0,
            created_at=portfolio.created_at, updated_at=portfolio.updated_at,
        )

    async def update_portfolio(
        self, portfolio_id: int, user_id: int, data: UpdatePortfolioRequest
    ) -> PortfolioResponse:
        """更新组合名称"""
        portfolio = self._get_user_portfolio(portfolio_id, user_id)

        # 检查新名称是否与其他组合重复
        for p in store.get_user_portfolios(user_id):
            if p.name == data.name and p.id != portfolio_id:
                raise ConflictError(detail="组合名称已存在", code="PORTFOLIO_NAME_EXISTS")

        portfolio.name = data.name
        portfolio.updated_at = datetime.now(timezone.utc)

        return PortfolioResponse(
            id=portfolio.id, name=portfolio.name, sort_order=portfolio.sort_order,
            is_default=portfolio.is_default,
            item_count=store.get_portfolio_item_count(portfolio.id),
            created_at=portfolio.created_at, updated_at=portfolio.updated_at,
        )

    async def delete_portfolio(self, portfolio_id: int, user_id: int) -> None:
        """删除组合（默认组合不可删除）"""
        portfolio = self._get_user_portfolio(portfolio_id, user_id)
        if portfolio.is_default:
            raise AppException(
                detail="默认组合不可删除", code="DEFAULT_PORTFOLIO_PROTECTED", status_code=400
            )
        store.delete_portfolio(portfolio_id)

    async def reorder_portfolios(self, user_id: int, ids: list[int]) -> None:
        """调整组合排序"""
        portfolios = {p.id: p for p in store.get_user_portfolios(user_id)}
        if set(ids) != set(portfolios.keys()):
            raise AppException(
                detail="组合 ID 列表不匹配", code="INVALID_PORTFOLIO_IDS", status_code=400
            )
        for order, pid in enumerate(ids):
            portfolios[pid].sort_order = order

    def _get_user_portfolio(self, portfolio_id: int, user_id: int):
        """获取并验证组合归属"""
        portfolio = store.get_portfolio(portfolio_id)
        if not portfolio or portfolio.user_id != user_id:
            raise AppException(
                detail="组合不存在", code="PORTFOLIO_NOT_FOUND", status_code=404
            )
        return portfolio
