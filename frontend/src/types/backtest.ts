export interface BacktestMetric {
  total_return: number;          // 总收益率
  annual_return: number;         // 年化收益率
  max_drawdown: number;          // 最大回撤
  sharpe_ratio: number;          // 夏普比率
  win_rate: number;              // 胜率
  trade_count: number;           // 交易次数
  profit_loss_ratio: number;     // 盈亏比
  volatility: number;            // 波动率
  calmar_ratio: number;          // 卡尔马比率
  max_single_profit: number;     // 单笔最大盈利
}

export interface TradeRecord {
  id: string;
  open_date: string;             // 开仓时间
  close_date: string;            // 平仓时间
  type: '买入' | '卖出' | '多' | '空';
  open_price: number;            // 开仓价格
  close_price: number;           // 平仓价格
  profit: number;                // 盈亏金额
  profit_pct: number;            // 盈亏比例
  amount: number;                // 交易金额
  status: string;                // 状态
}

export interface EquityPoint {
  date: string;                  // 时间点
  strategy_value: number;        // 策略净值
  benchmark_value: number;       // 基准净值
  drawdown: number;              // 当前回撤
  indicator?: number;            // 辅助指标
  open?: number;                 // 开盘价
  high?: number;                 // 最高价
  low?: number;                  // 最低价
  close?: number;                // 收盘价
}

export interface BacktestResult {
  id: string;
  strategy_name: string;
  stock_code: string;
  start_date: string;
  end_date: string;
  create_time: string;
  frequency: string;
  initial_capital: number;
  final_capital: number;
  metrics: BacktestMetric;
  trades: TradeRecord[];
  equity_curve: EquityPoint[];
}
