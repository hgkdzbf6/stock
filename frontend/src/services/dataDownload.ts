/**
 * 数据下载服务
 */

import api from './api';

export interface DownloadRequest {
  stock_code: string;
  start_date: string;
  end_date: string;
  frequency?: string;
  source?: string;
  force_download?: boolean;
}

export interface BatchDownloadRequest {
  stock_codes: string[];
  start_date: string;
  end_date: string;
  frequency?: string;
  source?: string;
}

export interface DownloadResponse {
  status: 'completed' | 'exists' | 'partial_overlap' | 'failed';
  message: string;
  download_id: string;
  stock_code: string;
  stock_name?: string;
  data_count?: number;
  record_id?: number;
  existing_data?: any;
}

export interface BatchDownloadResponse {
  total: number;
  success: number;
  failed: number;
  results: DownloadResponse[];
}

export interface CheckDataResponse {
  available: boolean;
  overlap_type?: 'exact' | 'partial';
  existing_data?: any;
}

export interface DownloadedData {
  id: number;
  stock_code: string;
  stock_name?: string;
  start_date: string;
  end_date: string;
  frequency: string;
  data_count: number;
  downloaded_at: string;
  updated_at: string;
  source?: string;
  file_path: string;
  file_size: number;
  file_size_str: string;
}

export interface DownloadedListResponse {
  downloads: DownloadedData[];
  total: number;
}

export interface StatisticsResponse {
  total_downloads: number;
  unique_stocks: number;
  total_data_points: number;
  total_file_size: number;
  total_file_size_str: string;
  frequency_distribution: Record<string, number>;
}

/**
 * 下载股票数据
 */
export const downloadStockData = async (request: DownloadRequest): Promise<DownloadResponse> => {
  const response = await api.post('/data/download', request);
  return response.data;
};

/**
 * 批量下载股票数据
 */
export const batchDownloadStockData = async (
  request: BatchDownloadRequest
): Promise<BatchDownloadResponse> => {
  const response = await api.post('/data/batch-download', request);
  return response.data;
};

/**
 * 检查数据是否可用
 */
export const checkDataAvailability = async (
  stock_code: string,
  start_date: string,
  end_date: string,
  frequency: string = 'daily'
): Promise<CheckDataResponse> => {
  const response = await api.get('/data/check', {
    params: { stock_code, start_date, end_date, frequency }
  });
  return response.data;
};

/**
 * 获取已下载数据列表
 */
export const getDownloadedList = async (
  stock_code?: string,
  limit: number = 100,
  offset: number = 0
): Promise<DownloadedListResponse> => {
  const response = await api.get('/data/downloads', {
    params: stock_code ? { stock_code, limit, offset } : { limit, offset }
  });
  return response.data;
};

/**
 * 删除已下载数据
 */
export const deleteDownloadedData = async (record_id: number): Promise<{ status: string; message: string }> => {
  const response = await api.delete(`/data/downloads/${record_id}`);
  return response.data;
};

/**
 * 获取下载统计信息
 */
export const getStatistics = async (): Promise<StatisticsResponse> => {
  const response = await api.get('/data/statistics');
  return response.data;
};

/**
 * 获取下载状态
 */
export const getDownloadStatus = async (download_id: string): Promise<any> => {
  const response = await api.get(`/data/status/${download_id}`);
  return response.data;
};

export default {
  downloadStockData,
  batchDownloadStockData,
  checkDataAvailability,
  getDownloadedList,
  deleteDownloadedData,
  getStatistics,
  getDownloadStatus
};