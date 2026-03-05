/**
 * 全局布局组件
 * Webull 风格：紧凑导航 + 全宽内容区
 */

import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import BottomTabBar from './BottomTabBar';

/** 响应式断点 */
const MOBILE_BREAKPOINT = 768;

const AppLayout: React.FC = () => {
  const [isMobile, setIsMobile] = useState(window.innerWidth < MOBILE_BREAKPOINT);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < MOBILE_BREAKPOINT);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* 桌面端顶部导航 */}
      {!isMobile && <Navbar />}

      {/* 内容区域 */}
      <main
        style={{
          padding: isMobile ? '12px 12px 64px' : '16px 20px',
          maxWidth: 1280,
          width: '100%',
          margin: '0 auto',
        }}
      >
        <Outlet />
      </main>

      {/* 移动端底部标签栏 */}
      {isMobile && (
        <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 100 }}>
          <BottomTabBar />
        </div>
      )}
    </div>
  );
};

export default AppLayout;
