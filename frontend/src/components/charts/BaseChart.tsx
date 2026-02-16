/**
 * 图表组件基类
 * 
 * @module frontend/src/components/charts/BaseChart
 * @description 提供所有图表组件的基础功能，包括初始化、更新、销毁等
 * @author System
 * @version 1.0.0
 * @since 2024-02-16
 * 
 * @example
 * ```tsx
 * <BaseChart
 *   data={chartData}
 *   title="示例图表"
 *   onRefresh={handleRefresh}
 * />
 * ```
 * 
 * @features
 * - 自动初始化ECharts实例
 * - 响应式图表大小调整
 * - 主题切换支持
 * - 加载状态和错误处理
 * - 统一的控制栏
 * 
 * @dependencies
 * - react
 * - echarts
 * - antd
 * 
 * @see {@link ARCHITECTURE_STANDARDS.md}
 */

import React, { FC, useEffect, useRef, useState, useCallback, ReactNode } from 'react';
import * as echarts from 'echarts';
import { Button, Space, Tooltip } from 'antd';
import { ZoomInOutlined, ZoomOutOutlined, UndoOutlined, ReloadOutlined, FullscreenOutlined, FullscreenExitOutlined } from '@ant-design/icons';

// ==================== 类型定义 ====================

/**
 * 图表数据项类型
 */
export interface ChartDataItem {
  /** 数据标识 */
  id?: string;
  /** 数据值 */
  value?: number;
  /** 时间戳 */
  timestamp?: string;
  /** 其他自定义字段 */
  [key: string]: any;
}

/**
 * 图表主题类型
 */
export type ChartTheme = 'light' | 'dark';

/**
 * 图表控制栏配置
 */
export interface ChartToolbarConfig {
  /** 是否显示缩放控制 */
  showZoom?: boolean;
  /** 是否显示重置按钮 */
  showReset?: boolean;
  /** 是否显示刷新按钮 */
  showRefresh?: boolean;
  /** 是否显示全屏按钮 */
  showFullscreen?: boolean;
  /** 自定义控制按钮 */
  customButtons?: ReactNode;
}

/**
 * 图表组件基础Props
 */
export interface BaseChartProps {
  /** 数据源 */
  data: ChartDataItem[];
  
  /** 图表标题 */
  title?: string;
  
  /** 图表副标题 */
  subtitle?: string;
  
  /** 图表高度，默认为"600px" */
  height?: string;
  
  /** 图表主题，默认为"light" */
  theme?: ChartTheme;
  
  /** 是否显示工具栏，默认为true */
  showToolbar?: boolean;
  
  /** 工具栏配置 */
  toolbarConfig?: ChartToolbarConfig;
  
  /** 数据加载状态 */
  loading?: boolean;
  
  /** 错误信息 */
  error?: string | null;
  
  /** 数据刷新回调 */
  onRefresh?: () => void;
  
  /** 数据更新回调 */
  onUpdate?: (data: ChartDataItem[]) => void;
  
  /** 自定义图表配置 */
  getChartOption?: (data: ChartDataItem[]) => echarts.EChartsOption;
  
  /** 图表容器样式 */
  containerStyle?: React.CSSProperties;
  
  /** 是否启用全屏功能，默认为true */
  enableFullscreen?: boolean;
}

// ==================== 常量定义 ====================

/** 默认配置 */
export const DEFAULT_CHART_CONFIG = {
  HEIGHT: '600px',
  THEME: 'light' as ChartTheme,
  SHOW_TOOLBAR: true,
  ENABLE_FULLSCREEN: true,
  ANIMATION_DURATION: 1000,
  ANIMATION_EASING: 'cubicOut' as const
} as const;

/** 颜色常量 */
export const CHART_COLORS = {
  PRIMARY: '#1890ff',
  SUCCESS: '#52c41a',
  WARNING: '#faad14',
  ERROR: '#f5222d',
  INFO: '#1890ff',
  CANDLE_UP: '#ef5350',
  CANDLE_DOWN: '#26a69a',
  MA5: '#f39c12',
  MA10: '#e74c3c',
  MA20: '#9b59b6',
  MA30: '#3498db'
} as const;

// ==================== 主组件 ====================

/**
 * 图表组件基类
 * 
 * 提供所有图表组件的通用功能，子类可以通过getChartOption自定义图表配置
 */
const BaseChart: FC<BaseChartProps> = ({
  data,
  title = '',
  subtitle = '',
  height = DEFAULT_CHART_CONFIG.HEIGHT,
  theme = DEFAULT_CHART_CONFIG.THEME,
  showToolbar = DEFAULT_CHART_CONFIG.SHOW_TOOLBAR,
  toolbarConfig = {},
  loading = false,
  error = null,
  onRefresh,
  onUpdate,
  getChartOption,
  containerStyle,
  enableFullscreen = DEFAULT_CHART_CONFIG.ENABLE_FULLSCREEN
}) => {
  // ==================== Ref定义 ====================
  
  /** 图表容器Ref */
  const chartRef = useRef<HTMLDivElement>(null);
  /** 图表实例Ref */
  const chartInstance = useRef<echarts.ECharts | null>(null);

  // ==================== State定义 ====================
  
  /** 是否全屏状态 */
  const [isFullscreen, setIsFullscreen] = useState(false);

  // ==================== 工具栏配置 ====================
  
  const toolbarSettings = {
    showZoom: true,
    showReset: true,
    showRefresh: true,
    showFullscreen: enableFullscreen,
    ...toolbarConfig
  };

  // ==================== 副作用 ====================
  
  /**
   * 初始化图表实例
   */
  useEffect(() => {
    if (!chartRef.current) return;

    // 初始化图表
    chartInstance.current = echarts.init(chartRef.current, theme);

    // 监听窗口大小变化
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener('resize', handleResize);

    // 清理函数
    return () => {
      window.removeEventListener('resize', handleResize);
      chartInstance.current?.dispose();
    };
  }, [theme]);

  /**
   * 更新图表数据
   */
  useEffect(() => {
    if (!chartInstance.current || data.length === 0) return;

    // 获取图表配置
    const option = getChartOption ? getChartOption(data) : {};

    // 更新图表
    chartInstance.current.setOption({
      animation: true,
      animationDuration: DEFAULT_CHART_CONFIG.ANIMATION_DURATION,
      animationEasing: DEFAULT_CHART_CONFIG.ANIMATION_EASING,
      ...option
    }, true);

    // 触发更新回调
    onUpdate?.(data);
  }, [data, getChartOption, onUpdate]);

  /**
   * 全屏状态变化处理
   */
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  // ==================== 图表操作方法 ====================
  
  /**
   * 放大图表
   */
  const handleZoomIn = useCallback(() => {
    chartInstance.current?.dispatchAction({
      type: 'dataZoom',
      start: 0,
      end: 80
    });
  }, []);

  /**
   * 缩小图表
   */
  const handleZoomOut = useCallback(() => {
    chartInstance.current?.dispatchAction({
      type: 'dataZoom',
      start: 0,
      end: 100
    });
  }, []);

  /**
   * 重置图表
   */
  const handleReset = useCallback(() => {
    chartInstance.current?.dispatchAction({
      type: 'restore'
    });
  }, []);

  /**
   * 刷新图表
   */
  const handleRefresh = useCallback(() => {
    onRefresh?.();
    if (chartInstance.current) {
      const currentOption = chartInstance.current.getOption();
      chartInstance.current.setOption(currentOption, true);
    }
  }, [onRefresh]);

  /**
   * 切换全屏
   */
  const handleFullscreen = useCallback(() => {
    if (!isFullscreen) {
      chartRef.current?.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }, [isFullscreen]);

  /**
   * 获取图表实例（供外部使用）
   */
  const getChartInstance = useCallback(() => {
    return chartInstance.current;
  }, []);

  // ==================== 渲染加载状态 ====================
  
  if (loading) {
    return (
      <div 
        style={{ 
          width: '100%', 
          height, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          backgroundColor: theme === 'dark' ? '#1f1f1f' : '#f5f5f5',
          color: theme === 'dark' ? '#fff' : '#333'
        }}
      >
        <div className="loading-spinner">加载中...</div>
      </div>
    );
  }

  // ==================== 渲染错误状态 ====================
  
  if (error) {
    return (
      <div 
        style={{ 
          width: '100%', 
          height, 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center',
          backgroundColor: theme === 'dark' ? '#1f1f1f' : '#f5f5f5',
          color: theme === 'dark' ? '#fff' : '#333'
        }}
      >
        <div className="error-message">
          <p>加载失败: {error}</p>
          <Button type="primary" onClick={handleRefresh} size="small">
            重试
          </Button>
        </div>
      </div>
    );
  }

  // ==================== 渲染主界面 ====================
  
  return (
    <div 
      className="base-chart-container"
      style={{ 
        width: '100%',
        border: `1px solid ${theme === 'dark' ? '#333' : '#e0e0e0'}`,
        borderRadius: '4px',
        backgroundColor: theme === 'dark' ? '#1f1f1f' : '#fff',
        ...containerStyle
      }}
    >
      {/* 标题栏 */}
      {(title || subtitle) && (
        <div 
          className="chart-header"
          style={{
            padding: '12px 16px',
            borderBottom: `1px solid ${theme === 'dark' ? '#333' : '#e0e0e0'}`
          }}
        >
          {title && (
            <h3 
              style={{
                margin: 0,
                fontSize: '16px',
                fontWeight: 'bold',
                color: theme === 'dark' ? '#fff' : '#333'
              }}
            >
              {title}
            </h3>
          )}
          {subtitle && (
            <p 
              style={{
                margin: '4px 0 0 0',
                fontSize: '12px',
                color: theme === 'dark' ? '#999' : '#666'
              }}
            >
              {subtitle}
            </p>
          )}
        </div>
      )}

      {/* 控制栏 */}
      {showToolbar && (
        <div 
          className="chart-toolbar"
          style={{ 
            padding: '8px 12px',
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: `1px solid ${theme === 'dark' ? '#333' : '#e0e0e0'}`
          }}
        >
          <Space>
            {toolbarSettings.showZoom && (
              <>
                <Tooltip title="放大">
                  <Button 
                    icon={<ZoomInOutlined />} 
                    onClick={handleZoomIn}
                    size="small"
                    type="text"
                  />
                </Tooltip>
                <Tooltip title="缩小">
                  <Button 
                    icon={<ZoomOutOutlined />} 
                    onClick={handleZoomOut}
                    size="small"
                    type="text"
                  />
                </Tooltip>
              </>
            )}
            {toolbarSettings.showReset && (
              <Tooltip title="重置">
                <Button 
                  icon={<UndoOutlined />} 
                  onClick={handleReset}
                  size="small"
                  type="text"
                />
              </Tooltip>
            )}
            {toolbarSettings.showRefresh && (
              <Tooltip title="刷新">
                <Button 
                  icon={<ReloadOutlined />} 
                  onClick={handleRefresh}
                  size="small"
                  type="text"
                />
              </Tooltip>
            )}
          </Space>

          <Space>
            {toolbarConfig.customButtons}
            {toolbarSettings.showFullscreen && (
              <Tooltip title={isFullscreen ? "退出全屏" : "全屏"}>
                <Button 
                  icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />} 
                  onClick={handleFullscreen}
                  size="small"
                  type="text"
                />
              </Tooltip>
            )}
          </Space>
        </div>
      )}

      {/* 图表容器 */}
      <div 
        ref={chartRef} 
        style={{ 
          width: '100%', 
          height
        }} 
      />
    </div>
  );
};

// ==================== 导出 ====================

export default BaseChart;
