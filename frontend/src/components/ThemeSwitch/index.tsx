/**
 * 主题切换组件
 * 点击在明暗主题之间切换
 */

import React from 'react';
import { Switch } from 'antd';
import { SunOutlined, MoonOutlined } from '@ant-design/icons';
import { useThemeStore } from '@/stores/themeStore';

const ThemeSwitch: React.FC = () => {
  const { theme, toggleTheme } = useThemeStore();

  return (
    <Switch
      checked={theme === 'dark'}
      onChange={toggleTheme}
      checkedChildren={<MoonOutlined />}
      unCheckedChildren={<SunOutlined />}
      aria-label="切换主题"
    />
  );
};

export default ThemeSwitch;
