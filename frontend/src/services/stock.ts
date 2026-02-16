/** 股票服务 */
import apiClient from './api';
import cacheService from '../utils/cache';
import type { Stock, PaginatedResponse } from '../types/api';

export const stockService = {
  /** 获取股票列表 */
  async getStockList(params: {
    page?: number;
    page_size?: number;
    sector?: string;
    keyword?: string;
    data_source?: string;
    use_local?: boolean;  // 是否使用本地已下载数据（默认true）
  } = {}) {
    // 默认使用本地数据
    if (params.use_local === undefined) {
      params.use_local = true;
    }
    
    const cacheKey = `stock_list_${JSON.stringify(params)}`;
    
    // 如果使用本地数据，不缓存（因为数据会变化）
    if (params.use_local) {
      console.log(`[股票列表] 请求API (不缓存): ${JSON.stringify(params)}`);
      return apiClient.get<PaginatedResponse<any>>('/stocks', { params });
    }
    
    // 远程数据缓存5分钟
    const cached = cacheService.get<PaginatedResponse<any>>(cacheKey, 5 * 60 * 1000);
    if (cached) {
      console.log(`[股票列表] 使用缓存: ${JSON.stringify(params)}`);
      return cached;
    }
    
    console.log(`[股票列表] 请求API: ${JSON.stringify(params)}`);
    const data = await apiClient.get<PaginatedResponse<any>>('/stocks', { params });
    cacheService.set(cacheKey, data, 5 * 60 * 1000);
    
    return data;
  },

  /** 获取股票详情 */
  async getStock(code: string) {
    const cacheKey = `stock_detail_${code}`;
    
    // 先检查缓存（股票详情缓存10分钟）
    const cached = cacheService.get<{ code: number; message: string; data: Stock }>(cacheKey, 10 * 60 * 1000);
    if (cached) {
      console.log(`[股票详情] 使用缓存: ${code}`);
      return cached;
    }
    
    console.log(`[股票详情] 请求API: ${code}`);
    const data = await apiClient.get<{ code: number; message: string; data: Stock }>(`/stocks/${code}`, {
      timeout: 60000, // 60秒超时
    });
    
    // 缓存结果
    cacheService.set(cacheKey, data, 10 * 60 * 1000);
    
    return data;
  },

  /** 搜索股票 */
  async searchStocks(keyword: string, limit: number = 20) {
    const cacheKey = `stock_search_${keyword}_${limit}`;
    
    // 先检查缓存（搜索结果缓存5分钟）
    const cached = cacheService.get<any>(cacheKey, 5 * 60 * 1000);
    if (cached) {
      console.log(`[股票搜索] 使用缓存: ${keyword}`);
      return cached;
    }
    
    console.log(`[股票搜索] 请求API: ${keyword}`);
    const data = await apiClient.get<any>(`/stocks/search/${keyword}`, {
      params: { limit },
      timeout: 60000, // 60秒超时
    });
    
    // 缓存结果
    cacheService.set(cacheKey, data, 5 * 60 * 1000);
    
    return data;
  },
};