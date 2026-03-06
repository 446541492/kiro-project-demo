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
# 确保所有 Lambda 实例使用相同的 JWT 密钥（demo 用途）
os.environ.setdefault("JWT_SECRET_KEY", "vercel-demo-stocks-assist-2024-fixed-key")
# Demo 环境延长 token 有效期（7 天 = 10080 分钟）
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")

from app.main import app  # noqa: E402
