# U1 后端认证模块 - 代码生成计划

## 单元上下文

### 单元信息
- **单元名称**: U1 - 后端认证模块
- **单元类型**: 后端 (Python/FastAPI)
- **项目类型**: 全新项目 (Greenfield)
- **代码位置**: `backend/`

### 实现的功能需求
| 功能需求 | 优先级 |
|---------|--------|
| 1.1 用户注册（手机/邮箱） | P0 |
| 1.2 用户登录 | P0 |
| 1.2 JWT Token 认证 | P0 |
| 1.3 两步验证 (2FA) | P1 |
| 1.4 用户管理（查看信息、修改密码、登出） | P1 |
| 1.2 新设备检测 | P2 |
| 1.4 设备管理 | P2 |
| 数据模型：users, devices, recovery_codes | P0 |

### 依赖关系
- **前置依赖**: 无（U1 是所有单元的基础）
- **被依赖**: U2, U3, U4, U5 均依赖 U1

### 数据库实体
- User（用户）
- Device（设备）
- RecoveryCode（恢复码）

---

## 代码生成步骤

### 步骤 1：项目基础结构搭建
- [x] 创建 `backend/` 目录结构
- [x] 创建 `backend/requirements.txt` — Python 依赖清单
- [x] 创建 `backend/.env.example` — 环境变量模板
- [x] 创建 `backend/app/__init__.py`
- [x] 创建 `backend/app/core/__init__.py`
- [x] 创建 `backend/app/models/__init__.py`
- [x] 创建 `backend/app/schemas/__init__.py`
- [x] 创建 `backend/app/routers/__init__.py`
- [x] 创建 `backend/app/services/__init__.py`
- [x] 创建 `backend/tests/__init__.py`
- [x] 创建 `backend/data/.gitkeep`

### 步骤 2：核心配置层
- [x] 创建 `backend/app/core/config.py` — Pydantic Settings 应用配置
- [x] 创建 `backend/app/core/database.py` — SQLAlchemy 异步引擎和会话管理
- [x] 创建 `backend/app/core/security.py` — JWT Token 和 bcrypt 密码工具

### 步骤 3：数据模型层
- [x] 创建 `backend/app/models/base.py` — SQLAlchemy Base 声明
- [x] 创建 `backend/app/models/user.py` — User 模型
- [x] 创建 `backend/app/models/device.py` — Device 模型
- [x] 创建 `backend/app/models/recovery_code.py` — RecoveryCode 模型
- [x] 更新 `backend/app/models/__init__.py` — 导出所有模型

### 步骤 4：请求/响应模型层
- [x] 创建 `backend/app/schemas/auth.py` — 认证相关 Pydantic 模型（注册、登录、Token、用户信息、2FA、密码修改、设备）
- [x] 创建 `backend/app/schemas/common.py` — 通用响应模型（错误响应、成功响应）

### 步骤 5：自定义异常和依赖注入
- [x] 创建 `backend/app/core/exceptions.py` — 自定义异常类层次（AppException 及子类）
- [x] 创建 `backend/app/core/deps.py` — FastAPI 依赖注入（get_db, get_current_user, get_current_active_user）

### 步骤 6：业务服务层 — 认证服务
- [x] 创建 `backend/app/services/auth_service.py` — AuthService（注册、登录、登出、Token 刷新）
  - 功能需求: 1.1 用户注册, 1.2 用户登录, 1.2 JWT Token 认证

### 步骤 7：业务服务层 — 用户服务和 2FA 服务
- [x] 创建 `backend/app/services/user_service.py` — UserService（获取用户信息、修改密码、设备管理）
  - 功能需求: 1.4 用户管理, 1.2 新设备检测, 1.4 设备管理
- [x] 创建 `backend/app/services/two_factor_service.py` — TwoFactorService（TOTP 密钥生成、二维码、验证、恢复码）
  - 功能需求: 1.3 两步验证 (2FA)

### 步骤 8：API 路由层
- [x] 创建 `backend/app/routers/auth.py` — 认证 API 路由
  - POST /api/auth/register — 用户注册
  - POST /api/auth/login — 用户登录
  - POST /api/auth/logout — 用户登出
  - POST /api/auth/refresh — Token 刷新
  - GET /api/auth/me — 获取当前用户信息
  - PUT /api/auth/password — 修改密码
  - POST /api/auth/2fa/setup — 启用 2FA（获取密钥和二维码）
  - POST /api/auth/2fa/enable — 确认启用 2FA（验证首次 TOTP 码）
  - POST /api/auth/2fa/verify — 登录时 2FA 验证
  - POST /api/auth/2fa/disable — 禁用 2FA
  - GET /api/auth/2fa/recovery-codes — 获取恢复码
  - POST /api/auth/2fa/recovery-codes/regenerate — 重新生成恢复码
  - GET /api/auth/devices — 获取设备列表

### 步骤 9：应用入口和中间件
- [x] 创建 `backend/app/main.py` — FastAPI 应用入口
  - CORS 中间件配置
  - 全局异常处理器
  - 请求频率限制中间件
  - 路由注册
  - 启动事件（数据库初始化）

### 步骤 10：数据库初始化和测试数据
- [x] 创建 `backend/migrations/init_db.py` — 数据库初始化脚本
  - 创建所有表
  - 插入测试用户（admin, testuser）
  - 为测试用户创建默认自选组合

### 步骤 11：单元测试
- [x] 创建 `backend/tests/conftest.py` — 测试配置和 fixtures
  - 内存 SQLite 测试数据库
  - httpx AsyncClient
  - 预创建测试用户
  - 带 Token 的请求头
- [x] 创建 `backend/tests/test_auth.py` — 认证 API 测试
  - 注册测试（正常/重复/格式错误）
  - 登录测试（正常/错误密码/锁定/验证码触发）
  - Token 刷新测试
  - 登出测试
  - 获取用户信息测试
- [x] 创建 `backend/tests/test_2fa.py` — 2FA 测试
  - 启用 2FA 测试
  - TOTP 验证测试
  - 禁用 2FA 测试
  - 恢复码测试
- [x] 创建 `backend/tests/test_password.py` — 密码相关测试
  - 修改密码测试
  - 密码策略验证测试

### 步骤 12：根目录启动脚本
- [x] 创建 `package.json` — 根目录启动脚本（npm run dev:all）

### 步骤 13：代码生成总结
- [x] 验证所有文件已创建
- [x] 确认功能需求覆盖完整
- [x] 创建代码生成总结文档 `aidlc-docs/construction/u1-backend-auth/code/code-summary.md`

---

## 文件清单

| 文件路径 | 说明 |
|---------|------|
| `backend/requirements.txt` | Python 依赖 |
| `backend/.env.example` | 环境变量模板 |
| `backend/app/__init__.py` | 包初始化 |
| `backend/app/main.py` | FastAPI 应用入口 |
| `backend/app/core/__init__.py` | 核心包初始化 |
| `backend/app/core/config.py` | 应用配置 |
| `backend/app/core/database.py` | 数据库连接 |
| `backend/app/core/security.py` | 安全工具 |
| `backend/app/core/exceptions.py` | 自定义异常 |
| `backend/app/core/deps.py` | 依赖注入 |
| `backend/app/models/__init__.py` | 模型包初始化 |
| `backend/app/models/base.py` | SQLAlchemy Base |
| `backend/app/models/user.py` | User 模型 |
| `backend/app/models/device.py` | Device 模型 |
| `backend/app/models/recovery_code.py` | RecoveryCode 模型 |
| `backend/app/schemas/__init__.py` | Schema 包初始化 |
| `backend/app/schemas/auth.py` | 认证 Schema |
| `backend/app/schemas/common.py` | 通用 Schema |
| `backend/app/routers/__init__.py` | 路由包初始化 |
| `backend/app/routers/auth.py` | 认证路由 |
| `backend/app/services/__init__.py` | 服务包初始化 |
| `backend/app/services/auth_service.py` | 认证服务 |
| `backend/app/services/user_service.py` | 用户服务 |
| `backend/app/services/two_factor_service.py` | 2FA 服务 |
| `backend/data/.gitkeep` | 数据目录占位 |
| `backend/migrations/init_db.py` | 数据库初始化 |
| `backend/tests/__init__.py` | 测试包初始化 |
| `backend/tests/conftest.py` | 测试配置 |
| `backend/tests/test_auth.py` | 认证测试 |
| `backend/tests/test_2fa.py` | 2FA 测试 |
| `backend/tests/test_password.py` | 密码测试 |
| `package.json` | 根目录启动脚本 |

**总计**: 31 个文件，13 个步骤
