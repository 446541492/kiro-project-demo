"""
Vercel Serverless Function 入口
将 FastAPI 应用挂载为 Vercel 函数
"""

import sys
import os

# 将 backend 目录加入 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# 设置环境变量默认值（Vercel 环境中 .env 不生效，需在 Vercel 控制台配置）
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///tmp/database.db")

from app.main import app  # noqa: E402

# Vercel 会自动识别名为 app 的 ASGI/WSGI 应用
