/**
 * 新闻服务测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { newsService } from '../../src/services/news';
import axios from 'axios';

vi.mock('axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

// Mock authService
vi.mock('../../src/services/auth', () => ({
  authService: {
    getAuthHeader: vi.fn(() => ({ Authorization: 'Bearer test-token' }))
  }
}));

describe('新闻服务', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('healthCheck', () => {
    it('应该成功进行健康检查', async () => {
      const mockResponse = {
        data: {
          data: {
            status: 'healthy',
            sources: ['财经', '股票', '银行', '科技']
          }
        }
      };

      vi.mocked(axios.get).mockResolvedValue(mockResponse);

      const result = await newsService.healthCheck();

      expect(result).toEqual({
        status: 'healthy',
        sources: ['财经', '股票', '银行', '科技']
      });

      expect(vi.mocked(axios.get)).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/public/news/health'
      );
    });
  });

  describe('fetchStockNews', () => {
    it('应该成功获取股票新闻', async () => {
      const mockRequest = {
        stock_code: '600000',
        stock_name: '浦发银行',
        sector_name: '银行',
        limit: 10
      };

      const mockResponse = {
        data: {
          data: {
            news: [
              {
                id: 'news_001',
                title: '测试新闻',
                content: '新闻内容',
                source: '财经新闻',
                published_time: '2026-02-20T12:00:00'
              }
            ],
            total: 1
          }
        }
      };

      vi.mocked(axios.post).mockResolvedValue(mockResponse);

      const result = await newsService.fetchStockNews(mockRequest);

      expect(result).toEqual({
        news: [
          {
            id: 'news_001',
            title: '测试新闻',
            content: '新闻内容',
            source: '财经新闻',
            published_time: '2026-02-20T12:00:00'
          }
        ],
        total: 1
      });

      expect(vi.mocked(axios.post)).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/public/news/fetch/stock',
        mockRequest
      );
    });
  });

  describe('fetchSectorNews', () => {
    it('应该成功获取板块新闻', async () => {
      const mockRequest = {
        sector_name: '银行',
        limit: 20
      };

      const mockResponse = {
        data: {
          data: {
            news: [
              {
                id: 'news_002',
                title: '银行板块新闻',
                content: '银行新闻内容',
                source: '财经新闻',
                published_time: '2026-02-20T12:00:00'
              }
            ],
            total: 1
          }
        }
      };

      vi.mocked(axios.post).mockResolvedValue(mockResponse);

      const result = await newsService.fetchSectorNews(mockRequest);

      expect(result).toEqual({
        news: [
          {
            id: 'news_002',
            title: '银行板块新闻',
            content: '银行新闻内容',
            source: '财经新闻',
            published_time: '2026-02-20T12:00:00'
          }
        ],
        total: 1
      });

      expect(vi.mocked(axios.post)).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/public/news/fetch/sector',
        mockRequest
      );
    });
  });

  describe('summarizeFundamentals', () => {
    it('应该成功总结基本面信息', async () => {
      const mockFundamentals = {
        market_cap: '5000亿',
        pe_ratio: 5.5,
        pb_ratio: 0.6,
        roe: 12.5,
        revenue: '1800亿',
        net_profit: '200亿',
        revenue_growth: 8.5,
        profit_growth: 15.2,
        dividend_yield: 4.2,
        industry: '银行'
      };

      const mockResponse = {
        data: {
          data: {
            stock_code: '600000',
            stock_name: '浦发银行',
            market_cap: '5000亿',
            pe_ratio: '5.5',
            pb_ratio: '0.6',
            roe: '12.5',
            revenue: '1800亿',
            net_profit: '200亿',
            revenue_growth: '8.5',
            profit_growth: '15.2',
            dividend_yield: '4.2',
            industry: '银行',
            summary_text: '市盈率较低，估值相对便宜；净资产收益率中等，盈利能力尚可；净利润增长率高，成长性好；股息率高，分红回报好'
          }
        }
      };

      vi.mocked(axios.post).mockResolvedValue(mockResponse);

      const result = await newsService.summarizeFundamentals(
        '600000',
        '浦发银行',
        mockFundamentals
      );

      expect(result).toEqual(mockResponse.data.data);

      expect(vi.mocked(axios.post)).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/news/summarize/fundamentals',
        {
          stock_code: '600000',
          stock_name: '浦发银行',
          fundamentals: mockFundamentals
        },
        expect.objectContaining({
          headers: expect.any(Object)
        })
      );
    });
  });

  describe('formatNewsForSentiment', () => {
    it('应该成功格式化新闻用于舆情分析', async () => {
      const mockNewsList = [
        {
          id: 'news_003',
          title: '格式化测试',
          content: '测试内容',
          source: '测试源',
          published_time: '2026-02-20T12:00:00',
          link: 'https://example.com/news/1'
        }
      ];

      const mockFundamentals = {
        market_cap: '5000亿',
        pe_ratio: 5.5
      };

      const mockResponse = {
        data: {
          data: {
            news: [
              {
                id: 'news_003',
                title: '格式化测试',
                content: '测试内容【基本面信息】\n股票代码: 600000\n股票名称: 浦发银行\n市值: 5000亿\n市盈率: 5.5',
                source: '测试源',
                published_time: '2026-02-20T12:00:00',
                url: 'https://example.com/news/1'
              }
            ],
            total: 1
          }
        }
      };

      vi.mocked(axios.post).mockResolvedValue(mockResponse);

      const result = await newsService.formatNewsForSentiment(
        mockNewsList,
        mockFundamentals
      );

      expect(result).toEqual(mockResponse.data.data);

      expect(vi.mocked(axios.post)).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/public/news/format',
        {
          news_list: mockNewsList,
          fundamentals: mockFundamentals
        }
      );
    });

    it('应该在没有基本面数据时格式化新闻', async () => {
      const mockNewsList = [
        {
          id: 'news_004',
          title: '无基本面测试',
          content: '测试内容',
          source: '测试源',
          published_time: '2026-02-20T12:00:00'
        }
      ];

      const mockResponse = {
        data: {
          data: {
            news: [
              {
                id: 'news_004',
                title: '无基本面测试',
                content: '测试内容',
                source: '测试源',
                published_time: '2026-02-20T12:00:00',
                url: ''
              }
            ],
            total: 1
          }
        }
      };

      vi.mocked(axios.post).mockResolvedValue(mockResponse);

      const result = await newsService.formatNewsForSentiment(mockNewsList);

      expect(result).toEqual(mockResponse.data.data);

      expect(vi.mocked(axios.post)).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/public/news/format',
        {
          news_list: mockNewsList,
          fundamentals: undefined
        }
      );
    });
  });
});
