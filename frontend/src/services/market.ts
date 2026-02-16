/** 行情服务 */
import apiClient from './api';
import cacheService from '../utils/cache';
import type { Quote, KlineData, Indicators } from '../types/api';

export type { Quote, KlineData, Indicators } from '../types/api';

export const marketService = {
  /** 获取实时行情 */
  async getQuote(code: string) {
    const cacheKey = `market_quote_${code}`;
    
    // 先检查缓存（实时行情缓存30秒）
    const cached = cacheService.get<any>(cacheKey, 30 * 1000);
    if (cached) {
      console.log(`[实时行情] 使用缓存: ${code}`);
      return cached;
    }
    
    console.log(`[实时行情] 请求API: ${code}`);
    const data = await apiClient.get<Quote>(`/market/quote/${code}`);
    
    // 缓存结果
    cacheService.set(cacheKey, data, 30 * 1000);
    
    return data;
  },

  /** 获取K线数据 */
  async getKlineData(params: {
    code: string;
    freq?: string;
    start_date: string;
    end_date: string;
  }) {
    const { code, freq = 'daily', start_date, end_date } = params;
    const cacheKey = `market_kline_${code}_${freq}_${start_date}_${end_date}`;
    
    // 先检查缓存（K线数据缓存10分钟）
    const cached = cacheService.get<any>(cacheKey, 10 * 60 * 1000);
    if (cached) {
      console.log(`[K线数据] 使用缓存: ${code} ${freq} ${start_date}-${end_date}`);
      return cached;
    }
    
    console.log(`[K线数据] 请求API: ${code} ${freq} ${start_date}-${end_date}`);
    const data = await apiClient.get<any>(`/market/kline/${code}`, {
      params: { freq, start_date, end_date },
      timeout: 60000, // 60秒超时
    });
    
    // 缓存结果
    cacheService.set(cacheKey, data, 10 * 60 * 1000);
    
    return data;
  },

  /** 获取技术指标 */
  async getIndicators(params: {
    code: string;
    freq?: string;
    start_date: string;
    end_date: string;
    indicators?: string[];
  }) {
    const { code, ...rest } = params;
    const cacheKey = `market_indicators_${code}_${JSON.stringify(rest)}`;
    
    // 先检查缓存（技术指标缓存10分钟）
    const cached = cacheService.get<Indicators>(cacheKey, 10 * 60 * 1000);
    if (cached) {
      console.log(`[技术指标] 使用缓存: ${code}`);
      return cached;
    }
    
    console.log(`[技术指标] 请求API: ${code}`);
    const data = await apiClient.get<Indicators>(`/market/indicators/${code}`, {
      params: rest,
      timeout: 60000, // 60秒超时
    });
    
    // 缓存结果
    cacheService.set(cacheKey, data, 10 * 60 * 1000);
    
    return data;
  },

  /** 批量获取行情 */
  async getBatchQuotes(codes: string) {
    const cacheKey = `market_batch_${codes}`;
    
    // 先检查缓存（批量行情缓存30秒）
    const cached = cacheService.get<any>(cacheKey, 30 * 1000);
    if (cached) {
      console.log(`[批量行情] 使用缓存: ${codes}`);
      return cached;
    }
    
    console.log(`[批量行情] 请求API: ${codes}`);
    const data = await apiClient.get<any>('/market/batch', {
      params: { codes },
      timeout: 60000, // 60秒超时
    });
    
    // 缓存结果
    cacheService.set(cacheKey, data, 30 * 1000);
    
    return data;
  },
};