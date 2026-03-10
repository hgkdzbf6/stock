/** 交易相关类型定义 */

/** 订单方向 */
export enum OrderSide {
  BUY = 'buy',
  SELL = 'sell',
}

/** 订单类型 */
export enum OrderType {
  MARKET = 'market', // 市价单
  LIMIT = 'limit', // 限价单
  STOP = 'stop', // 止损单
  STOP_LIMIT = 'stop_limit', // 止损限价单
}

/** 订单状态 */
export enum OrderStatus {
  PENDING = 'pending', // 待提交
  SUBMITTED = 'submitted', // 已提交
  PARTIAL_FILLED = 'partial_filled', // 部分成交
  FILLED = 'filled', // 全部成交
  CANCELLED = 'cancelled', // 已撤销
  REJECTED = 'rejected', // 已拒绝
}

/** 订单 */
export interface Order {
  id: string;
  stock_code: string;
  side: OrderSide;
  order_type: OrderType;
  quantity: number;
  price?: number;
  stop_price?: number;
  filled_quantity: number;
  avg_fill_price?: number;
  status: OrderStatus;
  commission?: number;
  remark?: string;
  broker_order_id?: string;
  created_at: string;
  submitted_at?: string;
  filled_at?: string;
  cancelled_at?: string;
}

/** 持仓 */
export interface Position {
  id: string;
  stock_code: string;
  quantity: number;
  available_quantity: number;
  cost_price: number;
  current_price: number;
  market_value: number;
  pnl_amount: number;
  pnl_ratio: number;
}

/** 账户 */
export interface Account {
  id: string;
  user_id: number;
  broker: string;
  broker_account_id: string;
  total_assets: number;
  available_cash: number;
  frozen_cash: number;
  market_value: number;
  pnl_amount: number;
  pnl_ratio: number;
}

/** 风险等级 */
export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

/** 风险检查结果 */
export interface RiskCheckResult {
  passed: boolean;
  message: string;
  level: RiskLevel;
}

/** 订单统计 */
export interface OrderStatistics {
  total: number;
  pending: number;
  submitted: number;
  partial_filled: number;
  filled: number;
  cancelled: number;
  rejected: number;
  filled_rate: number;
}

/** 持仓汇总 */
export interface PositionSummary {
  total_positions: number;
  total_market_value: number;
  total_pnl_amount: number;
  avg_pnl_ratio: number;
}

/** 账户汇总 */
export interface AccountSummary {
  total_users: number;
  total_assets: number;
  total_market_value: number;
  total_pnl_amount: number;
}

/** 风险汇总 */
export interface RiskSummary {
  active_orders: number;
  total_exposure: number;
  risk_level: RiskLevel;
  warnings: string[];
}

/** 创建订单请求 */
export interface CreateOrderRequest {
  stock_code: string;
  side: OrderSide;
  order_type: OrderType;
  quantity: number;
  price?: number;
  stop_price?: number;
  remark?: string;
}

/** 创建订单响应 */
export interface CreateOrderResponse {
  order_id: string;
  broker_order_id?: string;
  status?: OrderStatus;
  risk_passed: boolean;
  risk_level?: RiskLevel;
}

/** 获取订单列表响应 */
export interface GetOrdersResponse {
  orders: Order[];
  total: number;
}

/** 获取持仓列表响应 */
export interface GetPositionsResponse {
  positions: Position[];
  total: number;
}

/** 交易账号配置 */
export interface TradingAccountConfig {
  broker_id: string;
  account: string;
  password: string;
  trading_server: string;
  trading_port: number;
  quote_server: string;
  quote_port: number;
}
