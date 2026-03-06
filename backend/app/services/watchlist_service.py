"""
自选标的服务
处理组合内标的的增删、排序、行情合并
"""

from __future__ import annotations

import logging

from app.core.exceptions import AppException, ConflictError
from app.core.memory_store import store
from app.schemas.watchlist import AddItemRequest, WatchlistItemResponse
from app.services.market_service import MarketService

logger = logging.getLogger(__name__)

MAX_ITEMS_PER_PORTFOLIO = 200
market_service = MarketService()


class WatchlistService:
    """自选标的服务类"""

    async def get_items(
        self, portfolio_id: int, user_id: int
    ) -> list[WatchlistItemResponse]:
        """获取组合内所有标的（含实时行情）"""
        self._verify_portfolio_ownership(portfolio_id, user_id)
        items = store.get_portfolio_items(portfolio_id)
        if not items:
            return []

        # 批量获取实时行情（使用新浪财经）
        symbols = [item.symbol for item in items]
        quote_map = {}
        try:
            quotes = await market_service.get_batch_quotes(symbols)
            for q in quotes:
                quote_map[q.symbol] = q
        except Exception as e:
            logger.warning(f"获取实时行情失败: {e}")

        return [
            WatchlistItemResponse(
                id=item.id, portfolio_id=item.portfolio_id,
                symbol=item.symbol, name=item.name, market=item.market,
                sort_order=item.sort_order, quote=quote_map.get(item.symbol),
                created_at=item.created_at,
            )
            for item in items
        ]

    async def add_item(
        self, portfolio_id: int, user_id: int, data: AddItemRequest
    ) -> WatchlistItemResponse:
        """添加标的到组合"""
        self._verify_portfolio_ownership(portfolio_id, user_id)

        if store.get_portfolio_item_count(portfolio_id) >= MAX_ITEMS_PER_PORTFOLIO:
            raise AppException(
                detail=f"每个组合最多添加 {MAX_ITEMS_PER_PORTFOLIO} 个标的",
                code="ITEM_LIMIT_EXCEEDED", status_code=400,
            )

        if store.get_portfolio_item_by_symbol(portfolio_id, data.symbol):
            raise ConflictError(detail="该标的已在组合中", code="ITEM_ALREADY_EXISTS")

        items = store.get_portfolio_items(portfolio_id)
        next_order = max((i.sort_order for i in items), default=-1) + 1

        item = store.add_watchlist_item(
            portfolio_id=portfolio_id, symbol=data.symbol,
            name=data.name, market=data.market, sort_order=next_order,
        )
        return WatchlistItemResponse(
            id=item.id, portfolio_id=item.portfolio_id,
            symbol=item.symbol, name=item.name, market=item.market,
            sort_order=item.sort_order, created_at=item.created_at,
        )

    async def add_items_batch(
        self, portfolio_id: int, user_id: int, items_data: list[AddItemRequest]
    ) -> list[WatchlistItemResponse]:
        """批量添加标的到组合（跳过已存在的）"""
        self._verify_portfolio_ownership(portfolio_id, user_id)

        existing_symbols = {
            item.symbol for item in store.get_portfolio_items(portfolio_id)
        }
        new_items_data = [d for d in items_data if d.symbol not in existing_symbols]
        if not new_items_data:
            return []

        current_count = len(existing_symbols)
        if current_count + len(new_items_data) > MAX_ITEMS_PER_PORTFOLIO:
            raise AppException(
                detail=f"超出标的数量上限（{MAX_ITEMS_PER_PORTFOLIO}）",
                code="ITEM_LIMIT_EXCEEDED", status_code=400,
            )

        items = store.get_portfolio_items(portfolio_id)
        next_order = max((i.sort_order for i in items), default=-1) + 1

        responses = []
        for i, data in enumerate(new_items_data):
            item = store.add_watchlist_item(
                portfolio_id=portfolio_id, symbol=data.symbol,
                name=data.name, market=data.market, sort_order=next_order + i,
            )
            responses.append(WatchlistItemResponse(
                id=item.id, portfolio_id=item.portfolio_id,
                symbol=item.symbol, name=item.name, market=item.market,
                sort_order=item.sort_order, created_at=item.created_at,
            ))
        return responses

    async def remove_item(
        self, portfolio_id: int, item_id: int, user_id: int
    ) -> None:
        """从组合移除标的"""
        self._verify_portfolio_ownership(portfolio_id, user_id)
        item = store.get_watchlist_item(item_id)
        if not item or item.portfolio_id != portfolio_id:
            raise AppException(
                detail="标的不存在", code="ITEM_NOT_FOUND", status_code=404
            )
        store.delete_watchlist_item(item_id)

    async def reorder_items(
        self, portfolio_id: int, user_id: int, ids: list[int]
    ) -> None:
        """调整标的排序"""
        self._verify_portfolio_ownership(portfolio_id, user_id)
        items = {item.id: item for item in store.get_portfolio_items(portfolio_id)}
        if set(ids) != set(items.keys()):
            raise AppException(
                detail="标的 ID 列表不匹配", code="INVALID_ITEM_IDS", status_code=400
            )
        for order, item_id in enumerate(ids):
            items[item_id].sort_order = order
        store.save()

    def _verify_portfolio_ownership(self, portfolio_id: int, user_id: int):
        """验证组合归属"""
        portfolio = store.get_portfolio(portfolio_id)
        if not portfolio or portfolio.user_id != user_id:
            raise AppException(
                detail="组合不存在", code="PORTFOLIO_NOT_FOUND", status_code=404
            )
