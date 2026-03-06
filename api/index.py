"""
Vercel Serverless Function 入口
将 FastAPI 应用挂载为 Vercel 函数
"""

import sys
import os

# 将 backend 目录加入 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Vercel 环境中强制设置关键环境变量
os.environ.setdefault("CORS_ORIGINS", "*")
os.environ.setdefault("DEBUG", "false")

from app.main import app  # noqa: E402
