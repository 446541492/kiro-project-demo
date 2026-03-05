# U4 业务规则 - 前端基础架构

## 1. 路由守卫规则

| 规则编号 | 规则名称 | 规则描述 |
|---------|---------|---------|
| RT-001 | 公开路由 | /login 和 /register 无需登录即可访问 |
| RT-002 | 受保护路由 | /、/watchlist、/profile、/2fa/setup 需要登录 |
| RT-003 | 已登录重定向 | 已登录用户访问 /login 或 /register 自动重定向到 / |
| RT-004 | 未登录重定向 | 未登录用户访问受保护路由自动重定向到 /login |
| RT-005 | 默认路由 | 未匹配路由重定向到 / |

## 2. Token 管理规则

| 规则编号 | 规则名称 | 规则描述 |
|---------|---------|---------|
| TK-001 | Access Token 存储 | 仅存储在内存（Zustand store），不持久化 |
| TK-002 | Refresh Token 存储 | 存储在 localStorage |
| TK-003 | Token 注入 | 每个请求自动注入 Authorization: Bearer {token} |
| TK-004 | 自动刷新 | 收到 401 响应时自动使用 refresh_token 刷新 |
| TK-005 | 刷新失败 | refresh_token 也失效时清除状态并跳转登录页 |
| TK-006 | 并发刷新 | 多个请求同时 401 时，只发起一次刷新，其他请求排队等待 |

## 3. 主题规则

| 规则编号 | 规则名称 | 规则描述 |
|---------|---------|---------|
| TH-001 | 默认主题 | 浅色主题 (light) |
| TH-002 | 主题持久化 | 主题偏好保存到 localStorage |
| TH-003 | 系统跟随 | 首次访问时检测系统主题偏好 |
| TH-004 | 切换方式 | 点击切换按钮在 light/dark 之间切换 |
| TH-005 | Ant Design 集成 | 使用 ConfigProvider 的 algorithm 属性切换主题 |

## 4. 响应式布局规则

| 规则编号 | 规则名称 | 规则描述 |
|---------|---------|---------|
| RES-001 | 断点定义 | 移动端 < 768px，桌面端 >= 768px |
| RES-002 | 桌面端导航 | 顶部导航栏（Navbar） |
| RES-003 | 移动端导航 | 底部标签栏（BottomTabBar） |
| RES-004 | 内容区域 | 自适应宽度，最大宽度 1200px，居中显示 |

## 5. 错误处理规则

| 规则编号 | 规则名称 | 规则描述 |
|---------|---------|---------|
| ERR-001 | 网络错误 | 显示"网络连接失败，请检查网络" |
| ERR-002 | 服务器错误 (5xx) | 显示"服务器繁忙，请稍后重试" |
| ERR-003 | 业务错误 (4xx) | 显示后端返回的 detail 信息 |
| ERR-004 | 错误提示方式 | 使用 Ant Design message 组件全局提示 |
| ERR-005 | 加载状态 | 所有异步操作显示 loading 状态 |

## 6. 状态管理规则

| 规则编号 | 规则名称 | 规则描述 |
|---------|---------|---------|
| ST-001 | Store 划分 | authStore、marketStore、portfolioStore、themeStore |
| ST-002 | 持久化 | 仅 themeStore 和 refresh_token 持久化到 localStorage |
| ST-003 | 初始化 | 应用启动时从 localStorage 恢复持久化状态 |
| ST-004 | 清理 | 登出时清除所有 store 状态和 localStorage |
