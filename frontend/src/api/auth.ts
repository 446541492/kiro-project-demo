/**
 * 认证 API 服务
 * 封装所有认证相关的 HTTP 请求
 */

import apiClient from '@/api/client';
import type {
  User,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  TokenResponse,
  MessageResponse,
  DeviceInfo,
} from '@/types';

/** 两步验证设置响应 */
export interface TwoFactorSetupResponse {
  qr_code: string;       // Base64 二维码图片
  secret: string;        // TOTP 密钥
}

/** 恢复码响应 */
export interface RecoveryCodesResponse {
  recovery_codes: string[];
}

/** 修改密码请求 */
export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

const authApi = {
  /** 用户注册 */
  register: (data: RegisterRequest) =>
    apiClient.post<LoginResponse>('/api/auth/register', data),

  /** 用户登录 */
  login: (data: LoginRequest) =>
    apiClient.post<LoginResponse>('/api/auth/login', data),

  /** 用户登出 */
  logout: () =>
    apiClient.post('/api/auth/logout'),

  /** 刷新 Token */
  refreshToken: (refreshToken: string) =>
    apiClient.post<TokenResponse>('/api/auth/refresh', { refresh_token: refreshToken }),

  /** 获取当前用户信息 */
  getMe: () =>
    apiClient.get<User>('/api/auth/me'),

  /** 启用两步验证 */
  enable2FA: () =>
    apiClient.post<TwoFactorSetupResponse>('/api/auth/2fa/enable'),

  /** 验证两步验证码 */
  verify2FA: (code: string, tempToken?: string) =>
    apiClient.post<LoginResponse>('/api/auth/2fa/verify', { code, temp_token: tempToken }),

  /** 禁用两步验证 */
  disable2FA: (code: string) =>
    apiClient.post<MessageResponse>('/api/auth/2fa/disable', { code }),

  /** 获取恢复码 */
  getRecoveryCodes: () =>
    apiClient.get<RecoveryCodesResponse>('/api/auth/2fa/recovery-codes'),

  /** 修改密码 */
  changePassword: (data: ChangePasswordRequest) =>
    apiClient.put<MessageResponse>('/api/auth/password', data),

  /** 获取登录设备列表 */
  getDevices: () =>
    apiClient.get<DeviceInfo[]>('/api/auth/devices'),
};

export default authApi;
