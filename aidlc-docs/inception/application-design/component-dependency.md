# 组件依赖关系文档 - Stocks Assist

## 一、后端依赖关系

### 依赖关系图

```
+------------------------------------------------------------------+
|                        API 路由层                                  |
|  +-------------+ +-------------+ +-----------+ +---------------+  |
|  | auth_router | | market_     | | portfolio_| | watchlist_    |  |
|  |             | | router      | | router    | | router        |  |
|  +------+------+ +------+------+ +-----+-----+ +-------+-------+  |
|         |               |              |                |          |
+------------------------------------------------------------------+
          |               |              |                |
          v               v              v                v
+------------------------------------------------------------------+
|                        服务层                                      |
|  +-------------+ +-------------+ +-----------+ +---------------+  |
|  | AuthService | | Market      | | Portfolio | | Watchlist     |  |
|  |             | | Service     | | Service   | | Service       |  |
|  +--+----+-----+ +------+------+ +-----+-----+ +----+----+-----+  |
|     |    |              |              |             |    |        |
|     |    |              |              |             |    |        |
|  +--v--+ +--v--------+  |              |             |    |        |
|  |User | |TwoFactor  |  |              |             |    |        |
|  |Svc  | |Service    |  |              |             |    |        |
|  +-----+ +-----------+  |              |             |    |        |
+------------------------------------------------------------------+
          |               |              |             |    |
          v               v              v             v    v
+------------------------------------------------------------------+
|                     基础设施层                                     |
|  +----------------+ +----------------+ +------------------------+ |
|  | SecurityUtils  | | TushareClient  | | DatabaseManager        | |
|  | (JWT/bcrypt)   | | (行情数据)      | | (SQLAlchemy/SQLite)    | |
|  +----------------+ +----------------+ +------------------------+ |
+------------------------------------------------------------------+
```

### 依赖矩阵

| 组件 | 依赖 | 依赖类型 | 说明 |
|------|------|---------|------|
| auth_router | AuthService | 直接 | 认证业务逻辑 |
| auth_router | JWT 中间件 | 直接 | 部分接口需要认证 |
| market_router | MarketService | 直接 | 行情业务逻辑 |
| market_router | JWT 中间件 | 直接 | 需要用户认证 |
| portfolio_router | PortfolioService | 直接 | 组合业务逻辑 |
| portfolio_router | JWT 中间件 | 直接 | 需要用户认证 |
| watchlist_router | WatchlistService | 直接 | 标的业务逻辑 |
| watchlist_router | JWT 中间件 | 直接 | 需要用户认证 |
| AuthService | UserService | 直接 | 用户查询/创建 |
| AuthService | TwoFactorService | 直接 | 2FA 验证 |
| AuthService | PortfolioService | 直接 | 注册时创建默认组合 |
| AuthService | SecurityUtils | 直接 | 密码加密/Token 生成 |
| AuthService | DatabaseManager | 直接 | 数据持久化 |
| MarketService | TushareClient | 直接 | 行情数据获取 |
| PortfolioService | DatabaseManager | 直接 | 数据持久化 |
| WatchlistService | DatabaseManager | 直接 | 数据持久化 |
| WatchlistService | MarketService | 直接 | 获取标的实时行情 |
| TwoFactorService | PyOTP | 外部库 | TOTP 实现 |
| SecurityUtils | bcrypt | 外部库 | 密码加密 |
| SecurityUtils | PyJWT | 外部库 | JWT 处理 |
| TushareClient | tushare | 外部库 | 行情 API |

---

## 二、前端依赖关系

### 依赖关系图

```
+------------------------------------------------------------------+
|                        页面组件层                                  |
|  +----------+ +----------+ +----------+ +----------+ +----------+ |
|  | Login    | | Register | | Market   | | Watchlist| | Profile  | |
|  | Page     | | Page     | | Page     | | Page     | | Page     | |
|  +----+-----+ +----+-----+ +----+-----+ +----+-----+ +----+-----+ |
|       |            |            |            |            |        |
+------------------------------------------------------------------+
        |            |            |            |            |
        v            v            v            v            v
+------------------------------------------------------------------+
|                        业务组件层                                  |
|  +----------+ +----------+ +----------+ +----------+ +----------+ |
|  | Slider   | | Market   | | Symbol   | | Portfolio| | Symbol   | |
|  | Captcha  | | Ranking  | | Search   | | List     | | List     | |
|  +----------+ +----------+ +----------+ +----------+ +----------+ |
|  +----------+ +----------+ +----------+                           |
|  | Portfolio| | Symbol   | | Theme    |                           |
|  | Modal    | | Card     | | Switch   |                           |
|  +----------+ +----------+ +----------+                           |
+------------------------------------------------------------------+
        |            |            |            |            |
        v            v            v            v            v
+------------------------------------------------------------------+
|                     状态管理层 (Zustand)                           |
|  +-------------+ +-------------+ +-----------+ +---------------+  |
|  | useAuth     | | useMarket   | | usePort   | | useTheme      |  |
|  | Store       | | Store       | | folioStore| | Store         |  |
|  +------+------+ +------+------+ +-----+-----+ +-------+-------+  |
+------------------------------------------------------------------+
          |               |              |                |
          v               v              v                v
+------------------------------------------------------------------+
|                     API 服务层                                     |
|  +-------------+ +-------------+ +-----------+                    |
|  | authApi     | | marketApi   | | portfolio |                    |
|  |             | |             | | Api       |                    |
|  +------+------+ +------+------+ +-----+-----+                    |
+------------------------------------------------------------------+
          |               |              |
          v               v              v
+------------------------------------------------------------------+
|                     HTTP 客户端                                    |
|  +----------------------------------------------------------+     |
|  | apiClient (Axios)                                         |     |
|  | - 请求拦截: Token 注入                                     |     |
|  | - 响应拦截: 错误处理、Token 刷新                            |     |
|  +----------------------------------------------------------+     |
+------------------------------------------------------------------+
          |
          v
    后端 API (FastAPI)
```

### 页面组件依赖

| 页面组件 | 业务组件 | Store | API 服务 |
|---------|---------|-------|---------|
| LoginPage | SliderCaptcha | useAuthStore | authApi |
| RegisterPage | SliderCaptcha | useAuthStore | authApi |
| MarketPage | MarketRanking, SymbolSearch | useMarketStore, usePortfolioStore | marketApi |
| WatchlistPage | PortfolioList, SymbolList, PortfolioModal, SymbolCard, SymbolSearch | usePortfolioStore, useMarketStore | portfolioApi |
| ProfilePage | ThemeSwitch | useAuthStore, useThemeStore | authApi |
| TwoFactorSetupPage | - | useAuthStore | authApi |

### 布局组件依赖

| 布局组件 | 依赖 | 说明 |
|---------|------|------|
| AppLayout | Navbar, BottomTabBar, useAuthStore | 全局布局，根据登录状态显示不同内容 |
| Navbar | useAuthStore, useThemeStore, SymbolSearch | 桌面端导航，包含搜索和用户菜单 |
| BottomTabBar | useAuthStore | 移动端底部导航 |

---

## 三、数据流向

### 用户认证数据流
```
用户输入 -> LoginPage -> useAuthStore.login()
  -> authApi.login() -> apiClient -> 后端 /api/auth/login
  -> AuthService -> SecurityUtils -> 数据库
  -> 返回 Token -> useAuthStore 保存 Token -> localStorage 持久化
```

### 行情数据流
```
页面加载 -> MarketPage -> useMarketStore.fetchRankings()
  -> marketApi.getRankings() -> apiClient -> 后端 /api/market/rankings
  -> MarketService -> TushareClient -> Tushare API
  -> 返回行情数据 -> useMarketStore 更新状态 -> MarketRanking 组件渲染
```

### 自选管理数据流
```
用户操作 -> WatchlistPage -> usePortfolioStore.addItem()
  -> portfolioApi.addItem() -> apiClient -> 后端 /api/portfolios/{id}/items
  -> WatchlistService -> 数据库
  -> 返回标的信息 -> usePortfolioStore 更新状态 -> SymbolList 组件渲染
```

---

## 四、通信模式

### 前后端通信
- **协议**: HTTP/HTTPS
- **格式**: JSON
- **认证**: JWT Bearer Token（Authorization 头）
- **错误处理**: 统一错误响应格式 `{ detail: string, code: string }`

### 后端内部通信
- **模式**: 直接方法调用（依赖注入）
- **数据库访问**: SQLAlchemy ORM + 异步会话
- **外部 API**: Tushare Python SDK

### 前端内部通信
- **状态管理**: Zustand Store（响应式更新）
- **组件通信**: Props 传递 + Store 共享状态
- **事件处理**: React 事件系统

---

## 五、第三方依赖

### 后端依赖
| 依赖 | 版本 | 用途 |
|------|------|------|
| fastapi | 最新 | Web 框架 |
| uvicorn | 最新 | ASGI 服务器 |
| sqlalchemy | 最新 | ORM |
| aiosqlite | 最新 | SQLite 异步驱动 |
| pyjwt | 最新 | JWT 处理 |
| bcrypt | 最新 | 密码加密 |
| pyotp | 最新 | TOTP 实现 |
| qrcode | 最新 | 二维码生成 |
| tushare | 最新 | 行情数据 |
| pydantic | 最新 | 数据验证 |

### 前端依赖
| 依赖 | 版本 | 用途 |
|------|------|------|
| react | 18.x | UI 框架 |
| react-router-dom | 6.x | 路由 |
| antd | 5.x | UI 组件库 |
| zustand | 最新 | 状态管理 |
| axios | 最新 | HTTP 客户端 |
| @dnd-kit/core | 最新 | 拖拽排序 |
| react-slider-captcha | 最新 | 滑块验证码（或自实现） |
