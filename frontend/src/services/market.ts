/** 行情服务 */
import apiClient from './api';
import type { Quote, KlineData, Indicators } from '@types/api';

export const marketService = {
  /** 获取实时行情 */
  async getQuote(code: string) {
    return apiClient.get<Quote>(`/market/quote/${code}`);
  },

  /** 获取K线数据 */
  async getKlineData(params: {
    code: string;
    freq?: string;
    start_date: string;
    end_date: string;
  }) {
    const { code, ...rest } = params;
    return apiClient.get<any>(`/market/kline/${code}`, { params: rest });
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
    return apiClient.get<Indicators>(`/market/indicators/${code}`, { params: rest });
  },

  /** 批量获取行情 */
  async getBatchQuotes(codes: string) {
    return apiClient.get<any>('/market/batch', {
      params: { codes },
    });
  },
};
