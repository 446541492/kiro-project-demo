# U6 前端行情与自选 - 代码生成计划

## 单元上下文
- **单元名称**: U6 - 前端行情与自选
- **代码位置**: `frontend/`
- **前置依赖**: U2（后端行情 API）、U3（后端自选管理 API）、U4（前端基础架构）

## 代码生成步骤

### 步骤 1：API 服务层
- [x] 创建 `frontend/src/api/market.ts` — 行情 API 封装
- [x] 创建 `frontend/src/api/portfolio.ts` — 自选组合 API 封装

### 步骤 2：工具函数
- [x] 创建 `frontend/src/utils/format.ts` — 数据格式化工具

### 步骤 3：业务组件
- [x] 创建 `frontend/src/components/SymbolSearch/index.tsx` — 标的搜索
- [x] 创建 `frontend/src/components/AddToWatchlistModal/index.tsx` — 添加到自选弹窗

### 步骤 4：行情页面
- [x] 替换 `frontend/src/pages/MarketPage.tsx` — 完整行情页面

### 步骤 5：自选页面
- [x] 替换 `frontend/src/pages/WatchlistPage.tsx` — 完整自选页面

### 步骤 6：总结
- [x] 创建 `aidlc-docs/construction/u6-frontend-market-watchlist/code/code-summary.md`
