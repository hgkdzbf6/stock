/** 交易服务 */
import apiClient from './api';
import type {
  CreateOrderRequest,
  CreateOrderResponse,
  GetOrdersResponse,
  GetPositionsResponse,
  Order,
  OrderStatus,
  OrderStatistics,
  Position,
  PositionSummary,
  Account,
  AccountSummary,
  RiskSummary,
  TradingAccountConfig,
} from '../types/trading';

class TradingService {
  /** 连接交易系统 */
  async connectTrading(config: TradingAccountConfig): Promise<{ connected: boolean }> {
    const response: any = await apiClient.post('/trading/connect', null, {
      params: config,
    });
    return response.data;
  }

  /** 创建订单 */
  async createOrder(request: CreateOrderRequest): Promise<CreateOrderResponse> {
    const response: any = await apiClient.post('/trading/orders', {
      stock_code: request.stock_code,
      side: request.side,
      order_type: request.order_type,
      quantity: request.quantity,
      price: request.price,
      stop_price: request.stop_price,
      remark: request.remark,
    });
    return response.data;
  }

  /** 获取订单列表 */
  async getOrders(params?: {
    stock_code?: string;
    status?: OrderStatus;
    limit?: number;
  }): Promise<GetOrdersResponse> {
    const response: any = await apiClient.get('/trading/orders', {
      params,
    });
    return response.data;
  }

  /** 撤销订单 */
  async cancelOrder(orderId: string): Promise<{ order_id: string }> {
    const response: any = await apiClient.delete(`/trading/orders/${orderId}`);
    return response.data;
  }

  /** 获取订单统计 */
  async getOrderStatistics(): Promise<OrderStatistics> {
    const response: any = await apiClient.get('/trading/orders/statistics');
    return response.data;
  }

  /** 获取持仓列表 */
  async getPositions(): Promise<GetPositionsResponse> {
    const response: any = await apiClient.get('/trading/positions');
    return response.data;
  }

  /** 获取持仓汇总 */
  async getPositionSummary(): Promise<PositionSummary> {
    const response: any = await apiClient.get('/trading/positions/summary');
    return response.data;
  }

  /** 获取账户信息 */
  async getAccount(): Promise<Account> {
    const response: any = await apiClient.get('/trading/account');
    return response.data;
  }

  /** 获取账户汇总 */
  async getAccountSummary(): Promise<AccountSummary> {
    const response: any = await apiClient.get('/trading/account/summary');
    return response.data;
  }

  /** 获取风险汇总 */
  async getRiskSummary(): Promise<RiskSummary> {
    const response: any = await apiClient.get('/trading/risk/summary');
    return response.data;
  }
}

// 导出单例
export const tradingService = new TradingService();

export default tradingService;