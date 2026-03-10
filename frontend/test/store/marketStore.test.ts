import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useMarketStore } from '@/store/marketStore';
import { marketService } from '@services/market';

vi.mock('@services/market', () => ({
  marketService: {
    getQuote: vi.fn(),
    getBatchQuotes: vi.fn(),
  },
}));

describe('useMarketStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useMarketStore.setState({
      quotes: {},
      isLoading: false,
      error: null,
    });
  });

  it('stores quote from getQuote direct response', async () => {
    const code = '600000';
    const quote = {
      stock_code: code,
      price: 10.5,
      change: 0.2,
      change_pct: 1.94,
      open: 10.3,
      high: 10.7,
      low: 10.2,
      volume: 100000,
      timestamp: '2026-03-07T10:00:00',
    };

    vi.mocked(marketService.getQuote).mockResolvedValue(quote as any);

    await useMarketStore.getState().fetchQuote(code);

    const state = useMarketStore.getState();
    expect(state.quotes[code]).toEqual(quote);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('stores batch quotes when response is array', async () => {
    const quotes = [
      {
        stock_code: '600000',
        price: 10,
        change: 0,
        change_pct: 0,
        open: 10,
        high: 10,
        low: 10,
        volume: 1,
        timestamp: '2026-03-07T10:00:00',
      },
      {
        stock_code: '000001',
        price: 12,
        change: 1,
        change_pct: 9,
        open: 11,
        high: 12,
        low: 10,
        volume: 2,
        timestamp: '2026-03-07T10:00:00',
      },
    ];

    vi.mocked(marketService.getBatchQuotes).mockResolvedValue(quotes as any);

    await useMarketStore.getState().fetchBatchQuotes('600000,000001');

    const state = useMarketStore.getState();
    expect(Object.keys(state.quotes)).toHaveLength(2);
    expect(state.quotes['600000'].price).toBe(10);
    expect(state.quotes['000001'].price).toBe(12);
  });

  it('stores batch quotes when response has items field', async () => {
    const quotes = [
      {
        stock_code: '300750',
        price: 150,
        change: -2,
        change_pct: -1.3,
        open: 152,
        high: 153,
        low: 149,
        volume: 3,
        timestamp: '2026-03-07T10:00:00',
      },
    ];

    vi.mocked(marketService.getBatchQuotes).mockResolvedValue({ items: quotes } as any);

    await useMarketStore.getState().fetchBatchQuotes('300750');

    const state = useMarketStore.getState();
    expect(state.quotes['300750']).toEqual(quotes[0]);
    expect(state.isLoading).toBe(false);
  });
});
