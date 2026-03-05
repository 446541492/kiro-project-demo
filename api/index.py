"""
Vercel Serverless Function 入口
将 FastAPI 应用挂载为 Vercel 函数
"""

import sys
import os

# 将 backend 目录加入 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Vercel 环境中强制设置关键环境变量
# os.environ 优先级高于 .env 文件和 pydantic-settings 默认值
os.environ["DATABASE_URL"] = os.environ.get(
    "DATABASE_URL", "sqlite+aiosqlite:////tmp/database.db"
)
os.environ.setdefault("CORS_ORIGINS", "*")
os.environ.setdefault("DEBUG", "false")

# 确保 /tmp 目录下数据库文件可创建
import pathlib
pathlib.Path("/tmp").mkdir(parents=True, exist_ok=True)

# Vercel serverless 环境不会触发 FastAPI lifespan 事件
# 需要在模块加载时手动初始化数据库表
import app.models  # noqa: F401, 确保所有模型被注册
from app.models.base import Base
from app.core.database import engine
from app.main import app as application  # noqa: E402

_db_initialized = False


@application.middleware("http")
async def ensure_db_middleware(request, call_next):
    """确保数据库表在首次请求前已创建"""
    global _db_initialized
    if not _db_initialized:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _db_initialized = True
    return await call_next(request)

# Vercel 会自动识别名为 app 的 ASGI/WSGI 应用
app = application
