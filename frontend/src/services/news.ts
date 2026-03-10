/**
 * 新闻服务
 */
import axios from 'axios';
import {
  NewsItem,
  FundamentalsData,
  FundamentalsSummary,
  FetchStockNewsRequest,
  FetchSectorNewsRequest,
  NewsResponse
} from '../types/news';
import { authService } from './auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * 获取新闻服务
 * 
 * 注意：新闻API使用公共端点（/public/news），不需要用户认证
 * 这样可以在未登录状态下也能获取新闻，提升用户体验
 */
export const newsService = {
  /**
   * 健康检查（公共端点，不需要认证）
   */
  async healthCheck(): Promise<{ status: string; sources: any[] }> {
    const response = await axios.get(`${API_BASE_URL}/public/news/health`);
    return response.data.data;
  },

  /**
   * 检查新闻源健康状态
   */
  async checkSourceHealth(): Promise<{ status: string; sources: any[] }> {
    const response = await axios.get(`${API_BASE_URL}/public/news/health`);
    return response.data.data;
  },

  /**
   * 获取股票新闻（公共端点，不需要认证）
   */
  async fetchStockNews(request: FetchStockNewsRequest): Promise<NewsResponse> {
    const response = await axios.post(`${API_BASE_URL}/public/news/fetch/stock`, request);
    return response.data.data;
  },

  /**
   * 获取板块新闻（公共端点，不需要认证）
   */
  async fetchSectorNews(request: FetchSectorNewsRequest): Promise<NewsResponse> {
    const response = await axios.post(`${API_BASE_URL}/public/news/fetch/sector`, request);
    return response.data.data;
  },

  /**
   * 总结基本面信息（需要认证）
   */
  async summarizeFundamentals(
    stockCode: string,
    stockName: string,
    fundamentals: FundamentalsData
  ): Promise<FundamentalsSummary> {
    const response = await axios.post(
      `${API_BASE_URL}/news/summarize/fundamentals`,
      {
        stock_code: stockCode,
        stock_name: stockName,
        fundamentals
      },
      {
        headers: authService.getAuthHeader()
      }
    );
    return response.data.data;
  },

  /**
   * 格式化新闻用于舆情分析（公共端点，不需要认证）
   */
  async formatNewsForSentiment(
    newsList: NewsItem[],
    fundamentals?: FundamentalsData
  ): Promise<NewsResponse> {
    const response = await axios.post(
      `${API_BASE_URL}/public/news/format`,
      {
        news_list: newsList,
        fundamentals
      }
    );
    return response.data.data;
  },

  /**
   * 一键情绪分析（公共端点，不需要认证）
   */
  async analyzeSentiment(request: {
    stock_code: string;
    stock_name: string;
    sector_name?: string;
    news_list: any[];
  }): Promise<any> {
    const response = await axios.post(
      `${API_BASE_URL}/public/news/analyze/sentiment`,
      request
    );
    return response.data.data;
  }
};
