"""
行情 API 测试
覆盖榜单、搜索、标的行情等场景
注意: 实际 Tushare API 调用在测试中会被跳过（无 Token）
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRankings:
    """榜单测试"""

    async def test_rankings_unauthorized(self, client: AsyncClient):
        """未认证访问"""
        resp = await client.get("/api/market/rankings")
        assert resp.status_code == 401

    async def test_rankings_invalid_type(self, client: AsyncClient, auth_headers):
        """无效的榜单类型"""
        resp = await client.get(
            "/api/market/rankings?ranking_type=invalid",
            headers=auth_headers,
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestSearch:
    """搜索测试"""

    async def test_search_unauthorized(self, client: AsyncClient):
        """未认证访问"""
        resp = await client.get("/api/market/search?keyword=test")
        assert resp.status_code == 401

    async def test_search_empty_keyword(self, client: AsyncClient, auth_headers):
        """空关键词"""
        resp = await client.get(
            "/api/market/search?keyword=",
            headers=auth_headers,
        )
        # FastAPI 会因为 Query(...) 的必填验证返回 422
        assert resp.status_code in [422]


@pytest.mark.asyncio
class TestQuote:
    """标的行情测试"""

    async def test_quote_unauthorized(self, client: AsyncClient):
        """未认证访问"""
        resp = await client.get("/api/market/quote/600519.SH")
        assert resp.status_code == 401
