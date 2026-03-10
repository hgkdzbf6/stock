import { describe, it, expect, beforeEach, vi } from 'vitest';
import { tradingService } from '@/services/trading';
import apiClient from '@/services/api';

// Mock apiClient
vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('Trading Service', () => {
  const mockTradingConfig = {
    broker_id: '1234',
    account: 'test_account',
    password: 'test_password',
    trading_server: '127.0.0.1',
    trading_port: 6001,
    quote_server: '127.0.0.1',
    quote_port: 6002,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('connectTrading', () => {
    it('should connect to trading system successfully', async () => {
      const mockResponse = {
        code: 200,
        message: '连接成功',
        data: { connected: true },
      };
      (apiClient.post as any).mockResolvedValue(mockResponse);

      const result = await tradingService.connectTrading(mockTradingConfig as any);

      expect(apiClient.post).toHaveBeenCalledWith('/trading/connect', null, {
        params: mockTradingConfig,
      });
      expect(result).toEqual({ connected: true });
    });

    it('should handle connection failure', async () => {
      (apiClient.post as any).mockRejectedValue(new Error('Connection failed'));

      await expect(tradingService.connectTrading(mockTradingConfig as any)).rejects.toThrow('Connection failed');
    });
  });

  describe('createOrder', () => {
    it('should create order successfully', async () => {
      const mockOrderRequest = {
        stock_code: '600000',
        side: 'buy' as const,
        order_type: 'limit' as const,
        quantity: 100,
        price: 10.5,
        stop_price: null,
        remark: 'test',
      };

      const mockResponse = {
        code: 200,
        message: '订单提交成功',
        data: {
          order_id: '12345',
          broker_order_id: '67890',
          status: 'submitted',
          risk_passed: true,
        },
      };

      (apiClient.post as any).mockResolvedValue(mockResponse);

      const result = await tradingService.createOrder(mockOrderRequest);

      expect(apiClient.post).toHaveBeenCalledWith('/trading/orders', mockOrderRequest);
      expect(result.order_id).toBe('12345');
      expect(result.risk_passed).toBe(true);
    });

    it('should handle order creation failure', async () => {
      const mockOrderRequest = {
        stock_code: '600000',
        side: 'buy' as const,
        order_type: 'limit' as const,
        quantity: 100,
        price: 10.5,
      };

      (apiClient.post as any).mockRejectedValue(new Error('Order creation failed'));

      await expect(tradingService.createOrder(mockOrderRequest)).rejects.toThrow(
        'Order creation failed'
      );
    });

    it('should handle order not passing risk check', async () => {
      const mockOrderRequest = {
        stock_code: '600000',
        side: 'buy' as const,
        order_type: 'limit' as const,
        quantity: 100,
        price: 10.5,
      };

      const mockResponse = {
        code: 400,
        message: '风险检查未通过',
        data: {
          order_id: '12345',
          risk_passed: false,
          risk_level: 'high',
        },
      };

      (apiClient.post as any).mockResolvedValue(mockResponse);

      const result = await tradingService.createOrder(mockOrderRequest);

      expect(result.risk_passed).toBe(false);
      expect(result.risk_level).toBe('high');
    });
  });

  describe('getOrders', () => {
    it('should get orders list successfully', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          orders: [
            {
              id: '12345',
              stock_code: '600000',
              side: 'buy',
              order_type: 'limit',
              quantity: 100,
              price: 10.5,
              filled_quantity: 50,
              status: 'partial_filled',
              created_at: '2024-01-01T00:00:00',
            },
          ],
          total: 1,
        },
      };

      (apiClient.get as any).mockResolvedValue(mockResponse);

      const result = await tradingService.getOrders();

      expect(apiClient.get).toHaveBeenCalledWith('/trading/orders', { params: undefined });
      expect(result.orders).toHaveLength(1);
      expect(result.total).toBe(1);
      expect(result.orders[0].id).toBe('12345');
    });

    it('should get orders with filters', async () => {
      const params = {
        stock_code: '600000',
        status: 'filled' as const,
        limit: 10,
      };

      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          orders: [],
          total: 0,
        },
      };

      (apiClient.get as any).mockResolvedValue(mockResponse);

      await tradingService.getOrders(params);

      expect(apiClient.get).toHaveBeenCalledWith('/trading/orders', { params });
    });

    it('should handle get orders failure', async () => {
      (apiClient.get as any).mockRejectedValue(new Error('Get orders failed'));

      await expect(tradingService.getOrders()).rejects.toThrow('Get orders failed');
    });
  });

  describe('cancelOrder', () => {
    it('should cancel order successfully', async () => {
      const orderId = '12345';
      const mockResponse = {
        code: 200,
        message: '订单撤销成功',
        data: { order_id: orderId },
      };

      (apiClient.delete as any).mockResolvedValue(mockResponse);

      const result = await tradingService.cancelOrder(orderId);

      expect(apiClient.delete).toHaveBeenCalledWith(`/trading/orders/${orderId}`);
      expect(result.order_id).toBe(orderId);
    });

    it('should handle cancel order failure', async () => {
      const orderId = '12345';
      (apiClient.delete as any).mockRejectedValue(new Error('Cancel order failed'));

      await expect(tradingService.cancelOrder(orderId)).rejects.toThrow('Cancel order failed');
    });
  });

  describe('getOrderStatistics', () => {
    it('should get order statistics successfully', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          total: 10,
          pending: 1,
          submitted: 2,
          partial_filled: 1,
          filled: 5,
          cancelled: 1,
          rejected: 0,
          filled_rate: 0.5,
        },
      };

      (apiClient.get as any).mockResolvedValue(mockResponse);

      const result = await tradingService.getOrderStatistics();

      expect(apiClient.get).toHaveBeenCalledWith('/trading/orders/statistics');
      expect(result.total).toBe(10);
      expect(result.filled_rate).toBe(0.5);
    });

    it('should handle get statistics failure', async () => {
      (apiClient.get as any).mockRejectedValue(new Error('Get statistics failed'));

      await expect(tradingService.getOrderStatistics()).rejects.toThrow('Get statistics failed');
    });
  });

  describe('getPositions', () => {
    it('should get positions list successfully', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          positions: [
            {
              id: '1',
              stock_code: '600000',
              quantity: 100,
              available_quantity: 100,
              cost_price: 10.5,
              current_price: 11.0,
              market_value: 1100,
              pnl_amount: 50,
              pnl_ratio: 0.0476,
            },
          ],
          total: 1,
        },
      };

      (apiClient.get as any).mockResolvedValue(mockResponse);

      const result = await tradingService.getPositions();

      expect(apiClient.get).toHaveBeenCalledWith('/trading/positions');
      expect(result.positions).toHaveLength(1);
      expect(result.positions[0].stock_code).toBe('600000');
    });

    it('should handle get positions failure', async () => {
      (apiClient.get as any).mockRejectedValue(new Error('Get positions failed'));

      await expect(tradingService.getPositions()).rejects.toThrow('Get positions failed');
    });
  });

  describe('getAccount', () => {
    it('should get account information successfully', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          id: '1',
          user_id: 1,
          total_assets: 1000000,
          available_cash: 500000,
          frozen_cash: 0,
          market_value: 500000,
          pnl_amount: 0,
          pnl_ratio: 0,
        },
      };

      (apiClient.get as any).mockResolvedValue(mockResponse);

      const result = await tradingService.getAccount();

      expect(apiClient.get).toHaveBeenCalledWith('/trading/account');
      expect(result.total_assets).toBe(1000000);
      expect(result.available_cash).toBe(500000);
    });

    it('should handle get account failure', async () => {
      (apiClient.get as any).mockRejectedValue(new Error('Get account failed'));

      await expect(tradingService.getAccount()).rejects.toThrow('Get account failed');
    });
  });

  describe('API Response Data Extraction', () => {
    it('should correctly extract data field from API response', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: { connected: true },
      };

      (apiClient.post as any).mockResolvedValue(mockResponse);

      const result = await tradingService.connectTrading(mockTradingConfig as any);

      // Verify that the service extracts the 'data' field
      expect(result).not.toHaveProperty('code');
      expect(result).not.toHaveProperty('message');
      expect(result).toHaveProperty('connected', true);
    });

    it('should handle nested data structure correctly', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          orders: [{ id: '1', stock_code: '600000' }],
          total: 1,
        },
      };

      (apiClient.get as any).mockResolvedValue(mockResponse);

      const result = await tradingService.getOrders();

      expect(result).toHaveProperty('orders');
      expect(result).toHaveProperty('total');
      expect(result.orders).toEqual([{ id: '1', stock_code: '600000' }]);
    });
  });
});
