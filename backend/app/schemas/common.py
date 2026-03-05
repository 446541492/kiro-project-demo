"""
通用响应模型
统一的错误响应和成功响应格式
"""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """统一错误响应"""
    detail: str
    code: str


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
