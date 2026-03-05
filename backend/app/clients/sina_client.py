"""
新浪财经行情客户端
免费、无需 Token，通过 HTTP 接口获取 A 股实时行情
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Optional

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# 新浪财经 API 地址
SINA_HQ_URL = "https://hq.sinajs.cn/list="
SINA_LIST_URL = (
    "https://vip.stock.finance.sina.com.cn"
    "/quotes_service/api/json_v2.php"
    "/Market_Center.getHQNodeData"
)
SINA_HEADERS = {"Referer": "https://finance.sina.com.cn"}


class SinaClient:
    """新浪财经行情客户端"""

    def _call_api(
        self,
        url: str,
        max_retries: int = 3,
        params: Optional[dict] = None,
        timeout: int = 10,
    ) -> requests.Response:
        """
        统一的 HTTP 请求方法，带重试
        @param url: 请求地址
        @param max_retries: 最大重试次数
        @param params: 查询参数
        @param timeout: 超时秒数
        @return: Response 对象
        """
        last_err: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                start = time.time()
                resp = requests.get(
                    url,
                    params=params,
                    headers=SINA_HEADERS,
                    timeout=timeout,
                )
                elapsed = time.time() - start
                logger.debug(
                    f"新浪 API 调用: {url} 耗时={elapsed:.2f}s"
                )
                resp.raise_for_status()
                return resp
            except Exception as e:
                last_err = e
                logger.warning(
                    f"新浪 API 调用失败 (第 {attempt + 1} 次): {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(0.5)
        raise last_err  # type: ignore[misc]

    def get_market_list(
        self,
        node: str = "hs_a",
        sort: str = "changepercent",
        asc: int = 0,
        page: int = 1,
        num: int = 80,
    ) -> pd.DataFrame:
        """
        获取 A 股行情列表（分页）
        @param node: 板块节点，hs_a=沪深A股, sh_a=沪A, sz_a=深A
        @param sort: 排序字段
        @param asc: 0=降序, 1=升序
        @param page: 页码
        @param num: 每页数量（最大 80）
        @return: 行情 DataFrame
        """
        params = {
            "page": page,
            "num": min(num, 80),
            "sort": sort,
            "asc": asc,
            "node": node,
            "symbol": "",
            "_s_r_a": "page",
        }
        try:
            resp = self._call_api(SINA_LIST_URL, params=params)
            data = resp.json()
            if not data:
                return pd.DataFrame()
            df = pd.DataFrame(data)
            # 生成 ts_code 格式（兼容现有服务层）
            if "symbol" in df.columns:
                df["ts_code"] = df["symbol"].apply(self._to_ts_code)
            return df
        except Exception as e:
            logger.error(f"获取行情列表失败: {e}")
            return pd.DataFrame()

    def get_multi_page_list(
        self,
        node: str = "hs_a",
        sort: str = "changepercent",
        asc: int = 0,
        total: int = 100,
    ) -> pd.DataFrame:
        """
        获取多页行情数据
        @param node: 板块节点
        @param sort: 排序字段
        @param asc: 排序方向
        @param total: 需要的总条数
        @return: 合并后的 DataFrame
        """
        frames = []
        page = 1
        collected = 0
        while collected < total:
            num = min(80, total - collected)
            df = self.get_market_list(
                node=node, sort=sort, asc=asc, page=page, num=num
            )
            if df.empty:
                break
            frames.append(df)
            collected += len(df)
            if len(df) < num:
                break
            page += 1
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    def get_quotes_by_symbols(self, symbols: list[str]) -> pd.DataFrame:
        """
        批量获取指定标的的实时行情（通过 hq.sinajs.cn）
        @param symbols: 标的代码列表，如 ["sh600519", "sz000001"]
        @return: 行情 DataFrame
        """
        if not symbols:
            return pd.DataFrame()

        # 转换为新浪格式
        sina_symbols = [self._from_ts_code(s) for s in symbols]
        symbol_str = ",".join(sina_symbols)

        try:
            resp = self._call_api(f"{SINA_HQ_URL}{symbol_str}")
            return self._parse_hq_response(resp.text, symbols)
        except Exception as e:
            logger.error(f"批量获取行情失败: {e}")
            return pd.DataFrame()

    def _parse_hq_response(
        self, text: str, ts_codes: list[str]
    ) -> pd.DataFrame:
        """
        解析 hq.sinajs.cn 返回的行情数据
        格式: var hq_str_sh600519="名称,今开,昨收,当前价,...";
        """
        rows = []
        pattern = re.compile(r'var hq_str_(\w+)="(.*)";')
        matches = pattern.findall(text)

        for i, (sina_code, data_str) in enumerate(matches):
            if not data_str:
                continue
            parts = data_str.split(",")
            if len(parts) < 32:
                continue
            ts_code = ts_codes[i] if i < len(ts_codes) else self._to_ts_code(sina_code)
            try:
                rows.append({
                    "ts_code": ts_code,
                    "name": parts[0],
                    "open": float(parts[1] or 0),
                    "pre_close": float(parts[2] or 0),
                    "close": float(parts[3] or 0),
                    "high": float(parts[4] or 0),
                    "low": float(parts[5] or 0),
                    "vol": float(parts[8] or 0),
                    "amount": float(parts[9] or 0),
                })
            except (ValueError, IndexError) as e:
                logger.warning(f"解析行情数据失败 {sina_code}: {e}")
                continue

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        # 计算涨跌幅和涨跌额
        if "close" in df.columns and "pre_close" in df.columns:
            df["change"] = df["close"] - df["pre_close"]
            df["pct_chg"] = df.apply(
                lambda r: round(r["change"] / r["pre_close"] * 100, 2)
                if r["pre_close"] != 0 else 0,
                axis=1,
            )
        return df

    @staticmethod
    def _to_ts_code(sina_symbol: str) -> str:
        """
        新浪代码 → ts_code 格式
        sh600519 → 600519.SH, sz000001 → 000001.SZ
        bj920001 → 920001.BJ
        """
        sina_symbol = str(sina_symbol).lower()
        if sina_symbol.startswith("sh"):
            return f"{sina_symbol[2:]}.SH"
        elif sina_symbol.startswith("sz"):
            return f"{sina_symbol[2:]}.SZ"
        elif sina_symbol.startswith("bj"):
            return f"{sina_symbol[2:]}.BJ"
        # 纯数字代码：根据首位判断
        code = sina_symbol
        if code.startswith(("6", "9")):
            return f"{code}.SH"
        elif code.startswith(("0", "3")):
            return f"{code}.SZ"
        elif code.startswith(("4", "8")):
            return f"{code}.BJ"
        return f"{code}.SZ"

    @staticmethod
    def _from_ts_code(ts_code: str) -> str:
        """
        ts_code → 新浪代码格式
        600519.SH → sh600519, 000001.SZ → sz000001
        """
        if "." in ts_code:
            code, market = ts_code.split(".", 1)
            prefix = market.lower()
            return f"{prefix}{code}"
        # 纯数字
        if ts_code.startswith(("6", "9")):
            return f"sh{ts_code}"
        return f"sz{ts_code}"


# 全局单例
sina_client = SinaClient()
