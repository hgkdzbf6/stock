/** 常量定义 */

/** 频率选项 */
export const FREQUENCY_OPTIONS = [
  { label: '1分钟', value: '1min' },
  { label: '5分钟', value: '5min' },
  { label: '15分钟', value: '15min' },
  { label: '30分钟', value: '30min' },
  { label: '60分钟', value: '60min' },
  { label: '日线', value: 'daily' },
];

/** 策略类型 */
export const STRATEGY_TYPES = [
  { label: '双均线(MA)', value: 'MA' },
  { label: 'EMA', value: 'EMA' },
  { label: 'RSI', value: 'RSI' },
  { label: 'MACD', value: 'MACD' },
  { label: '布林带(BOLL)', value: 'BOLL' },
  { label: 'KDJ', value: 'KDJ' },
  { label: 'Dual Thrust', value: 'DualThrust' },
  { label: '网格', value: 'Grid' },
  { label: '均值回归', value: 'MeanReversion' },
  { label: '趋势跟随', value: 'TrendFollowing' },
  { label: 'Williams R', value: 'WilliamsR' },
];

/** 技术指标 */
export const INDICATORS = [
  { label: 'MA均线', value: 'MA' },
  { label: 'BOLL布林带', value: 'BOLL' },
  { label: 'RSI', value: 'RSI' },
  { label: 'MACD', value: 'MACD' },
  { label: 'KDJ', value: 'KDJ' },
];

/** 分页大小选项 */
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

/** 默认分页大小 */
export const DEFAULT_PAGE_SIZE = 20;

/** 默认初始资金 */
export const DEFAULT_INITIAL_CAPITAL = 100000;

/** 主题颜色 */
export const THEME_COLORS = {
  primary: '#1890ff',
  success: '#52c41a',
  warning: '#faad14',
  error: '#f5222d',
  up: '#f5222d',    // 涨 - 红色
  down: '#52c41a',  // 跌 - 绿色
  flat: '#8c8c8c',  // 平
};
