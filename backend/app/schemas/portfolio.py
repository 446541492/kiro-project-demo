"""
自选组合请求/响应模型
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ==================== 请求模型 ====================

class CreatePortfolioRequest(BaseModel):
    """创建组合请求"""
    name: str = Field(..., min_length=1, max_length=50, description="组合名称")


class UpdatePortfolioRequest(BaseModel):
    """更新组合请求"""
    name: str = Field(..., min_length=1, max_length=50, description="新组合名称")


class ReorderPortfoliosRequest(BaseModel):
    """组合排序请求"""
    ids: list[int] = Field(..., min_length=1, description="按新顺序排列的组合 ID 列表")


# ==================== 响应模型 ====================

class PortfolioResponse(BaseModel):
    """组合响应"""
    id: int
    name: str
    sort_order: int
    is_default: bool
    item_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
