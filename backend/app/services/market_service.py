"""
行情服务
处理行情榜单、标的搜索、行情查询，带内存缓存
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any, Optional

import pandas as pd

from app.clients.tushare_client import tushare_client
from app.core.exceptions import AppException
from app.schemas.market import StockQuoteResponse, SymbolInfoResponse

logger = logging.getLogger(__name__)


# ==================== 内存缓存 ====================

_cache: dict[str, dict[str, Any]] = {}

# 缓存过期时间配置（秒）
CACHE_TTL_RANKING = 30
CACHE_TTL_SEARCH = 300
CACHE_TTL_QUOTE = 15
CACHE_TTL_BASIC = 86400  # 24 小时


def _get_cache(key: str) -> Optional[Any]:
    """获取缓存，过期返回 None"""
    entry = _cache.get(key)
    if entry and time.time() < entry["expire_at"]:
        return entry["data"]
    if entry:
        del _cache[key]
    return None


def _set_cache(key: str, data: Any, ttl: int) -> None:
    """设置缓存"""
    _cache[key] = {"data": data, "expire_at": time.time() + ttl}


# ==================== 数据转换 ====================

def _get_trade_date() -> str:
    """获取当前交易日期（YYYYMMDD 格式）"""
    return datetime.now().strftime("%Y%m%d")


def _df_to_quotes(df: pd.DataFrame) -> list[StockQuoteResponse]:
    """将 DataFrame 转换为 StockQuoteResponse 列表"""
    if df.empty:
        return []

    quotes = []
    for _, row in df.iterrows():
        try:
            quotes.append(StockQuoteResponse(
                symbol=str(row.get("ts_code", "")),
                name=str(row.get("name", "")),
                current_price=float(row.get("close", 0) or 0),
                change_percent=float(row.get("pct_chg", 0) or 0),
                change_amount=float(row.get("change", 0) or 0),
                open_price=float(row.get("open", 0) or 0),
                high_price=float(row.get("high", 0) or 0),
                low_price=float(row.get("low", 0) or 0),
                pre_close=float(row.get("pre_close", 0) or 0),
                volume=float(row.get("vol", 0) or 0),
                amount=float(row.get("amount", 0) or 0),
                turnover_rate=float(row.get("turnover_rate", 0) or 0),
                pe_ratio=float(row.get("pe", 0) or 0),
                pb_ratio=float(row.get("pb", 0) or 0),
                market=_detect_market(str(row.get("ts_code", ""))),
            ))
        except Exception as e:
            logger.warning(f"数据转换失败: {e}")
            continue
    return quotes


def _detect_market(symbol: str) -> str:
    """根据标的代码判断市场"""
    if symbol.endswith(".SH"):
        return "沪市"
    elif symbol.endswith(".SZ"):
        return "深市"
    elif symbol.endswith(".HK"):
        return "港股"
    else:
        return "其他"


# ==================== 行情服务 ====================

class MarketService:
    """行情服务类"""

    async def get_rankings(
        self,
        ranking_type: str = "rise",
        market: Optional[str] = None,
        limit: int = 20,
    ) -> list[StockQuoteResponse]:
        """
        获取行情榜单
        @param ranking_type: 榜单类型 (rise/fall/volume/amount/turnover)
        @param market: 市场过滤
        @param limit: 返回数量，默认 20，最大 100
        """
        # 验证参数
        valid_types = {"rise", "fall", "volume", "amount", "turnover"}
        if ranking_type not in valid_types:
            raise AppException(
                detail="不支持的榜单类型",
                code="INVALID_RANKING_TYPE",
                status_code=422,
            )
        limit = min(max(1, limit), 100)

        # 检查缓存
        cache_key = f"ranking:{ranking_type}:{market}:{limit}"
        cached = _get_cache(cache_key)
        if cached:
            return cached

        try:
            trade_date = _get_trade_date()

            # 获取行情数据
            daily_df = tushare_client.get_daily_quotes(trade_date=trade_date)
            if daily_df.empty:
                return []

            # 获取基础信息（带缓存）
            basic_df = self._get_stock_basic_cached()

            # 合并数据
            if not basic_df.empty:
                daily_df = daily_df.merge(
                    basic_df[["ts_code", "name"]],
                    on="ts_code",
                    how="left",
                )

            # 获取每日指标（换手率、市盈率等）
            basic_daily = _get_cache("daily_basic")
            if basic_daily is None:
                try:
                    basic_daily_df = tushare_client.get_daily_basic(trade_date=trade_date)
                    if not basic_daily_df.empty:
                        _set_cache("daily_basic", basic_daily_df, CACHE_TTL_RANKING)
                        daily_df = daily_df.merge(
                            basic_daily_df[["ts_code", "turnover_rate", "pe", "pb"]],
                            on="ts_code",
                            how="left",
                        )
                except Exception:
                    pass
            elif isinstance(basic_daily, pd.DataFrame) and not basic_daily.empty:
                daily_df = daily_df.merge(
                    basic_daily[["ts_code", "turnover_rate", "pe", "pb"]],
                    on="ts_code",
                    how="left",
                )

            # 排序
            sort_map = {
                "rise": ("pct_chg", False),
                "fall": ("pct_chg", True),
                "volume": ("vol", False),
                "amount": ("amount", False),
                "turnover": ("turnover_rate", False),
            }
            sort_col, ascending = sort_map[ranking_type]
            if sort_col in daily_df.columns:
                daily_df = daily_df.sort_values(sort_col, ascending=ascending)

            # 截取
            daily_df = daily_df.head(limit)

            # 转换
            result = _df_to_quotes(daily_df)
            _set_cache(cache_key, result, CACHE_TTL_RANKING)
            return result

        except AppException:
            raise
        except Exception as e:
            logger.error(f"获取榜单失败: {e}")
            raise AppException(
                detail="行情数据获取失败，请稍后重试",
                code="MARKET_DATA_ERROR",
                status_code=502,
            )

    async def search_symbols(
        self,
        keyword: str,
        market: Optional[str] = None,
    ) -> list[SymbolInfoResponse]:
        """
        搜索标的
        @param keyword: 搜索关键词
        @param market: 市场过滤
        """
        if not keyword or not keyword.strip():
            raise AppException(
                detail="搜索关键词不能为空",
                code="EMPTY_KEYWORD",
                status_code=422,
            )
        keyword = keyword.strip()

        # 检查缓存
        cache_key = f"search:{keyword}:{market}"
        cached = _get_cache(cache_key)
        if cached:
            return cached

        try:
            basic_df = self._get_stock_basic_cached()
            if basic_df.empty:
                return []

            # 搜索过滤
            keyword_lower = keyword.lower()
            mask = (
                basic_df["ts_code"].str.lower().str.contains(keyword_lower, na=False)
                | basic_df["name"].str.contains(keyword, na=False)
            )
            filtered = basic_df[mask].head(20)

            result = []
            for _, row in filtered.iterrows():
                result.append(SymbolInfoResponse(
                    symbol=str(row.get("ts_code", "")),
                    name=str(row.get("name", "")),
                    market=_detect_market(str(row.get("ts_code", ""))),
                    industry=str(row.get("industry", "") or ""),
                    list_date=str(row.get("list_date", "") or ""),
                ))

            _set_cache(cache_key, result, CACHE_TTL_SEARCH)
            return result

        except AppException:
            raise
        except Exception as e:
            logger.error(f"搜索标的失败: {e}")
            raise AppException(
                detail="行情数据获取失败，请稍后重试",
                code="MARKET_DATA_ERROR",
                status_code=502,
            )

    async def get_quote(self, symbol: str) -> StockQuoteResponse:
        """
        获取单个标的行情
        @param symbol: 标的代码
        """
        # 检查缓存
        cache_key = f"quote:{symbol}"
        cached = _get_cache(cache_key)
        if cached:
            return cached

        try:
            trade_date = _get_trade_date()
            daily_df = tushare_client.get_daily_quotes(trade_date=trade_date)

            if daily_df.empty:
                raise AppException(
                    detail="未找到该标的", code="SYMBOL_NOT_FOUND", status_code=404
                )

            row = daily_df[daily_df["ts_code"] == symbol]
            if row.empty:
                raise AppException(
                    detail="未找到该标的", code="SYMBOL_NOT_FOUND", status_code=404
                )

            # 获取名称
            basic_df = self._get_stock_basic_cached()
            name = ""
            if not basic_df.empty:
                name_row = basic_df[basic_df["ts_code"] == symbol]
                if not name_row.empty:
                    name = str(name_row.iloc[0].get("name", ""))

            row_data = row.iloc[0]
            result = StockQuoteResponse(
                symbol=symbol,
                name=name,
                current_price=float(row_data.get("close", 0) or 0),
                change_percent=float(row_data.get("pct_chg", 0) or 0),
                change_amount=float(row_data.get("change", 0) or 0),
                open_price=float(row_data.get("open", 0) or 0),
                high_price=float(row_data.get("high", 0) or 0),
                low_price=float(row_data.get("low", 0) or 0),
                pre_close=float(row_data.get("pre_close", 0) or 0),
                volume=float(row_data.get("vol", 0) or 0),
                amount=float(row_data.get("amount", 0) or 0),
                market=_detect_market(symbol),
            )
            _set_cache(cache_key, result, CACHE_TTL_QUOTE)
            return result

        except AppException:
            raise
        except Exception as e:
            logger.error(f"获取标的行情失败: {e}")
            raise AppException(
                detail="行情数据获取失败，请稍后重试",
                code="MARKET_DATA_ERROR",
                status_code=502,
            )

    async def get_batch_quotes(
        self, symbols: list[str]
    ) -> list[StockQuoteResponse]:
        """
        批量获取标的行情
        @param symbols: 标的代码列表
        """
        if not symbols:
            return []

        # 分离缓存命中和未命中
        result_map: dict[str, StockQuoteResponse] = {}
        uncached = []
        for s in symbols:
            cached = _get_cache(f"quote:{s}")
            if cached:
                result_map[s] = cached
            else:
                uncached.append(s)

        # 批量查询未缓存的
        if uncached:
            try:
                trade_date = _get_trade_date()
                daily_df = tushare_client.get_daily_quotes(trade_date=trade_date)
                basic_df = self._get_stock_basic_cached()

                if not daily_df.empty:
                    filtered = daily_df[daily_df["ts_code"].isin(uncached)]
                    if not basic_df.empty:
                        filtered = filtered.merge(
                            basic_df[["ts_code", "name"]], on="ts_code", how="left"
                        )
                    quotes = _df_to_quotes(filtered)
                    for q in quotes:
                        result_map[q.symbol] = q
                        _set_cache(f"quote:{q.symbol}", q, CACHE_TTL_QUOTE)
            except Exception as e:
                logger.error(f"批量获取行情失败: {e}")

        # 按输入顺序返回
        return [result_map[s] for s in symbols if s in result_map]

    def _get_stock_basic_cached(self) -> pd.DataFrame:
        """获取股票基础信息（带 24 小时缓存）"""
        cached = _get_cache("stock_basic")
        if cached is not None:
            return cached
        try:
            df = tushare_client.get_stock_basic()
            _set_cache("stock_basic", df, CACHE_TTL_BASIC)
            return df
        except Exception as e:
            logger.error(f"获取股票基础信息失败: {e}")
            return pd.DataFrame()
