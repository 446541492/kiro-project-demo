"""
数据模型包
导出所有 SQLAlchemy 模型，确保 Base.metadata 包含所有表定义
"""

from app.models.base import Base
from app.models.user import User
from app.models.device import Device
from app.models.recovery_code import RecoveryCode
from app.models.portfolio import Portfolio
from app.models.watchlist_item import WatchlistItem

__all__ = ["Base", "User", "Device", "RecoveryCode", "Portfolio", "WatchlistItem"]
