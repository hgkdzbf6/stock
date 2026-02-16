import { useState } from 'react';
import ReactECharts from 'echarts-for-react';

const KLineChart = () => {
  const [timePeriod, setTimePeriod] = useState('1d');
  const [indicator, setIndicator] = useState('ma');

  const timePeriods = [
    { value: '1m', label: '1分' },
    { value: '5m', label: '5分' },
    { value: '15m', label: '15分' },
    { value: '1h', label: '1小时' },
    { value: '1d', label: '1天' },
  ];

  const indicators = [
    { value: 'ma', label: 'MA' },
    { value: 'boll', label: 'BOLL' },
    { value: 'kdj', label: 'KDJ' },
    { value: 'macd', label: 'MACD' },
  ];

  // 生成模拟K线数据
  const generateKLineData = (count: number) => {
    const data = [];
    let basePrice = 1.4;
    const now = new Date('2026-02-13').getTime();

    for (let i = count - 1; i >= 0; i--) {
      const date = new Date(now - i * 24 * 60 * 60 * 1000);
      const open = basePrice + (Math.random() - 0.5) * 0.05;
      const close = open + (Math.random() - 0.5) * 0.1;
      const high = Math.max(open, close) + Math.random() * 0.02;
      const low = Math.min(open, close) - Math.random() * 0.02;
      basePrice = close;

      data.push([
        date.toISOString().split('T')[0],
        open.toFixed(2),
        close.toFixed(2),
        low.toFixed(2),
        high.toFixed(2)
      ]);
    }
    return data;
  };

  // 生成模拟MA数据
  const generateMAData = (klineData: any[], period: number) => {
    const maData = [];
    for (let i = 0; i < klineData.length; i++) {
      if (i < period - 1) {
        maData.push('-');
      } else {
        let sum = 0;
        for (let j = 0; j < period; j++) {
          sum += parseFloat(klineData[i - j][1]); // 收盘价
        }
        maData.push((sum / period).toFixed(2));
      }
    }
    return maData;
  };

  // 生成模拟BOLL数据
  const generateBOLLData = (klineData: any[], period: number = 20, multiplier: number = 2) => {
    const upper = [];
    const middle = [];
    const lower = [];

    for (let i = 0; i < klineData.length; i++) {
      if (i < period - 1) {
        upper.push('-');
        middle.push('-');
        lower.push('-');
      } else {
        let sum = 0;
        const closes = [];
        for (let j = 0; j < period; j++) {
          const close = parseFloat(klineData[i - j][1]);
          sum += close;
          closes.push(close);
        }
        const ma = sum / period;
        const variance = closes.reduce((acc, val) => acc + Math.pow(val - ma, 2), 0) / period;
        const std = Math.sqrt(variance);

        middle.push(ma.toFixed(2));
        upper.push((ma + multiplier * std).toFixed(2));
        lower.push((ma - multiplier * std).toFixed(2));
      }
    }

    return { upper, middle, lower };
  };

  // 生成模拟成交量数据
  const generateVolumeData = (klineData: any[]) => {
    return klineData.map((_, index) => {
      return Math.floor(Math.random() * 1000000) + 500000;
    });
  };

  const klineData = generateKLineData(100);
  const ma5 = generateMAData(klineData, 5);
  const ma10 = generateMAData(klineData, 10);
  const ma20 = generateMAData(klineData, 20);
  const ma60 = generateMAData(klineData, 60);
  const boll = generateBOLLData(klineData);
  const volumeData = generateVolumeData(klineData);

  const dates = klineData.map(item => item[0]);

  const getOption = () => {
    return {
      backgroundColor: 'transparent',
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
        }
      },
      legend: {
        data: ['K线', 'MA5', 'MA10', 'MA20', 'MA60', 'BOLL上轨', 'BOLL中轨', 'BOLL下轨', '成交量'],
        top: 0,
        textStyle: {
          color: '#666'
        }
      },
      grid: [
        {
          left: '10%',
          right: '8%',
          top: '10%',
          height: '50%'
        },
        {
          left: '10%',
          right: '8%',
          top: '65%',
          height: '25%'
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax'
        },
        {
          type: 'category',
          gridIndex: 1,
          data: dates,
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          min: 'dataMin',
          max: 'dataMax'
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
          splitLine: { show: false }
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 50,
          end: 100
        },
        {
          show: true,
          xAxisIndex: [0, 1],
          type: 'slider',
          top: '90%',
          start: 50,
          end: 100
        }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: klineData.map(item => [parseFloat(item[1]), parseFloat(item[2]), parseFloat(item[3]), parseFloat(item[4])]),
          itemStyle: {
            color: '#ec0000',
            color0: '#00da3c',
            borderColor: '#8A0000',
            borderColor0: '#008F28'
          }
        },
        {
          name: 'MA5',
          type: 'line',
          data: ma5,
          smooth: true,
          lineStyle: {
            opacity: 0.8,
            width: 1
          },
          symbol: 'none'
        },
        {
          name: 'MA10',
          type: 'line',
          data: ma10,
          smooth: true,
          lineStyle: {
            opacity: 0.8,
            width: 1
          },
          symbol: 'none'
        },
        {
          name: 'MA20',
          type: 'line',
          data: ma20,
          smooth: true,
          lineStyle: {
            opacity: 0.8,
            width: 1
          },
          symbol: 'none'
        },
        {
          name: 'MA60',
          type: 'line',
          data: ma60,
          smooth: true,
          lineStyle: {
            opacity: 0.8,
            width: 1
          },
          symbol: 'none'
        },
        {
          name: 'BOLL上轨',
          type: 'line',
          data: boll.upper,
          smooth: true,
          lineStyle: {
            opacity: 0.5,
            width: 1,
            type: 'dashed'
          },
          symbol: 'none'
        },
        {
          name: 'BOLL中轨',
          type: 'line',
          data: boll.middle,
          smooth: true,
          lineStyle: {
            opacity: 0.5,
            width: 1,
            type: 'dashed'
          },
          symbol: 'none'
        },
        {
          name: 'BOLL下轨',
          type: 'line',
          data: boll.lower,
          smooth: true,
          lineStyle: {
            opacity: 0.5,
            width: 1,
            type: 'dashed'
          },
          symbol: 'none'
        },
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumeData,
          itemStyle: {
            color: (params: any) => {
              const i = params.dataIndex;
              if (parseFloat(klineData[i][1]) > parseFloat(klineData[i][2])) {
                return '#00da3c';
              } else {
                return '#ec0000';
              }
            }
          }
        }
      ]
    };
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex flex-col space-y-4">
        {/* 控制区 */}
        <div className="flex flex-wrap justify-between items-center gap-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">K线图与成交量</h2>

          <div className="flex items-center space-x-4">
            {/* 时间周期选择 */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">时间周期:</span>
              <div className="flex space-x-1">
                {timePeriods.map((period) => (
                  <button
                    key={period.value}
                    onClick={() => setTimePeriod(period.value)}
                    className={`px-3 py-1 rounded text-sm font-medium transition-all ${
                      timePeriod === period.value
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                    }`}
                  >
                    {period.label}
                  </button>
                ))}
              </div>
            </div>

            {/* 技术指标选择 */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">技术指标:</span>
              <div className="flex space-x-1">
                {indicators.map((ind) => (
                  <button
                    key={ind.value}
                    onClick={() => setIndicator(ind.value)}
                    className={`px-3 py-1 rounded text-sm font-medium transition-all ${
                      indicator === ind.value
                        ? 'bg-purple-500 text-white'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                    }`}
                  >
                    {ind.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 图表区域 */}
        <div className="h-[500px]">
          <ReactECharts option={getOption()} style={{ height: '100%', width: '100%' }} />
        </div>
      </div>
    </div>
  );
};

export default KLineChart;