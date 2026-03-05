# U4 领域实体设计 - 前端基础架构

## 说明

U4 前端基础架构定义 TypeScript 类型接口，作为前后端数据交互的契约。

## TypeScript 类型定义

### 1. 用户相关

```typescript
// 用户信息
interface User {
  id: number;
  username: string;
  email: string | null;
  phone: string | null;
  is_2fa_enabled: boolean;
  created_at: string;
}

// 登录请求
interface LoginRequest {
  username: string;
  password: string;
  device_id?: string;
  captcha_token?: string;
}

// 注册请求
interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
  phone?: string;
}

// Token 响应
interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// 登录响应（可能需要 2FA）
interface LoginResponse {
  requires_2fa: boolean;
  temp_token?: string;
  access_token?: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
}
```

### 2. 行情相关

```typescript
// 股票行情
interface StockQuote {
  symbol: string;
  name: string;
  current_price: number;
  change_percent: number;
  change_amount: number;
  open_price: number;
  high_price: number;
  low_price: number;
  pre_close: number;
  volume: number;
  amount: number;
  turnover_rate: number;
  pe_ratio: number;
  pb_ratio: number;
  market: string;
}

// 标的基础信息
interface SymbolInfo {
  symbol: string;
  name: string;
  market: string;
  industry: string;
  list_date: string;
}
```

### 3. 自选组合相关

```typescript
// 自选组合
interface Portfolio {
  id: number;
  name: string;
  sort_order: number;
  is_default: boolean;
  item_count: number;
  created_at: string;
}

// 自选标的
interface WatchlistItem {
  id: number;
  portfolio_id: number;
  symbol: string;
  name: string;
  market: string;
  sort_order: number;
  quote?: StockQuote;  // 实时行情（可选）
  created_at: string;
}
```

### 4. 通用类型

```typescript
// API 错误响应
interface ApiError {
  detail: string;
  code: string;
}

// 消息响应
interface MessageResponse {
  message: string;
}

// 设备信息
interface DeviceInfo {
  id: number;
  device_id: string;
  device_name: string;
  ip_address: string | null;
  last_login_at: string;
  created_at: string;
}

// 主题类型
type ThemeMode = 'light' | 'dark';

// 榜单类型
type RankingType = 'rise' | 'fall' | 'volume' | 'amount' | 'turnover';
```
