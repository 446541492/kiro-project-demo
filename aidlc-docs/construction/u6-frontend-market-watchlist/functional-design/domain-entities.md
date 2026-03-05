# U6 领域实体 - 前端行情与自选

## 1. 行情页面组件 Props

### MarketRankingProps
| 属性 | 类型 | 说明 |
|------|------|------|
| rankingType | RankingType | 当前榜单类型 |
| data | StockQuote[] | 榜单数据 |
| loading | boolean | 加载状态 |
| onAddToWatchlist | (symbol: SymbolInfo) => void | 添加到自选回调 |

### SymbolSearchProps
| 属性 | 类型 | 说明 |
|------|------|------|
| onSelect | (symbol: SymbolInfo) => void | 选中标的回调 |

## 2. 自选页面组件 Props

### PortfolioListProps
| 属性 | 类型 | 说明 |
|------|------|------|
| portfolios | Portfolio[] | 组合列表 |
| activeId | number | null | 当前选中组合 ID |
| onSelect | (id: number) => void | 切换组合回调 |
| onCreate | () => void | 创建组合回调 |
| onRename | (id: number) => void | 重命名回调 |
| onDelete | (id: number) => void | 删除回调 |

### SymbolListProps
| 属性 | 类型 | 说明 |
|------|------|------|
| items | WatchlistItem[] | 标的列表 |
| loading | boolean | 加载状态 |
| onRemove | (itemId: number) => void | 移除标的回调 |
