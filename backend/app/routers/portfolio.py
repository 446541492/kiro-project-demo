"""
自选组合路由
处理组合的增删改查和排序
每次自选变更后，通过响应头 X-New-Token 返回包含最新自选快照的新 Token
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.deps import get_current_active_user
from app.core.memory_store import UserData
from app.core.security import create_access_token, create_token_data_with_watchlist
from app.schemas.common import MessageResponse
from app.schemas.portfolio import (
    CreatePortfolioRequest,
    PortfolioResponse,
    ReorderPortfoliosRequest,
    UpdatePortfolioRequest,
)
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/api/portfolios", tags=["自选组合"])

portfolio_service = PortfolioService()


def _make_response_with_new_token(data, user: UserData, status_code: int = 200):
    """构建带新 Token 的响应"""
    token_data = create_token_data_with_watchlist(user.id, user.username)
    new_token = create_access_token(token_data)
    if hasattr(data, "model_dump"):
        body = data.model_dump(mode="json")
    elif isinstance(data, dict):
        body = data
    else:
        body = data
    resp = JSONResponse(content=body, status_code=status_code)
    resp.headers["X-New-Token"] = new_token
    return resp


@router.get("", response_model=list[PortfolioResponse])
async def get_portfolios(current_user: UserData = Depends(get_current_active_user)):
    """获取用户所有自选组合"""
    return await portfolio_service.get_portfolios(current_user.id)


@router.post("", status_code=201)
async def create_portfolio(
    data: CreatePortfolioRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """创建新自选组合"""
    result = await portfolio_service.create_portfolio(current_user.id, data)
    return _make_response_with_new_token(result, current_user, 201)


@router.put("/reorder")
async def reorder_portfolios(
    data: ReorderPortfoliosRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """调整组合排序"""
    await portfolio_service.reorder_portfolios(current_user.id, data.ids)
    return _make_response_with_new_token(
        {"message": "排序更新成功"}, current_user
    )


@router.put("/{portfolio_id}")
async def update_portfolio(
    portfolio_id: int,
    data: UpdatePortfolioRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """更新组合信息（重命名）"""
    result = await portfolio_service.update_portfolio(
        portfolio_id, current_user.id, data
    )
    return _make_response_with_new_token(result, current_user)


@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: int,
    current_user: UserData = Depends(get_current_active_user),
):
    """删除组合（默认组合不可删除）"""
    await portfolio_service.delete_portfolio(portfolio_id, current_user.id)
    return _make_response_with_new_token(
        {"message": "组合删除成功"}, current_user
    )
