"""
2FA 两步验证测试
覆盖启用、验证、禁用、恢复码等场景
"""

from __future__ import annotations

import pyotp
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTwoFactorSetup:
    """2FA 设置测试"""

    async def test_setup_2fa(self, client: AsyncClient, test_user, auth_headers):
        """获取 2FA 设置信息"""
        resp = await client.post("/api/auth/2fa/setup", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "secret" in data
        assert "qr_code_base64" in data
        assert "provisioning_uri" in data

    async def test_enable_2fa(self, client: AsyncClient, test_user, auth_headers):
        """启用 2FA"""
        # 获取密钥
        setup_resp = await client.post("/api/auth/2fa/setup", headers=auth_headers)
        secret = setup_resp.json()["secret"]

        # 生成有效的 TOTP 码
        totp = pyotp.TOTP(secret)
        code = totp.now()

        # 启用 2FA
        resp = await client.post("/api/auth/2fa/enable", headers=auth_headers, json={
            "secret": secret,
            "code": code,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["recovery_codes"]) == 8

    async def test_enable_2fa_wrong_code(self, client: AsyncClient, test_user, auth_headers):
        """启用 2FA 时验证码错误"""
        setup_resp = await client.post("/api/auth/2fa/setup", headers=auth_headers)
        secret = setup_resp.json()["secret"]

        resp = await client.post("/api/auth/2fa/enable", headers=auth_headers, json={
            "secret": secret,
            "code": "000000",
        })
        assert resp.status_code == 401
        assert resp.json()["code"] == "INVALID_2FA_CODE"


@pytest.mark.asyncio
class TestTwoFactorDisable:
    """禁用 2FA 测试"""

    async def _enable_2fa(self, client: AsyncClient, auth_headers: dict) -> tuple[str, list[str]]:
        """辅助方法：启用 2FA 并返回 (secret, recovery_codes)"""
        setup_resp = await client.post("/api/auth/2fa/setup", headers=auth_headers)
        secret = setup_resp.json()["secret"]
        totp = pyotp.TOTP(secret)
        code = totp.now()
        enable_resp = await client.post("/api/auth/2fa/enable", headers=auth_headers, json={
            "secret": secret,
            "code": code,
        })
        return secret, enable_resp.json()["recovery_codes"]

    async def test_disable_2fa(self, client: AsyncClient, test_user, auth_headers):
        """正常禁用 2FA"""
        secret, _ = await self._enable_2fa(client, auth_headers)
        totp = pyotp.TOTP(secret)
        code = totp.now()

        resp = await client.post("/api/auth/2fa/disable", headers=auth_headers, json={
            "code": code,
        })
        assert resp.status_code == 200

    async def test_disable_2fa_wrong_code(self, client: AsyncClient, test_user, auth_headers):
        """禁用 2FA 时验证码错误"""
        await self._enable_2fa(client, auth_headers)

        resp = await client.post("/api/auth/2fa/disable", headers=auth_headers, json={
            "code": "000000",
        })
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestRecoveryCodes:
    """恢复码测试"""

    async def _enable_2fa(self, client: AsyncClient, auth_headers: dict) -> tuple[str, list[str]]:
        """辅助方法：启用 2FA"""
        setup_resp = await client.post("/api/auth/2fa/setup", headers=auth_headers)
        secret = setup_resp.json()["secret"]
        totp = pyotp.TOTP(secret)
        enable_resp = await client.post("/api/auth/2fa/enable", headers=auth_headers, json={
            "secret": secret,
            "code": totp.now(),
        })
        return secret, enable_resp.json()["recovery_codes"]

    async def test_get_recovery_codes(self, client: AsyncClient, test_user, auth_headers):
        """获取恢复码"""
        await self._enable_2fa(client, auth_headers)

        resp = await client.get("/api/auth/2fa/recovery-codes", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()["recovery_codes"]) == 8

    async def test_regenerate_recovery_codes(self, client: AsyncClient, test_user, auth_headers):
        """重新生成恢复码"""
        await self._enable_2fa(client, auth_headers)

        resp = await client.post("/api/auth/2fa/recovery-codes/regenerate", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()["recovery_codes"]) == 8
