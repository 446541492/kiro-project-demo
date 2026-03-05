"""
行情相关 Pydantic 请求/响应模型
"""

from pydantic import BaseModel


class StockQuoteResponse(BaseModel):
    """股票行情响应"""
    symbol: str
    name: str
    current_price: float = 0.0
    change_percent: float = 0.0
    change_amount: float = 0.0
    open_price: float = 0.0
    high_price: float = 0.0
    low_price: float = 0.0
    pre_close: float = 0.0
    volume: float = 0.0
    amount: float = 0.0
    turnover_rate: float = 0.0
    pe_ratio: float = 0.0
    pb_ratio: float = 0.0
    market: str = ""


class KlineDataResponse(BaseModel):
    """K线数据响应"""
    day: str
    open: str
    high: str
    low: str
    close: str
    volume: str


class SymbolInfoResponse(BaseModel):
    """标的基础信息响应"""
    symbol: str
    name: str
    market: str = ""
    industry: str = ""
    list_date: str = ""
