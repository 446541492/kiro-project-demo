# 工作单元定义 - Stocks Assist

## 分解策略

系统分解为 6 个工作单元，按依赖关系顺序执行。将认证、行情、自选管理等业务模块独立拆分，便于开发和测试。

---

## 单元概览

| 单元 | 名称 | 类型 | 说明 |
|------|------|------|------|
| U1 | 后端认证模块 | 后端 | 用户注册/登录、JWT、2FA |
| U2 | 后端行情模块 | 后端 | Tushare 集成、行情查询、搜索 |
| U3 | 后端自选管理模块 | 后端 | 自选组合和标的 CRUD |
| U4 | 前端基础架构 | 前端 | 项目搭建、路由、状态管理、布局 |
| U5 | 前端认证与个人中心 | 前端 | 登录/注册、2FA、个人中心 |
| U6 | 前端行情与自选 | 前端 | 行情榜单、搜索、自选管理 |

---

## 单元详细定义

### 单元 1：后端认证模块 (U1)

**职责**: 用户身份认证和授权的完整实现

**包含组件**:
- FastAPI 项目搭建和基础配置
- 数据库模型（User, Device）和迁移脚本
- SecurityUtils（密码加密、JWT Token 管理）
- AuthService（注册、登录、登出、Token 刷新）
- UserService（用户信息管理、设备记录）
- TwoFactorService（TOTP 密钥生成、二维码、验证）
- auth_router（认证相关 API 路由）
- JWT 认证中间件
- 数据库连接管理（DatabaseManager）

**交付物**:
- `backend/` 项目基础结构
- 用户认证相关的所有 API
- 数据库初始化和迁移脚本
- 测试用户数据

**前置依赖**: 无

---

### 单元 2：后端行情模块 (U2)

**职责**: 行情数据获取、缓存和查询

**包含组件**:
- TushareClient（Tushare API 客户端封装）
- MarketService（行情服务：榜单、搜索、行情查询、缓存）
- market_router（行情相关 API 路由）

**交付物**:
- 行情相关的所有 API
- Tushare API 集成和数据转换
- 内存缓存机制

**前置依赖**: U1（需要 FastAPI 基础架构和 JWT 中间件）

---

### 单元 3：后端自选管理模块 (U3)

**职责**: 自选组合和标的的完整管理

**包含组件**:
- 数据库模型（Portfolio, WatchlistItem）
- PortfolioService（组合 CRUD、排序、默认组合）
- WatchlistService（标的 CRUD、排序、行情合并）
- portfolio_router（组合 API 路由）
- watchlist_router（标的 API 路由）

**交付物**:
- 自选组合和标的相关的所有 API
- 示例自选组合和标的测试数据
- 启动脚本（npm run dev:all）

**前置依赖**: U1（数据库基础、JWT 中间件）、U2（MarketService 获取实时行情）

---

### 单元 4：前端基础架构 (U4)

**职责**: 前端项目搭建和基础设施

**包含组件**:
- React + TypeScript + Vite 项目初始化
- Ant Design 5.x 集成和主题配置（深色/浅色）
- React Router v6 路由配置（History 模式）
- Zustand Store 定义（useAuthStore, useMarketStore, usePortfolioStore, useThemeStore）
- Axios HTTP 客户端封装（apiClient：拦截器、Token 注入、错误处理、自动刷新）
- 全局布局组件（AppLayout, Navbar, BottomTabBar）
- 主题切换组件（ThemeSwitch）
- ESLint + Prettier 配置

**交付物**:
- `frontend/` 项目基础结构
- 全局布局和导航
- 状态管理和 API 客户端
- 主题切换功能

**前置依赖**: U1（需要后端 API 地址进行 apiClient 配置）

---

### 单元 5：前端认证与个人中心 (U5)

**职责**: 用户认证界面和个人设置

**包含组件**:
- LoginPage（登录页）
- RegisterPage（注册页）
- SliderCaptcha（滑块验证码组件）
- TwoFactorSetupPage（2FA 设置页）
- ProfilePage（个人中心页）
- authApi（认证 API 服务）

**交付物**:
- 登录/注册完整流程
- 滑块验证码
- 2FA 启用/禁用/验证
- 个人中心（信息查看、密码修改、设备管理）

**前置依赖**: U1（后端认证 API）、U4（前端基础架构）

---

### 单元 6：前端行情与自选 (U6)

**职责**: 行情展示和自选组合管理界面

**包含组件**:
- MarketPage（行情页/首页）
- MarketRanking（行情榜单组件）
- SymbolSearch（标的搜索组件）
- WatchlistPage（自选页）
- PortfolioList（自选组合列表组件）
- SymbolList（标的列表组件）
- PortfolioModal（组合管理弹窗组件）
- SymbolCard（标的行情卡片组件）
- marketApi（行情 API 服务）
- portfolioApi（自选组合 API 服务）

**交付物**:
- 行情榜单展示（标签页切换）
- 标的搜索（下拉列表）
- 自选组合管理（创建/重命名/删除/拖拽排序）
- 自选标的管理（添加/移除/拖拽排序）
- 从搜索/榜单快速添加标的到自选

**前置依赖**: U2（后端行情 API）、U3（后端自选管理 API）、U4（前端基础架构）

---

## 执行顺序

```
阶段 1: U1（后端认证模块）
    |
阶段 2: U2（后端行情模块）+ U4（前端基础架构）  [可并行]
    |
阶段 3: U3（后端自选管理模块）+ U5（前端认证与个人中心）  [可并行]
    |
阶段 4: U6（前端行情与自选）
```

**说明**:
- U1 必须最先完成（所有模块的基础）
- U2 和 U4 可以并行（互不依赖）
- U3 和 U5 可以并行（U3 依赖 U1+U2，U5 依赖 U1+U4）
- U6 最后完成（依赖 U2+U3+U4）

---

## 代码组织策略

```
stocks-assist/
├── frontend/                        # 前端项目 (U4, U5, U6)
│   ├── public/
│   ├── src/
│   │   ├── api/                     # API 服务层
│   │   │   ├── client.ts            # Axios 客户端
│   │   │   ├── auth.ts              # 认证 API
│   │   │   ├── market.ts            # 行情 API
│   │   │   └── portfolio.ts         # 自选组合 API
│   │   ├── components/              # 业务组件
│   │   │   ├── SliderCaptcha/
│   │   │   ├── MarketRanking/
│   │   │   ├── SymbolSearch/
│   │   │   ├── PortfolioList/
│   │   │   ├── SymbolList/
│   │   │   ├── PortfolioModal/
│   │   │   ├── SymbolCard/
│   │   │   └── ThemeSwitch/
│   │   ├── layouts/                 # 布局组件
│   │   │   ├── AppLayout.tsx
│   │   │   ├── Navbar.tsx
│   │   │   └── BottomTabBar.tsx
│   │   ├── pages/                   # 页面组件
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── MarketPage.tsx
│   │   │   ├── WatchlistPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   └── TwoFactorSetupPage.tsx
│   │   ├── stores/                  # Zustand 状态管理
│   │   │   ├── authStore.ts
│   │   │   ├── marketStore.ts
│   │   │   ├── portfolioStore.ts
│   │   │   └── themeStore.ts
│   │   ├── types/                   # TypeScript 类型定义
│   │   │   └── index.ts
│   │   ├── utils/                   # 工具函数
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── .eslintrc.cjs
│
├── backend/                         # 后端项目 (U1, U2, U3)
│   ├── app/
│   │   ├── routers/                 # API 路由
│   │   │   ├── auth.py
│   │   │   ├── market.py
│   │   │   ├── portfolio.py
│   │   │   └── watchlist.py
│   │   ├── services/                # 业务服务
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── market_service.py
│   │   │   ├── portfolio_service.py
│   │   │   ├── watchlist_service.py
│   │   │   └── two_factor_service.py
│   │   ├── models/                  # 数据模型
│   │   │   ├── user.py
│   │   │   ├── device.py
│   │   │   ├── portfolio.py
│   │   │   └── watchlist_item.py
│   │   ├── schemas/                 # Pydantic 请求/响应模型
│   │   │   ├── auth.py
│   │   │   ├── market.py
│   │   │   ├── portfolio.py
│   │   │   └── watchlist.py
│   │   ├── core/                    # 核心配置
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── deps.py
│   │   ├── clients/                 # 外部 API 客户端
│   │   │   └── tushare_client.py
│   │   └── main.py                  # 应用入口
│   ├── data/                        # 数据目录
│   │   └── database.db
│   ├── migrations/                  # 数据库迁移
│   │   └── init_db.py
│   ├── tests/                       # 测试
│   ├── requirements.txt
│   └── .env.example
│
├── aidlc-docs/                      # AI-DLC 文档
├── package.json                     # 根目录启动脚本
└── README.md
```
