/** K线图组件 */
import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface KLineData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface KLineChartProps {
  data: KLineData[];
  title?: string;
  height?: string;
  showVolume?: boolean;
  indicators?: {
    ma5?: number[];
    ma10?: number[];
    ma20?: number[];
    ma30?: number[];
  };
}

export default function KLineChart({ 
  data, 
  title = 'K线图', 
  height = '500px',
  showVolume = true,
  indicators 
}: KLineChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // 初始化图表
    chartInstance.current = echarts.init(chartRef.current);

    // 窗口大小改变时重绘
    const handleResize = () => {
      chartInstance.current?.resize();
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chartInstance.current?.dispose();
    };
  }, []);

  useEffect(() => {
    if (!chartInstance.current || data.length === 0) return;

    // 处理K线数据
    const kLineData = data.map(item => [
      item.date,
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

    // 处理MA指标数据
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

    // 添加MA指标
    if (indicators?.ma5) {
      const ma5Data = data.map((item, index) => ({
        value: [item.date, indicators.ma5?.[index] || '-'],
        itemStyle: { color: '#f39c12' }
      }));
      series.push({
        name: 'MA5',
        type: 'line',
        data: ma5Data,
        smooth: true,
        lineStyle: { width: 1 },
        symbol: 'none'
      });
    }

    if (indicators?.ma10) {
      const ma10Data = data.map((item, index) => ({
        value: [item.date, indicators.ma10?.[index] || '-'],
        itemStyle: { color: '#e74c3c' }
      }));
      series.push({
        name: 'MA10',
        type: 'line',
        data: ma10Data,
        smooth: true,
        lineStyle: { width: 1 },
        symbol: 'none'
      });
    }

    if (indicators?.ma20) {
      const ma20Data = data.map((item, index) => ({
        value: [item.date, indicators.ma20?.[index] || '-'],
        itemStyle: { color: '#9b59b6' }
      }));
      series.push({
        name: 'MA20',
        type: 'line',
        data: ma20Data,
        smooth: true,
        lineStyle: { width: 1 },
        symbol: 'none'
      });
    }

    if (indicators?.ma30) {
      const ma30Data = data.map((item, index) => ({
        value: [item.date, indicators.ma30?.[index] || '-'],
        itemStyle: { color: '#3498db' }
      }));
      series.push({
        name: 'MA30',
        type: 'line',
        data: ma30Data,
        smooth: true,
        lineStyle: { width: 1 },
        symbol: 'none'
      });
    }

    // 配置选项
    const option: echarts.EChartsOption = {
      title: {
        text: title,
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#ccc',
        borderWidth: 1,
        textStyle: {
          color: '#333'
        },
        formatter: function (params: any) {
          let result = params[0].value[0] + '<br/>';
          params.forEach((param: any) => {
            if (param.seriesType === 'candlestick') {
              result += `开: ${param.data[1]}<br/>`;
              result += `收: ${param.data[2]}<br/>`;
              result += `低: ${param.data[3]}<br/>`;
              result += `高: ${param.data[4]}<br/>`;
              result += `成交量: ${data[params.indexOf(param)].volume}<br/>`;
            } else {
              result += `${param.seriesName}: ${param.data.value[1]}<br/>`;
            }
          });
          return result;
        }
      },
      legend: {
        data: ['日K', 'MA5', 'MA10', 'MA20', 'MA30'].filter((_, i) => {
            return i === 0 || (indicators?.ma5 && i === 1) || 
                   (indicators?.ma10 && i === 2) || (indicators?.ma20 && i === 3) || 
                   (indicators?.ma30 && i === 4);
          }
        ),
        top: 30
      },
      grid: [
        {
          left: '10%',
          right: '10%',
          top: '80',
          height: showVolume ? '60%' : '75%'
        },
        {
          left: '10%',
          right: '10%',
          top: showVolume ? '70%' : '85%',
          height: showVolume ? '15%' : '0%',
          show: showVolume
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
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: {
            show: true
          }
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: { show: false },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { show: false },
          show: showVolume
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 70,
          end: 100
        },
        {
          type: 'slider',
          xAxisIndex: [0, 1],
          top: showVolume ? '90%' : '90%',
          start: 70,
          end: 100
        }
      ],
      series
    };

    chartInstance.current.setOption(option);
  }, [data, title, height, showVolume, indicators]);

  return <div ref={chartRef} style={{ width: '100%', height }} />;
}