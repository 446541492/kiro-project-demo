"""
测试配置和共享 fixtures
使用内存 SQLite 数据库，每个测试函数独立隔离
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.database import get_db
from app.core.security import create_access_token, hash_password
from app.models.base import Base
from app.models.user import User


# 内存 SQLite 测试数据库引擎
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    """覆盖数据库依赖，使用测试数据库"""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """每个测试前创建表，测试后清理"""
    # 重置频率限制计数器，避免测试间互相影响
    from app.main import rate_limit_store
    rate_limit_store.clear()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """获取测试数据库会话"""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """获取测试 HTTP 客户端"""
    from app.main import app
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """创建预置测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        phone="13800000001",
        password_hash=hash_password("Test@123456"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict[str, str]:
    """生成带 Token 的请求头"""
    token = create_access_token(
        {"user_id": test_user.id, "username": test_user.username}
    )
    return {"Authorization": f"Bearer {token}"}
