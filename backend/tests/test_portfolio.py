"""
自选组合接口测试
覆盖组合的增删改查和排序
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio
from app.models.user import User


@pytest_asyncio.fixture
async def default_portfolio(db_session: AsyncSession, test_user: User) -> Portfolio:
    """创建默认自选组合"""
    portfolio = Portfolio(
        user_id=test_user.id,
        name="我的自选",
        sort_order=0,
        is_default=True,
    )
    db_session.add(portfolio)
    await db_session.commit()
    await db_session.refresh(portfolio)
    return portfolio


class TestGetPortfolios:
    """获取组合列表测试"""

    @pytest.mark.asyncio
    async def test_get_empty_portfolios(self, client: AsyncClient, auth_headers: dict):
        """无组合时返回空列表"""
        resp = await client.get("/api/portfolios", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_get_portfolios_with_data(
        self, client: AsyncClient, auth_headers: dict, default_portfolio: Portfolio
    ):
        """有组合时返回组合列表"""
        resp = await client.get("/api/portfolios", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "我的自选"
        assert data[0]["is_default"] is True

    @pytest.mark.asyncio
    async def test_get_portfolios_unauthorized(self, client: AsyncClient):
        """未登录返回 401"""
        resp = await client.get("/api/portfolios")
        assert resp.status_code == 401


class TestCreatePortfolio:
    """创建组合测试"""

    @pytest.mark.asyncio
    async def test_create_portfolio_success(self, client: AsyncClient, auth_headers: dict):
        """成功创建组合"""
        resp = await client.post(
            "/api/portfolios",
            json={"name": "科技股"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "科技股"
        assert data["is_default"] is False

    @pytest.mark.asyncio
    async def test_create_duplicate_name(
        self, client: AsyncClient, auth_headers: dict, default_portfolio: Portfolio
    ):
        """重复名称返回 409"""
        resp = await client.post(
            "/api/portfolios",
            json={"name": "我的自选"},
            headers=auth_headers,
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_create_portfolio_empty_name(self, client: AsyncClient, auth_headers: dict):
        """空名称返回 422"""
        resp = await client.post(
            "/api/portfolios",
            json={"name": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422


class TestUpdatePortfolio:
    """更新组合测试"""

    @pytest.mark.asyncio
    async def test_update_portfolio_success(
        self, client: AsyncClient, auth_headers: dict, default_portfolio: Portfolio
    ):
        """成功重命名组合"""
        resp = await client.put(
            f"/api/portfolios/{default_portfolio.id}",
            json={"name": "新名称"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "新名称"

    @pytest.mark.asyncio
    async def test_update_nonexistent_portfolio(self, client: AsyncClient, auth_headers: dict):
        """不存在的组合返回 404"""
        resp = await client.put(
            "/api/portfolios/9999",
            json={"name": "新名称"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestDeletePortfolio:
    """删除组合测试"""

    @pytest.mark.asyncio
    async def test_delete_default_portfolio_rejected(
        self, client: AsyncClient, auth_headers: dict, default_portfolio: Portfolio
    ):
        """默认组合不可删除"""
        resp = await client.delete(
            f"/api/portfolios/{default_portfolio.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_normal_portfolio(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession, test_user: User
    ):
        """成功删除非默认组合"""
        portfolio = Portfolio(
            user_id=test_user.id, name="临时组合", sort_order=1, is_default=False
        )
        db_session.add(portfolio)
        await db_session.commit()
        await db_session.refresh(portfolio)

        resp = await client.delete(
            f"/api/portfolios/{portfolio.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
