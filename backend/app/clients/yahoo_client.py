"""
Yahoo Finance 客户端
全球可访问，用于标的搜索和自选行情获取（解决 Vercel 海外访问新浪被 403 问题）
内置 A 股热门股票列表，通过本地匹配实现搜索
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Yahoo Finance API
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
YAHOO_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

# A 股热门股票列表（用于搜索匹配）
A_STOCK_LIST: list[dict] = [
    {"code": "600519", "name": "贵州茅台", "market": "SH"},
    {"code": "000858", "name": "五粮液", "market": "SZ"},
    {"code": "601318", "name": "中国平安", "market": "SH"},
    {"code": "600036", "name": "招商银行", "market": "SH"},
    {"code": "000333", "name": "美的集团", "market": "SZ"},
    {"code": "600276", "name": "恒瑞医药", "market": "SH"},
    {"code": "601166", "name": "兴业银行", "market": "SH"},
    {"code": "000001", "name": "平安银行", "market": "SZ"},
    {"code": "600900", "name": "长江电力", "market": "SH"},
    {"code": "601398", "name": "工商银行", "market": "SH"},
    {"code": "600030", "name": "中信证券", "market": "SH"},
    {"code": "000651", "name": "格力电器", "market": "SZ"},
    {"code": "601888", "name": "中国中免", "market": "SH"},
    {"code": "600809", "name": "山西汾酒", "market": "SH"},
    {"code": "002714", "name": "牧原股份", "market": "SZ"},
    {"code": "300750", "name": "宁德时代", "market": "SZ"},
    {"code": "600887", "name": "伊利股份", "market": "SH"},
    {"code": "000568", "name": "泸州老窖", "market": "SZ"},
    {"code": "601012", "name": "隆基绿能", "market": "SH"},
    {"code": "002475", "name": "立讯精密", "market": "SZ"},
    {"code": "600031", "name": "三一重工", "market": "SH"},
    {"code": "601899", "name": "紫金矿业", "market": "SH"},
    {"code": "002594", "name": "比亚迪", "market": "SZ"},
    {"code": "600585", "name": "海螺水泥", "market": "SH"},
    {"code": "002304", "name": "洋河股份", "market": "SZ"},
    {"code": "601668", "name": "中国建筑", "market": "SH"},
    {"code": "600048", "name": "保利发展", "market": "SH"},
    {"code": "000002", "name": "万科A", "market": "SZ"},
    {"code": "601288", "name": "农业银行", "market": "SH"},
    {"code": "601939", "name": "建设银行", "market": "SH"},
    {"code": "600000", "name": "浦发银行", "market": "SH"},
    {"code": "601328", "name": "交通银行", "market": "SH"},
    {"code": "600016", "name": "民生银行", "market": "SH"},
    {"code": "000725", "name": "京东方A", "market": "SZ"},
    {"code": "601857", "name": "中国石油", "market": "SH"},
    {"code": "600028", "name": "中国石化", "market": "SH"},
    {"code": "601088", "name": "中国神华", "market": "SH"},
    {"code": "600050", "name": "中国联通", "market": "SH"},
    {"code": "601728", "name": "中国电信", "market": "SH"},
    {"code": "600941", "name": "中国移动", "market": "SH"},
    {"code": "300059", "name": "东方财富", "market": "SZ"},
    {"code": "002415", "name": "海康威视", "market": "SZ"},
    {"code": "300760", "name": "迈瑞医疗", "market": "SZ"},
    {"code": "688981", "name": "中芯国际", "market": "SH"},
    {"code": "002230", "name": "科大讯飞", "market": "SZ"},
    {"code": "300124", "name": "汇川技术", "market": "SZ"},
    {"code": "601985", "name": "中国核电", "market": "SH"},
    {"code": "600104", "name": "上汽集团", "market": "SH"},
    {"code": "000063", "name": "中兴通讯", "market": "SZ"},
    {"code": "002352", "name": "顺丰控股", "market": "SZ"},
]


def _detect_market(ts_code: str) -> str:
    """根据标的代码判断市场"""
    if ts_code.endswith(".SH"):
        return "沪市"
    elif ts_code.endswith(".SZ"):
        return "深市"
    return "其他"


class YahooClient:
    """标的搜索和行情客户端（搜索基于内置列表，行情通过 Yahoo Finance API）"""

    @staticmethod
    def _to_yahoo_symbol(ts_code: str) -> str:
        """ts_code → Yahoo 格式: 600519.SH → 600519.SS, 000001.SZ → 000001.SZ"""
        if ts_code.endswith(".SH"):
            return ts_code.replace(".SH", ".SS")
        return ts_code  # .SZ 不变

    @staticmethod
    def _from_yahoo_symbol(yahoo_symbol: str) -> str:
        """Yahoo 格式 → ts_code: 600519.SS → 600519.SH"""
        if yahoo_symbol.endswith(".SS"):
            return yahoo_symbol.replace(".SS", ".SH")
        return yahoo_symbol

    def get_quotes(self, ts_codes: list[str]) -> list[dict]:
        """
        批量获取实时行情（通过 Yahoo Finance API）
        逐个请求避免并发，每个带缓存
        @param ts_codes: 标的代码列表，如 ["600519.SH", "000001.SZ"]
        @return: 行情数据列表
        """
        if not ts_codes:
            return []

        results = []
        for ts_code in ts_codes:
            try:
                quote = self._get_single_quote(ts_code)
                if quote:
                    results.append(quote)
            except Exception as e:
                logger.warning(f"Yahoo 获取行情失败 {ts_code}: {e}")
                continue
        return results

    def _get_single_quote(self, ts_code: str) -> Optional[dict]:
        """获取单个标的行情"""
        yahoo_symbol = self._to_yahoo_symbol(ts_code)
        url = f"{YAHOO_QUOTE_URL}{yahoo_symbol}"
        params = {"interval": "1d", "range": "1d"}

        try:
            resp = requests.get(
                url, params=params, headers=YAHOO_HEADERS, timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            chart = data.get("chart", {}).get("result", [])
            if not chart:
                return None

            meta = chart[0].get("meta", {})
            price = meta.get("regularMarketPrice", 0)
            pre_close = meta.get("chartPreviousClose", 0) or meta.get("previousClose", 0)
            change = round(price - pre_close, 4) if pre_close else 0
            pct = round(change / pre_close * 100, 2) if pre_close else 0

            # 尝试从 indicators 获取成交量
            volume = 0
            indicators = chart[0].get("indicators", {}).get("quote", [])
            if indicators and indicators[0].get("volume"):
                vol_list = indicators[0]["volume"]
                # 取最后一个非 None 的值
                for v in reversed(vol_list):
                    if v is not None:
                        volume = v
                        break

            # 从内置列表查找中文名
            name = self._find_name(ts_code) or meta.get("shortName", ts_code)

            return {
                "ts_code": ts_code,
                "name": name,
                "close": price,
                "pre_close": pre_close,
                "change": change,
                "pct_chg": pct,
                "vol": volume,
                "amount": 0,  # Yahoo 免费 API 不提供成交额
                "open": meta.get("regularMarketOpen", 0) or 0,
                "high": meta.get("regularMarketDayHigh", 0) or meta.get("dayHigh", 0) or 0,
                "low": meta.get("regularMarketDayLow", 0) or meta.get("dayLow", 0) or 0,
            }
        except Exception as e:
            logger.warning(f"Yahoo API 请求失败 {yahoo_symbol}: {e}")
            return None

    @staticmethod
    def _find_name(ts_code: str) -> str:
        """从内置列表查找股票中文名"""
        code = ts_code.split(".")[0] if "." in ts_code else ts_code
        for stock in A_STOCK_LIST:
            if stock["code"] == code:
                return stock["name"]
        return ""

    def search(self, keyword: str) -> list[dict]:
        """
        搜索标的（从内置列表中匹配代码或名称）
        @param keyword: 搜索关键词
        @return: 匹配的股票列表
        """
        keyword_lower = keyword.lower().strip()
        matched = []
        for stock in A_STOCK_LIST:
            ts_code = f"{stock['code']}.{stock['market']}"
            if keyword_lower in stock["code"] or keyword in stock["name"]:
                matched.append({
                    "symbol": ts_code,
                    "name": stock["name"],
                    "market": _detect_market(ts_code),
                })
            if len(matched) >= 20:
                break
        return matched


# 全局单例
yahoo_client = YahooClient()
