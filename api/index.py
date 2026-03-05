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

from app.main import app  # noqa: E402

# Vercel 会自动识别名为 app 的 ASGI/WSGI 应用
