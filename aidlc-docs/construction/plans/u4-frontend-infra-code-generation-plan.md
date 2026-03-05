# U4 前端基础架构 - 代码生成计划

## 单元上下文
- **单元名称**: U4 - 前端基础架构
- **代码位置**: `frontend/`
- **前置依赖**: U1（后端 API 地址）

## 代码生成步骤

### 步骤 1：项目初始化
- [x] 创建 `frontend/package.json` — 依赖清单
- [x] 创建 `frontend/tsconfig.json` — TypeScript 配置
- [x] 创建 `frontend/vite.config.ts` — Vite 配置
- [x] 创建 `frontend/index.html` — HTML 入口
- [x] 创建 `frontend/.eslintrc.cjs` — ESLint 配置

### 步骤 2：类型定义和 API 客户端
- [x] 创建 `frontend/src/types/index.ts` — TypeScript 类型定义
- [x] 创建 `frontend/src/api/client.ts` — Axios 客户端封装

### 步骤 3：状态管理
- [x] 创建 `frontend/src/stores/authStore.ts` — 认证状态
- [x] 创建 `frontend/src/stores/themeStore.ts` — 主题状态
- [x] 创建 `frontend/src/stores/marketStore.ts` — 行情状态（骨架）
- [x] 创建 `frontend/src/stores/portfolioStore.ts` — 自选状态（骨架）

### 步骤 4：布局组件
- [x] 创建 `frontend/src/layouts/AppLayout.tsx` — 全局布局
- [x] 创建 `frontend/src/layouts/Navbar.tsx` — 顶部导航栏
- [x] 创建 `frontend/src/layouts/BottomTabBar.tsx` — 底部标签栏
- [x] 创建 `frontend/src/components/ThemeSwitch/index.tsx` — 主题切换

### 步骤 5：路由和入口
- [x] 创建 `frontend/src/App.tsx` — 路由配置和主题 Provider
- [x] 创建 `frontend/src/main.tsx` — 应用入口
- [x] 创建 `frontend/src/App.css` — 全局样式

### 步骤 6：页面占位
- [x] 创建页面占位组件（LoginPage、RegisterPage、MarketPage、WatchlistPage、ProfilePage、TwoFactorSetupPage）

### 步骤 7：更新根目录配置
- [x] 更新 `package.json` — 添加前端启动脚本

### 步骤 8：总结
- [x] 创建 `aidlc-docs/construction/u4-frontend-infra/code/code-summary.md`
