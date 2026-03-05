"""
自选标的请求/响应模型
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.market import StockQuoteResponse


# ==================== 请求模型 ====================

class AddItemRequest(BaseModel):
    """添加标的请求"""
    symbol: str = Field(..., min_length=1, max_length=20, description="标的代码")
    name: str = Field(..., min_length=1, max_length=50, description="标的名称")
    market: str = Field(..., min_length=1, max_length=20, description="市场")


class AddItemsBatchRequest(BaseModel):
    """批量添加标的请求"""
    items: list[AddItemRequest] = Field(..., min_length=1, max_length=50, description="标的列表")


class ReorderItemsRequest(BaseModel):
    """标的排序请求"""
    ids: list[int] = Field(..., min_length=1, description="按新顺序排列的标的 ID 列表")


# ==================== 响应模型 ====================

class WatchlistItemResponse(BaseModel):
    """标的响应"""
    id: int
    portfolio_id: int
    symbol: str
    name: str
    market: str
    sort_order: int
    quote: Optional[StockQuoteResponse] = None
    created_at: datetime

    model_config = {"from_attributes": True}
