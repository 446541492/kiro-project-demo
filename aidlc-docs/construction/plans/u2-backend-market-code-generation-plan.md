# U2 后端行情模块 - 代码生成计划

## 单元上下文
- **单元名称**: U2 - 后端行情模块
- **代码位置**: `backend/`
- **前置依赖**: U1（FastAPI 基础架构和 JWT 中间件）

## 代码生成步骤

### 步骤 1：配置更新和依赖
- [ ] 更新 `backend/requirements.txt` — 添加 tushare、pandas 依赖
- [ ] 更新 `backend/.env.example` — 添加 TUSHARE_TOKEN
- [ ] 更新 `backend/app/core/config.py` — 添加 Tushare 配置项

### 步骤 2：Pydantic Schema
- [ ] 创建 `backend/app/schemas/market.py` — 行情相关请求/响应模型

### 步骤 3：Tushare 客户端
- [ ] 创建 `backend/app/clients/__init__.py`
- [ ] 创建 `backend/app/clients/tushare_client.py` — Tushare API 客户端封装

### 步骤 4：行情服务
- [ ] 创建 `backend/app/services/market_service.py` — MarketService（榜单、搜索、行情查询、缓存）

### 步骤 5：API 路由
- [ ] 创建 `backend/app/routers/market.py` — 行情 API 路由
- [ ] 更新 `backend/app/main.py` — 注册行情路由

### 步骤 6：单元测试
- [ ] 创建 `backend/tests/test_market.py` — 行情 API 测试

### 步骤 7：总结
- [ ] 创建 `aidlc-docs/construction/u2-backend-market/code/code-summary.md`
