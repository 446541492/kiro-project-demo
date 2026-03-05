"""
Tushare API 客户端封装
统一异常处理、自动重试、日志记录
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

import tushare as ts
import pandas as pd

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TushareClient:
    """Tushare API 客户端"""

    def __init__(self):
        """初始化 Tushare 客户端"""
        # 如果没有配置 token，延迟初始化（测试环境）
        self._api: Optional[Any] = None
        if settings.TUSHARE_TOKEN:
            try:
                self._api = ts.pro_api(settings.TUSHARE_TOKEN)
            except Exception as e:
                logger.warning(f"Tushare API 初始化失败: {e}")

    def _ensure_api(self) -> Any:
        """确保 API 已初始化"""
        if self._api is None:
            if not settings.TUSHARE_TOKEN:
                raise ValueError("TUSHARE_TOKEN 未配置")
            self._api = ts.pro_api(settings.TUSHARE_TOKEN)
        return self._api

    def _call_api(
        self,
        api_name: str,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        统一的 API 调用方法，带重试和异常处理
        @param api_name: Tushare API 名称
        @param max_retries: 最大重试次数
        @param kwargs: API 参数
        @return: DataFrame 结果
        """
        api = self._ensure_api()
        for attempt in range(max_retries):
            try:
                start = time.time()
                result = getattr(api, api_name)(**kwargs)
                elapsed = time.time() - start
                logger.debug(
                    f"Tushare API 调用: {api_name} 参数={kwargs} "
                    f"耗时={elapsed:.2f}s 行数={len(result)}"
                )
                return result if result is not None else pd.DataFrame()

            except Exception as e:
                logger.warning(
                    f"Tushare API 调用失败 (第 {attempt + 1} 次): "
                    f"{api_name} 错误={e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    logger.error(f"Tushare API 调用最终失败: {api_name}")
                    raise

        return pd.DataFrame()

    def get_daily_quotes(self, trade_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取日线行情数据
        @param trade_date: 交易日期 (YYYYMMDD)，默认当天
        @return: 行情 DataFrame
        """
        params: dict[str, Any] = {}
        if trade_date:
            params["trade_date"] = trade_date
        return self._call_api("daily", **params)

    def get_stock_basic(self, market: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票基础信息
        @param market: 市场类型
        @return: 股票基础信息 DataFrame
        """
        params: dict[str, Any] = {"list_status": "L"}
        if market:
            params["exchange"] = market
        return self._call_api("stock_basic", **params)

    def get_daily_basic(self, trade_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取每日指标（市盈率、换手率等）
        @param trade_date: 交易日期
        @return: 指标 DataFrame
        """
        params: dict[str, Any] = {}
        if trade_date:
            params["trade_date"] = trade_date
        return self._call_api("daily_basic", **params)


# 全局单例
tushare_client = TushareClient()
