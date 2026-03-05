# 组件定义文档 - Stocks Assist

## 一、后端组件

### 1. API 路由层

#### 1.1 auth_router（认证路由）
- **职责**: 处理用户注册、登录、登出、Token 刷新等认证相关请求
- **接口**:
  - POST /api/auth/register - 用户注册
  - POST /api/auth/login - 用户登录
  - POST /api/auth/logout - 用户登出
  - POST /api/auth/refresh - 刷新 Token
  - GET /api/auth/me - 获取当前用户信息
  - POST /api/auth/2fa/enable - 启用 2FA
  - POST /api/auth/2fa/verify - 验证 2FA
  - POST /api/auth/2fa/disable - 禁用 2FA
  - GET /api/auth/2fa/recovery-codes - 获取恢复码

#### 1.2 market_router（行情路由）
- **职责**: 处理行情数据查询、榜单获取、标的搜索等请求
- **接口**:
  - GET /api/market/rankings - 获取行情榜单
  - GET /api/market/search - 搜索标的
  - GET /api/market/quote/{symbol} - 获取标的详情

#### 1.3 portfolio_router（自选组合路由）
- **职责**: 处理自选组合的增删改查和排序
- **接口**:
  - GET /api/portfolios - 获取用户所有组合
  - POST /api/portfolios - 创建新组合
  - PUT /api/portfolios/{id} - 更新组合
  - DELETE /api/portfolios/{id} - 删除组合
  - PUT /api/portfolios/reorder - 调整组合排序

#### 1.4 watchlist_router（自选标的路由）
- **职责**: 处理组合内标的的增删和排序
- **接口**:
  - GET /api/portfolios/{id}/items - 获取组合内标的
  - POST /api/portfolios/{id}/items - 添加标的
  - DELETE /api/portfolios/{id}/items/{item_id} - 移除标的
  - PUT /api/portfolios/{id}/items/reorder - 调整标的排序

### 2. 服务层

#### 2.1 AuthService（认证服务）
- **职责**: 用户注册、登录验证、Token 管理、密码加密
- **依赖**: UserService, TwoFactorService, 数据库

#### 2.2 UserService（用户服务）
- **职责**: 用户信息管理、设备记录
- **依赖**: 数据库

#### 2.3 MarketService（行情服务）
- **职责**: 对接 Tushare API，获取行情数据、榜单、搜索结果
- **依赖**: TushareClient, 缓存

#### 2.4 PortfolioService（自选组合服务）
- **职责**: 自选组合的增删改查、排序管理
- **依赖**: 数据库

#### 2.5 WatchlistService（自选标的服务）
- **职责**: 组合内标的的增删、排序管理
- **依赖**: 数据库, MarketService（获取标的信息）

#### 2.6 TwoFactorService（两步验证服务）
- **职责**: TOTP 密钥生成、二维码生成、验证码验证、恢复码管理
- **依赖**: PyOTP 库

### 3. 数据模型层

#### 3.1 User（用户模型）
- **职责**: 用户数据的持久化和查询
- **字段**: id, username, email, phone, password_hash, is_2fa_enabled, totp_secret, created_at, updated_at

#### 3.2 Device（设备模型）
- **职责**: 登录设备信息的记录
- **字段**: id, user_id, device_id, device_name, last_login_at, created_at

#### 3.3 Portfolio（自选组合模型）
- **职责**: 自选组合数据的持久化和查询
- **字段**: id, user_id, name, sort_order, is_default, created_at, updated_at

#### 3.4 WatchlistItem（自选标的模型）
- **职责**: 自选标的数据的持久化和查询
- **字段**: id, portfolio_id, symbol, name, market, sort_order, created_at

### 4. 工具层

#### 4.1 TushareClient（Tushare API 客户端）
- **职责**: 封装 Tushare API 调用，提供统一的数据获取接口
- **功能**: 行情查询、榜单获取、标的搜索、数据缓存

#### 4.2 SecurityUtils（安全工具）
- **职责**: 密码哈希、JWT Token 生成/验证
- **功能**: bcrypt 加密、JWT 编码/解码、Token 过期管理

#### 4.3 DatabaseManager（数据库管理）
- **职责**: SQLite 数据库连接管理、会话管理
- **功能**: 连接池、事务管理、迁移脚本

---

## 二、前端组件

### 1. 页面组件

#### 1.1 LoginPage（登录页）
- **职责**: 用户登录表单、滑块验证码、2FA 验证
- **路由**: /login

#### 1.2 RegisterPage（注册页）
- **职责**: 用户注册表单、滑块验证码
- **路由**: /register

#### 1.3 MarketPage（行情页/首页）
- **职责**: 展示行情榜单、标的搜索入口
- **路由**: /market

#### 1.4 WatchlistPage（自选页）
- **职责**: 展示自选组合列表、组合内标的列表、组合管理
- **路由**: /watchlist

#### 1.5 ProfilePage（个人中心页）
- **职责**: 用户信息展示、密码修改、2FA 设置、设备管理、主题切换
- **路由**: /profile

#### 1.6 TwoFactorSetupPage（2FA 设置页）
- **职责**: 2FA 启用/禁用、二维码展示、恢复码管理
- **路由**: /profile/2fa

### 2. 业务组件

#### 2.1 SliderCaptcha（滑块验证码）
- **职责**: 前端生成滑块验证码，验证用户操作
- **使用场景**: 登录、注册

#### 2.2 MarketRanking（行情榜单）
- **职责**: 展示各类行情榜单数据（涨幅榜、跌幅榜等）
- **交互**: 标签页切换榜单类型，点击标的可添加到自选

#### 2.3 SymbolSearch（标的搜索）
- **职责**: 搜索标的，展示搜索结果下拉列表
- **交互**: 输入搜索、键盘导航、点击添加到自选

#### 2.4 PortfolioList（自选组合列表）
- **职责**: 展示用户的自选组合列表，支持拖拽排序
- **交互**: 点击切换组合、右键/长按弹出管理菜单

#### 2.5 SymbolList（标的列表）
- **职责**: 展示当前组合内的标的列表及实时行情
- **交互**: 拖拽排序、滑动删除、点击查看详情

#### 2.6 PortfolioModal（组合管理弹窗）
- **职责**: 创建/重命名/删除组合的弹窗
- **交互**: 表单输入、确认/取消

#### 2.7 SymbolCard（标的行情卡片）
- **职责**: 展示单个标的的行情信息
- **数据**: 代码、名称、价格、涨跌幅、成交量等

#### 2.8 ThemeSwitch（主题切换）
- **职责**: 切换深色/浅色主题
- **交互**: 开关切换

### 3. 布局组件

#### 3.1 AppLayout（应用布局）
- **职责**: 全局布局容器，包含导航栏和内容区域
- **响应式**: 桌面端顶部导航 + 移动端底部标签栏

#### 3.2 Navbar（顶部导航栏）
- **职责**: 桌面端顶部导航，包含 Logo、导航链接、搜索、用户菜单
- **显示条件**: 桌面端（宽度 >= 768px）

#### 3.3 BottomTabBar（底部标签栏）
- **职责**: 移动端底部导航，包含行情、自选、我的标签
- **显示条件**: 移动端（宽度 < 768px）

### 4. 状态管理

#### 4.1 useAuthStore（认证状态）
- **职责**: 管理用户登录状态、Token、用户信息
- **数据**: token, user, isAuthenticated, is2FARequired

#### 4.2 useMarketStore（行情状态）
- **职责**: 管理行情数据、榜单数据、搜索结果
- **数据**: rankings, searchResults, currentQuote, refreshInterval

#### 4.3 usePortfolioStore（自选组合状态）
- **职责**: 管理自选组合列表、当前选中组合、组合内标的
- **数据**: portfolios, activePortfolioId, items

#### 4.4 useThemeStore（主题状态）
- **职责**: 管理主题偏好（深色/浅色）
- **数据**: theme, toggleTheme

### 5. API 服务层

#### 5.1 apiClient（HTTP 客户端）
- **职责**: Axios 实例封装，统一处理请求/响应拦截、Token 注入、错误处理

#### 5.2 authApi（认证 API）
- **职责**: 封装认证相关的 API 调用

#### 5.3 marketApi（行情 API）
- **职责**: 封装行情相关的 API 调用

#### 5.4 portfolioApi（自选组合 API）
- **职责**: 封装自选组合和标的相关的 API 调用
