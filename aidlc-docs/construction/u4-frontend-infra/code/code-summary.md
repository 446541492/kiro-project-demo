# U4 前端基础架构 - 代码总结

## 生成概览

- **单元**: U4 - 前端基础架构
- **代码位置**: `frontend/`
- **完成时间**: 2026-03-05

## 生成文件清单

### 步骤 1：项目初始化（已完成）
| 文件 | 说明 |
|------|------|
| `frontend/package.json` | 依赖清单（React 18 + Ant Design 5 + Zustand + Vite） |
| `frontend/tsconfig.json` | TypeScript 配置 |
| `frontend/tsconfig.node.json` | Node 环境 TypeScript 配置 |
| `frontend/vite.config.ts` | Vite 构建配置（含路径别名 @） |
| `frontend/index.html` | HTML 入口 |
| `frontend/.eslintrc.cjs` | ESLint 配置 |

### 步骤 2：类型定义和 API 客户端
| 文件 | 说明 |
|------|------|
| `frontend/src/types/index.ts` | 全局 TypeScript 类型定义（用户、行情、自选、通用） |
| `frontend/src/api/client.ts` | Axios 客户端封装（Token 注入、401 自动刷新、错误处理） |

### 步骤 3：状态管理
| 文件 | 说明 |
|------|------|
| `frontend/src/stores/authStore.ts` | 认证状态（登录/注册/登出/2FA/Token 刷新） |
| `frontend/src/stores/themeStore.ts` | 主题状态（明暗切换、localStorage 持久化、系统偏好检测） |
| `frontend/src/stores/marketStore.ts` | 行情状态骨架（榜单/搜索/自动刷新） |
| `frontend/src/stores/portfolioStore.ts` | 自选状态骨架（组合 CRUD/标的管理） |

### 步骤 4：布局组件
| 文件 | 说明 |
|------|------|
| `frontend/src/layouts/AppLayout.tsx` | 全局布局（响应式：桌面顶部导航 + 移动底部标签栏） |
| `frontend/src/layouts/Navbar.tsx` | 顶部导航栏（Logo + 菜单 + 主题切换） |
| `frontend/src/layouts/BottomTabBar.tsx` | 底部标签栏（行情/自选/我的） |
| `frontend/src/components/ThemeSwitch/index.tsx` | 主题切换开关组件 |

### 步骤 5：路由和入口
| 文件 | 说明 |
|------|------|
| `frontend/src/App.tsx` | 路由配置 + Ant Design 主题 Provider + 路由守卫 |
| `frontend/src/main.tsx` | 应用入口 |
| `frontend/src/App.css` | 全局样式（CSS 变量、涨跌颜色、滚动条） |

### 步骤 6：页面占位
| 文件 | 说明 |
|------|------|
| `frontend/src/pages/LoginPage.tsx` | 登录页占位 |
| `frontend/src/pages/RegisterPage.tsx` | 注册页占位 |
| `frontend/src/pages/MarketPage.tsx` | 行情页占位 |
| `frontend/src/pages/WatchlistPage.tsx` | 自选页占位 |
| `frontend/src/pages/ProfilePage.tsx` | 个人中心页占位 |
| `frontend/src/pages/TwoFactorSetupPage.tsx` | 两步验证设置页占位 |

### 步骤 7：根目录配置
| 文件 | 说明 |
|------|------|
| `package.json`（更新） | 添加前端构建/安装脚本，更新 dev:all 并行启动 |

## 技术要点

### 架构特性
- 响应式布局：768px 断点，桌面端顶部导航 + 移动端底部标签栏
- 主题系统：Ant Design ConfigProvider + CSS 变量双轨驱动
- Token 管理：access_token 仅存内存，refresh_token 存 localStorage
- 并发刷新控制：多个 401 请求只触发一次 Token 刷新，其余排队等待

### 路由守卫
- 公开路由：/login、/register（已登录自动重定向到首页）
- 受保护路由：/、/watchlist、/profile、/2fa/setup（未登录重定向到登录页）
- 应用初始化时自动尝试恢复登录状态

### 文件总数
- 新建文件：22 个
- 更新文件：1 个（根 package.json）
