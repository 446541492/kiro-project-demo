/**
 * Axios HTTP 客户端封装
 * 统一请求拦截（Token 注入）和响应拦截（错误处理、Token 自动刷新）
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { message } from 'antd';
import type { ApiError } from '@/types';

// 创建 Axios 实例
const apiClient = axios.create({
  baseURL: '',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// 刷新 Token 的锁，防止并发刷新
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

/** 等待 Token 刷新完成后重试请求 */
function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

/** 通知所有等待的请求 */
function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

// ==================== 请求拦截器 ====================

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从内存获取 token（通过 store 的 getState）
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ==================== 响应拦截器 ====================

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config;
    if (!originalRequest) return Promise.reject(error);

    // 401 错误：尝试刷新 Token
    if (error.response?.status === 401 && !('_retry' in originalRequest)) {
      // 标记已重试，防止无限循环
      (originalRequest as unknown as Record<string, unknown>)._retry = true;

      if (!isRefreshing) {
        isRefreshing = true;
        const refreshToken = localStorage.getItem('refresh_token');

        if (refreshToken) {
          try {
            const resp = await axios.post('/api/auth/refresh', {
              refresh_token: refreshToken,
            });
            const newToken = resp.data.access_token;
            setAccessToken(newToken);

            // 如果返回了新的 refresh_token，也更新
            if (resp.data.refresh_token) {
              localStorage.setItem('refresh_token', resp.data.refresh_token);
            }

            isRefreshing = false;
            onTokenRefreshed(newToken);

            // 重试原请求
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            return apiClient(originalRequest);
          } catch {
            isRefreshing = false;
            // 刷新失败，清除状态跳转登录
            clearAuth();
            window.location.href = '/login';
            return Promise.reject(error);
          }
        } else {
          isRefreshing = false;
          clearAuth();
          window.location.href = '/login';
          return Promise.reject(error);
        }
      } else {
        // 正在刷新中，排队等待
        return new Promise((resolve) => {
          subscribeTokenRefresh((token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(apiClient(originalRequest));
          });
        });
      }
    }

    // 其他错误：显示提示
    const errorMsg = error.response?.data?.detail || '网络连接失败，请检查网络';
    if (error.response?.status && error.response.status >= 500) {
      message.error('服务器繁忙，请稍后重试');
    } else if (error.response?.status !== 401) {
      message.error(errorMsg);
    }

    return Promise.reject(error);
  }
);

// ==================== Token 管理（与 authStore 桥接） ====================

let _accessToken: string | null = null;

export function getAccessToken(): string | null {
  return _accessToken;
}

export function setAccessToken(token: string | null) {
  _accessToken = token;
}

export function clearAuth() {
  _accessToken = null;
  localStorage.removeItem('refresh_token');
}

export default apiClient;
