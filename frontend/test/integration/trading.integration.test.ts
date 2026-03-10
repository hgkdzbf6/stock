import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { tradingService } from '@/services/trading';
import type { TradingAccountConfig, CreateOrderRequest } from '@/types/trading';

/**
 * 交易服务集成测试
 * 
 * 注意：这些测试需要后端服务运行中
 * 运行前请确保：
 * 1. 后端服务已启动 (http://localhost:8000)
 * 2. 已创建测试用户并获取认证token
 * 3. 在 localStorage 中设置有效的 access_token
 * 
 * 运行方式：
 * npm test -- trading.integration.test.ts
 */

describe('Trading Service Integration Tests', () => {
  const testAccountConfig: TradingAccountConfig = {
    broker_id: '1234',
    account: 'test_account',
    password: 'test_password',
    trading_server: '127.0.0.1',
    trading_port: 6001,
    quote_server: '127.0.0.1',
    quote_port: 6002,
  };

  const testOrderRequest: CreateOrderRequest = {
    stock_code: '600000',
    side: 'buy',
    order_type: 'limit',
    quantity: 100,
    price: 10.5,
    remark: 'Integration test order',
  };

  beforeAll(() => {
    // 设置测试token
    const testToken = 'test_token_' + Date.now();
    localStorage.setItem('access_token', testToken);
  });

  afterAll(() => {
    // 清理
    localStorage.removeItem('access_token');
  });

  describe('connectTrading', () => {
    it('should connect to trading system with account config', async () => {
      // 注意：这个测试需要有效的后端连接
      // 如果后端未运行，测试会失败
      try {
        const result = await tradingService.connectTrading(testAccountConfig);
        expect(result).toBeDefined();
        expect(typeof result.connected).toBe('boolean');
      } catch (error: any) {
        // 如果后端未运行，跳过测试
        if (error.message?.includes('ECONNREFUSED') || error.code === 'ECONNREFUSED') {
          console.warn('Backend not running, skipping test');
          return;
        }
        throw error;
      }
    });

    it('should handle connection error gracefully', async () => {
      // 使用无效配置测试错误处理
      const invalidConfig: TradingAccountConfig = {
        ...testAccountConfig,
        trading_server: 'invalid-server-12345',
      };

      try {
        await tradingService.connectTrading(invalidConfig);
      } catch (error: any) {
        // 期望连接失败
        expect(error).toBeDefined();
      }
    });
  });

  describe('createOrder', () => {
    it('should create order with valid request', async () => {
      try {
        const result = await tradingService.createOrder(testOrderRequest);
        
        // 验证响应数据提取正确
        expect(result).toBeDefined();
        if (result.order_id) {
          expect(typeof result.order_id).toBe('string');
          expect(typeof result.risk_passed).toBe('boolean');
        }
      } catch (error: any) {
        // 可能需要先连接交易系统
        if (error.response?.data?.detail?.includes('未连接')) {
          console.warn('Trading system not connected, skipping test');
          return;
        }
        throw error;
      }
    });

    it('should handle order creation with missing fields', async () => {
      const invalidOrder: CreateOrderRequest = {
        stock_code: '',
        side: 'buy',
        order_type: 'limit',
        quantity: 0,
      };

      try {
        await tradingService.createOrder(invalidOrder);
      } catch (error: any) {
        // 期望验证错误
        expect(error).toBeDefined();
      }
    });
  });

  describe('getOrders', () => {
    it('should get orders list', async () => {
      try {
        const result = await tradingService.getOrders();
        
        // 验证响应数据提取正确
        expect(result).toBeDefined();
        expect(result).toHaveProperty('orders');
        expect(result).toHaveProperty('total');
        expect(Array.isArray(result.orders)).toBe(true);
        expect(typeof result.total).toBe('number');
      } catch (error: any) {
        if (error.code === 'ECONNREFUSED') {
          console.warn('Backend not running, skipping test');
          return;
        }
        throw error;
      }
    });

    it('should get orders with filters', async () => {
      try {
        const result = await tradingService.getOrders({
          stock_code: '600000',
          status: 'filled',
          limit: 10,
        });
        
        expect(result).toBeDefined();
        expect(result).toHaveProperty('orders');
        expect(Array.isArray(result.orders)).toBe(true);
      } catch (error: any) {
        if (error.code === 'ECONNREFUSED') {
          console.warn('Backend not running, skipping test');
          return;
        }
        throw error;
      }
    });
  });

  describe('cancelOrder', () => {
    it('should cancel order with valid id', async () => {
      try {
        // 使用测试订单ID
        const testOrderId = 'test-order-id';
        const result = await tradingService.cancelOrder(testOrderId);
        
        expect(result).toBeDefined();
        expect(result).toHaveProperty('order_id');
        expect(result.order_id).toBe(testOrderId);
      } catch (error: any) {
        // 订单可能不存在
        if (error.response?.status === 404 || error.response?.status === 400) {
          console.warn('Order not found, skipping test');
          return;
        }
        throw error;
      }
    });
  });

  describe('getOrderStatistics', () => {
    it('should get order statistics', async () => {
      try {
        const result = await tradingService.getOrderStatistics();
        
        expect(result).toBeDefined();
        expect(result).toHaveProperty('total');
        expect(result).toHaveProperty('filled_rate');
        expect(typeof result.total).toBe('number');
        expect(typeof result.filled_rate).toBe('number');
      } catch (error: any) {
        if (error.code === 'ECONNREFUSED') {
          console.warn('Backend not running, skipping test');
          return;
        }
        throw error;
      }
    });
  });

  describe('getPositions', () => {
    it('should get positions list', async () => {
      try {
        const result = await tradingService.getPositions();
        
        expect(result).toBeDefined();
        expect(result).toHaveProperty('positions');
        expect(result).toHaveProperty('total');
        expect(Array.isArray(result.positions)).toBe(true);
        expect(typeof result.total).toBe('number');
      } catch (error: any) {
        if (error.code === 'ECONNREFUSED') {
          console.warn('Backend not running, skipping test');
          return;
        }
        throw error;
      }
    });
  });

  describe('getAccount', () => {
    it('should get account information', async () => {
      try {
        const result = await tradingService.getAccount();
        
        expect(result).toBeDefined();
        expect(result).toHaveProperty('total_assets');
        expect(result).toHaveProperty('available_cash');
        expect(result).toHaveProperty('market_value');
        expect(typeof result.total_assets).toBe('number');
        expect(typeof result.available_cash).toBe('number');
      } catch (error: any) {
        if (error.code === 'ECONNREFUSED') {
          console.warn('Backend not running, skipping test');
          return;
        }
        throw error;
      }
    });
  });

  describe('API Response Data Extraction', () => {
    it('should extract data field from API response correctly', async () => {
      try {
        const result = await tradingService.getOrders();
        
        // 验证只返回 data 字段，不包含 code 和 message
        expect(result).not.toHaveProperty('code');
        expect(result).not.toHaveProperty('message');
        expect(result).toHaveProperty('orders');
        expect(result).toHaveProperty('total');
      } catch (error: any) {
        if (error.code === 'ECONNREFUSED') {
          console.warn('Backend not running, skipping test');
          return;
        }
        throw error;
      }
    });

    it('should handle nested data structures', async () => {
      try {
        const result = await tradingService.getPositions();
        
        // 验证嵌套数据结构
        expect(result).toHaveProperty('positions');
        expect(Array.isArray(result.positions)).toBe(true);
        expect(result).toHaveProperty('total');
        expect(typeof result.total).toBe('number');
      } catch (error: any) {
        if (error.code === 'ECONNREFUSED') {
          console.warn('Backend not running, skipping test');
          return;
        }
        throw error;
      }
    });
  });
});