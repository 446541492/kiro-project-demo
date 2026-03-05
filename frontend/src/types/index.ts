/**
 * 全局 TypeScript 类型定义
 * 前后端数据交互的类型契约
 */

// ==================== 用户相关 ====================

/** 用户信息 */
export interface User {
  id: number;
  username: string;
  email: string | null;
  phone: string | null;
  is_2fa_enabled: boolean;
  created_at: string;
}

/** 登录请求 */
export interface LoginRequest {
  username: string;
  password: string;
  device_id?: string;
  captcha_token?: string;
}

/** 注册请求 */
export interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
  phone?: string;
}

/** Token 响应 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

/** 登录响应（可能需要 2FA） */
export interface LoginResponse {
  requires_2fa: boolean;
  temp_token?: string;
  access_token?: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
}

// ==================== 行情相关 ====================

/** 股票行情 */
export interface StockQuote {
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

/** 标的基础信息 */
export interface SymbolInfo {
  symbol: string;
  name: string;
  market: string;
  industry: string;
  list_date: string;
}

// ==================== 自选组合相关 ====================

/** 自选组合 */
export interface Portfolio {
  id: number;
  name: string;
  sort_order: number;
  is_default: boolean;
  item_count: number;
  created_at: string;
}

/** 自选标的 */
export interface WatchlistItem {
  id: number;
  portfolio_id: number;
  symbol: string;
  name: string;
  market: string;
  sort_order: number;
  quote?: StockQuote;
  created_at: string;
}

// ==================== 通用类型 ====================

/** API 错误响应 */
export interface ApiError {
  detail: string;
  code: string;
}

/** 消息响应 */
export interface MessageResponse {
  message: string;
}

/** 设备信息 */
export interface DeviceInfo {
  id: number;
  device_id: string;
  device_name: string;
  ip_address: string | null;
  last_login_at: string;
  created_at: string;
}

/** 主题类型 */
export type ThemeMode = 'light' | 'dark';

/** 榜单类型 */
export type RankingType = 'rise' | 'fall' | 'volume' | 'amount' | 'turnover';

/** K线数据 */
export interface KlineData {
  day: string;
  open: string;
  high: string;
  low: string;
  close: string;
  volume: string;
}

/** K线周期类型 */
export type KlinePeriod = 'daily' | 'weekly' | 'monthly';
