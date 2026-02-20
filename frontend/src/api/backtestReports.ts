/** 回测报告API */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface BacktestReportMetadata {
  filename: string;
  strategy_name: string;
  stock_code: string;
  start_date: string;
  end_date: string;
  create_time: string;
  file_path: string;
}

export interface BacktestReportData {
  metadata?: BacktestReportMetadata;
  data: any;
}

/**
 * 获取回测报告列表
 */
export async function getBacktestReports(): Promise<BacktestReportMetadata[]> {
  const response = await fetch(`${API_BASE_URL}/backtest-reports/list`);
  
  if (!response.ok) {
    throw new Error('获取回测报告列表失败');
  }
  
  const result = await response.json();
  
  // 后端直接返回数组，不需要检查code字段
  return Array.isArray(result) ? result : [];
}

/**
 * 保存回测报告
 */
export async function saveBacktestReport(data: any, strategyName?: string): Promise<{ filename: string; file_path: string }> {
  const response = await fetch(`${API_BASE_URL}/backtest-reports/save`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      data,
      strategy_name: strategyName,
    }),
  });
  
  const result = await response.json();
  
  if (result.code === 200) {
    return result.data;
  }
  
  throw new Error(result.message || '保存回测报告失败');
}

/**
 * 加载回测报告
 */
export async function loadBacktestReport(filename: string): Promise<BacktestReportData> {
  const response = await fetch(`${API_BASE_URL}/backtest-reports/load/${filename}`);
  const result = await response.json();
  
  if (result.code === 200) {
    return {
      data: result.data,
      metadata: result.metadata,
    };
  }
  
  throw new Error(result.message || '加载回测报告失败');
}

/**
 * 删除回测报告
 */
export async function deleteBacktestReport(filename: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/backtest-reports/${filename}`, {
    method: 'DELETE',
  });
  
  const result = await response.json();
  
  if (result.code !== 200) {
    throw new Error(result.message || '删除回测报告失败');
  }
}