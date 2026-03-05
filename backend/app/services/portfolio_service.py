"""
自选组合服务
处理组合的增删改查、排序、默认组合管理
"""

from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ConflictError
from app.models.portfolio import Portfolio
from app.schemas.portfolio import CreatePortfolioRequest, PortfolioResponse, UpdatePortfolioRequest

logger = logging.getLogger(__name__)

# 每个用户最多创建的组合数
MAX_PORTFOLIOS_PER_USER = 20


class PortfolioService:
    """自选组合服务类"""

    async def get_portfolios(self, user_id: int, db: AsyncSession) -> list[PortfolioResponse]:
        """
        获取用户所有组合（含标的数量）
        @param user_id: 用户 ID
        @param db: 数据库会话
        """
        result = await db.execute(
            select(Portfolio)
            .where(Portfolio.user_id == user_id)
            .order_by(Portfolio.sort_order)
        )
        portfolios = result.scalars().all()

        responses = []
        for p in portfolios:
            # 计算标的数量
            count_result = await db.execute(
                select(func.count())
                .select_from(Portfolio)
                .join(Portfolio.items)
                .where(Portfolio.id == p.id)
            )
            item_count = count_result.scalar() or 0

            responses.append(PortfolioResponse(
                id=p.id,
                name=p.name,
                sort_order=p.sort_order,
                is_default=p.is_default,
                item_count=item_count,
                created_at=p.created_at,
                updated_at=p.updated_at,
            ))
        return responses


    async def create_portfolio(
        self, user_id: int, data: CreatePortfolioRequest, db: AsyncSession
    ) -> PortfolioResponse:
        """
        创建新组合
        @param user_id: 用户 ID
        @param data: 创建请求
        @param db: 数据库会话
        """
        # 检查组合数量上限
        count_result = await db.execute(
            select(func.count()).select_from(Portfolio).where(Portfolio.user_id == user_id)
        )
        count = count_result.scalar() or 0
        if count >= MAX_PORTFOLIOS_PER_USER:
            raise AppException(
                detail=f"最多创建 {MAX_PORTFOLIOS_PER_USER} 个组合",
                code="PORTFOLIO_LIMIT_EXCEEDED",
                status_code=400,
            )

        # 检查同名组合
        existing = await db.execute(
            select(Portfolio).where(
                Portfolio.user_id == user_id, Portfolio.name == data.name
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError(detail="组合名称已存在", code="PORTFOLIO_NAME_EXISTS")

        # 计算排序顺序
        max_order = await db.execute(
            select(func.max(Portfolio.sort_order)).where(Portfolio.user_id == user_id)
        )
        next_order = (max_order.scalar() or -1) + 1

        portfolio = Portfolio(
            user_id=user_id,
            name=data.name,
            sort_order=next_order,
            is_default=False,
        )
        db.add(portfolio)
        await db.flush()

        return PortfolioResponse(
            id=portfolio.id,
            name=portfolio.name,
            sort_order=portfolio.sort_order,
            is_default=portfolio.is_default,
            item_count=0,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at,
        )

    async def update_portfolio(
        self, portfolio_id: int, user_id: int, data: UpdatePortfolioRequest, db: AsyncSession
    ) -> PortfolioResponse:
        """
        更新组合名称
        @param portfolio_id: 组合 ID
        @param user_id: 用户 ID
        @param data: 更新请求
        @param db: 数据库会话
        """
        portfolio = await self._get_user_portfolio(portfolio_id, user_id, db)

        # 检查新名称是否与其他组合重复
        existing = await db.execute(
            select(Portfolio).where(
                Portfolio.user_id == user_id,
                Portfolio.name == data.name,
                Portfolio.id != portfolio_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError(detail="组合名称已存在", code="PORTFOLIO_NAME_EXISTS")

        portfolio.name = data.name
        await db.flush()

        # 计算标的数量
        count_result = await db.execute(
            select(func.count())
            .select_from(Portfolio)
            .join(Portfolio.items)
            .where(Portfolio.id == portfolio.id)
        )
        item_count = count_result.scalar() or 0

        return PortfolioResponse(
            id=portfolio.id,
            name=portfolio.name,
            sort_order=portfolio.sort_order,
            is_default=portfolio.is_default,
            item_count=item_count,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at,
        )

    async def delete_portfolio(
        self, portfolio_id: int, user_id: int, db: AsyncSession
    ) -> None:
        """
        删除组合（默认组合不可删除）
        @param portfolio_id: 组合 ID
        @param user_id: 用户 ID
        @param db: 数据库会话
        """
        portfolio = await self._get_user_portfolio(portfolio_id, user_id, db)

        if portfolio.is_default:
            raise AppException(
                detail="默认组合不可删除",
                code="DEFAULT_PORTFOLIO_PROTECTED",
                status_code=400,
            )

        await db.delete(portfolio)
        await db.flush()

    async def reorder_portfolios(
        self, user_id: int, ids: list[int], db: AsyncSession
    ) -> None:
        """
        调整组合排序
        @param user_id: 用户 ID
        @param ids: 按新顺序排列的组合 ID 列表
        @param db: 数据库会话
        """
        # 获取用户所有组合
        result = await db.execute(
            select(Portfolio).where(Portfolio.user_id == user_id)
        )
        portfolios = {p.id: p for p in result.scalars().all()}

        # 验证 ID 列表
        if set(ids) != set(portfolios.keys()):
            raise AppException(
                detail="组合 ID 列表不匹配",
                code="INVALID_PORTFOLIO_IDS",
                status_code=400,
            )

        # 更新排序
        for order, pid in enumerate(ids):
            portfolios[pid].sort_order = order
        await db.flush()

    async def create_default_portfolio(
        self, user_id: int, db: AsyncSession
    ) -> Portfolio:
        """
        创建默认自选组合（注册时调用）
        @param user_id: 用户 ID
        @param db: 数据库会话
        """
        portfolio = Portfolio(
            user_id=user_id,
            name="我的自选",
            sort_order=0,
            is_default=True,
        )
        db.add(portfolio)
        await db.flush()
        return portfolio

    async def _get_user_portfolio(
        self, portfolio_id: int, user_id: int, db: AsyncSession
    ) -> Portfolio:
        """
        获取并验证组合归属
        @raises AppException: 组合不存在或不属于当前用户
        """
        result = await db.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id, Portfolio.user_id == user_id
            )
        )
        portfolio = result.scalar_one_or_none()
        if not portfolio:
            raise AppException(
                detail="组合不存在", code="PORTFOLIO_NOT_FOUND", status_code=404
            )
        return portfolio
