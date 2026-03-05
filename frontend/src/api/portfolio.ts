/**
 * 自选组合 API 服务
 * 封装组合和标的管理相关请求
 */

import apiClient from '@/api/client';
import type { Portfolio, WatchlistItem, MessageResponse } from '@/types';

/** 添加标的请求 */
interface AddItemRequest {
  symbol: string;
  name: string;
  market: string;
}

const portfolioApi = {
  /** 获取用户所有组合 */
  getPortfolios: () =>
    apiClient.get<Portfolio[]>('/api/portfolios'),

  /** 创建新组合 */
  createPortfolio: (name: string) =>
    apiClient.post<Portfolio>('/api/portfolios', { name }),

  /** 更新组合（重命名） */
  updatePortfolio: (id: number, name: string) =>
    apiClient.put<Portfolio>(`/api/portfolios/${id}`, { name }),

  /** 删除组合 */
  deletePortfolio: (id: number) =>
    apiClient.delete<MessageResponse>(`/api/portfolios/${id}`),

  /** 调整组合排序 */
  reorderPortfolios: (ids: number[]) =>
    apiClient.put<MessageResponse>('/api/portfolios/reorder', { ids }),

  /** 获取组合内标的（含行情） */
  getItems: (portfolioId: number) =>
    apiClient.get<WatchlistItem[]>(`/api/portfolios/${portfolioId}/items`),

  /** 添加标的到组合 */
  addItem: (portfolioId: number, data: AddItemRequest) =>
    apiClient.post<WatchlistItem>(`/api/portfolios/${portfolioId}/items`, data),

  /** 移除标的 */
  removeItem: (portfolioId: number, itemId: number) =>
    apiClient.delete<MessageResponse>(`/api/portfolios/${portfolioId}/items/${itemId}`),

  /** 调整标的排序 */
  reorderItems: (portfolioId: number, ids: number[]) =>
    apiClient.put<MessageResponse>(`/api/portfolios/${portfolioId}/items/reorder`, { ids }),
};

export default portfolioApi;
