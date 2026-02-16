/** API响应类型 */
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data?: T;
  timestamp?: string;
}

/** 分页响应 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

/** 用户信息 */
export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  phone?: string;
}

/** Token响应 */
export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/** 股票信息 */
export interface Stock {
  代码?: string;
  code?: string;
  名称?: string;
  name?: string;
  market?: string;
  sector?: string;
  industry?: string;
  list_date?: string;
}

/** 实时行情 */
export interface Quote {
  stock_code: string;
  code?: string;
  name?: string;
  price: number;
  change: number;
  change_pct: number;
  open: number;
  high: number;
  low: number;
  pre_close?: number;
  volume: number;
  amount?: number;
  timestamp: string;
}

/** K线数据 */
export interface KlineData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/** 技术指标 */
export interface Indicators {
  MA?: {
    MA5: (number | string)[];
    MA10: (number | string)[];
    MA20: (number | string)[];
    MA60: (number | string)[];
  };
  BOLL?: {
    upper: (number | string)[];
    middle: (number | string)[];
    lower: (number | string)[];
  };
  RSI?: (number | string)[];
  MACD?: {
    DIF: (number | string)[];
    DEA: (number | string)[];
    MACD: (number | string)[];
  };
}

/** 策略信息 */
export interface Strategy {
  id: number;
  name: string;
  type: string;
  description?: string;
  params: Record<string, any>;
  status: string;
  performance?: {
    total_return: number;
    sharpe_ratio: number;
  };
  created_at: string;
}

/** 回测请求 */
export interface BacktestRequest {
  stock_code: string;
  start_date: string;
  end_date: string;
  frequency?: string;
  initial_capital?: number;
}

/** 回测结果 */
export interface BacktestResult {
  id: number;
  strategy_id: number;
  stock_code: string;
  start_date: string;
  end_date: string;
  frequency: string;
  initial_capital: number;
  final_capital: number;
  total_return: number;
  annual_return: number;
  max_drawdown: number;
  sharpe_ratio: number;
  win_rate: number;
  profit_loss_ratio: number;
  volatility: number;
  calmar_ratio: number;
  trade_count: number;
  params: Record<string, any>;
  equity_curve: any[];
  created_at: string;
}
