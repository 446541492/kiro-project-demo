/**
 * 应用根组件
 * 路由配置、主题 Provider、路由守卫
 */

import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ConfigProvider, theme as antTheme, App as AntApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { useThemeStore } from '@/stores/themeStore';
import { useAuthStore } from '@/stores/authStore';
import AppLayout from '@/layouts/AppLayout';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';
import MarketPage from '@/pages/MarketPage';
import WatchlistPage from '@/pages/WatchlistPage';
import StockDetailPage from '@/pages/StockDetailPage';
import ProfilePage from '@/pages/ProfilePage';
import TwoFactorSetupPage from '@/pages/TwoFactorSetupPage';
import './App.css';

/** 路由守卫：需要登录 */
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <>{children}</>;
};

/** 路由守卫：已登录重定向 */
const GuestRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
};

/** 应用初始化：尝试恢复登录状态 */
const AppInitializer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { refreshToken, fetchUser } = useAuthStore();

  useEffect(() => {
    const init = async () => {
      const success = await refreshToken();
      if (success) await fetchUser();
    };
    init();
  }, [refreshToken, fetchUser]);

  return <>{children}</>;
};

const App: React.FC = () => {
  const { theme } = useThemeStore();

  // 初始化时设置 data-theme 属性
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme === 'dark' ? antTheme.darkAlgorithm : antTheme.defaultAlgorithm,
        token: { colorPrimary: '#1677ff' },
      }}
    >
      <AntApp>
        <BrowserRouter>
          <AppInitializer>
            <Routes>
              {/* 公开路由 */}
              <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
              <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />

              {/* 受保护路由 */}
              <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
                <Route path="/" element={<MarketPage />} />
                <Route path="/stock/:symbol" element={<StockDetailPage />} />
                <Route path="/watchlist" element={<WatchlistPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/2fa/setup" element={<TwoFactorSetupPage />} />
              </Route>

              {/* 未匹配路由重定向 */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AppInitializer>
        </BrowserRouter>
      </AntApp>
    </ConfigProvider>
  );
};

export default App;
