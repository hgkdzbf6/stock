/** 增强版K线图组件 - 支持缩放、拖动、多种交互 */
import { useEffect, useRef, useState, useCallback } from 'react';
import * as echarts from 'echarts';
import { Button, Select, Space, Tooltip } from 'antd';
import { ZoomInOutlined, ZoomOutOutlined, UndoOutlined, ReloadOutlined, FullscreenOutlined, FullscreenExitOutlined } from '@ant-design/icons';

const { Option } = Select;

interface KLineData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount?: number;
}

interface IndicatorData {
  ma5?: number[];
  ma10?: number[];
  ma20?: number[];
  ma30?: number[];
  macd?: {
    dif: number[];
    dea: number[];
    macd: number[];
  };
  kdj?: {
    k: number[];
    d: number[];
    j: number[];
  };
}

interface EnhancedKLineChartProps {
  data: KLineData[];
  title?: string;
  subtitle?: string;
  height?: string;
  showVolume?: boolean;
  indicators?: IndicatorData;
  theme?: 'light' | 'dark';
  onStockSelect?: (stockCode: string) => void;
  enableFullscreen?: boolean;
}

export default function EnhancedKLineChart({
  data,
  title = 'K线图',
  subtitle = '',
  height = '600px',
  showVolume = true,
  indicators,
  theme = 'light',
  onStockSelect,
  enableFullscreen = true
}: EnhancedKLineChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [activeIndicator, setActiveIndicator] = useState<string>('ma');

  // 计算MA指标
  const calculateMA = useCallback((dayCount: number, data: KLineData[]): number[] => {
    const result: number[] = [];
    for (let i = 0; i < data.length; i++) {
      if (i < dayCount - 1) {
        result.push(NaN);
      } else {
        let sum = 0;
        for (let j = 0; j < dayCount; j++) {
          sum += data[i - j].close;
        }
        result.push(+(sum / dayCount).toFixed(2));
      }
    }
    return result;
  }, []);

  // 计算MACD指标
  const calculateMACD = useCallback((data: KLineData[]) => {
    const shortPeriod = 12;
    const longPeriod = 26;
    const signalPeriod = 9;
    
    const emaShort: number[] = [];
    const emaLong: number[] = [];
    const dif: number[] = [];
    const dea: number[] = [];
    const macd: number[] = [];

    // 计算EMA
    for (let i = 0; i < data.length; i++) {
      if (i === 0) {
        emaShort.push(data[i].close);
        emaLong.push(data[i].close);
      } else {
        emaShort.push(data[i].close * 2 / (shortPeriod + 1) + emaShort[i - 1] * (shortPeriod - 1) / (shortPeriod + 1));
        emaLong.push(data[i].close * 2 / (longPeriod + 1) + emaLong[i - 1] * (longPeriod - 1) / (longPeriod + 1));
      }

      const currentDif = emaShort[i] - emaLong[i];
      dif.push(currentDif);

      if (i === 0) {
        dea.push(currentDif);
      } else {
        dea.push(currentDif * 2 / (signalPeriod + 1) + dea[i - 1] * (signalPeriod - 1) / (signalPeriod + 1));
      }

      macd.push((currentDif - dea[i]) * 2);
    }

    return { dif, dea, macd };
  }, []);

  useEffect(() => {
    if (!chartRef.current) return;

    // 初始化图表
    chartInstance.current = echarts.init(chartRef.current, theme);

    // 窗口大小改变时重绘
    const handleResize = () => {
      chartInstance.current?.resize();
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chartInstance.current?.dispose();
    };
  }, [theme]);

  useEffect(() => {
    if (!chartInstance.current || data.length === 0) return;

    // 处理K线数据
    const kLineData = data.map(item => [
      item.open,
      item.close,
      item.low,
      item.high
    ]);

    // 处理成交量数据
    const volumeData = data.map(item => ({
      value: [
        item.date,
        item.volume,
        item.close > item.open ? 1 : -1
      ]
    }));

    // 计算MA指标
    const ma5 = indicators?.ma5 || calculateMA(5, data);
    const ma10 = indicators?.ma10 || calculateMA(10, data);
    const ma20 = indicators?.ma20 || calculateMA(20, data);
    const ma30 = indicators?.ma30 || calculateMA(30, data);

    // 构建系列
    const series: any[] = [
      {
        type: 'candlestick',
        name: '日K',
        data: kLineData,
        itemStyle: {
          color: '#ef5350',
          color0: '#26a69a',
          borderColor: '#ef5350',
          borderColor0: '#26a69a'
        }
      }
    ];

    // 根据选择的指标类型添加系列
    if (activeIndicator === 'ma') {
      const maSeries = [
        { name: 'MA5', data: ma5, color: '#f39c12' },
        { name: 'MA10', data: ma10, color: '#e74c3c' },
        { name: 'MA20', data: ma20, color: '#9b59b6' },
        { name: 'MA30', data: ma30, color: '#3498db' }
      ];

      maSeries.forEach(ma => {
        series.push({
          name: ma.name,
          type: 'line',
          data: data.map((item, index) => ({
            value: [item.date, ma.data[index]],
            itemStyle: { color: ma.color }
          })),
          smooth: true,
          lineStyle: { width: 1.5 },
          symbol: 'none',
          showSymbol: false
        });
      });
    } else if (activeIndicator === 'macd' && !indicators?.macd) {
      const macdData = calculateMACD(data);
      
      series.push(
        {
          name: 'DIF',
          type: 'line',
          data: data.map((item, index) => [item.date, macdData.dif[index]]),
          yAxisIndex: 2,
          lineStyle: { color: '#ffffff', width: 1.5 }
        },
        {
          name: 'DEA',
          type: 'line',
          data: data.map((item, index) => [item.date, macdData.dea[index]]),
          yAxisIndex: 2,
          lineStyle: { color: '#ffd700', width: 1.5 }
        },
        {
          name: 'MACD',
          type: 'bar',
          data: data.map((item, index) => ({
            value: [item.date, macdData.macd[index]],
            itemStyle: {
              color: macdData.macd[index] >= 0 ? '#ef5350' : '#26a69a'
            }
          })),
          yAxisIndex: 2
        }
      );
    }

    // 配置选项
    const option: echarts.EChartsOption = {
      title: {
        text: title,
        subtext: subtitle,
        left: 'center',
        textStyle: {
          fontSize: 18,
          fontWeight: 'bold'
        },
        subtextStyle: {
          fontSize: 14,
          color: '#999'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        backgroundColor: 'rgba(50, 50, 50, 0.95)',
        borderColor: '#ccc',
        borderWidth: 1,
        textStyle: {
          color: '#fff'
        },
        formatter: function (params: any) {
          let result = `<strong>${params[0].value[0]}</strong><br/><hr/>`;
          params.forEach((param: any) => {
            if (param.seriesType === 'candlestick') {
              const dataIndex = params.indexOf(param);
              result += `开: <strong>${param.data[1]}</strong><br/>`;
              result += `收: <strong>${param.data[2]}</strong><br/>`;
              result += `低: <strong>${param.data[3]}</strong><br/>`;
              result += `高: <strong>${param.data[4]}</strong><br/>`;
              result += `成交量: <strong>${(data[dataIndex].volume / 10000).toFixed(2)}万</strong><br/>`;
              if (data[dataIndex].amount) {
                result += `成交额: <strong>${(data[dataIndex].amount / 10000).toFixed(2)}万</strong><br/>`;
              }
              result += `涨跌: <strong style="color: ${data[dataIndex].close >= data[dataIndex].open ? '#ef5350' : '#26a69a'}">
                ${data[dataIndex].close >= data[dataIndex].open ? '+' : ''}${((data[dataIndex].close - data[dataIndex].open) / data[dataIndex].open * 100).toFixed(2)}%
              </strong><br/>`;
            } else if (param.seriesType === 'line') {
              result += `${param.seriesName}: <strong>${param.data.value[1].toFixed(2)}</strong><br/>`;
            } else if (param.seriesType === 'bar') {
              result += `${param.seriesName}: <strong>${param.data.value[1].toFixed(4)}</strong><br/>`;
            }
          });
          return result;
        }
      },
      legend: {
        data: ['日K', 'MA5', 'MA10', 'MA20', 'MA30'],
        top: 60,
        textStyle: {
          color: '#666'
        }
      },
      animation: true,
      animationDuration: 1000,
      animationEasing: 'cubicOut',
      grid: [
        {
          left: '10%',
          right: '10%',
          top: showVolume ? '100' : '90',
          height: showVolume ? '50%' : '60%'
        },
        {
          left: '10%',
          right: '10%',
          top: showVolume ? '70%' : '85%',
          height: showVolume ? '15%' : '0%',
          show: showVolume
        },
        {
          left: '10%',
          right: '10%',
          top: showVolume && activeIndicator === 'macd' ? '65%' : '0%',
          height: showVolume && activeIndicator === 'macd' ? '15%' : '0%',
          show: activeIndicator === 'macd'
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: data.map(item => item.date),
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax'
        },
        {
          type: 'category',
          gridIndex: 1,
          data: data.map(item => item.date),
          boundaryGap: false,
          axisLine: { onZero: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          min: 'dataMin',
          max: 'dataMax',
          show: showVolume
        },
        {
          type: 'category',
          gridIndex: 2,
          data: data.map(item => item.date),
          boundaryGap: false,
          axisLine: { onZero: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          min: 'dataMin',
          max: 'dataMax',
          show: activeIndicator === 'macd'
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: {
            show: true,
            areaStyle: {
              color: ['rgba(250,250,250,0.3)', 'rgba(200,200,200,0.3)']
            }
          },
          axisLabel: {
            formatter: (value: number) => value.toFixed(2)
          }
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: { 
            show: showVolume,
            formatter: (value: number) => (value / 10000).toFixed(0) + '万'
          },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { show: false },
          show: showVolume
        },
        {
          scale: true,
          gridIndex: 2,
          splitNumber: 2,
          axisLabel: { show: false },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { show: false },
          show: activeIndicator === 'macd'
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1, 2],
          start: Math.max(0, 100 - (100 / data.length) * 60),
          end: 100,
          zoomOnMouseWheel: true,
          moveOnMouseMove: true,
          moveOnMouseWheel: false
        },
        {
          type: 'slider',
          xAxisIndex: [0, 1, 2],
          top: showVolume ? '92%' : '95%',
          start: Math.max(0, 100 - (100 / data.length) * 60),
          end: 100,
          height: 25,
          borderColor: '#ccc',
          fillerColor: 'rgba(78, 167, 236, 0.2)',
          handleStyle: {
            color: '#4a90e2'
          }
        }
      ],
      series
    };

    chartInstance.current.setOption(option, true);
  }, [data, title, subtitle, height, showVolume, indicators, activeIndicator, theme, calculateMA, calculateMACD]);

  // 缩放控制
  const handleZoomIn = () => {
    chartInstance.current?.dispatchAction({
      type: 'dataZoom',
      start: 0,
      end: 80
    });
  };

  const handleZoomOut = () => {
    chartInstance.current?.dispatchAction({
      type: 'dataZoom',
      start: 0,
      end: 100
    });
  };

  const handleReset = () => {
    chartInstance.current?.dispatchAction({
      type: 'restore'
    });
  };

  const handleRefresh = () => {
    chartInstance.current?.setOption(chartInstance.current.getOption(), true);
  };

  const handleFullscreen = () => {
    if (!isFullscreen) {
      chartRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  return (
    <div style={{ width: '100%' }}>
      {/* 控制栏 */}
      <div style={{ 
        marginBottom: 16, 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '12px',
        backgroundColor: theme === 'dark' ? '#1f1f1f' : '#f5f5f5',
        borderRadius: '4px'
      }}>
        <Space>
          <Tooltip title="缩放控制">
            <Button 
              icon={<ZoomInOutlined />} 
              onClick={handleZoomIn}
              size="small"
            />
          </Tooltip>
          <Tooltip title="缩小">
            <Button 
              icon={<ZoomOutOutlined />} 
              onClick={handleZoomOut}
              size="small"
            />
          </Tooltip>
          <Tooltip title="重置">
            <Button 
              icon={<UndoOutlined />} 
              onClick={handleReset}
              size="small"
            />
          </Tooltip>
          <Tooltip title="刷新">
            <Button 
              icon={<ReloadOutlined />} 
              onClick={handleRefresh}
              size="small"
            />
          </Tooltip>
        </Space>

        <Space>
          <Tooltip title="指标选择">
            <Select 
              value={activeIndicator}
              onChange={setActiveIndicator}
              style={{ width: 120 }}
              size="small"
            >
              <Option value="ma">均线指标</Option>
              <Option value="macd">MACD指标</Option>
            </Select>
          </Tooltip>
          
          {enableFullscreen && (
            <Tooltip title={isFullscreen ? "退出全屏" : "全屏显示"}>
              <Button 
                icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />} 
                onClick={handleFullscreen}
                size="small"
              />
            </Tooltip>
          )}
        </Space>
      </div>

      {/* K线图容器 */}
      <div 
        ref={chartRef} 
        style={{ 
          width: '100%', 
          height,
          border: `1px solid ${theme === 'dark' ? '#333' : '#e0e0e0'}`,
          borderRadius: '4px',
          padding: '10px'
        }} 
      />
    </div>
  );
}