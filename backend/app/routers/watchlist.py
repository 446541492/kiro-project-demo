"""
自选标的路由
处理组合内标的的增删和排序
每次自选变更后，通过响应头 X-New-Token 返回包含最新自选快照的新 Token
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.deps import get_current_active_user
from app.core.memory_store import UserData
from app.core.security import create_access_token, create_token_data_with_watchlist
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


def _make_response_with_new_token(data, user: UserData, status_code: int = 200):
    """构建带新 Token 的响应"""
    token_data = create_token_data_with_watchlist(user.id, user.username)
    new_token = create_access_token(token_data)
    if hasattr(data, "model_dump"):
        body = data.model_dump(mode="json")
    elif isinstance(data, list):
        body = [item.model_dump(mode="json") if hasattr(item, "model_dump") else item for item in data]
    elif isinstance(data, dict):
        body = data
    else:
        body = data
    resp = JSONResponse(content=body, status_code=status_code)
    resp.headers["X-New-Token"] = new_token
    return resp


@router.get("", response_model=list[WatchlistItemResponse])
async def get_items(
    portfolio_id: int,
    current_user: UserData = Depends(get_current_active_user),
):
    """获取组合内所有标的（含实时行情）"""
    return await watchlist_service.get_items(portfolio_id, current_user.id)


@router.post("", status_code=201)
async def add_item(
    portfolio_id: int,
    data: AddItemRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """添加标的到组合"""
    result = await watchlist_service.add_item(portfolio_id, current_user.id, data)
    return _make_response_with_new_token(result, current_user, 201)


@router.post("/batch", status_code=201)
async def add_items_batch(
    portfolio_id: int,
    data: AddItemsBatchRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """批量添加标的到组合"""
    result = await watchlist_service.add_items_batch(
        portfolio_id, current_user.id, data.items
    )
    return _make_response_with_new_token(result, current_user, 201)


@router.put("/reorder")
async def reorder_items(
    portfolio_id: int,
    data: ReorderItemsRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """调整标的排序"""
    await watchlist_service.reorder_items(portfolio_id, current_user.id, data.ids)
    return _make_response_with_new_token(
        {"message": "排序更新成功"}, current_user
    )


@router.delete("/{item_id}")
async def remove_item(
    portfolio_id: int,
    item_id: int,
    current_user: UserData = Depends(get_current_active_user),
):
    """从组合移除标的"""
    await watchlist_service.remove_item(portfolio_id, item_id, current_user.id)
    return _make_response_with_new_token(
        {"message": "标的移除成功"}, current_user
    )
