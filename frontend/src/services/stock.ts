/** 股票服务 */
import apiClient from './api';
import type { Stock, PaginatedResponse } from '@types/api';

export const stockService = {
  /** 获取股票列表 */
  async getStockList(params: {
    page?: number;
    page_size?: number;
    sector?: string;
    keyword?: string;
  } = {}) {
    return apiClient.get<PaginatedResponse<any>>('/stocks', { params });
  },

  /** 获取股票详情 */
  async getStock(code: string) {
    return apiClient.get<Stock>(`/stocks/${code}`);
  },

  /** 搜索股票 */
  async searchStocks(keyword: string, limit: number = 20) {
    return apiClient.get<any>(`/stocks/search/${keyword}`, {
      params: { limit },
    });
  },
};
