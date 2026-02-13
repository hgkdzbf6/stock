/** 策略服务 */
import apiClient from './api';
import type { Strategy, BacktestRequest, PaginatedResponse } from '@types/api';

export const strategyService = {
  /** 获取策略列表 */
  async getStrategies() {
    return apiClient.get<any>('/strategies');
  },

  /** 创建策略 */
  async createStrategy(data: {
    name: string;
    type: string;
    description?: string;
    params: Record<string, any>;
  }) {
    return apiClient.post('/strategies', data);
  },

  /** 获取策略详情 */
  async getStrategy(id: number) {
    return apiClient.get<Strategy>(`/strategies/${id}`);
  },

  /** 更新策略 */
  async updateStrategy(
    id: number,
    data: {
      name?: string;
      description?: string;
      params?: Record<string, any>;
      status?: string;
    }
  ) {
    return apiClient.put(`/strategies/${id}`, data);
  },

  /** 删除策略 */
  async deleteStrategy(id: number) {
    return apiClient.delete(`/strategies/${id}`);
  },

  /** 运行回测 */
  async runBacktest(id: number, data: BacktestRequest) {
    return apiClient.post(`/strategies/${id}/backtest`, data);
  },

  /** 参数优化 */
  async optimizeStrategy(id: number, params: {
    method: string;
    stock_code: string;
    param_ranges?: Record<string, any>;
  }) {
    return apiClient.post(`/strategies/${id}/optimize`, null, { params });
  },
};
