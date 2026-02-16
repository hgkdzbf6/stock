/**
 * 图表类型定义
 * 
 * @module frontend/src/types/chart.types
 * @description 定义所有图表相关的数据类型和接口
 * @author System
 * @version 1.0.0
 * @since 2024-02-16
 * 
 * @see {@link ARCHITECTURE_STANDARDS.md}
 */

import * as echarts from 'echarts';

// ==================== K线图类型 ====================

/**
 * K线数据项
 */
export interface KLineDataItem {
  /** 日期 (YYYY-MM-DD 或 YYYY-MM-DD HH:mm:ss) */
  date: string;
  
  /** 开盘价 */
  open: number;
  
  /** 最高价 */
  high: number;
  
  /** 最低价 */
  low: number;
  
  /** 收盘价 */
  close: number;
  
  /** 成交量 */
  volume: number;
  
  /** 成交额 (可选) */
  amount?: number;
  
  /** 涨跌幅 (可选) */
  change_pct?: number;
  
  /** 涨跌额 (可选) */
  change?: number;
}

/**
 * 指标数据
 */
export interface IndicatorData {
  /** MA5均线数据 */
  ma5?: number[];
  
  /** MA10均线数据 */
  ma10?: number[];
  
  /** MA20均线数据 */
  ma20?: number[];
  
  /** MA30均线数据 */
  ma30?: number[];
  
  /** MACD指标数据 */
  macd?: {
    /** DIF线 */
    dif: number[];
    /** DEA线 */
    dea: number[];
    /** MACD柱 */
    macd: number[];
  };
  
  /** KDJ指标数据 */
  kdj?: {
    /** K值 */
    k: number[];
    /** D值 */
    d: number[];
    /** J值 */
    j: number[];
  };
}

/**
 * K线图Props
 */
export interface KLineChartProps {
  /** K线数据 */
  data: KLineDataItem[];
  
  /** 图表标题 */
  title?: string;
  
  /** 图表副标题 */
  subtitle?: string;
  
  /** 图表高度 */
  height?: string;
  
  /** 是否显示成交量 */
  showVolume?: boolean;
  
  /** 指标数据 */
  indicators?: IndicatorData;
  
  /** 图表主题 */
  theme?: 'light' | 'dark';
  
  /** 股票选择回调 */
  onStockSelect?: (stockCode: string) => void;
  
  /** 是否启用全屏 */
  enableFullscreen?: boolean;
  
  /** 加载状态 */
  loading?: boolean;
  
  /** 错误信息 */
  error?: string | null;
}

// ==================== 市场图类型 ====================

/**
 * 市场数据项
 */
export interface MarketDataItem {
  /** 股票代码 */
  code: string;
  
  /** 股票名称 */
  name: string;
  
  /** 当前价格 */
  price: number;
  
  /** 涨跌额 */
  change: number;
  
  /** 涨跌幅 */
  change_pct: number;
  
  /** 开盘价 */
  open: number;
  
  /** 最高价 */
  high: number;
  
  /** 最低价 */
  low: number;
  
  /** 成交量 */
  volume: number;
  
  /** 成交额 */
  amount: number;
  
  /** 市值 */
  market_cap?: number;
  
  /** 时间戳 */
  timestamp: string;
}

/**
 * 市场图Props
 */
export interface MarketChartProps {
  /** 市场数据 */
  data: MarketDataItem[];
  
  /** 图表标题 */
  title?: string;
  
  /** 图表高度 */
  height?: string;
  
  /** 图表主题 */
  theme?: 'light' | 'dark';
  
  /** 数据刷新回调 */
  onRefresh?: () => void;
}

// ==================== 行业图类型 ====================

/**
 * 行业数据项
 */
export interface SectorDataItem {
  /** 行业代码 */
  code: string;
  
  /** 行业名称 */
  name: string;
  
  /** 涨跌幅 */
  change_pct: number;
  
  /** 涨跌额 */
  change: number;
  
  /** 成交额 */
  amount: number;
  
  /** 时间戳 */
  timestamp: string;
}

/**
 * 行业图Props
 */
export interface SectorChartProps {
  /** 行业数据 */
  data: SectorDataItem[];
  
  /** 图表标题 */
  title?: string;
  
  /** 图表高度 */
  height?: string;
  
  /** 图表主题 */
  theme?: 'light' | 'dark';
  
  /** 行业选择回调 */
  onSectorSelect?: (sectorCode: string) => void;
}

// ==================== 通用图表类型 ====================

/**
 * 图表配置选项
 */
export interface ChartOptions {
  /** 标题配置 */
  title?: echarts.TitleComponentOption;
  
  /** 提示框配置 */
  tooltip?: echarts.TooltipComponentOption;
  
  /** 图例配置 */
  legend?: echarts.LegendComponentOption;
  
  /** 网格配置 */
  grid?: echarts.GridComponentOption | echarts.GridComponentOption[];
  
  /** X轴配置 */
  xAxis?: echarts.XAXisComponentOption | echarts.XAXisComponentOption[];
  
  /** Y轴配置 */
  yAxis?: echarts.YAXisComponentOption | echarts.YAXisComponentOption[];
  
  /** 数据缩放配置 */
  dataZoom?: echarts.DataZoomComponentOption | echarts.DataZoomComponentOption[];
  
  /** 系列配置 */
  series?: echarts.SeriesOption | echarts.SeriesOption[];
  
  /** 动画配置 */
  animation?: boolean;
  
  /** 动画时长 */
  animationDuration?: number;
  
  /** 动画缓动函数 */
  animationEasing?: string;
}

/**
 * 图表事件
 */
export interface ChartEvents {
  /** 点击事件 */
  onClick?: (params: any) => void;
  
  /** 鼠标悬停事件 */
  onHover?: (params: any) => void;
  
  /** 图例选择事件 */
  onLegendSelectChanged?: (params: any) => void;
  
  /** 数据缩放事件 */
  onDataZoom?: (params: any) => void;
}

// ==================== API响应类型 ====================

/**
 * 基础API响应
 */
export interface BaseApiResponse<T = any> {
  /** 响应码 */
  code: number;
  
  /** 响应消息 */
  message: string;
  
  /** 响应数据 */
  data?: T;
}

/**
 * 分页API响应
 */
export interface PaginatedApiResponse<T = any> {
  /** 响应码 */
  code: number;
  
  /** 响应消息 */
  message: string;
  
  /** 响应数据 */
  data?: {
    /** 数据列表 */
    items: T[];
    /** 总记录数 */
    total: number;
    /** 当前页码 */
    page: number;
    /** 每页大小 */
    page_size: number;
  };
}

// ==================== 股票信息类型 ====================

/**
 * 股票基本信息
 */
export interface StockInfo {
  /** 股票代码 */
  code: string;
  
  /** 股票名称 */
  name: string;
  
  /** 当前价格 */
  price?: number;
  
  /** 涨跌额 */
  change?: number;
  
  /** 涨跌幅 */
  change_pct?: number;
  
  /** 开盘价 */
  open?: number;
  
  /** 最高价 */
  high?: number;
  
  /** 最低价 */
  low?: number;
  
  /** 成交量 */
  volume?: number;
  
  /** 成交额 */
  amount?: number;
  
  /** 市值 */
  market_cap?: number;
  
  /** 市场类型 */
  market?: string;
  
  /** 更新时间 */
  update_time?: string;
}

// ==================== 导出 ====================

// 所有类型已通过 export interface / export type 声明时导出
