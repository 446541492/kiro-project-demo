"""
行情 API 路由
包含榜单、搜索、标的行情等端点
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_active_user
from app.core.memory_store import UserData
from app.schemas.market import KlineDataResponse, StockQuoteResponse, SymbolInfoResponse
from app.services.market_service import MarketService

router = APIRouter(prefix="/api/market", tags=["行情"])


@router.get("/rankings", response_model=list[StockQuoteResponse], summary="获取行情榜单")
async def get_rankings(
    ranking_type: str = Query("rise", description="榜单类型: rise/fall/volume/amount/turnover"),
    market: Optional[str] = Query(None, description="市场过滤: SH/SZ"),
    limit: int = Query(20, description="返回数量，最大 100"),
    current_user: UserData = Depends(get_current_active_user),
):
    """获取行情榜单数据"""
    service = MarketService()
    return await service.get_rankings(ranking_type, market, limit)


@router.get("/search", response_model=list[SymbolInfoResponse], summary="搜索标的")
async def search_symbols(
    keyword: str = Query(..., description="搜索关键词"),
    market: Optional[str] = Query(None, description="市场过滤"),
    current_user: UserData = Depends(get_current_active_user),
):
    """搜索标的（支持代码、名称）"""
    service = MarketService()
    return await service.search_symbols(keyword, market)


@router.get("/quote/{symbol}", response_model=StockQuoteResponse, summary="获取标的行情")
async def get_quote(
    symbol: str,
    current_user: UserData = Depends(get_current_active_user),
):
    """获取单个标的详细行情"""
    service = MarketService()
    return await service.get_quote(symbol)


@router.get("/kline/{symbol}", response_model=list[KlineDataResponse], summary="获取K线数据")
async def get_kline(
    symbol: str,
    period: str = Query("daily", description="周期: daily/weekly/monthly"),
    limit: int = Query(120, description="数据条数，最大 300"),
    current_user: UserData = Depends(get_current_active_user),
):
    """获取标的K线数据"""
    service = MarketService()
    return await service.get_kline(symbol, period, min(limit, 300))
