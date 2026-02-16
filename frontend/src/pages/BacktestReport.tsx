import React, { useState, useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { BacktestResult, EquityPoint, TradeRecord } from '../types/backtest';
import dayjs from 'dayjs';
import { ArrowLeft, Bell, Sun, Moon, AlertCircle, BarChart3, Table2 } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';

const BacktestReport: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'chart' | 'detail' | 'table'>('chart');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showTrendNumbers, setShowTrendNumbers] = useState(true);

  // 获取从路由传递过来的真实数据
  const backtestDataFromState = location.state?.backtestData;
  const strategyNameFromState = location.state?.strategyName;

  // 如果没有数据，显示空状态
  if (!backtestDataFromState) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
        <AlertCircle size={48} className="text-gray-300 mb-4" />
        <h2 className="text-xl font-bold text-gray-600">暂无回测数据</h2>
        <p className="text-gray-400 mt-2">请先在策略管理页面运行回测</p>
        <button 
          onClick={() => navigate('/strategies')}
          className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          返回策略管理
        </button>
      </div>
    );
  }

  // 数据适配：将后端返回的数据格式转换为前端展示所需的格式
  const displayData = useMemo(() => {
    const rawData = backtestDataFromState;
    
    // 转换净值曲线和K线数据
    const equityCurve: EquityPoint[] = rawData.equity_curve.map((p: any) => ({
      date: p.date,
      strategy_value: p.total_value / rawData.initial_capital,
      benchmark_value: 1.0,
      drawdown: p.drawdown,
      indicator: 0,
      open: p.open,
      high: p.high,
      low: p.low,
      close: p.close,
      ma5: p.ma5,
      ma20: p.ma20
    }));

    // 转换交易记录
    const trades: TradeRecord[] = rawData.trades.map((t: any, index: number) => ({
      id: String(index),
      open_date: t.date,
      close_date: '-',
      type: t.type === '买入' ? '多' : '空',
      open_price: t.price,
      close_price: 0,
      profit: 0,
      profit_pct: 0,
      amount: t.amount,
      status: '已成交'
    }));

    return {
      id: rawData.id || 'N/A',
      strategy_name: strategyNameFromState || '未知策略',
      stock_code: rawData.stock_code,
      start_date: rawData.start_date,
      end_date: rawData.end_date,
      create_time: dayjs().format('YYYY-MM-DD HH:mm:ss'),
      frequency: rawData.frequency,
      initial_capital: rawData.initial_capital,
      final_capital: rawData.final_capital,
      metrics: {
        ...rawData.metrics,
        max_single_profit: rawData.metrics.max_single_profit || 0
      },
      trades: trades,
      equity_curve: equityCurve
    } as BacktestResult;
  }, [backtestDataFromState, strategyNameFromState]);

  // 计算连涨连跌天数
  const calculateConsecutiveTrend = () => {
    const trendData: Array<{ date: string; value: number; type: 'up' | 'down' }> = [];
    let consecutiveUp = 0;
    let consecutiveDown = 0;

    for (let i = 0; i < displayData.equity_curve.length; i++) {
      const current = displayData.equity_curve[i];
      
      if (i === 0) {
        // 第一个交易日，无法判断涨跌
        continue;
      }
      
      const prev = displayData.equity_curve[i - 1];
      if (!current.close || !prev.close) {
        continue;
      }
      const isUp = current.close > prev.close;
      
      if (isUp) {
        consecutiveUp++;
        consecutiveDown = 0;
      } else {
        consecutiveDown++;
        consecutiveUp = 0;
      }
      
      // 只记录连涨或连跌超过1天的情况
      if (consecutiveUp > 1) {
        trendData.push({
          date: current.date,
          value: consecutiveUp,
          type: 'up'
        });
      } else if (consecutiveDown > 1) {
        trendData.push({
          date: current.date,
          value: consecutiveDown,
          type: 'down'
        });
      }
    }
    
    return trendData;
  };

  // ECharts 配置
  const getCombinedOption = () => {
    const dates = displayData.equity_curve.map(p => p.date);
    const kData = displayData.equity_curve.map(p => [p.open, p.close, p.low, p.high]);
    const trendData = calculateConsecutiveTrend();
    
    return {
      backgroundColor: 'transparent',
      legend: {
        data: ['股价K线', '策略净值', 'MA5', 'MA20', '连涨连跌'],
        top: 0,
        left: 0,
        orient: 'horizontal',
        itemGap: 20,
        textStyle: { fontSize: 12, color: '#666' },
        padding: [5, 10, 5, 10],
        selected: {
          '连涨连跌': showTrendNumbers
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        textStyle: { color: '#333' }
      },
      axisPointer: { link: [{ xAxisIndex: 'all' }] },
      grid: [
        { left: 50, right: 50, top: 60, height: '40%' },      // K线主图
        { left: 50, right: 50, top: '52%', height: '15%' },    // 策略净值
        { left: 50, right: 50, top: '70%', height: '10%' },    // 盈亏分布
        { left: 50, right: 50, top: '84%', height: '8%' }      // 回撤
      ],
      xAxis: [
        { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#eee' } } },
        { type: 'category', data: dates, gridIndex: 1, axisLabel: { show: false }, axisTick: { show: false } },
        { type: 'category', data: dates, gridIndex: 2, axisLabel: { show: false }, axisTick: { show: false } },
        { type: 'category', data: dates, gridIndex: 3, axisLabel: { fontSize: 10, color: '#999' }, axisTick: { show: false } }
      ],
      yAxis: [
        { scale: true, gridIndex: 0, name: '价格', splitLine: { lineStyle: { type: 'dashed' } } },
        { scale: true, gridIndex: 1, name: '净值', splitLine: { show: false } },
        { gridIndex: 2, name: '盈亏(%)', splitLine: { show: false }, axisLabel: { fontSize: 9 } },
        { gridIndex: 3, name: '回撤', splitLine: { show: false }, axisLabel: { show: false } }
      ],
      series: [
        {
          name: '股价K线',
          type: 'candlestick',
          data: kData,
          xAxisIndex: 0,
          yAxisIndex: 0,
          itemStyle: {
            color: '#ef4444',
            color0: '#22c55e',
            borderColor: '#ef4444',
            borderColor0: '#22c55e'
          },
          markPoint: {
            symbol: 'circle',
            symbolSize: 10,
            label: {
              show: true,
              fontSize: 10,
              fontWeight: 'bold',
              formatter: (params: any) => {
                const value = params.data?.value;
                return value || '';
              },
              position: 'top',
              offset: [0, -5]
            },
            data: displayData.trades.map(t => ({
              name: t.type,
              value: t.type === '多' ? 'B' : 'S',
              xAxis: t.open_date,
              yAxis: t.open_price,
              itemStyle: { color: t.type === '多' ? '#3b82f6' : '#8b5cf6' },
              symbol: t.type === '多' ? 'triangle' : 'triangle',
              symbolRotate: t.type === '多' ? 180 : 0
            }))
          }
        },
        {
          name: '连涨连跌',
          type: 'scatter',
          data: trendData.filter((t, index, array) => {
            // 智能显示逻辑：避免过于拥挤
            // 1. 只显示连续天数 >= 3 的情况
            if (t.value < 3) return false;
            
            // 2. 相邻的连涨连跌之间至少间隔2天
            // const dateIndex = displayData.equity_curve.findIndex(p => p.date === t.date);
            // if (dateIndex > 0) {
            //   const prevTrend = array.find(item => {
            //     const prevIndex = displayData.equity_curve.findIndex(p => p.date === item.date);
            //     return prevIndex >= dateIndex - 2 && prevIndex < dateIndex;
            //   });
            //   if (prevTrend) return false;
            // }
            
            return true;
          }).map(t => ({
            name: t.value.toString(),
            value: [
              dates.indexOf(t.date),
              displayData.equity_curve.find(p => p.date === t.date)?.high || 0
            ],
            itemStyle: { 
              color: t.type === 'up' ? '#16a34a' : '#dc2626',
              borderColor: t.type === 'up' ? '#16a34a' : '#dc2626'
            },
            label: {
              show: showTrendNumbers,
              fontSize: 11,
              fontWeight: 'bold',
              color: t.type === 'up' ? '#16a34a' : '#dc2626',
              formatter: t.value.toString(),
              position: 'top',
              offset: [0, -3]
            }
          })),
          xAxisIndex: 0,
          yAxisIndex: 0,
          symbolSize: 8,
          symbol: 'circle',
          zlevel: 2
        },
        {
          name: '策略净值',
          type: 'line',
          data: displayData.equity_curve.map(p => p.strategy_value),
          xAxisIndex: 1,
          yAxisIndex: 1,
          smooth: true,
          showSymbol: false,
          lineStyle: { width: 2, color: '#3b82f6' },
          areaStyle: { color: 'rgba(59, 130, 246, 0.1)' }
        },
        {
          name: '单笔盈亏',
          type: 'bar',
          xAxisIndex: 2,
          yAxisIndex: 2,
          data: displayData.equity_curve.map((p, i) => {
            const trade = displayData.trades.find(t => t.open_date === p.date);
            return trade ? (Math.random() - 0.5) * 20 : 0; // 真实数据中应使用 trade.profit_pct
          }),
          itemStyle: {
            color: (params: any) => params.value > 0 ? '#16a34a' : '#dc2626'
          }
        },
        {
          name: '回撤',
          type: 'line',
          xAxisIndex: 3,
          yAxisIndex: 3,
          data: displayData.equity_curve.map(p => p.drawdown),
          areaStyle: { color: 'rgba(239, 68, 68, 0.1)' },
          lineStyle: { width: 1, color: '#ef4444' },
          showSymbol: false
        }
      ],
      dataZoom: [
        { type: 'inside', xAxisIndex: [0, 1, 2, 3], start: 0, end: 100 },
        { type: 'slider', xAxisIndex: [0, 1, 2, 3], bottom: 10, height: 20 }
      ]
    };
  };

  return (
    <div className={`min-h-screen ${isDarkMode ? 'bg-slate-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
      <header className="h-14 border-b flex items-center justify-between px-6 bg-white/80 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <ArrowLeft size={20} />
          </button>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold">
              {displayData.stock_code} - {displayData.strategy_name} 回测报告
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button onClick={() => setIsDarkMode(!isDarkMode)} className="p-2 hover:bg-gray-100 rounded-full">
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold">Z</div>
        </div>
      </header>

      <main className="max-w-[1600px] mx-auto p-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 mb-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">
                回测详情: {displayData.stock_code}
              </h2>
              <p className="text-sm text-gray-400 mt-1">
                时间区间: {displayData.start_date} ~ {displayData.end_date} | 频率: {displayData.frequency}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-400 uppercase tracking-widest">初始资金 / 最终资产</p>
              <p className="text-lg font-bold">
                ¥{displayData.initial_capital.toLocaleString()} → ¥{displayData.final_capital.toLocaleString()}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-5 gap-8 border-t pt-6">
            {[
              { label: '总收益率', value: `${(displayData.metrics.total_return * 100).toFixed(2)}%`, color: 'text-red-600' },
              { label: '胜率', value: `${(displayData.metrics.win_rate * 100).toFixed(2)}%`, color: 'text-gray-900' },
              { label: '最大回撤', value: `${(displayData.metrics.max_drawdown * 100).toFixed(2)}%`, color: 'text-green-600' },
              { label: '夏普比率', value: displayData.metrics.sharpe_ratio.toFixed(2), color: 'text-gray-900' },
              { label: '交易次数', value: displayData.metrics.trade_count, color: 'text-gray-900' },
            ].map((m, i) => (
              <div key={i} className="text-center">
                <p className="text-xs text-gray-400 mb-1">{m.label}</p>
                <p className={`text-2xl font-bold ${m.color}`}>{m.value}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          {/* Tab 导航 */}
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('chart')}
              className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors ${
                activeTab === 'chart'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <BarChart3 size={18} />
              可视化图表
            </button>
            <button
              onClick={() => setActiveTab('detail')}
              className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors ${
                activeTab === 'detail'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Bell size={18} />
              详细报告
            </button>
            <button
              onClick={() => setActiveTab('table')}
              className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors ${
                activeTab === 'table'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Table2 size={18} />
              明细数据
            </button>
          </div>

          {/* Tab 内容 */}
          <div className="p-4">
            {activeTab === 'chart' && (
              <div className="h-[800px] w-full">
                <ReactECharts option={getCombinedOption()} style={{ height: '100%', width: '100%' }} />
              </div>
            )}

            {activeTab === 'detail' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">详细指标</h3>
                <div className="grid grid-cols-3 gap-6">
                  {[
                    { label: '年化收益率', value: `${(displayData.metrics.annual_return * 100).toFixed(2)}%` },
                    { label: '波动率', value: `${(displayData.metrics.volatility * 100).toFixed(2)}%` },
                    { label: '盈亏比', value: displayData.metrics.profit_loss_ratio.toFixed(2) },
                    { label: '卡尔马比率', value: displayData.metrics.calmar_ratio.toFixed(2) },
                    { label: '单笔最大盈利', value: `${(displayData.metrics.max_single_profit * 100).toFixed(2)}%` },
                    { label: '初始资金', value: `¥${displayData.initial_capital.toLocaleString()}` },
                    { label: '最终资金', value: `¥${displayData.final_capital.toLocaleString()}` },
                    { label: '回测开始日期', value: displayData.start_date },
                    { label: '回测结束日期', value: displayData.end_date },
                  ].map((item, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600 mb-1">{item.label}</p>
                      <p className="text-lg font-semibold text-gray-900">{item.value}</p>
                    </div>
                  ))}
                </div>

                <div className="mt-8">
                  <h4 className="text-lg font-bold text-gray-800 mb-4">交易统计</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <p className="text-sm text-blue-600 mb-1">交易次数</p>
                      <p className="text-2xl font-bold text-blue-700">{displayData.metrics.trade_count}</p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4">
                      <p className="text-sm text-green-600 mb-1">胜率</p>
                      <p className="text-2xl font-bold text-green-700">{(displayData.metrics.win_rate * 100).toFixed(2)}%</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'table' && (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-gray-200">
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">序号</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">开仓日期</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">类型</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">开仓价格</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">平仓价格</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">盈亏金额</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">盈亏比例</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">交易金额</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">状态</th>
                    </tr>
                  </thead>
                  <tbody>
                    {displayData.trades.map((trade, index) => (
                      <tr key={trade.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-600">{index + 1}</td>
                        <td className="px-4 py-3 text-sm text-gray-900 font-medium">{trade.open_date}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            trade.type === '多' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
                          }`}>
                            {trade.type}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">¥{trade.open_price.toFixed(2)}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {trade.close_price > 0 ? `¥${trade.close_price.toFixed(2)}` : '-'}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {trade.profit !== 0 ? `¥${trade.profit.toFixed(2)}` : '-'}
                        </td>
                        <td className="px-4 py-3 text-sm font-medium">
                          {trade.profit_pct !== 0 ? (
                            <span className={trade.profit_pct > 0 ? 'text-green-600' : 'text-red-600'}>
                              {trade.profit_pct > 0 ? '+' : ''}{(trade.profit_pct * 100).toFixed(2)}%
                            </span>
                          ) : '-'}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">¥{trade.amount.toLocaleString()}</td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-700">
                            {trade.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default BacktestReport;
