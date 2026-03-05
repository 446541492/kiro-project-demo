# U6 业务逻辑模型 - 前端行情与自选

## 1. 行情页面

```
[MarketPage]
  初始化:
    -> 调用 marketStore.fetchRankings('rise')
    -> 启动自动刷新 (30 秒间隔)
    |
  标签页切换:
    -> 切换 rankingType (rise/fall/volume/amount/turnover)
    -> 调用 marketStore.fetchRankings(type)
    |
  搜索:
    -> 用户输入关键词
    -> 防抖 300ms
    -> 调用 marketStore.searchSymbols(keyword)
    -> 显示搜索结果下拉列表
    -> 点击结果: 添加到自选（弹出组合选择）
    |
  榜单操作:
    -> 点击标的行: 添加到自选（弹出组合选择）
    |
  离开页面:
    -> 停止自动刷新
```

## 2. 自选页面

```
[WatchlistPage]
  初始化:
    -> 调用 portfolioStore.fetchPortfolios()
    -> 自动选中第一个组合
    -> 加载组合内标的
    |
  组合切换:
    -> 点击组合 -> portfolioStore.setActivePortfolio(id)
    -> 自动加载该组合的标的列表
    |
  组合管理:
    -> 创建: 弹出输入框 -> portfolioStore.createPortfolio(name)
    -> 重命名: 弹出输入框 -> portfolioStore.updatePortfolio(id, name)
    -> 删除: 确认弹窗 -> portfolioStore.deletePortfolio(id)
    |
  标的管理:
    -> 移除: 滑动/点击删除 -> portfolioStore.removeItem(portfolioId, itemId)
    |
  添加标的（从搜索/榜单跳转）:
    -> 弹出组合选择器
    -> 选择目标组合
    -> portfolioStore.addItem(portfolioId, symbol)
```

## 3. 添加到自选弹窗

```
[AddToWatchlistModal]
  打开时:
    -> 加载用户组合列表
    -> 显示组合选择列表
    |
  选择组合:
    -> 调用 portfolioStore.addItem(portfolioId, symbol)
    -> 成功: 提示"已添加到 {组合名}"
    -> 失败（已存在）: 提示"该标的已在组合中"
    -> 关闭弹窗
```
