/**
 * 全局布局组件
 * 桌面端：顶部导航栏 + 内容区域
 * 移动端：内容区域 + 底部标签栏
 */

import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Layout } from 'antd';
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
    <Layout style={{ minHeight: '100vh' }}>
      {/* 桌面端顶部导航 */}
      {!isMobile && (
        <Layout.Header style={{ background: 'inherit', padding: 0, height: 56, lineHeight: '56px' }}>
          <Navbar />
        </Layout.Header>
      )}

      {/* 内容区域 */}
      <Layout.Content
        style={{
          padding: isMobile ? '16px 12px 72px' : '16px 24px',
          maxWidth: 1200,
          width: '100%',
          margin: '0 auto',
          flex: 1,
        }}
      >
        <Outlet />
      </Layout.Content>

      {/* 移动端底部标签栏 */}
      {isMobile && (
        <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 100 }}>
          <BottomTabBar />
        </div>
      )}
    </Layout>
  );
};

export default AppLayout;
