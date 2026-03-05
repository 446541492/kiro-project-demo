"""
数据库初始化脚本
创建所有表并插入测试数据
可独立运行: python -m migrations.init_db
"""

import asyncio
import sys
import os

# 将 backend 目录添加到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, AsyncSessionLocal
from app.core.security import hash_password
from app.models.base import Base
from app.models.user import User
from app.models.device import Device
from app.models.recovery_code import RecoveryCode
from app.models.portfolio import Portfolio
from app.models.watchlist_item import WatchlistItem


async def init_database():
    """初始化数据库：创建表和插入测试数据"""
    print("开始初始化数据库...")

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表创建完成")

    # 插入测试数据
    async with AsyncSessionLocal() as session:
        try:
            # 检查是否已有数据
            from sqlalchemy import select, func
            result = await session.execute(
                select(func.count()).select_from(User)
            )
            count = result.scalar()
            if count > 0:
                print(f"数据库已有 {count} 个用户，跳过测试数据插入")
                return

            # 创建测试用户 1: admin
            admin = User(
                username="admin",
                email="admin@example.com",
                phone="13800000001",
                password_hash=hash_password("Admin@123456"),
            )
            session.add(admin)

            # 创建测试用户 2: testuser
            testuser = User(
                username="testuser",
                email="test@example.com",
                phone="13800000002",
                password_hash=hash_password("Test@123456"),
            )
            session.add(testuser)

            await session.commit()
            print("测试用户创建完成:")
            print("  - admin / Admin@123456")
            print("  - testuser / Test@123456")

            # 刷新获取用户 ID
            await session.refresh(admin)
            await session.refresh(testuser)

            # 为 admin 创建默认自选组合
            default_portfolio = Portfolio(
                user_id=admin.id,
                name="我的自选",
                sort_order=0,
                is_default=True,
            )
            session.add(default_portfolio)

            # 为 admin 创建额外组合
            tech_portfolio = Portfolio(
                user_id=admin.id,
                name="科技股",
                sort_order=1,
                is_default=False,
            )
            session.add(tech_portfolio)

            # 为 testuser 创建默认自选组合
            test_default = Portfolio(
                user_id=testuser.id,
                name="我的自选",
                sort_order=0,
                is_default=True,
            )
            session.add(test_default)

            await session.commit()

            # 刷新获取组合 ID
            await session.refresh(default_portfolio)
            await session.refresh(tech_portfolio)

            # 为 admin 默认组合添加示例标的
            sample_items = [
                WatchlistItem(
                    portfolio_id=default_portfolio.id,
                    symbol="600519.SH", name="贵州茅台", market="沪市", sort_order=0,
                ),
                WatchlistItem(
                    portfolio_id=default_portfolio.id,
                    symbol="000858.SZ", name="五粮液", market="深市", sort_order=1,
                ),
                WatchlistItem(
                    portfolio_id=default_portfolio.id,
                    symbol="601318.SH", name="中国平安", market="沪市", sort_order=2,
                ),
            ]
            for item in sample_items:
                session.add(item)

            # 为科技股组合添加示例标的
            tech_items = [
                WatchlistItem(
                    portfolio_id=tech_portfolio.id,
                    symbol="000001.SZ", name="平安银行", market="深市", sort_order=0,
                ),
                WatchlistItem(
                    portfolio_id=tech_portfolio.id,
                    symbol="600036.SH", name="招商银行", market="沪市", sort_order=1,
                ),
            ]
            for item in tech_items:
                session.add(item)

            await session.commit()
            print("测试自选组合和标的创建完成")

        except Exception as e:
            await session.rollback()
            print(f"插入测试数据失败: {e}")
            raise

    print("数据库初始化完成")


if __name__ == "__main__":
    asyncio.run(init_database())
