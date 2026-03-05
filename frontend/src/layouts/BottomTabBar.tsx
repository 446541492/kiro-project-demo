/**
 * 底部标签栏组件
 * 移动端显示，提供行情、自选、我的三个标签
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
        height: 56,
        borderTop: '1px solid var(--border-color, #f0f0f0)',
        background: 'var(--bg-color, #fff)',
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
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
              cursor: 'pointer',
              color: isActive ? '#1677ff' : '#999',
              fontSize: 12,
            }}
          >
            <span style={{ fontSize: 20 }}>{tab.icon}</span>
            <span>{tab.label}</span>
          </div>
        );
      })}
    </div>
  );
};

export default BottomTabBar;
