"""
自选标的路由
处理组合内标的的增删和排序
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
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
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取组合内所有标的（含实时行情）"""
    return await watchlist_service.get_items(portfolio_id, current_user.id, db)


@router.post("", response_model=WatchlistItemResponse, status_code=201)
async def add_item(
    portfolio_id: int,
    data: AddItemRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """添加标的到组合"""
    return await watchlist_service.add_item(portfolio_id, current_user.id, data, db)


@router.post("/batch", response_model=list[WatchlistItemResponse], status_code=201)
async def add_items_batch(
    portfolio_id: int,
    data: AddItemsBatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """批量添加标的到组合"""
    return await watchlist_service.add_items_batch(
        portfolio_id, current_user.id, data.items, db
    )


@router.put("/reorder", response_model=MessageResponse)
async def reorder_items(
    portfolio_id: int,
    data: ReorderItemsRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """调整标的排序"""
    await watchlist_service.reorder_items(portfolio_id, current_user.id, data.ids, db)
    return MessageResponse(message="排序更新成功")


@router.delete("/{item_id}", response_model=MessageResponse)
async def remove_item(
    portfolio_id: int,
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """从组合移除标的"""
    await watchlist_service.remove_item(portfolio_id, item_id, current_user.id, db)
    return MessageResponse(message="标的移除成功")
