# U1 技术栈决策 - 后端认证模块

## 核心技术栈

| 技术 | 版本 | 选择理由 |
|------|------|---------|
| Python | 3.10+ | 现代 Python 特性（类型提示、async/await） |
| FastAPI | 0.100+ | 高性能异步框架，自动 API 文档，类型安全 |
| Uvicorn | 最新 | ASGI 服务器，支持异步 |
| SQLAlchemy | 2.0+ | 成熟的 ORM，支持异步，类型提示友好 |
| aiosqlite | 最新 | SQLite 异步驱动 |
| Pydantic | 2.0+ | 数据验证和序列化，FastAPI 原生支持 |

## 安全相关依赖

| 技术 | 版本 | 选择理由 |
|------|------|---------|
| bcrypt | 最新 | 业界标准密码哈希算法 |
| PyJWT | 最新 | JWT Token 编码/解码 |
| PyOTP | 最新 | TOTP 实现，兼容 Google Authenticator |
| qrcode | 最新 | 2FA 二维码生成 |
| Pillow | 最新 | qrcode 图片生成依赖 |

## 开发工具

| 技术 | 版本 | 选择理由 |
|------|------|---------|
| pytest | 最新 | Python 测试框架 |
| pytest-asyncio | 最新 | 异步测试支持 |
| httpx | 最新 | 异步 HTTP 客户端，用于 API 测试 |
| python-dotenv | 最新 | 环境变量管理 |

## 技术决策说明

### 为什么选择 FastAPI？
- 原生异步支持，性能优秀
- 自动生成 OpenAPI/Swagger 文档
- Pydantic 集成，类型安全
- 依赖注入系统，便于测试和扩展
- 学习曲线低，社区活跃

### 为什么选择 SQLite？
- 用户选择，适合本地开发和演示
- 零配置，无需安装数据库服务
- 通过 SQLAlchemy ORM 抽象，未来可轻松切换到 PostgreSQL/MySQL
- aiosqlite 提供异步支持

### 为什么选择 bcrypt？
- 业界标准的密码哈希算法
- 内置 salt，防止彩虹表攻击
- cost factor 可调，平衡安全性和性能
- 广泛使用，经过充分安全审计

### 为什么选择 PyJWT + HS256？
- 轻量级，适合单服务架构
- HS256 对称加密，性能好
- 如果未来需要微服务架构，可切换到 RS256

### 项目结构决策

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── core/                # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py        # Pydantic Settings 配置
│   │   ├── database.py      # 数据库连接管理
│   │   ├── security.py      # JWT/bcrypt 工具
│   │   └── deps.py          # FastAPI 依赖注入
│   ├── models/              # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── device.py
│   │   └── recovery_code.py
│   ├── schemas/             # Pydantic 请求/响应模型
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── routers/             # API 路由
│   │   ├── __init__.py
│   │   └── auth.py
│   └── services/            # 业务服务
│       ├── __init__.py
│       ├── auth_service.py
│       ├── user_service.py
│       └── two_factor_service.py
├── data/                    # 数据目录
│   └── .gitkeep
├── migrations/              # 数据库迁移
│   └── init_db.py
├── tests/                   # 测试
│   ├── __init__.py
│   ├── conftest.py          # 测试配置和 fixtures
│   ├── test_auth.py
│   └── test_2fa.py
├── .env.example             # 环境变量示例
└── requirements.txt         # Python 依赖
```

### 环境变量配置

```env
# 数据库
DATABASE_URL=sqlite+aiosqlite:///./data/database.db

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# 2FA
TWO_FA_ISSUER=StocksAssist

# CORS
CORS_ORIGINS=http://localhost:5173

# 应用
APP_NAME=Stocks Assist
DEBUG=true
```
