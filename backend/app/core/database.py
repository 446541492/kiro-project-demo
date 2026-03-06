"""
数据库连接管理模块
使用 SQLAlchemy 2.0 异步引擎和会话
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import get_settings

settings = get_settings()

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    # SQLite 需要设置 connect_args
    connect_args={"check_same_thread": False},
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 数据库表是否已初始化（Vercel serverless 环境可能不触发 lifespan 事件）
_tables_created = False


async def _ensure_tables():
    """确保数据库表已创建（仅执行一次）"""
    global _tables_created
    if not _tables_created:
        from app.models.base import Base
        import app.models  # noqa: F401, 确保所有模型被注册
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _tables_created = True


async def get_db():
    """
    获取数据库会话的依赖注入函数
    每个请求创建独立会话，请求结束后自动关闭
    """
    await _ensure_tables()
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
