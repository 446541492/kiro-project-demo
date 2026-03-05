# U2 领域实体设计 - 后端行情模块

## 说明

U2 行情模块不涉及持久化数据模型（无数据库表）。行情数据来自 Tushare API，通过内存缓存临时存储。

## 数据传输对象

### 1. StockQuote（股票行情）

| 字段 | 类型 | 说明 |
|------|------|------|
| symbol | str | 标的代码（如 600519.SH） |
| name | str | 标的名称（如 贵州茅台） |
| current_price | float | 当前价格 |
| change_percent | float | 涨跌幅（%） |
| change_amount | float | 涨跌额 |
| open_price | float | 开盘价 |
| high_price | float | 最高价 |
| low_price | float | 最低价 |
| pre_close | float | 昨收价 |
| volume | float | 成交量（手） |
| amount | float | 成交额（元） |
| turnover_rate | float | 换手率（%） |
| pe_ratio | float | 市盈率 |
| pb_ratio | float | 市净率 |
| market | str | 市场类型（A股/港股/美股） |

### 2. SymbolInfo（标的基础信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| symbol | str | 标的代码 |
| name | str | 标的名称 |
| market | str | 市场类型 |
| industry | str | 所属行业 |
| list_date | str | 上市日期 |

### 3. CacheEntry（缓存条目）

| 字段 | 类型 | 说明 |
|------|------|------|
| data | Any | 缓存数据 |
| expire_at | float | 过期时间戳 |
