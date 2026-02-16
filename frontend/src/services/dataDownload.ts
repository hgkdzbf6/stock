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
  try {
    const response = await api.post('/data/download', request);
    
    // 确保响应包含必要的字段
    if (!response) {
      throw new Error('服务器返回了空响应');
    }
    
    // 检查响应格式
    if (!response.status) {
      console.error('返回的数据格式不正确:', response);
      throw new Error('服务器返回的数据格式不正确');
    }
    
    return response;
  } catch (error: any) {
    console.error('下载API调用失败:', error);
    
    // 如果是网络错误或服务器错误，返回一个失败状态
    if (error.response) {
      // 服务器返回了错误状态码
      throw new Error(error.response.data?.detail || error.response.data?.message || '服务器错误');
    } else if (error.request) {
      // 请求已发出但没有收到响应
      throw new Error('无法连接到服务器，请检查网络连接');
    } else {
      // 其他错误
      throw error;
    }
  }
};

/**
 * 批量下载股票数据
 */
export const batchDownloadStockData = async (
  request: BatchDownloadRequest
): Promise<BatchDownloadResponse> => {
  try {
    const response = await api.post('/data/batch-download', request);
    return response;
  } catch (error: any) {
    console.error('批量下载失败:', error);
    throw new Error(error.response?.data?.detail || error.message || '批量下载失败');
  }
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
  try {
    const response = await api.get('/data/check', {
      params: { stock_code, start_date, end_date, frequency }
    });
    return response;
  } catch (error: any) {
    console.error('检查数据可用性失败:', error);
    throw new Error(error.response?.data?.detail || error.message || '检查数据失败');
  }
};

/**
 * 获取已下载数据列表
 */
export const getDownloadedList = async (
  stock_code?: string,
  limit: number = 100,
  offset: number = 0
): Promise<DownloadedListResponse> => {
  try {
    const response = await api.get('/data/downloads', {
      params: stock_code ? { stock_code, limit, offset } : { limit, offset }
    });
    return response;
  } catch (error: any) {
    console.error('获取已下载数据列表失败:', error);
    throw new Error(error.response?.data?.detail || error.message || '获取数据列表失败');
  }
};

/**
 * 删除已下载数据
 */
export const deleteDownloadedData = async (record_id: number): Promise<{ status: string; message: string }> => {
  try {
    const response = await api.delete(`/data/downloads/${record_id}`);
    return response;
  } catch (error: any) {
    console.error('删除数据失败:', error);
    throw new Error(error.response?.data?.detail || error.message || '删除数据失败');
  }
};

/**
 * 获取下载统计信息
 */
export const getStatistics = async (): Promise<StatisticsResponse> => {
  try {
    const response = await api.get('/data/statistics');
    return response;
  } catch (error: any) {
    console.error('获取统计信息失败:', error);
    throw new Error(error.response?.data?.detail || error.message || '获取统计信息失败');
  }
};

/**
 * 获取下载状态
 */
export const getDownloadStatus = async (download_id: string): Promise<any> => {
  try {
    const response = await api.get(`/data/status/${download_id}`);
    return response;
  } catch (error: any) {
    console.error('获取下载状态失败:', error);
    throw new Error(error.response?.data?.detail || error.message || '获取下载状态失败');
  }
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