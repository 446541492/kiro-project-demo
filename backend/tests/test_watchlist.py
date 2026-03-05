"""
自选标的接口测试
覆盖标的的增删和排序
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.watchlist_item import WatchlistItem


@pytest_asyncio.fixture
async def portfolio(db_session: AsyncSession, test_user: User) -> Portfolio:
    """创建测试组合"""
    p = Portfolio(
        user_id=test_user.id, name="测试组合", sort_order=0, is_default=True
    )
    db_session.add(p)
    await db_session.commit()
    await db_session.refresh(p)
    return p


@pytest_asyncio.fixture
async def sample_item(db_session: AsyncSession, portfolio: Portfolio) -> WatchlistItem:
    """创建测试标的"""
    item = WatchlistItem(
        portfolio_id=portfolio.id,
        symbol="600519.SH",
        name="贵州茅台",
        market="沪市",
        sort_order=0,
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item


class TestAddItem:
    """添加标的测试"""

    @pytest.mark.asyncio
    async def test_add_item_success(
        self, client: AsyncClient, auth_headers: dict, portfolio: Portfolio
    ):
        """成功添加标的"""
        resp = await client.post(
            f"/api/portfolios/{portfolio.id}/items",
            json={"symbol": "000001.SZ", "name": "平安银行", "market": "深市"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["symbol"] == "000001.SZ"
        assert data["name"] == "平安银行"

    @pytest.mark.asyncio
    async def test_add_duplicate_item(
        self, client: AsyncClient, auth_headers: dict, portfolio: Portfolio, sample_item: WatchlistItem
    ):
        """重复标的返回 409"""
        resp = await client.post(
            f"/api/portfolios/{portfolio.id}/items",
            json={"symbol": "600519.SH", "name": "贵州茅台", "market": "沪市"},
            headers=auth_headers,
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_add_item_to_nonexistent_portfolio(
        self, client: AsyncClient, auth_headers: dict
    ):
        """不存在的组合返回 404"""
        resp = await client.post(
            "/api/portfolios/9999/items",
            json={"symbol": "000001.SZ", "name": "平安银行", "market": "深市"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestGetItems:
    """获取标的列表测试"""

    @pytest.mark.asyncio
    async def test_get_items_empty(
        self, client: AsyncClient, auth_headers: dict, portfolio: Portfolio
    ):
        """空组合返回空列表"""
        resp = await client.get(
            f"/api/portfolios/{portfolio.id}/items",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_get_items_with_data(
        self, client: AsyncClient, auth_headers: dict, portfolio: Portfolio, sample_item: WatchlistItem
    ):
        """有标的时返回标的列表"""
        resp = await client.get(
            f"/api/portfolios/{portfolio.id}/items",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["symbol"] == "600519.SH"


class TestRemoveItem:
    """移除标的测试"""

    @pytest.mark.asyncio
    async def test_remove_item_success(
        self, client: AsyncClient, auth_headers: dict, portfolio: Portfolio, sample_item: WatchlistItem
    ):
        """成功移除标的"""
        resp = await client.delete(
            f"/api/portfolios/{portfolio.id}/items/{sample_item.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_remove_nonexistent_item(
        self, client: AsyncClient, auth_headers: dict, portfolio: Portfolio
    ):
        """不存在的标的返回 404"""
        resp = await client.delete(
            f"/api/portfolios/{portfolio.id}/items/9999",
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestBatchAdd:
    """批量添加测试"""

    @pytest.mark.asyncio
    async def test_batch_add_success(
        self, client: AsyncClient, auth_headers: dict, portfolio: Portfolio
    ):
        """成功批量添加"""
        resp = await client.post(
            f"/api/portfolios/{portfolio.id}/items/batch",
            json={
                "items": [
                    {"symbol": "000001.SZ", "name": "平安银行", "market": "深市"},
                    {"symbol": "600036.SH", "name": "招商银行", "market": "沪市"},
                ]
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert len(resp.json()) == 2

    @pytest.mark.asyncio
    async def test_batch_add_skip_existing(
        self, client: AsyncClient, auth_headers: dict, portfolio: Portfolio, sample_item: WatchlistItem
    ):
        """批量添加跳过已存在的标的"""
        resp = await client.post(
            f"/api/portfolios/{portfolio.id}/items/batch",
            json={
                "items": [
                    {"symbol": "600519.SH", "name": "贵州茅台", "market": "沪市"},
                    {"symbol": "000001.SZ", "name": "平安银行", "market": "深市"},
                ]
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        # 只新增了 1 个（跳过已存在的贵州茅台）
        assert len(resp.json()) == 1
