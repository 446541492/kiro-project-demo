"""
密码相关测试
覆盖修改密码和密码策略验证场景
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestChangePassword:
    """修改密码测试"""

    async def test_change_password_success(self, client: AsyncClient, test_user, auth_headers):
        """正常修改密码"""
        resp = await client.put("/api/auth/password", headers=auth_headers, json={
            "old_password": "Test@123456",
            "new_password": "NewPass@789",
        })
        assert resp.status_code == 200
        assert resp.json()["message"] == "密码修改成功"

        # 用新密码登录
        login_resp = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "NewPass@789",
        })
        assert login_resp.status_code == 200

    async def test_change_password_wrong_old(self, client: AsyncClient, test_user, auth_headers):
        """旧密码错误"""
        resp = await client.put("/api/auth/password", headers=auth_headers, json={
            "old_password": "WrongOld@123",
            "new_password": "NewPass@789",
        })
        assert resp.status_code == 401
        assert resp.json()["code"] == "WRONG_PASSWORD"

    async def test_change_password_same(self, client: AsyncClient, test_user, auth_headers):
        """新旧密码相同"""
        resp = await client.put("/api/auth/password", headers=auth_headers, json={
            "old_password": "Test@123456",
            "new_password": "Test@123456",
        })
        assert resp.status_code == 409
        assert resp.json()["code"] == "SAME_PASSWORD"


@pytest.mark.asyncio
class TestPasswordValidation:
    """密码策略验证测试"""

    async def test_password_too_short(self, client: AsyncClient):
        """密码太短"""
        resp = await client.post("/api/auth/register", json={
            "username": "shortpwd",
            "password": "Ab@1",
            "email": "short@example.com",
        })
        assert resp.status_code == 409
        assert resp.json()["code"] == "WEAK_PASSWORD"

    async def test_password_no_uppercase(self, client: AsyncClient):
        """缺少大写字母"""
        resp = await client.post("/api/auth/register", json={
            "username": "nouppercase",
            "password": "abcdefg@1",
            "email": "noupper@example.com",
        })
        assert resp.status_code == 409

    async def test_password_no_special(self, client: AsyncClient):
        """缺少特殊字符"""
        resp = await client.post("/api/auth/register", json={
            "username": "nospecial",
            "password": "Abcdefg123",
            "email": "nospec@example.com",
        })
        assert resp.status_code == 409

    async def test_password_valid(self, client: AsyncClient):
        """合法密码"""
        resp = await client.post("/api/auth/register", json={
            "username": "validpwd",
            "password": "Valid@12345",
            "email": "valid@example.com",
        })
        assert resp.status_code == 200
