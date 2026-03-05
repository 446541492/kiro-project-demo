/**
 * 行情 API 服务
 * 封装行情榜单、搜索、行情查询相关请求
 */

import apiClient from '@/api/client';
import type { StockQuote, SymbolInfo, RankingType } from '@/types';

const marketApi = {
  /** 获取行情榜单 */
  getRankings: (type: RankingType, market?: string, limit = 20) =>
    apiClient.get<StockQuote[]>('/api/market/rankings', {
      params: { ranking_type: type, market, limit },
    }),

  /** 搜索标的 */
  searchSymbols: (keyword: string) =>
    apiClient.get<SymbolInfo[]>('/api/market/search', {
      params: { keyword },
    }),

  /** 获取单个标的行情 */
  getQuote: (symbol: string) =>
    apiClient.get<StockQuote>(`/api/market/quote/${symbol}`),
};

export default marketApi;
