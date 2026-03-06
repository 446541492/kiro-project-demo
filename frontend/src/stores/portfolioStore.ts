/**
 * 自选组合状态管理（骨架）
 * 管理自选组合列表、标的列表
 */

import { create } from 'zustand';
import apiClient from '@/api/client';
import type { Portfolio, WatchlistItem, SymbolInfo } from '@/types';

interface PortfolioState {
  // 状态
  portfolios: Portfolio[];
  activePortfolioId: number | null;
  items: WatchlistItem[];
  loading: boolean;
  refreshTimer: ReturnType<typeof setInterval> | null;
  /** 轮询请求进行中标记，防止重复发请求 */
  _refreshing: boolean;

  // 方法
  fetchPortfolios: () => Promise<void>;
  createPortfolio: (name: string) => Promise<void>;
  updatePortfolio: (id: number, name: string) => Promise<void>;
  deletePortfolio: (id: number) => Promise<void>;
  reorderPortfolios: (ids: number[]) => Promise<void>;
  setActivePortfolio: (id: number) => void;
  fetchItems: (portfolioId: number) => Promise<void>;
  /** 静默刷新行情数据（不触发 loading 状态） */
  refreshItems: () => Promise<void>;
  addItem: (portfolioId: number, symbol: SymbolInfo) => Promise<void>;
  removeItem: (portfolioId: number, itemId: number) => Promise<void>;
  reorderItems: (portfolioId: number, ids: number[]) => Promise<void>;
  /** 启动自动轮询刷新 */
  startAutoRefresh: (interval?: number) => void;
  /** 停止自动轮询刷新 */
  stopAutoRefresh: () => void;
}

export const usePortfolioStore = create<PortfolioState>((set, get) => ({
  portfolios: [],
  activePortfolioId: null,
  items: [],
  loading: false,
  refreshTimer: null,
  _refreshing: false,

  fetchPortfolios: async () => {
    set({ loading: true });
    try {
      const resp = await apiClient.get<Portfolio[]>('/api/portfolios');
      const portfolios = resp.data;
      set({ portfolios });
      // 如果没有选中组合，默认选中第一个
      if (!get().activePortfolioId && portfolios.length > 0) {
        set({ activePortfolioId: portfolios[0].id });
        await get().fetchItems(portfolios[0].id);
      }
    } finally {
      set({ loading: false });
    }
  },

  createPortfolio: async (name: string) => {
    const resp = await apiClient.post<Portfolio>('/api/portfolios', { name });
    const newPortfolio = resp.data;
    set((state) => ({
      portfolios: [...state.portfolios, newPortfolio],
      // 如果是第一个组合，自动选中
      activePortfolioId: state.activePortfolioId ?? newPortfolio.id,
      items: state.activePortfolioId ? state.items : [],
    }));
  },

  updatePortfolio: async (id: number, name: string) => {
    const resp = await apiClient.put<Portfolio>(`/api/portfolios/${id}`, { name });
    set((state) => ({
      portfolios: state.portfolios.map((p) => (p.id === id ? resp.data : p)),
    }));
  },

  deletePortfolio: async (id: number) => {
    await apiClient.delete(`/api/portfolios/${id}`);
    set((state) => ({
      portfolios: state.portfolios.filter((p) => p.id !== id),
      // 如果删除的是当前选中的组合，切换到第一个
      activePortfolioId: state.activePortfolioId === id
        ? (state.portfolios.find((p) => p.id !== id)?.id ?? null)
        : state.activePortfolioId,
    }));
  },

  reorderPortfolios: async (ids: number[]) => {
    await apiClient.put('/api/portfolios/reorder', { ids });
    await get().fetchPortfolios();
  },

  setActivePortfolio: (id: number) => {
    set({ activePortfolioId: id });
    get().fetchItems(id);
  },

  fetchItems: async (portfolioId: number) => {
    set({ loading: true });
    try {
      const resp = await apiClient.get<WatchlistItem[]>(`/api/portfolios/${portfolioId}/items`);
      set({ items: resp.data });
    } finally {
      set({ loading: false });
    }
  },

  refreshItems: async () => {
    const { activePortfolioId, _refreshing } = get();
    if (!activePortfolioId || _refreshing) return;
    set({ _refreshing: true });
    try {
      const resp = await apiClient.get<WatchlistItem[]>(`/api/portfolios/${activePortfolioId}/items`);
      set({ items: resp.data });
    } catch {
      // 静默刷新失败不提示
    } finally {
      set({ _refreshing: false });
    }
  },

  startAutoRefresh: (interval = 15000) => {
    const { stopAutoRefresh } = get();
    stopAutoRefresh();
    const timer = setInterval(() => {
      get().refreshItems();
    }, interval);
    set({ refreshTimer: timer });
  },

  stopAutoRefresh: () => {
    const { refreshTimer } = get();
    if (refreshTimer) {
      clearInterval(refreshTimer);
      set({ refreshTimer: null });
    }
  },

  addItem: async (portfolioId: number, symbol: SymbolInfo) => {
    const resp = await apiClient.post<WatchlistItem>(`/api/portfolios/${portfolioId}/items`, {
      symbol: symbol.symbol,
      name: symbol.name,
      market: symbol.market,
    });
    set((state) => ({ items: [...state.items, resp.data] }));
  },

  removeItem: async (portfolioId: number, itemId: number) => {
    await apiClient.delete(`/api/portfolios/${portfolioId}/items/${itemId}`);
    set((state) => ({ items: state.items.filter((i) => i.id !== itemId) }));
  },

  reorderItems: async (portfolioId: number, ids: number[]) => {
    await apiClient.put(`/api/portfolios/${portfolioId}/items/reorder`, { ids });
    await get().fetchItems(portfolioId);
  },
}));
