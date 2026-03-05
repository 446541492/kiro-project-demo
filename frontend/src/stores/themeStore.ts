/**
 * 主题状态管理
 * 管理明暗主题切换，持久化到 localStorage
 */

import { create } from 'zustand';
import type { ThemeMode } from '@/types';

/** localStorage 存储键 */
const THEME_STORAGE_KEY = 'theme';

/** 获取初始主题：localStorage > 系统偏好 > 默认浅色 */
function getInitialTheme(): ThemeMode {
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === 'light' || stored === 'dark') return stored;

  // 检测系统主题偏好
  if (window.matchMedia?.('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

interface ThemeState {
  theme: ThemeMode;
  toggleTheme: () => void;
  setTheme: (theme: ThemeMode) => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  theme: getInitialTheme(),

  toggleTheme: () => {
    set((state) => {
      const next = state.theme === 'light' ? 'dark' : 'light';
      localStorage.setItem(THEME_STORAGE_KEY, next);
      document.documentElement.setAttribute('data-theme', next);
      return { theme: next };
    });
  },

  setTheme: (theme: ThemeMode) => {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
    document.documentElement.setAttribute('data-theme', theme);
    set({ theme });
  },
}));
