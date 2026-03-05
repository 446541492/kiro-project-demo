# U3 领域实体 - 后端自选管理模块

## 1. Portfolio（自选组合）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | 主键, 自增 | 组合 ID |
| user_id | Integer | 外键(users.id), 非空, 索引 | 所属用户 |
| name | String(50) | 非空 | 组合名称 |
| sort_order | Integer | 非空, 默认 0 | 排序顺序 |
| is_default | Boolean | 非空, 默认 False | 是否为默认组合 |
| created_at | DateTime | 非空, 默认当前时间 | 创建时间 |
| updated_at | DateTime | 非空, 自动更新 | 更新时间 |

### 约束
- 联合唯一: (user_id, name) — 同一用户下组合名不可重复
- 每个用户有且仅有一个 is_default=True 的组合

### 关联
- Portfolio.user → User (多对一)
- Portfolio.items → WatchlistItem[] (一对多, 级联删除)

---

## 2. WatchlistItem（自选标的）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | 主键, 自增 | 标的记录 ID |
| portfolio_id | Integer | 外键(portfolios.id), 非空, 索引 | 所属组合 |
| symbol | String(20) | 非空 | 标的代码（如 000001.SZ） |
| name | String(50) | 非空 | 标的名称 |
| market | String(20) | 非空 | 市场（沪市/深市/港股） |
| sort_order | Integer | 非空, 默认 0 | 排序顺序 |
| created_at | DateTime | 非空, 默认当前时间 | 创建时间 |

### 约束
- 联合唯一: (portfolio_id, symbol) — 同一组合内标的不可重复

### 关联
- WatchlistItem.portfolio → Portfolio (多对一)
