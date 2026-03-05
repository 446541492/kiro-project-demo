# U3 后端自选管理模块 - 代码总结

## 生成概览
- **单元**: U3 - 后端自选管理模块
- **代码位置**: `backend/`
- **完成时间**: 2026-03-05

## 生成文件清单

| 文件 | 说明 |
|------|------|
| `backend/app/models/portfolio.py` | 自选组合模型（联合唯一约束、级联删除） |
| `backend/app/models/watchlist_item.py` | 自选标的模型（联合唯一约束） |
| `backend/app/models/__init__.py`（更新） | 注册新模型 |
| `backend/app/schemas/portfolio.py` | 组合请求/响应 Schema |
| `backend/app/schemas/watchlist.py` | 标的请求/响应 Schema |
| `backend/app/services/portfolio_service.py` | 组合服务（CRUD、排序、默认组合） |
| `backend/app/services/watchlist_service.py` | 标的服务（CRUD、排序、行情合并） |
| `backend/app/routers/portfolio.py` | 组合 API 路由（5 个端点） |
| `backend/app/routers/watchlist.py` | 标的 API 路由（5 个端点） |
| `backend/app/main.py`（更新） | 注册新路由 |
| `backend/migrations/init_db.py`（更新） | 添加测试组合和标的数据 |
| `backend/tests/test_portfolio.py` | 组合接口测试（8 个用例） |
| `backend/tests/test_watchlist.py` | 标的接口测试（8 个用例） |

## API 端点

### 组合管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/portfolios | 获取用户所有组合 |
| POST | /api/portfolios | 创建新组合 |
| PUT | /api/portfolios/reorder | 调整组合排序 |
| PUT | /api/portfolios/{id} | 更新组合（重命名） |
| DELETE | /api/portfolios/{id} | 删除组合 |

### 标的管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/portfolios/{id}/items | 获取组合内标的（含行情） |
| POST | /api/portfolios/{id}/items | 添加标的 |
| POST | /api/portfolios/{id}/items/batch | 批量添加标的 |
| PUT | /api/portfolios/{id}/items/reorder | 调整标的排序 |
| DELETE | /api/portfolios/{id}/items/{item_id} | 移除标的 |

## 文件总数
- 新建文件：10 个
- 更新文件：3 个
