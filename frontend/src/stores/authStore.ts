/**
 * 认证状态管理
 * 管理用户登录状态、Token、用户信息
 */

import { create } from 'zustand';
import apiClient, { setAccessToken, clearAuth } from '@/api/client';
import type { User, LoginRequest, RegisterRequest, LoginResponse } from '@/types';

interface AuthState {
  // 状态
  user: User | null;
  isAuthenticated: boolean;
  is2FARequired: boolean;
  tempToken: string | null;
  loading: boolean;

  // 方法
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  verify2FA: (code: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  reset: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  // 初始化时检查 localStorage 是否有 token，避免刷新页面闪烁到登录页
  isAuthenticated: !!localStorage.getItem('access_token'),
  is2FARequired: false,
  tempToken: null,
  loading: false,

  login: async (data: LoginRequest) => {
    set({ loading: true });
    try {
      const resp = await apiClient.post<LoginResponse>('/api/auth/login', data);
      const result = resp.data;

      if (result.requires_2fa) {
        // 需要 2FA 验证
        set({ is2FARequired: true, tempToken: result.temp_token || null });
      } else {
        // 登录成功
        setAccessToken(result.access_token || null);
        localStorage.setItem('refresh_token', result.refresh_token || '');
        set({ isAuthenticated: true, is2FARequired: false, tempToken: null });
        await get().fetchUser();
      }
    } finally {
      set({ loading: false });
    }
  },

  register: async (data: RegisterRequest) => {
    set({ loading: true });
    try {
      const resp = await apiClient.post('/api/auth/register', data);
      setAccessToken(resp.data.access_token);
      localStorage.setItem('refresh_token', resp.data.refresh_token);
      set({ isAuthenticated: true });
      await get().fetchUser();
    } finally {
      set({ loading: false });
    }
  },

  verify2FA: async (code: string) => {
    set({ loading: true });
    try {
      const { tempToken } = get();
      const resp = await apiClient.post('/api/auth/2fa/verify', {
        temp_token: tempToken,
        code,
      });
      setAccessToken(resp.data.access_token);
      localStorage.setItem('refresh_token', resp.data.refresh_token);
      set({ isAuthenticated: true, is2FARequired: false, tempToken: null });
      await get().fetchUser();
    } finally {
      set({ loading: false });
    }
  },

  logout: async () => {
    try {
      await apiClient.post('/api/auth/logout');
    } catch {
      // 登出失败也清除本地状态
    }
    clearAuth();
    set({ user: null, isAuthenticated: false, is2FARequired: false, tempToken: null });
  },

  fetchUser: async () => {
    try {
      const resp = await apiClient.get<User>('/api/auth/me');
      set({ user: resp.data, isAuthenticated: true });
    } catch {
      set({ user: null, isAuthenticated: false });
    }
  },

  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;
    try {
      const resp = await apiClient.post('/api/auth/refresh', {
        refresh_token: refreshToken,
      });
      setAccessToken(resp.data.access_token);
      if (resp.data.refresh_token) {
        localStorage.setItem('refresh_token', resp.data.refresh_token);
      }
      set({ isAuthenticated: true });
      return true;
    } catch {
      clearAuth();
      set({ user: null, isAuthenticated: false });
      return false;
    }
  },

  reset: () => {
    clearAuth();
    set({ user: null, isAuthenticated: false, is2FARequired: false, tempToken: null, loading: false });
  },
}));
