/**AI服务API调用*/
import request from './api';
import type { AxiosProgressEvent } from 'axios';

// ==================== 类型定义 ====================

export interface AIAnalyzeRequest {
  type: 'portfolio' | 'market' | 'indicators' | 'risk' | 'strategy';
  context: Record<string, any>;
  stream?: boolean;
}

export interface ChatRequest {
  question: string;
  context?: Record<string, any>;
  stream?: boolean;
}

export interface PortfolioAnalysisRequest {
  positions: Array<{
    stock_code: string;
    stock_name: string;
    quantity: number;
    cost_price: number;
    current_price?: number;
  }>;
  market_data: Record<string, any>;
  indicators: Record<string, any>;
  stream?: boolean;
}

export interface MarketAnalysisRequest {
  stock_code: string;
  stock_name: string;
  current_price: number;
  kline_data: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
  indicators: Record<string, any>;
  volume_info: Record<string, any>;
  stream?: boolean;
}

export interface IndicatorAnalysisRequest {
  indicators: Record<string, any>;
  stream?: boolean;
}

export interface RiskAssessmentRequest {
  portfolio_info: Record<string, any>;
  risk_metrics: Record<string, any>;
  market_environment: Record<string, any>;
  stream?: boolean;
}

export interface StrategyOptimizationRequest {
  strategy_type: string;
  strategy_params: Record<string, any>;
  backtest_results: Record<string, any>;
  trades_summary: string;
  stream?: boolean;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'warning' | 'error';
  message: string;
  configured: boolean;
  model?: string;
}

// ==================== AI分析API ====================

/**
 * 通用AI分析
 */
export const analyze = async (data: AIAnalyzeRequest): Promise<Record<string, any>> => {
  const response = await request.post('/ai/analyze', data);
  return response.data.data;
};

/**
 * 持仓分析
 */
export const analyzePortfolio = async (
  data: PortfolioAnalysisRequest
): Promise<Record<string, any>> => {
  const response = await request.post('/ai/analyze/portfolio', data);
  return response.data.data;
};

/**
 * 市场分析
 */
export const analyzeMarket = async (
  data: MarketAnalysisRequest
): Promise<Record<string, any>> => {
  const response = await request.post('/ai/analyze/market', data);
  return response.data.data;
};

/**
 * 技术指标分析
 */
export const analyzeIndicators = async (
  data: IndicatorAnalysisRequest
): Promise<Record<string, any>> => {
  const response = await request.post('/ai/analyze/indicators', data);
  return response.data.data;
};

/**
 * 风险评估
 */
export const assessRisk = async (
  data: RiskAssessmentRequest
): Promise<Record<string, any>> => {
  const response = await request.post('/ai/assess/risk', data);
  return response.data.data;
};

/**
 * 策略优化
 */
export const optimizeStrategy = async (
  data: StrategyOptimizationRequest
): Promise<Record<string, any>> => {
  const response = await request.post('/ai/optimize/strategy', data);
  return response.data.data;
};

// ==================== 流式响应API ====================

/**
 * 流式AI分析
 */
export const analyzeStream = async (
  data: AIAnalyzeRequest,
  onChunk: (chunk: string) => void,
  onComplete?: () => void,
  onError?: (error: Error) => void
): Promise<void> => {
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ai/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        ...data,
        stream: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body is not readable');
    }

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        onComplete?.();
        break;
      }

      const chunk = decoder.decode(value);
      onChunk(chunk);
    }
  } catch (error) {
    onError?.(error as Error);
    throw error;
  }
};

/**
 * 流式聊天
 */
export const chatStream = async (
  data: ChatRequest,
  onChunk: (chunk: string) => void,
  onComplete?: () => void,
  onError?: (error: Error) => void
): Promise<void> => {
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        ...data,
        stream: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body is not readable');
    }

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        onComplete?.();
        break;
      }

      const chunk = decoder.decode(value);
      onChunk(chunk);
    }
  } catch (error) {
    onError?.(error as Error);
    throw error;
  }
};

// ==================== 聊天API ====================

/**
 * 非流式聊天
 */
export const chat = async (data: ChatRequest): Promise<{ answer: string }> => {
  const response = await request.post('/ai/chat', data);
  return response.data.data;
};

// ==================== 辅助API ====================

/**
 * 健康检查
 */
export const healthCheck = async (): Promise<HealthCheckResponse> => {
  const response = await request.get('/ai/health');
  return response.data.data;
};

/**
 * 获取模板列表
 */
export const getTemplates = async (): Promise<Record<string, string>> => {
  const response = await request.get('/ai/templates');
  return response.data.data;
};

// ==================== 快速问题模板 ====================

export const QUICK_QUESTIONS = [
  {
    id: 1,
    question: '什么是移动平均线？',
    category: '技术指标',
  },
  {
    id: 2,
    question: '如何判断买入信号？',
    category: '交易策略',
  },
  {
    id: 3,
    question: '什么是MACD指标？',
    category: '技术指标',
  },
  {
    id: 4,
    question: '如何控制投资风险？',
    category: '风险管理',
  },
  {
    id: 5,
    question: '什么是RSI指标？',
    category: '技术指标',
  },
  {
    id: 6,
    question: '如何设置止损？',
    category: '风险管理',
  },
];

// ==================== 默认导出 ====================

export default {
  analyze,
  analyzePortfolio,
  analyzeMarket,
  analyzeIndicators,
  assessRisk,
  optimizeStrategy,
  analyzeStream,
  chat,
  chatStream,
  healthCheck,
  getTemplates,
  QUICK_QUESTIONS,
};