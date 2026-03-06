"""
自选标的路由
处理组合内标的的增删和排序
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_active_user
from app.core.memory_store import UserData
from app.schemas.common import MessageResponse
from app.schemas.watchlist import (
    AddItemRequest,
    AddItemsBatchRequest,
    ReorderItemsRequest,
    WatchlistItemResponse,
)
from app.services.watchlist_service import WatchlistService

router = APIRouter(prefix="/api/portfolios/{portfolio_id}/items", tags=["自选标的"])

watchlist_service = WatchlistService()


@router.get("", response_model=list[WatchlistItemResponse])
async def get_items(
    portfolio_id: int,
    current_user: UserData = Depends(get_current_active_user),
):
    """获取组合内所有标的（含实时行情）"""
    return await watchlist_service.get_items(portfolio_id, current_user.id)


@router.post("", response_model=WatchlistItemResponse, status_code=201)
async def add_item(
    portfolio_id: int,
    data: AddItemRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """添加标的到组合"""
    return await watchlist_service.add_item(portfolio_id, current_user.id, data)


@router.post("/batch", response_model=list[WatchlistItemResponse], status_code=201)
async def add_items_batch(
    portfolio_id: int,
    data: AddItemsBatchRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """批量添加标的到组合"""
    return await watchlist_service.add_items_batch(
        portfolio_id, current_user.id, data.items
    )


@router.put("/reorder", response_model=MessageResponse)
async def reorder_items(
    portfolio_id: int,
    data: ReorderItemsRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """调整标的排序"""
    await watchlist_service.reorder_items(portfolio_id, current_user.id, data.ids)
    return MessageResponse(message="排序更新成功")


@router.delete("/{item_id}", response_model=MessageResponse)
async def remove_item(
    portfolio_id: int,
    item_id: int,
    current_user: UserData = Depends(get_current_active_user),
):
    """从组合移除标的"""
    await watchlist_service.remove_item(portfolio_id, item_id, current_user.id)
    return MessageResponse(message="标的移除成功")
