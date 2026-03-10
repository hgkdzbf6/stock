/** 舆情分析服务 */
import apiClient from './api';
import type {
  SentimentAnalysis,
  BatchAnalysisResult,
  SentimentBacktestResult,
  SentimentAggregation,
  AnalyzeSentimentRequest,
  BatchAnalyzeRequest,
  BacktestRequest,
  AggregateRequest,
} from '../types/sentiment';

class SentimentService {
  /** 分析新闻舆情 */
  async analyzeSentiment(request: AnalyzeSentimentRequest): Promise<SentimentAnalysis> {
    const response: any = await apiClient.post('/sentiment/analyze', {
      stock_code: request.stock_code,
      stock_name: request.stock_name,
      sector_name: request.sector_name,
      news_data: request.news_data,
    });
    return response.data;
  }

  /** 批量分析新闻舆情 */
  async batchAnalyze(request: BatchAnalyzeRequest): Promise<BatchAnalysisResult> {
    const response: any = await apiClient.post('/sentiment/analyze/batch', {
      news_items: request.news_items,
      stock_code: request.stock_code,
      stock_name: request.stock_name,
    });
    return response.data;
  }

  /** 回测舆情影响 */
  async backtestSentiment(request: BacktestRequest): Promise<SentimentBacktestResult> {
    const response: any = await apiClient.post('/sentiment/backtest', {
      stock_code: request.stock_code,
      stock_name: request.stock_name,
      start_date: request.start_date,
      end_date: request.end_date,
      sentiment_history: request.sentiment_history,
      price_data: request.price_data,
    });
    return response.data;
  }

  /** 聚合舆情分数 */
  async aggregateSentiment(request: AggregateRequest): Promise<SentimentAggregation> {
    const response: any = await apiClient.post('/sentiment/aggregate', {
      sentiment_scores: request.sentiment_scores,
      weights: request.weights,
    });
    return response.data;
  }

  /** 健康检查 */
  async healthCheck(): Promise<any> {
    const response: any = await apiClient.get('/sentiment/health');
    return response.data;
  }
}

// 导出单例
export const sentimentService = new SentimentService();

export default sentimentService;