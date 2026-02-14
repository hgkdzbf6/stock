/** 回测结果图表组件 */
import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface EquityCurveData {
  date: string;
  total_value: number;
  cumulative_return: number;
  drawdown: number;
}

interface BacktestChartsProps {
  equityCurve: EquityCurveData[];
  metrics?: {
    total_return: number;
    annual_return: number;
    max_drawdown: number;
    sharpe_ratio: number;
    win_rate: number;
    profit_loss_ratio: number;
  };
  height?: string;
}

export default function BacktestCharts({ 
  equityCurve, 
  metrics,
  height = '400px' 
}: BacktestChartsProps) {
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
    if (!chartInstance.current || equityCurve.length === 0) return;

    const dates = equityCurve.map(item => item.date);
    const totalValues = equityCurve.map(item => item.total_value);
    const returns = equityCurve.map(item => (item.cumulative_return * 100).toFixed(2));
    const drawdowns = equityCurve.map(item => (item.drawdown * 100).toFixed(2));

    const option: echarts.EChartsOption = {
      title: {
        text: '回测结果分析',
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
          let result = params[0].name + '<br/>';
          params.forEach((param: any) => {
            if (param.seriesName === '净值曲线') {
              result += `${param.seriesName}: ¥${param.value.toFixed(2)}<br/>`;
            } else {
              result += `${param.seriesName}: ${param.value}%<br/>`;
            }
          });
          return result;
        }
      },
      legend: {
        data: ['净值曲线', '累计收益率', '回撤'],
        top: 30
      },
      grid: [
        {
          left: '10%',
          right: '10%',
          top: '80',
          height: '60%'
        },
        {
          left: '10%',
          right: '10%',
          top: '75%',
          height: '15%'
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          axisLabel: {
            rotate: 45,
            interval: 'auto'
          }
        },
        {
          type: 'category',
          gridIndex: 1,
          data: dates,
          boundaryGap: false,
          axisLine: { onZero: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false }
        }
      ],
      yAxis: [
        {
          name: '净值 (¥)',
          type: 'value',
          position: 'left',
          splitArea: { show: true }
        },
        {
          name: '回撤 (%)',
          type: 'value',
          position: 'right',
          splitLine: { show: false },
          axisLabel: {
            formatter: '{value}%'
          }
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
          top: '95%',
          start: 70,
          end: 100
        }
      ],
      series: [
        {
          name: '净值曲线',
          type: 'line',
          data: totalValues,
          smooth: true,
          lineStyle: {
            width: 2,
            color: '#1890ff'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
              { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
            ])
          }
        },
        {
          name: '累计收益率',
          type: 'line',
          yAxisIndex: 1,
          data: returns,
          smooth: true,
          lineStyle: {
            width: 1.5,
            color: '#52c41a'
          },
          itemStyle: {
            color: '#52c41a'
          }
        },
        {
          name: '回撤',
          type: 'line',
          yAxisIndex: 1,
          data: drawdowns,
          smooth: true,
          lineStyle: {
            width: 1.5,
            color: '#f5222d'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(245, 34, 45, 0.3)' },
              { offset: 1, color: 'rgba(245, 34, 45, 0.05)' }
            ])
          }
        }
      ]
    };

    chartInstance.current.setOption(option);
  }, [equityCurve, height]);

  if (!metrics || equityCurve.length === 0) {
    return <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>暂无数据</div>;
  }

  return (
    <div>
      <div ref={chartRef} style={{ width: '100%', height }} />
      
      {/* 关键指标卡片 */}
      <div style={{ 
        marginTop: '20px', 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px'
      }}>
        <MetricCard 
          title="总收益率" 
          value={`${(metrics.total_return * 100).toFixed(2)}%`}
          trend={metrics.total_return >= 0 ? 'up' : 'down'}
        />
        <MetricCard 
          title="年化收益率" 
          value={`${(metrics.annual_return * 100).toFixed(2)}%`}
          trend={metrics.annual_return >= 0 ? 'up' : 'down'}
        />
        <MetricCard 
          title="最大回撤" 
          value={`${(metrics.max_drawdown * 100).toFixed(2)}%`}
          trend="down"
        />
        <MetricCard 
          title="夏普比率" 
          value={metrics.sharpe_ratio.toFixed(2)}
          trend={metrics.sharpe_ratio >= 1 ? 'up' : 'neutral'}
        />
        <MetricCard 
          title="胜率" 
          value={`${metrics.win_rate.toFixed(2)}%`}
          trend={metrics.win_rate >= 50 ? 'up' : 'down'}
        />
        <MetricCard 
          title="盈亏比" 
          value={metrics.profit_loss_ratio.toFixed(2)}
          trend={metrics.profit_loss_ratio >= 1 ? 'up' : 'down'}
        />
      </div>
    </div>
  );
}

function MetricCard({ title, value, trend }: { title: string; value: string; trend: 'up' | 'down' | 'neutral' }) {
  const getColor = () => {
    switch (trend) {
      case 'up':
        return '#52c41a';
      case 'down':
        return '#f5222d';
      default:
        return '#faad14';
    }
  };

  const getIcon = () => {
    switch (trend) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      default:
        return '→';
    }
  };

  return (
    <div style={{
      padding: '20px',
      background: '#fff',
      borderRadius: '8px',
      border: '1px solid #e8e8e8',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    }}>
      <div style={{ 
        fontSize: '14px', 
        color: '#666', 
        marginBottom: '12px' 
      }}>
        {title}
      </div>
      <div style={{ 
        fontSize: '24px', 
        fontWeight: 'bold', 
        color: getColor(),
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        <span>{getIcon()}</span>
        <span>{value}</span>
      </div>
    </div>
  );
}