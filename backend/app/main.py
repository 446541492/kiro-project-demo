"""
FastAPI 应用入口
配置 CORS、全局异常处理、频率限制中间件和路由注册
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import AppException

settings = get_settings()

# 配置日志
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


# ==================== 频率限制 ====================

rate_limit_store: dict[str, dict] = defaultdict(
    lambda: {"count": 0, "reset_time": 0.0}
)
RATE_LIMIT_MAX = 60
RATE_LIMIT_WINDOW = 60


# ==================== 创建应用 ====================

app = FastAPI(
    title=settings.APP_NAME,
    description="股票助手 - 自选标的管理系统 API",
    version="1.0.0",
)

# ==================== CORS 中间件 ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Device-Id"],
    max_age=600,
)


# ==================== 频率限制中间件 ====================

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """请求频率限制中间件，基于 IP 地址"""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    entry = rate_limit_store[client_ip]
    if now >= entry["reset_time"]:
        entry["count"] = 1
        entry["reset_time"] = now + RATE_LIMIT_WINDOW
    else:
        entry["count"] += 1

    if entry["count"] > RATE_LIMIT_MAX:
        return JSONResponse(
            status_code=429,
            content={"detail": "请求过于频繁，请稍后重试", "code": "RATE_LIMITED"},
        )

    response = await call_next(request)
    return response


# ==================== 全局异常处理 ====================

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """处理自定义业务异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误", "code": "INTERNAL_ERROR"},
    )


# ==================== 注册路由 ====================

from app.routers.auth import router as auth_router  # noqa: E402
from app.routers.market import router as market_router  # noqa: E402
from app.routers.portfolio import router as portfolio_router  # noqa: E402
from app.routers.watchlist import router as watchlist_router  # noqa: E402

app.include_router(auth_router)
app.include_router(market_router)
app.include_router(portfolio_router)
app.include_router(watchlist_router)


# ==================== 健康检查 ====================

@app.get("/api/health", tags=["系统"])
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "app": settings.APP_NAME}
