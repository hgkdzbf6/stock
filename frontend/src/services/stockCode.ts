/**
 * 股票代码搜索服务
 */

export interface StockInfo {
  code: string;
  name: string;
  price: number;
  change: number;
  change_pct: number;
  volume: number;
  amount: number;
  market_cap: number;
  market: string;
  open: number;
  high: number;
  low: number;
  pre_close: number;
  update_time: string;
}

export interface SearchResult {
  success: boolean;
  keyword: string;
  search_type: string;
  total: number;
  results: StockInfo[];
}

export interface StockDetail {
  success: boolean;
  data: StockInfo;
}

export interface Statistics {
  success: boolean;
  data: {
    total: number;
    by_market: Record<string, number>;
  };
}

const API_BASE = 'http://localhost:8000/api/v1/stock-code';

/**
 * 下载股票列表
 */
export const downloadStockList = async (page: number = 1, pageSize: number = 5000) => {
  const response = await fetch(`${API_BASE}/download?page=${page}&page_size=${pageSize}`, {
    method: 'POST',
  });
  return response.json();
};

/**
 * 搜索股票
 */
export const searchStocks = async (
  keyword: string,
  searchType: string = 'fuzzy',
  limit: number = 10
): Promise<SearchResult> => {
  const response = await fetch(
    `${API_BASE}/search?keyword=${encodeURIComponent(keyword)}&search_type=${searchType}&limit=${limit}`
  );
  return response.json();
};

/**
 * 根据名称搜索股票
 */
export const searchByName = async (name: string, limit: number = 10): Promise<SearchResult> => {
  const response = await fetch(`${API_BASE}/name/${encodeURIComponent(name)}?limit=${limit}`);
  return response.json();
};

/**
 * 根据代码搜索股票
 */
export const searchByCode = async (code: string, limit: number = 10): Promise<SearchResult> => {
  const response = await fetch(`${API_BASE}/code/${encodeURIComponent(code)}?limit=${limit}`);
  return response.json();
};

/**
 * 根据前缀搜索股票
 */
export const searchByPrefix = async (
  prefix: string,
  searchField: string = 'name',
  limit: number = 10
): Promise<SearchResult> => {
  const response = await fetch(
    `${API_BASE}/prefix?prefix=${encodeURIComponent(prefix)}&search_field=${searchField}&limit=${limit}`
  );
  return response.json();
};

/**
 * 获取股票详细信息
 */
export const getStockInfo = async (code: string): Promise<StockDetail> => {
  const response = await fetch(`${API_BASE}/info/${encodeURIComponent(code)}`);
  return response.json();
};

/**
 * 根据市场获取股票
 */
export const getStocksByMarket = async (market: string, limit: number = 100): Promise<SearchResult> => {
  const response = await fetch(`${API_BASE}/market/${encodeURIComponent(market)}?limit=${limit}`);
  return response.json();
};

/**
 * 获取统计信息
 */
export const getStatistics = async (): Promise<Statistics> => {
  const response = await fetch(`${API_BASE}/statistics`);
  return response.json();
};

/**
 * 刷新股票列表
 */
export const refreshStockList = async () => {
  const response = await fetch(`${API_BASE}/refresh`, {
    method: 'POST',
  });
  return response.json();
};