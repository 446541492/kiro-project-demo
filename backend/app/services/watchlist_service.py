"""
自选标的服务
处理组合内标的的增删、排序、行情合并
"""

from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ConflictError
from app.models.portfolio import Portfolio
from app.models.watchlist_item import WatchlistItem
from app.schemas.watchlist import AddItemRequest, WatchlistItemResponse
from app.services.market_service import MarketService

logger = logging.getLogger(__name__)

# 每个组合最多标的数
MAX_ITEMS_PER_PORTFOLIO = 200

market_service = MarketService()


class WatchlistService:
    """自选标的服务类"""

    async def get_items(
        self, portfolio_id: int, user_id: int, db: AsyncSession
    ) -> list[WatchlistItemResponse]:
        """
        获取组合内所有标的（含实时行情）
        @param portfolio_id: 组合 ID
        @param user_id: 用户 ID
        @param db: 数据库会话
        """
        await self._verify_portfolio_ownership(portfolio_id, user_id, db)

        result = await db.execute(
            select(WatchlistItem)
            .where(WatchlistItem.portfolio_id == portfolio_id)
            .order_by(WatchlistItem.sort_order)
        )
        items = result.scalars().all()

        if not items:
            return []

        # 批量获取实时行情
        symbols = [item.symbol for item in items]
        quote_map = {}
        try:
            quotes = await market_service.get_batch_quotes(symbols)
            quote_map = {q.symbol: q for q in quotes}
        except Exception as e:
            # 行情获取失败时仍返回标的基础信息
            logger.warning(f"获取实时行情失败: {e}")

        # 合并标的信息和行情数据
        responses = []
        for item in items:
            responses.append(WatchlistItemResponse(
                id=item.id,
                portfolio_id=item.portfolio_id,
                symbol=item.symbol,
                name=item.name,
                market=item.market,
                sort_order=item.sort_order,
                quote=quote_map.get(item.symbol),
                created_at=item.created_at,
            ))
        return responses


    async def add_item(
        self, portfolio_id: int, user_id: int, data: AddItemRequest, db: AsyncSession
    ) -> WatchlistItemResponse:
        """
        添加标的到组合
        @param portfolio_id: 组合 ID
        @param user_id: 用户 ID
        @param data: 添加请求
        @param db: 数据库会话
        """
        await self._verify_portfolio_ownership(portfolio_id, user_id, db)

        # 检查标的数量上限
        count_result = await db.execute(
            select(func.count())
            .select_from(WatchlistItem)
            .where(WatchlistItem.portfolio_id == portfolio_id)
        )
        count = count_result.scalar() or 0
        if count >= MAX_ITEMS_PER_PORTFOLIO:
            raise AppException(
                detail=f"每个组合最多添加 {MAX_ITEMS_PER_PORTFOLIO} 个标的",
                code="ITEM_LIMIT_EXCEEDED",
                status_code=400,
            )

        # 检查标的是否已存在
        existing = await db.execute(
            select(WatchlistItem).where(
                WatchlistItem.portfolio_id == portfolio_id,
                WatchlistItem.symbol == data.symbol,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError(detail="该标的已在组合中", code="ITEM_ALREADY_EXISTS")

        # 计算排序顺序
        max_order = await db.execute(
            select(func.max(WatchlistItem.sort_order))
            .where(WatchlistItem.portfolio_id == portfolio_id)
        )
        next_order = (max_order.scalar() or -1) + 1

        item = WatchlistItem(
            portfolio_id=portfolio_id,
            symbol=data.symbol,
            name=data.name,
            market=data.market,
            sort_order=next_order,
        )
        db.add(item)
        await db.flush()

        return WatchlistItemResponse(
            id=item.id,
            portfolio_id=item.portfolio_id,
            symbol=item.symbol,
            name=item.name,
            market=item.market,
            sort_order=item.sort_order,
            created_at=item.created_at,
        )

    async def add_items_batch(
        self,
        portfolio_id: int,
        user_id: int,
        items_data: list[AddItemRequest],
        db: AsyncSession,
    ) -> list[WatchlistItemResponse]:
        """
        批量添加标的到组合（跳过已存在的）
        @param portfolio_id: 组合 ID
        @param user_id: 用户 ID
        @param items_data: 标的列表
        @param db: 数据库会话
        """
        await self._verify_portfolio_ownership(portfolio_id, user_id, db)

        # 获取已存在的标的
        result = await db.execute(
            select(WatchlistItem.symbol)
            .where(WatchlistItem.portfolio_id == portfolio_id)
        )
        existing_symbols = {row[0] for row in result.all()}

        # 过滤已存在的标的
        new_items_data = [d for d in items_data if d.symbol not in existing_symbols]
        if not new_items_data:
            return []

        # 检查数量上限
        current_count = len(existing_symbols)
        if current_count + len(new_items_data) > MAX_ITEMS_PER_PORTFOLIO:
            raise AppException(
                detail=f"超出标的数量上限（{MAX_ITEMS_PER_PORTFOLIO}）",
                code="ITEM_LIMIT_EXCEEDED",
                status_code=400,
            )

        # 计算起始排序
        max_order = await db.execute(
            select(func.max(WatchlistItem.sort_order))
            .where(WatchlistItem.portfolio_id == portfolio_id)
        )
        next_order = (max_order.scalar() or -1) + 1

        # 批量创建
        responses = []
        for i, data in enumerate(new_items_data):
            item = WatchlistItem(
                portfolio_id=portfolio_id,
                symbol=data.symbol,
                name=data.name,
                market=data.market,
                sort_order=next_order + i,
            )
            db.add(item)
            await db.flush()
            responses.append(WatchlistItemResponse(
                id=item.id,
                portfolio_id=item.portfolio_id,
                symbol=item.symbol,
                name=item.name,
                market=item.market,
                sort_order=item.sort_order,
                created_at=item.created_at,
            ))
        return responses

    async def remove_item(
        self, portfolio_id: int, item_id: int, user_id: int, db: AsyncSession
    ) -> None:
        """
        从组合移除标的
        @param portfolio_id: 组合 ID
        @param item_id: 标的记录 ID
        @param user_id: 用户 ID
        @param db: 数据库会话
        """
        await self._verify_portfolio_ownership(portfolio_id, user_id, db)

        result = await db.execute(
            select(WatchlistItem).where(
                WatchlistItem.id == item_id,
                WatchlistItem.portfolio_id == portfolio_id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise AppException(
                detail="标的不存在", code="ITEM_NOT_FOUND", status_code=404
            )

        await db.delete(item)
        await db.flush()

    async def reorder_items(
        self, portfolio_id: int, user_id: int, ids: list[int], db: AsyncSession
    ) -> None:
        """
        调整标的排序
        @param portfolio_id: 组合 ID
        @param user_id: 用户 ID
        @param ids: 按新顺序排列的标的 ID 列表
        @param db: 数据库会话
        """
        await self._verify_portfolio_ownership(portfolio_id, user_id, db)

        # 获取组合内所有标的
        result = await db.execute(
            select(WatchlistItem).where(WatchlistItem.portfolio_id == portfolio_id)
        )
        items = {item.id: item for item in result.scalars().all()}

        # 验证 ID 列表
        if set(ids) != set(items.keys()):
            raise AppException(
                detail="标的 ID 列表不匹配",
                code="INVALID_ITEM_IDS",
                status_code=400,
            )

        # 更新排序
        for order, item_id in enumerate(ids):
            items[item_id].sort_order = order
        await db.flush()

    async def _verify_portfolio_ownership(
        self, portfolio_id: int, user_id: int, db: AsyncSession
    ) -> Portfolio:
        """
        验证组合归属
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
