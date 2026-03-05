# U2 业务逻辑模型 - 后端行情模块

## 1. 获取行情榜单流程

```
输入: ranking_type (涨幅榜/跌幅榜/成交量榜等), market?, limit?
  |
  v
[构建缓存键]
  - cache_key = f"ranking:{ranking_type}:{market}:{limit}"
  |
  v
[检查缓存]
  - 缓存命中且未过期 -> 直接返回缓存数据
  - 缓存未命中或已过期 -> 继续
  |
  v
[调用 Tushare API]
  - 获取当日行情数据 (daily 接口)
  - 获取股票基础信息 (stock_basic 接口)
  |
  v
[数据转换]
  - 将 Tushare DataFrame 转换为 StockQuote 列表
  - 合并基础信息和行情数据
  |
  v
[排序]
  - 涨幅榜: 按 change_percent 降序
  - 跌幅榜: 按 change_percent 升序
  - 成交量榜: 按 volume 降序
  - 成交额榜: 按 amount 降序
  - 换手率榜: 按 turnover_rate 降序
  |
  v
[截取 limit 条]
  - 默认 limit = 20
  |
  v
[更新缓存]
  - 缓存有效期 30 秒
  |
  v
输出: list[StockQuote]
```

## 2. 搜索标的流程

```
输入: keyword, market?
  |
  v
[判断搜索类型]
  - 纯数字 -> 按标的代码搜索
  - 纯英文大写 -> 按拼音首字母搜索
  - 其他 -> 按名称模糊搜索
  |
  v
[构建缓存键]
  - 搜索结果缓存 5 分钟（搜索变化不频繁）
  |
  v
[检查缓存]
  - 命中 -> 返回
  - 未命中 -> 继续
  |
  v
[调用 Tushare API]
  - 获取股票基础信息列表
  - 在本地进行过滤匹配
  |
  v
[过滤和排序]
  - 按匹配度排序（精确匹配 > 前缀匹配 > 模糊匹配）
  - 如果指定 market，过滤对应市场
  - 最多返回 20 条结果
  |
  v
[更新缓存]
  |
  v
输出: list[SymbolInfo]
```

## 3. 获取单个标的行情流程

```
输入: symbol
  |
  v
[构建缓存键]
  - cache_key = f"quote:{symbol}"
  |
  v
[检查缓存]
  - 命中且未过期 -> 返回
  - 未命中 -> 继续
  |
  v
[调用 Tushare API]
  - 获取该标的当日行情
  - 获取基础信息
  |
  v
[数据转换]
  - 合并为 StockQuote
  |
  v
[更新缓存]
  - 缓存有效期 15 秒（单个标的更新更频繁）
  |
  v
输出: StockQuote
```

## 4. 批量获取标的行情流程

```
输入: symbols (list[str])
  |
  v
[分离缓存命中和未命中]
  - 遍历 symbols，检查缓存
  - cached: 已缓存的标的
  - uncached: 未缓存的标的
  |
  v
[批量查询未缓存标的]
  - 调用 Tushare API 获取行情
  - 数据转换为 StockQuote
  - 更新缓存
  |
  v
[合并结果]
  - 合并缓存命中和新查询的数据
  - 按输入 symbols 顺序排列
  |
  v
输出: list[StockQuote]
```

## 5. Tushare 客户端封装

```
[初始化]
  - 使用 tushare.pro_api(token) 创建客户端
  - token 从环境变量读取
  |
  v
[API 调用封装]
  - 统一异常处理（网络错误、API 限流、数据为空）
  - 自动重试（最多 3 次，间隔 1 秒）
  - 日志记录（调用接口、参数、耗时）
  |
  v
[数据转换]
  - Tushare 返回 DataFrame -> Python dict/list
  - 字段名映射（Tushare 字段名 -> 应用字段名）
```

## 6. 缓存策略

```
缓存类型: 内存字典（适合单实例部署）

缓存配置:
  - 榜单数据: 30 秒过期
  - 搜索结果: 5 分钟过期
  - 单个标的行情: 15 秒过期
  - 股票基础信息: 24 小时过期（每日更新一次）

缓存清理:
  - 惰性清理（访问时检查过期）
  - 定期清理（每 10 分钟清理过期条目）
```
