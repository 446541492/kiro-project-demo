/**
 * 顶部导航栏组件
 * 桌面端显示，包含 Logo、导航链接、主题切换
 */

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Menu, Space } from 'antd';
import {
  LineChartOutlined,
  StarOutlined,
  UserOutlined,
} from '@ant-design/icons';
import ThemeSwitch from '@/components/ThemeSwitch';

/** 导航菜单项 */
const menuItems = [
  { key: '/', icon: <LineChartOutlined />, label: '行情' },
  { key: '/watchlist', icon: <StarOutlined />, label: '自选' },
  { key: '/profile', icon: <UserOutlined />, label: '个人中心' },
];

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div style={{ display: 'flex', alignItems: 'center', padding: '0 24px', height: 56 }}>
      <div
        style={{ fontSize: 18, fontWeight: 600, cursor: 'pointer', marginRight: 32, whiteSpace: 'nowrap' }}
        onClick={() => navigate('/')}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && navigate('/')}
      >
        📈 股票助手
      </div>
      <Menu
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
        style={{ flex: 1, border: 'none' }}
      />
      <Space>
        <ThemeSwitch />
      </Space>
    </div>
  );
};

export default Navbar;
