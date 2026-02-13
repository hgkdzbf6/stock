/** 格式化工具 */

/** 格式化百分比 */
export const formatPercent = (value: number, decimals: number = 2): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`;
};

/** 格式化金额 */
export const formatMoney = (value: number, decimals: number = 2): string => {
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

/** 格式化数量 */
export const formatNumber = (value: number): string => {
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`;
  } else if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}万`;
  }
  return value.toLocaleString();
};

/** 格式化日期 */
export const formatDate = (date: string | Date, format: string = 'YYYY-MM-DD'): string => {
  const d = typeof date === 'string' ? new Date(date) : date;

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');

  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
};

/** 格式化时间 */
export const formatTime = (timestamp: string): string => {
  return formatDate(timestamp, 'HH:mm:ss');
};

/** 颜色类名 */
export const getColorClass = (value: number): string => {
  if (value > 0) return 'text-red-500';
  if (value < 0) return 'text-green-500';
  return 'text-gray-500';
};

/** 判断涨跌 */
export const isUp = (value: number): boolean => value > 0;
export const isDown = (value: number): boolean => value < 0;
export const isFlat = (value: number): boolean => value === 0;
