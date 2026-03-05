"""
新浪财经行情客户端
免费、无需 Token，通过 HTTP 接口获取 A 股实时行情
使用原生 list[dict] 数据结构，无需 pandas
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

# 新浪财经 API 地址
SINA_HQ_URL = "https://hq.sinajs.cn/list="
# 列表接口：主域名 + 备用域名，456 限流时自动切换
SINA_LIST_URLS = [
    "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData",
    "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData",
]
SINA_HEADERS = {
    "Referer": "https://finance.sina.com.cn",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


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
        遇到 456 限流时加大重试间隔
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
                logger.debug(f"新浪 API 调用: {url} 耗时={elapsed:.2f}s")
                resp.raise_for_status()
                return resp
            except requests.exceptions.HTTPError as e:
                last_err = e
                status = e.response.status_code if e.response is not None else 0
                if status == 456:
                    wait = 2.0 * (attempt + 1)
                    logger.warning(
                        f"新浪 API 限流 456 (第 {attempt + 1} 次), "
                        f"等待 {wait:.1f}s 后重试"
                    )
                else:
                    wait = 0.5
                    logger.warning(
                        f"新浪 API HTTP {status} (第 {attempt + 1} 次): {e}"
                    )
                if attempt < max_retries - 1:
                    time.sleep(wait)
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
    ) -> list[dict]:
        """
        获取 A 股行情列表（分页）
        主域名失败时自动切换备用域名
        @param node: 板块节点，hs_a=沪深A股, sh_a=沪A, sz_a=深A
        @param sort: 排序字段
        @param asc: 0=降序, 1=升序
        @param page: 页码
        @param num: 每页数量（最大 80）
        @return: 行情数据列表
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
        last_err: Optional[Exception] = None
        for url in SINA_LIST_URLS:
            try:
                resp = self._call_api(url, params=params)
                data = resp.json()
                if not data:
                    return []
                # 为每行生成 ts_code
                for row in data:
                    if "symbol" in row:
                        row["ts_code"] = self._to_ts_code(row["symbol"])
                return data
            except Exception as e:
                last_err = e
                logger.warning(f"列表接口 {url} 失败，尝试备用域名: {e}")
                continue
        logger.error(f"所有列表接口均失败: {last_err}")
        return []

    def get_multi_page_list(
        self,
        node: str = "hs_a",
        sort: str = "changepercent",
        asc: int = 0,
        total: int = 100,
    ) -> list[dict]:
        """
        获取多页行情数据
        @param node: 板块节点
        @param sort: 排序字段
        @param asc: 排序方向
        @param total: 需要的总条数
        @return: 合并后的数据列表
        """
        all_rows: list[dict] = []
        page = 1
        while len(all_rows) < total:
            num = min(80, total - len(all_rows))
            rows = self.get_market_list(
                node=node, sort=sort, asc=asc, page=page, num=num
            )
            if not rows:
                break
            all_rows.extend(rows)
            if len(rows) < num:
                break
            page += 1
        return all_rows

    def get_quotes_by_symbols(self, symbols: list[str]) -> list[dict]:
        """
        批量获取指定标的的实时行情（通过 hq.sinajs.cn）
        @param symbols: 标的代码列表，如 ["600519.SH", "000001.SZ"]
        @return: 行情数据列表
        """
        if not symbols:
            return []

        sina_symbols = [self._from_ts_code(s) for s in symbols]
        symbol_str = ",".join(sina_symbols)

        try:
            resp = self._call_api(f"{SINA_HQ_URL}{symbol_str}")
            return self._parse_hq_response(resp.text, symbols)
        except Exception as e:
            logger.error(f"批量获取行情失败: {e}")
            return []

    def get_kline(
        self,
        symbol: str,
        scale: int = 240,
        datalen: int = 120,
    ) -> list[dict]:
        """
        获取K线数据（通过新浪财经K线接口）
        @param symbol: ts_code 格式，如 600519.SH
        @param scale: K线周期（分钟），240=日K, 1200=周K, 7200=月K
        @param datalen: 数据条数
        @return: K线数据列表
        """
        sina_symbol = self._from_ts_code(symbol)
        url = (
            f"https://quotes.sina.cn/cn/api/jsonp_v2.php"
            f"/var%20_={sina_symbol}_{scale}/CN_MarketDataService.getKLineData"
        )
        params = {
            "symbol": sina_symbol,
            "scale": scale,
            "ma": "no",
            "datalen": datalen,
        }
        try:
            resp = self._call_api(url, params=params)
            text = resp.text
            start = text.find("([")
            end = text.rfind("])")
            if start == -1 or end == -1:
                logger.warning(f"K线数据解析失败，响应格式异常: {text[:200]}")
                return []
            data = json.loads(text[start + 1 : end + 1])
            return data
        except Exception as e:
            logger.error(f"获取K线数据失败 {symbol}: {e}")
            return []

    def _parse_hq_response(self, text: str, ts_codes: list[str]) -> list[dict]:
        """
        解析 hq.sinajs.cn 返回的行情数据
        格式: var hq_str_sh600519="名称,今开,昨收,当前价,...";
        """
        rows: list[dict] = []
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
                close = float(parts[3] or 0)
                pre_close = float(parts[2] or 0)
                change = close - pre_close
                pct_chg = round(change / pre_close * 100, 2) if pre_close != 0 else 0
                rows.append({
                    "ts_code": ts_code,
                    "name": parts[0],
                    "open": float(parts[1] or 0),
                    "pre_close": pre_close,
                    "close": close,
                    "high": float(parts[4] or 0),
                    "low": float(parts[5] or 0),
                    "vol": float(parts[8] or 0),
                    "amount": float(parts[9] or 0),
                    "change": change,
                    "pct_chg": pct_chg,
                })
            except (ValueError, IndexError) as e:
                logger.warning(f"解析行情数据失败 {sina_code}: {e}")
                continue

        return rows

    @staticmethod
    def _to_ts_code(sina_symbol: str) -> str:
        """新浪代码 → ts_code 格式: sh600519 → 600519.SH"""
        sina_symbol = str(sina_symbol).lower()
        if sina_symbol.startswith("sh"):
            return f"{sina_symbol[2:]}.SH"
        elif sina_symbol.startswith("sz"):
            return f"{sina_symbol[2:]}.SZ"
        elif sina_symbol.startswith("bj"):
            return f"{sina_symbol[2:]}.BJ"
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
        """ts_code → 新浪代码格式: 600519.SH → sh600519"""
        if "." in ts_code:
            code, market = ts_code.split(".", 1)
            prefix = market.lower()
            return f"{prefix}{code}"
        if ts_code.startswith(("6", "9")):
            return f"sh{ts_code}"
        return f"sz{ts_code}"


# 全局单例
sina_client = SinaClient()
