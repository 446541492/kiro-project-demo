/**
 * 顶部导航栏组件
 * Webull 风格：深色紧凑导航、简洁 Logo、高亮当前页
 */

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  LineChartOutlined,
  StarOutlined,
  UserOutlined,
} from '@ant-design/icons';
import ThemeSwitch from '@/components/ThemeSwitch';

/** 导航菜单项 */
const navItems = [
  { key: '/', icon: <LineChartOutlined />, label: '行情' },
  { key: '/watchlist', icon: <StarOutlined />, label: '自选' },
  { key: '/profile', icon: <UserOutlined />, label: '我的' },
];

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        padding: '0 24px',
        height: 48,
        background: 'var(--navbar-bg)',
        borderBottom: '1px solid var(--border-color)',
      }}
    >
      {/* Logo */}
      <div
        style={{
          fontSize: 15,
          fontWeight: 600,
          cursor: 'pointer',
          marginRight: 32,
          whiteSpace: 'nowrap',
          color: 'var(--accent-color)',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}
        onClick={() => navigate('/')}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && navigate('/')}
      >
        <LineChartOutlined style={{ fontSize: 18 }} />
        <span>股票助手</span>
      </div>

      {/* 导航项 */}
      <nav style={{ display: 'flex', gap: 4, flex: 1 }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.key;
          return (
            <div
              key={item.key}
              onClick={() => navigate(item.key)}
              onKeyDown={(e) => e.key === 'Enter' && navigate(item.key)}
              role="button"
              tabIndex={0}
              aria-label={item.label}
              aria-current={isActive ? 'page' : undefined}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                padding: '6px 14px',
                borderRadius: 6,
                cursor: 'pointer',
                fontSize: 13,
                fontWeight: isActive ? 500 : 400,
                color: isActive ? 'var(--accent-color)' : 'var(--text-secondary)',
                background: isActive ? 'var(--tab-active-bg)' : 'transparent',
                transition: 'all 0.2s',
              }}
            >
              {item.icon}
              <span>{item.label}</span>
            </div>
          );
        })}
      </nav>

      {/* 主题切换 */}
      <ThemeSwitch />
    </div>
  );
};

export default Navbar;
