/** 市场行情状态管理 */
import { create } from 'zustand';
import type { Quote } from '@types/api';
import { marketService } from '@services/market';

interface MarketState {
  quotes: Record<string, Quote>;
  isLoading: boolean;
  error: string | null;

  fetchQuote: (code: string) => Promise<void>;
  fetchBatchQuotes: (codes: string) => Promise<void>;
  updateQuote: (code: string, quote: Quote) => void;
}

export const useMarketStore = create<MarketState>((set) => ({
  quotes: {},
  isLoading: false,
  error: null,

  fetchQuote: async (code: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await marketService.getQuote(code);
      set((state) => ({
        quotes: { ...state.quotes, [code]: response.data },
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || '获取行情失败',
      });
      throw error;
    }
  },

  fetchBatchQuotes: async (codes: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await marketService.getBatchQuotes(codes);
      const quotesMap = response.data.reduce(
        (acc: Record<string, Quote>, quote: Quote) => {
          acc[quote.stock_code] = quote;
          return acc;
        },
        {}
      );
      set((state) => ({
        quotes: { ...state.quotes, ...quotesMap },
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || '获取行情失败',
      });
      throw error;
    }
  },

  updateQuote: (code: string, quote: Quote) => {
    set((state) => ({
      quotes: { ...state.quotes, [code]: quote },
    }));
  },
}));
