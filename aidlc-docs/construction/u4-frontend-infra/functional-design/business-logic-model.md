# U4 业务逻辑模型 - 前端基础架构

## 1. HTTP 客户端逻辑

```
[请求拦截器]
  发起请求
    |
    v
  从 useAuthStore 获取 access_token
    |
    v
  token 存在 -> 注入 Authorization: Bearer {token}
  token 不存在 -> 不注入
    |
    v
  发送请求

[响应拦截器]
  收到响应
    |
    v
  状态码 2xx -> 返回 response.data
    |
  状态码 401 -> 检查是否为 Token 过期
    |
    v
  是 Token 过期:
    - 使用 refresh_token 调用 /api/auth/refresh
    - 刷新成功 -> 更新 token -> 重试原请求
    - 刷新失败 -> 清除认证状态 -> 跳转登录页
    |
  其他错误:
    - 提取错误信息 (response.data.detail)
    - 显示错误提示 (Ant Design message)
    - 返回 Promise.reject
```

## 2. 认证状态管理 (useAuthStore)

```
[初始化]
  - 从 localStorage 读取 refresh_token
  - access_token 仅存内存（Zustand store）
  - 如果有 refresh_token，尝试刷新获取 access_token

[登录]
  调用 authApi.login(data)
    |
    v
  响应 requires_2fa == true:
    - 保存 temp_token
    - 设置 is2FARequired = true
    - 等待用户输入 2FA 验证码
    |
  响应 requires_2fa == false:
    - 保存 access_token 到 store
    - 保存 refresh_token 到 localStorage
    - 调用 fetchUser() 获取用户信息
    - 跳转到首页

[登出]
  - 调用 authApi.logout()
  - 清除 access_token
  - 清除 localStorage 中的 refresh_token
  - 重置 user 为 null
  - 跳转到登录页

[Token 刷新]
  - 使用 refresh_token 调用 /api/auth/refresh
  - 更新 access_token
  - 如果返回新的 refresh_token，同时更新
```

## 3. 主题管理 (useThemeStore)

```
[初始化]
  - 从 localStorage 读取 theme 偏好
  - 如果没有偏好，检查系统主题 (prefers-color-scheme)
  - 默认 light

[切换主题]
  - 切换 light <-> dark
  - 保存到 localStorage
  - 更新 Ant Design ConfigProvider 的 theme
  - 更新 document.documentElement 的 data-theme 属性

[Ant Design 主题配置]
  - light: Ant Design 默认主题
  - dark: Ant Design darkAlgorithm
  - 自定义主色调: #1677ff（默认蓝色）
```

## 4. 路由配置

```
路由结构:
  /login          -> LoginPage（未登录可访问）
  /register       -> RegisterPage（未登录可访问）
  /               -> MarketPage（需要登录）
  /watchlist      -> WatchlistPage（需要登录）
  /profile        -> ProfilePage（需要登录）
  /2fa/setup      -> TwoFactorSetupPage（需要登录）

路由守卫:
  - 已登录用户访问 /login 或 /register -> 重定向到 /
  - 未登录用户访问受保护页面 -> 重定向到 /login
  - 路由切换时检查 Token 有效性
```

## 5. 全局布局

```
[桌面端布局] (宽度 >= 768px)
  +------------------------------------------+
  |  Navbar (顶部导航栏)                       |
  |  Logo | 行情 | 自选 | 个人中心 | 主题切换   |
  +------------------------------------------+
  |                                          |
  |  页面内容区域                              |
  |                                          |
  +------------------------------------------+

[移动端布局] (宽度 < 768px)
  +------------------------------------------+
  |                                          |
  |  页面内容区域                              |
  |                                          |
  +------------------------------------------+
  |  BottomTabBar (底部标签栏)                 |
  |  行情 | 自选 | 我的                        |
  +------------------------------------------+

[导航项]
  - 行情 (/) -> 行情榜单和搜索
  - 自选 (/watchlist) -> 自选组合管理
  - 个人中心 (/profile) -> 用户设置
```
