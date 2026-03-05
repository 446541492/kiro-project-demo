"""
行情服务
处理行情榜单、标的搜索、行情查询，带内存缓存
数据源：新浪财经（免费，无需 Token）
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

import pandas as pd

from app.clients.sina_client import sina_client
from app.core.exceptions import AppException
from app.schemas.market import StockQuoteResponse, SymbolInfoResponse

logger = logging.getLogger(__name__)


# ==================== 内存缓存 ====================

_cache: dict[str, dict[str, Any]] = {}

CACHE_TTL_RANKING = 30
CACHE_TTL_SEARCH = 300
CACHE_TTL_QUOTE = 15
CACHE_TTL_STOCK_LIST = 86400  # 股票列表缓存 24 小时


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

def _detect_market(symbol: str) -> str:
    """根据标的代码判断市场"""
    if symbol.endswith(".SH"):
        return "沪市"
    elif symbol.endswith(".SZ"):
        return "深市"
    elif symbol.endswith(".BJ"):
        return "北交所"
    else:
        return "其他"


def _list_row_to_quote(row: dict) -> StockQuoteResponse:
    """将新浪列表接口的一行数据转换为 StockQuoteResponse"""
    ts_code = str(row.get("ts_code", row.get("symbol", "")))
    return StockQuoteResponse(
        symbol=ts_code,
        name=str(row.get("name", "")),
        current_price=float(row.get("trade", 0) or 0),
        change_percent=float(row.get("changepercent", 0) or 0),
        change_amount=float(row.get("pricechange", 0) or 0),
        open_price=float(row.get("open", 0) or 0),
        high_price=float(row.get("high", 0) or 0),
        low_price=float(row.get("low", 0) or 0),
        pre_close=float(row.get("settlement", 0) or 0),
        volume=float(row.get("volume", 0) or 0),
        amount=float(row.get("amount", 0) or 0),
        turnover_rate=float(row.get("turnoverratio", 0) or 0),
        pe_ratio=float(row.get("per", 0) or 0),
        pb_ratio=float(row.get("pb", 0) or 0),
        market=_detect_market(ts_code),
    )


def _hq_row_to_quote(row: pd.Series) -> StockQuoteResponse:
    """将 hq.sinajs.cn 解析后的一行数据转换为 StockQuoteResponse"""
    ts_code = str(row.get("ts_code", ""))
    return StockQuoteResponse(
        symbol=ts_code,
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
        market=_detect_market(ts_code),
    )


# ==================== 行情服务 ====================

# 新浪排序字段映射
_SORT_MAP = {
    "rise": ("changepercent", 0),     # 涨幅榜，降序
    "fall": ("changepercent", 1),     # 跌幅榜，升序
    "volume": ("volume", 0),          # 成交量榜
    "amount": ("amount", 0),          # 成交额榜
    "turnover": ("turnoverratio", 0), # 换手率榜
}

# 新浪板块节点映射
_MARKET_NODE_MAP = {
    "SH": "sh_a",
    "SZ": "sz_a",
    None: "hs_a",
}


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
        @param market: 市场过滤: SH/SZ
        @param limit: 返回数量，默认 20，最大 100
        """
        valid_types = set(_SORT_MAP.keys())
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
            sort_field, asc = _SORT_MAP[ranking_type]
            node = _MARKET_NODE_MAP.get(market, "hs_a")

            # 新浪列表接口直接支持排序和分页，一次请求搞定
            df = sina_client.get_multi_page_list(
                node=node, sort=sort_field, asc=asc, total=limit
            )
            if df.empty:
                return []

            result = []
            for _, row in df.iterrows():
                try:
                    result.append(_list_row_to_quote(row.to_dict()))
                except Exception as e:
                    logger.warning(f"数据转换失败: {e}")
                    continue

            result = result[:limit]
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

        cache_key = f"search:{keyword}:{market}"
        cached = _get_cache(cache_key)
        if cached:
            return cached

        try:
            # 获取股票列表用于搜索（大列表，带长缓存）
            stock_list = self._get_stock_list_cached()
            if stock_list.empty:
                return []

            keyword_lower = keyword.lower()
            mask = pd.Series([False] * len(stock_list), index=stock_list.index)
            if "code" in stock_list.columns:
                mask = mask | stock_list["code"].str.contains(keyword_lower, na=False)
            if "symbol" in stock_list.columns:
                mask = mask | stock_list["symbol"].str.contains(keyword_lower, na=False)
            if "name" in stock_list.columns:
                mask = mask | stock_list["name"].str.contains(keyword, na=False)

            filtered = stock_list[mask].head(20)

            result = []
            for _, row in filtered.iterrows():
                ts_code = str(row.get("ts_code", row.get("symbol", "")))
                result.append(SymbolInfoResponse(
                    symbol=ts_code,
                    name=str(row.get("name", "")),
                    market=_detect_market(ts_code),
                    industry="",
                    list_date="",
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
        @param symbol: 标的代码（如 600519.SH）
        """
        cache_key = f"quote:{symbol}"
        cached = _get_cache(cache_key)
        if cached:
            return cached

        try:
            df = sina_client.get_quotes_by_symbols([symbol])
            if df.empty:
                raise AppException(
                    detail="未找到该标的", code="SYMBOL_NOT_FOUND", status_code=404
                )

            row = df.iloc[0]
            result = _hq_row_to_quote(row)
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

        if uncached:
            try:
                df = sina_client.get_quotes_by_symbols(uncached)
                if not df.empty:
                    for _, row in df.iterrows():
                        q = _hq_row_to_quote(row)
                        result_map[q.symbol] = q
                        _set_cache(f"quote:{q.symbol}", q, CACHE_TTL_QUOTE)
            except Exception as e:
                logger.error(f"批量获取行情失败: {e}")

        return [result_map[s] for s in symbols if s in result_map]

    def _get_stock_list_cached(self) -> pd.DataFrame:
        """获取全量股票列表（带 24 小时缓存，用于搜索）"""
        cached = _get_cache("stock_list_all")
        if cached is not None:
            return cached
        try:
            # 获取较大数量的股票列表用于搜索
            df = sina_client.get_multi_page_list(
                node="hs_a", sort="symbol", asc=1, total=6000
            )
            if not df.empty:
                _set_cache("stock_list_all", df, CACHE_TTL_STOCK_LIST)
            return df
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
