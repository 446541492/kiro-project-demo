# U3 后端自选管理模块 - 代码生成计划

## 单元上下文
- **单元名称**: U3 - 后端自选管理模块
- **代码位置**: `backend/`
- **前置依赖**: U1（数据库基础、JWT 中间件）、U2（MarketService 获取实时行情）

## 代码生成步骤

### 步骤 1：数据模型
- [x] 创建 `backend/app/models/portfolio.py` — 自选组合模型
- [x] 创建 `backend/app/models/watchlist_item.py` — 自选标的模型
- [x] 更新 `backend/app/models/__init__.py` — 注册新模型

### 步骤 2：Schema 定义
- [x] 创建 `backend/app/schemas/portfolio.py` — 组合请求/响应模型
- [x] 创建 `backend/app/schemas/watchlist.py` — 标的请求/响应模型

### 步骤 3：服务层
- [x] 创建 `backend/app/services/portfolio_service.py` — 组合服务
- [x] 创建 `backend/app/services/watchlist_service.py` — 标的服务

### 步骤 4：路由层
- [x] 创建 `backend/app/routers/portfolio.py` — 组合 API 路由
- [x] 创建 `backend/app/routers/watchlist.py` — 标的 API 路由

### 步骤 5：注册路由和更新初始化
- [x] 更新 `backend/app/main.py` — 注册组合和标的路由
- [x] 更新 `backend/migrations/init_db.py` — 添加测试组合和标的数据

### 步骤 6：测试
- [x] 创建 `backend/tests/test_portfolio.py` — 组合接口测试
- [x] 创建 `backend/tests/test_watchlist.py` — 标的接口测试

### 步骤 7：总结
- [x] 创建 `aidlc-docs/construction/u3-backend-watchlist/code/code-summary.md`
