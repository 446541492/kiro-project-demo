# U6 前端行情与自选 - 代码总结

## 生成概览
- **单元**: U6 - 前端行情与自选
- **代码位置**: `frontend/`
- **完成时间**: 2026-03-05

## 生成文件清单

| 文件 | 说明 |
|------|------|
| `frontend/src/api/market.ts` | 行情 API 封装（榜单/搜索/行情查询） |
| `frontend/src/api/portfolio.ts` | 自选组合 API 封装（组合 CRUD/标的管理） |
| `frontend/src/utils/format.ts` | 数据格式化工具（价格/涨跌幅/成交量/金额） |
| `frontend/src/components/SymbolSearch/index.tsx` | 标的搜索组件（防抖搜索/下拉选择） |
| `frontend/src/components/AddToWatchlistModal/index.tsx` | 添加到自选弹窗（组合选择） |
| `frontend/src/pages/MarketPage.tsx` | 行情页（榜单标签页/搜索/自动刷新/添加到自选） |
| `frontend/src/pages/WatchlistPage.tsx` | 自选页（组合管理/标的列表/移除标的） |

## 功能覆盖

- 行情榜单：5 种榜单标签页切换（涨幅/跌幅/成交量/成交额/换手率）
- 自动刷新：30 秒间隔自动刷新当前榜单
- 标的搜索：防抖 300ms、下拉结果列表
- 添加到自选：从搜索结果或榜单快速添加到指定组合
- 组合管理：创建/重命名/删除（右键菜单 + 管理按钮）
- 标的列表：实时行情展示、涨跌颜色、移除标的
- 数据格式化：价格 2 位小数、涨跌幅带符号、成交量万/亿单位

## 文件总数
- 新建文件：5 个
- 替换文件：2 个（MarketPage、WatchlistPage）
