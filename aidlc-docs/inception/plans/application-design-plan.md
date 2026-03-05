# 应用设计计划 - Stocks Assist（股票助手）

## 设计范围

基于需求文档，本阶段将设计以下内容：
- 前后端组件结构和职责
- 组件方法签名
- 服务层设计
- 组件依赖关系

---

## 设计计划

### 第一部分：后端组件设计

- [ ] 1.1 API 路由层组件设计
  - [ ] 认证路由 (auth_router)
  - [ ] 用户路由 (user_router)
  - [ ] 行情路由 (market_router)
  - [ ] 自选组合路由 (portfolio_router)
  - [ ] 自选标的路由 (watchlist_router)

- [ ] 1.2 服务层组件设计
  - [ ] 认证服务 (AuthService)
  - [ ] 用户服务 (UserService)
  - [ ] 行情服务 (MarketService)
  - [ ] 自选组合服务 (PortfolioService)
  - [ ] 自选标的服务 (WatchlistService)
  - [ ] 2FA 服务 (TwoFactorService)

- [ ] 1.3 数据模型层设计
  - [ ] 用户模型 (User)
  - [ ] 设备模型 (Device)
  - [ ] 自选组合模型 (Portfolio)
  - [ ] 自选标的模型 (WatchlistItem)

- [ ] 1.4 中间件和工具层设计
  - [ ] JWT 认证中间件
  - [ ] 请求验证中间件
  - [ ] Tushare API 客户端
  - [ ] 密码加密工具
  - [ ] 数据库连接管理

### 第二部分：前端组件设计

- [ ] 2.1 页面组件设计
  - [ ] 登录页 (LoginPage)
  - [ ] 注册页 (RegisterPage)
  - [ ] 首页/行情页 (MarketPage)
  - [ ] 自选页 (WatchlistPage)
  - [ ] 个人中心页 (ProfilePage)
  - [ ] 2FA 设置页 (TwoFactorSetupPage)

- [ ] 2.2 业务组件设计
  - [ ] 滑块验证码组件 (SliderCaptcha)
  - [ ] 行情榜单组件 (MarketRanking)
  - [ ] 标的搜索组件 (SymbolSearch)
  - [ ] 自选组合列表组件 (PortfolioList)
  - [ ] 标的列表组件 (SymbolList)
  - [ ] 组合管理弹窗组件 (PortfolioModal)
  - [ ] 标的行情卡片组件 (SymbolCard)
  - [ ] 主题切换组件 (ThemeSwitch)

- [ ] 2.3 布局组件设计
  - [ ] 应用布局 (AppLayout)
  - [ ] 导航栏 (Navbar)
  - [ ] 侧边栏 (Sidebar)
  - [ ] 底部导航 (BottomNav - 移动端)

- [ ] 2.4 状态管理设计
  - [ ] 用户状态 (useAuthStore)
  - [ ] 行情状态 (useMarketStore)
  - [ ] 自选组合状态 (usePortfolioStore)
  - [ ] 主题状态 (useThemeStore)

- [ ] 2.5 API 服务层设计
  - [ ] HTTP 客户端封装 (apiClient)
  - [ ] 认证 API (authApi)
  - [ ] 行情 API (marketApi)
  - [ ] 自选组合 API (portfolioApi)
  - [ ] 自选标的 API (watchlistApi)

### 第三部分：服务层和依赖关系

- [x] 3.1 生成组件定义文档 (components.md)
- [x] 3.2 生成组件方法文档 (component-methods.md)
- [x] 3.3 生成服务定义文档 (services.md)
- [x] 3.4 生成组件依赖关系文档 (component-dependency.md)
- [x] 3.5 验证设计完整性和一致性

---

## 设计问题

在开始设计之前，我需要确认几个关键的设计决策：

### Q1: 前端页面导航结构

对于桌面端和移动端的导航，您倾向于哪种方式？

**选项**:
- A) 桌面端顶部导航栏 + 移动端底部标签栏
- B) 桌面端侧边栏导航 + 移动端底部标签栏
- C) 统一使用顶部导航栏（移动端折叠为汉堡菜单）
- D) 由您决定最佳方案
- X) 其他（请说明）

[Answer]: D

### Q2: 自选组合与标的列表的布局

自选页面中，组合列表和标的列表如何布局？

**选项**:
- A) 左侧组合列表 + 右侧标的列表（桌面端），上下布局（移动端）
- B) 顶部标签页切换组合 + 下方标的列表
- C) 侧边抽屉组合列表 + 主区域标的列表
- D) 由您决定最佳方案
- X) 其他（请说明）

[Answer]: D

### Q3: 行情榜单展示方式

行情榜单页面如何组织多种榜单？

**选项**:
- A) 标签页切换不同榜单（涨幅榜、跌幅榜等）
- B) 卡片式布局，同时展示多个榜单
- C) 下拉选择切换榜单类型
- D) 由您决定最佳方案
- X) 其他（请说明）

[Answer]: D

### Q4: 后端项目结构

后端代码的组织方式？

**选项**:
- A) 按功能分层（routers/、services/、models/、schemas/）
- B) 按业务模块分包（auth/、market/、portfolio/）
- C) 混合方式（按模块分包，每个模块内按层分文件）
- D) 由您决定最佳方案
- X) 其他（请说明）

[Answer]: D

---

**请在每个 [Answer]: 后填写您的选择，完成后告知我。**
