/**
 * 股票代码服务
 */
import axios from 'axios';
import { authService } from './auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface StockInfo {
  code: string;
  name: string;
  market?: string;
  sector?: string;
  industry?: string;
}

/**
 * 股票代码服务
 */
export const stockCodeService = {
  /**
   * 获取股票详细信息
   */
  async getStockInfo(code: string): Promise<StockInfo | null> {
    try {
      const response = await axios.get(`${API_BASE_URL}/stock-code/info/${code}`, {
        headers: authService.getAuthHeader()
      });
      return response.data.data;
    } catch (error: any) {
      console.error('获取股票信息失败:', error);
      return null;
    }
  },

  /**
   * 搜索股票
   */
  async searchStocks(
    keyword: string,
    searchType: 'fuzzy' | 'code' | 'name' | 'prefix' = 'fuzzy',
    limit: number = 10
  ): Promise<{ results: StockInfo[]; total: number }> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/stock-code/search`,
        {
          params: { keyword, search_type: searchType, limit },
          headers: authService.getAuthHeader()
        }
      );
      return {
        results: response.data.results || [],
        total: response.data.total || 0
      };
    } catch (error: any) {
      console.error('搜索股票失败:', error);
      return { results: [], total: 0 };
    }
  },

  /**
   * 根据前缀搜索
   */
  async searchByPrefix(
    prefix: string,
    searchField: 'name' | 'code' = 'name',
    limit: number = 10
  ): Promise<StockInfo[]> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/stock-code/prefix`,
        {
          params: { prefix, search_field: searchField, limit },
          headers: authService.getAuthHeader()
        }
      );
      return response.data.results || [];
    } catch (error: any) {
      console.error('前缀搜索失败:', error);
      return [];
    }
  },

  /**
   * 根据名称搜索
   */
  async searchByName(name: string, limit: number = 10): Promise<StockInfo[]> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/stock-code/name/${name}`,
        {
          params: { limit },
          headers: authService.getAuthHeader()
        }
      );
      return response.data.results || [];
    } catch (error: any) {
      console.error('名称搜索失败:', error);
      return [];
    }
  },

  /**
   * 根据代码搜索
   */
  async searchByCode(code: string, limit: number = 10): Promise<StockInfo[]> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/stock-code/code/${code}`,
        {
          params: { limit },
          headers: authService.getAuthHeader()
        }
      );
      return response.data.results || [];
    } catch (error: any) {
      console.error('代码搜索失败:', error);
      return [];
    }
  }
};

// 导出独立的函数，方便直接导入使用
export async function searchStocks(
  keyword: string,
  searchType: 'fuzzy' | 'code' | 'name' | 'prefix' = 'fuzzy',
  limit: number = 10
): Promise<{ results: StockInfo[]; total: number }> {
  return stockCodeService.searchStocks(keyword, searchType, limit);
}

export async function getStockInfo(code: string): Promise<StockInfo | null> {
  return stockCodeService.getStockInfo(code);
}

export async function searchByCode(code: string, limit: number = 10): Promise<StockInfo[]> {
  return stockCodeService.searchByCode(code, limit);
}

export async function searchByName(name: string, limit: number = 10): Promise<StockInfo[]> {
  return stockCodeService.searchByName(name, limit);
}

export async function searchByPrefix(
  prefix: string,
  searchField: 'name' | 'code' = 'name',
  limit: number = 10
): Promise<StockInfo[]> {
  return stockCodeService.searchByPrefix(prefix, searchField, limit);
}