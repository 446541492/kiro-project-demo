"""
Yahoo Finance 搜索客户端
全球可访问，仅用于标的搜索（解决 Vercel 海外访问新浪超时问题）
内置 A 股热门股票列表，通过本地匹配实现搜索
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

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
    """标的搜索客户端（基于内置列表，无需网络请求）"""

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
