/**
 * 底部标签栏组件
 * 移动端显示，Webull 风格紧凑底栏
 */

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  LineChartOutlined,
  StarOutlined,
  UserOutlined,
} from '@ant-design/icons';

/** 标签项定义 */
const tabs = [
  { key: '/', icon: <LineChartOutlined />, label: '行情' },
  { key: '/watchlist', icon: <StarOutlined />, label: '自选' },
  { key: '/profile', icon: <UserOutlined />, label: '我的' },
];

const BottomTabBar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'center',
        height: 52,
        borderTop: '1px solid var(--border-color)',
        background: 'var(--navbar-bg)',
        backdropFilter: 'blur(12px)',
      }}
    >
      {tabs.map((tab) => {
        const isActive = location.pathname === tab.key;
        return (
          <div
            key={tab.key}
            onClick={() => navigate(tab.key)}
            onKeyDown={(e) => e.key === 'Enter' && navigate(tab.key)}
            role="button"
            tabIndex={0}
            aria-label={tab.label}
            aria-current={isActive ? 'page' : undefined}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 1,
              cursor: 'pointer',
              color: isActive ? 'var(--accent-color)' : 'var(--text-tertiary)',
              fontSize: 10,
              fontWeight: isActive ? 500 : 400,
              transition: 'color 0.2s',
            }}
          >
            <span style={{ fontSize: 18 }}>{tab.icon}</span>
            <span>{tab.label}</span>
          </div>
        );
      })}
    </div>
  );
};

export default BottomTabBar;
