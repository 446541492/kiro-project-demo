"""
认证 API 测试
覆盖注册、登录、Token 刷新、登出、获取用户信息等场景
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    """注册测试"""

    async def test_register_success(self, client: AsyncClient):
        """正常注册"""
        resp = await client.post("/api/auth/register", json={
            "username": "newuser",
            "password": "NewUser@123",
            "email": "new@example.com",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """用户名重复"""
        resp = await client.post("/api/auth/register", json={
            "username": "testuser",
            "password": "NewUser@123",
            "email": "other@example.com",
        })
        assert resp.status_code == 409
        assert resp.json()["code"] == "USERNAME_EXISTS"

    async def test_register_weak_password(self, client: AsyncClient):
        """密码不符合策略"""
        resp = await client.post("/api/auth/register", json={
            "username": "weakpwd",
            "password": "123",
            "email": "weak@example.com",
        })
        assert resp.status_code == 409
        assert resp.json()["code"] == "WEAK_PASSWORD"

    async def test_register_no_contact(self, client: AsyncClient):
        """未提供联系方式"""
        resp = await client.post("/api/auth/register", json={
            "username": "nocontact",
            "password": "NoContact@123",
        })
        assert resp.status_code == 409


@pytest.mark.asyncio
class TestLogin:
    """登录测试"""

    async def test_login_success(self, client: AsyncClient, test_user):
        """正常登录"""
        resp = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "Test@123456",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["requires_2fa"] is False
        assert "access_token" in data

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """密码错误"""
        resp = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "WrongPassword@1",
        })
        assert resp.status_code == 401
        assert resp.json()["code"] == "INVALID_CREDENTIALS"

    async def test_login_user_not_found(self, client: AsyncClient):
        """用户不存在"""
        resp = await client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "Test@123456",
        })
        assert resp.status_code == 401
        assert resp.json()["code"] == "INVALID_CREDENTIALS"

    async def test_login_lockout(self, client: AsyncClient, test_user):
        """连续失败锁定"""
        # 连续 5 次错误密码
        for i in range(5):
            resp = await client.post("/api/auth/login", json={
                "username": "testuser",
                "password": "Wrong@12345",
                "captcha_token": "fake" if i >= 3 else None,
            })

        # 第 5 次应该返回锁定
        assert resp.status_code == 423
        assert resp.json()["code"] == "ACCOUNT_LOCKED"

        # 锁定后再次尝试
        resp = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "Test@123456",
        })
        assert resp.status_code == 423


@pytest.mark.asyncio
class TestTokenRefresh:
    """Token 刷新测试"""

    async def test_refresh_success(self, client: AsyncClient, test_user):
        """正常刷新"""
        # 先登录获取 Token
        login_resp = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "Test@123456",
        })
        refresh_token = login_resp.json()["refresh_token"]

        # 刷新 Token
        resp = await client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_refresh_invalid_token(self, client: AsyncClient):
        """无效 Token"""
        resp = await client.post("/api/auth/refresh", json={
            "refresh_token": "invalid.token.here",
        })
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestUserInfo:
    """用户信息测试"""

    async def test_get_me(self, client: AsyncClient, test_user, auth_headers):
        """获取当前用户信息"""
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    async def test_get_me_unauthorized(self, client: AsyncClient):
        """未认证访问"""
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401
