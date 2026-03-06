"""
自选组合路由
处理组合的增删改查和排序
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_active_user
from app.core.memory_store import UserData
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


@router.get("", response_model=list[PortfolioResponse])
async def get_portfolios(current_user: UserData = Depends(get_current_active_user)):
    """获取用户所有自选组合"""
    return await portfolio_service.get_portfolios(current_user.id)


@router.post("", response_model=PortfolioResponse, status_code=201)
async def create_portfolio(
    data: CreatePortfolioRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """创建新自选组合"""
    return await portfolio_service.create_portfolio(current_user.id, data)


@router.put("/reorder", response_model=MessageResponse)
async def reorder_portfolios(
    data: ReorderPortfoliosRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """调整组合排序"""
    await portfolio_service.reorder_portfolios(current_user.id, data.ids)
    return MessageResponse(message="排序更新成功")


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    data: UpdatePortfolioRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """更新组合信息（重命名）"""
    return await portfolio_service.update_portfolio(portfolio_id, current_user.id, data)


@router.delete("/{portfolio_id}", response_model=MessageResponse)
async def delete_portfolio(
    portfolio_id: int,
    current_user: UserData = Depends(get_current_active_user),
):
    """删除组合（默认组合不可删除）"""
    await portfolio_service.delete_portfolio(portfolio_id, current_user.id)
    return MessageResponse(message="组合删除成功")
