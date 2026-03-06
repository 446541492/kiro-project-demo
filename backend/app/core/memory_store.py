"""
内存存储模块
替代 SQLAlchemy + SQLite，使用纯 Python 字典存储数据
适用于 Vercel serverless 环境（无持久化需求）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Optional


# ==================== 数据模型 ====================

@dataclass
class UserData:
    """用户数据"""
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    password_hash: str = ""
    is_active: bool = True
    is_2fa_enabled: bool = False
    totp_secret: Optional[str] = None
    failed_login_count: int = 0
    locked_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DeviceData:
    """设备数据"""
    id: int
    user_id: int
    device_id: str
    device_name: str
    ip_address: Optional[str] = None
    last_login_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RecoveryCodeData:
    """恢复码数据"""
    id: int
    user_id: int
    code: str
    is_used: bool = False
    used_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PortfolioData:
    """自选组合数据"""
    id: int
    user_id: int
    name: str
    sort_order: int = 0
    is_default: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class WatchlistItemData:
    """自选标的数据"""
    id: int
    portfolio_id: int
    symbol: str
    name: str
    market: str
    sort_order: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== 内存存储 ====================

class MemoryStore:
    """
    线程安全的内存存储
    所有数据存储在字典中，通过自增 ID 索引
    """

    def __init__(self):
        self._lock = Lock()
        # 自增 ID 计数器
        self._next_user_id = 1
        self._next_device_id = 1
        self._next_recovery_code_id = 1
        self._next_portfolio_id = 1
        self._next_watchlist_item_id = 1
        # 数据存储: {id: data}
        self.users: dict[int, UserData] = {}
        self.devices: dict[int, DeviceData] = {}
        self.recovery_codes: dict[int, RecoveryCodeData] = {}
        self.portfolios: dict[int, PortfolioData] = {}
        self.watchlist_items: dict[int, WatchlistItemData] = {}

    # ==================== 用户 ====================

    def add_user(self, **kwargs) -> UserData:
        """添加用户"""
        with self._lock:
            user = UserData(id=self._next_user_id, **kwargs)
            self.users[user.id] = user
            self._next_user_id += 1
            return user

    def get_user_by_id(self, user_id: int) -> Optional[UserData]:
        """按 ID 查找用户"""
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[UserData]:
        """按用户名查找用户（不区分大小写）"""
        username_lower = username.lower()
        for user in self.users.values():
            if user.username.lower() == username_lower:
                return user
        return None

    def get_user_by_email(self, email: str) -> Optional[UserData]:
        """按邮箱查找用户（不区分大小写）"""
        email_lower = email.lower()
        for user in self.users.values():
            if user.email and user.email.lower() == email_lower:
                return user
        return None

    def get_user_by_phone(self, phone: str) -> Optional[UserData]:
        """按手机号查找用户"""
        for user in self.users.values():
            if user.phone == phone:
                return user
        return None

    # ==================== 设备 ====================

    def add_device(self, **kwargs) -> DeviceData:
        """添加设备"""
        with self._lock:
            device = DeviceData(id=self._next_device_id, **kwargs)
            self.devices[device.id] = device
            self._next_device_id += 1
            return device

    def get_device(self, user_id: int, device_id: str) -> Optional[DeviceData]:
        """查找用户的指定设备"""
        for device in self.devices.values():
            if device.user_id == user_id and device.device_id == device_id:
                return device
        return None

    def get_user_devices(self, user_id: int) -> list[DeviceData]:
        """获取用户所有设备（按最后登录时间倒序）"""
        devices = [d for d in self.devices.values() if d.user_id == user_id]
        devices.sort(key=lambda d: d.last_login_at, reverse=True)
        return devices

    # ==================== 恢复码 ====================

    def add_recovery_code(self, **kwargs) -> RecoveryCodeData:
        """添加恢复码"""
        with self._lock:
            rc = RecoveryCodeData(id=self._next_recovery_code_id, **kwargs)
            self.recovery_codes[rc.id] = rc
            self._next_recovery_code_id += 1
            return rc

    def get_valid_recovery_code(self, user_id: int, code: str) -> Optional[RecoveryCodeData]:
        """查找未使用的恢复码"""
        for rc in self.recovery_codes.values():
            if rc.user_id == user_id and rc.code == code.upper() and not rc.is_used:
                return rc
        return None

    def get_unused_recovery_codes(self, user_id: int) -> list[str]:
        """获取用户未使用的恢复码"""
        return [
            rc.code for rc in self.recovery_codes.values()
            if rc.user_id == user_id and not rc.is_used
        ]

    def delete_user_recovery_codes(self, user_id: int) -> None:
        """删除用户所有恢复码"""
        to_delete = [
            rc_id for rc_id, rc in self.recovery_codes.items()
            if rc.user_id == user_id
        ]
        for rc_id in to_delete:
            del self.recovery_codes[rc_id]

    # ==================== 组合 ====================

    def add_portfolio(self, **kwargs) -> PortfolioData:
        """添加组合"""
        with self._lock:
            portfolio = PortfolioData(id=self._next_portfolio_id, **kwargs)
            self.portfolios[portfolio.id] = portfolio
            self._next_portfolio_id += 1
            return portfolio

    def get_portfolio(self, portfolio_id: int) -> Optional[PortfolioData]:
        """按 ID 查找组合"""
        return self.portfolios.get(portfolio_id)

    def get_user_portfolios(self, user_id: int) -> list[PortfolioData]:
        """获取用户所有组合（按排序顺序）"""
        portfolios = [p for p in self.portfolios.values() if p.user_id == user_id]
        portfolios.sort(key=lambda p: p.sort_order)
        return portfolios

    def delete_portfolio(self, portfolio_id: int) -> None:
        """删除组合及其标的"""
        self.portfolios.pop(portfolio_id, None)
        # 级联删除标的
        to_delete = [
            item_id for item_id, item in self.watchlist_items.items()
            if item.portfolio_id == portfolio_id
        ]
        for item_id in to_delete:
            del self.watchlist_items[item_id]

    # ==================== 标的 ====================

    def add_watchlist_item(self, **kwargs) -> WatchlistItemData:
        """添加标的"""
        with self._lock:
            item = WatchlistItemData(id=self._next_watchlist_item_id, **kwargs)
            self.watchlist_items[item.id] = item
            self._next_watchlist_item_id += 1
            return item

    def get_watchlist_item(self, item_id: int) -> Optional[WatchlistItemData]:
        """按 ID 查找标的"""
        return self.watchlist_items.get(item_id)

    def get_portfolio_items(self, portfolio_id: int) -> list[WatchlistItemData]:
        """获取组合内所有标的（按排序顺序）"""
        items = [
            item for item in self.watchlist_items.values()
            if item.portfolio_id == portfolio_id
        ]
        items.sort(key=lambda i: i.sort_order)
        return items

    def get_portfolio_item_count(self, portfolio_id: int) -> int:
        """获取组合内标的数量"""
        return sum(
            1 for item in self.watchlist_items.values()
            if item.portfolio_id == portfolio_id
        )

    def get_portfolio_item_by_symbol(
        self, portfolio_id: int, symbol: str
    ) -> Optional[WatchlistItemData]:
        """查找组合内指定标的"""
        for item in self.watchlist_items.values():
            if item.portfolio_id == portfolio_id and item.symbol == symbol:
                return item
        return None

    def delete_watchlist_item(self, item_id: int) -> None:
        """删除标的"""
        self.watchlist_items.pop(item_id, None)


# 全局单例
store = MemoryStore()
