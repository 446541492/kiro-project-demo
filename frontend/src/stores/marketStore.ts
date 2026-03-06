/**
 * 行情状态管理（骨架）
 * 管理榜单数据、搜索结果、自动刷新
 */

import { create } from 'zustand';
import apiClient from '@/api/client';
import type { StockQuote, SymbolInfo, RankingType } from '@/types';

interface MarketState {
  // 状态
  rankings: Record<string, StockQuote[]>;
  searchResults: SymbolInfo[];
  activeRankingType: RankingType;
  loading: boolean;
  searchLoading: boolean;
  refreshTimer: ReturnType<typeof setInterval> | null;
  /** 轮询请求进行中标记，防止重复发请求 */
  _refreshing: boolean;

  // 方法
  fetchRankings: (type: RankingType, market?: string) => Promise<void>;
  searchSymbols: (keyword: string) => Promise<void>;
  clearSearchResults: () => void;
  startAutoRefresh: (interval?: number) => void;
  stopAutoRefresh: () => void;
}

export const useMarketStore = create<MarketState>((set, get) => ({
  rankings: {},
  searchResults: [],
  activeRankingType: 'rise',
  loading: false,
  searchLoading: false,
  refreshTimer: null,
  _refreshing: false,

  fetchRankings: async (type: RankingType, market?: string) => {
    set({ loading: true, activeRankingType: type });
    try {
      const params: Record<string, string> = { ranking_type: type };
      if (market) params.market = market;
      const resp = await apiClient.get<StockQuote[]>('/api/market/rankings', { params });
      set((state) => ({
        rankings: { ...state.rankings, [type]: resp.data },
      }));
    } finally {
      set({ loading: false });
    }
  },

  searchSymbols: async (keyword: string) => {
    if (!keyword.trim()) {
      set({ searchResults: [] });
      return;
    }
    set({ searchLoading: true });
    try {
      const resp = await apiClient.get<SymbolInfo[]>('/api/market/search', {
        params: { keyword },
      });
      set({ searchResults: resp.data });
    } finally {
      set({ searchLoading: false });
    }
  },

  clearSearchResults: () => set({ searchResults: [] }),

  startAutoRefresh: (interval = 30000) => {
    const { stopAutoRefresh } = get();
    stopAutoRefresh();
    const timer = setInterval(async () => {
      const { _refreshing, activeRankingType } = get();
      if (_refreshing) return;
      set({ _refreshing: true });
      try {
        const params: Record<string, string> = { ranking_type: activeRankingType };
        const resp = await apiClient.get<StockQuote[]>('/api/market/rankings', { params });
        set((state) => ({
          rankings: { ...state.rankings, [activeRankingType]: resp.data },
        }));
      } catch {
        // 静默刷新失败不提示
      } finally {
        set({ _refreshing: false });
      }
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
}));
