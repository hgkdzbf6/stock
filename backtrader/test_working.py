#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试可工作的版本 - 直接使用模拟数据
"""

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.family'] = ['Hiragino Sans GB', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class DualMovingAverageStrategy(bt.Strategy):
    """双均线策略"""
    
    params = (
        ('ma_fast', 5),
        ('ma_slow', 20),
        ('printlog', True),
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.ma_fast = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.ma_fast)
        self.ma_slow = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.ma_slow)
        self.crossover = bt.indicators.CrossOver(self.ma_fast, self.ma_slow)
        self.order = None
    
    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}: {txt}')
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入执行, 价格: {order.executed.price:.2f}')
            else:
                self.log(f'卖出执行, 价格: {order.executed.price:.2f}')
        
        self.order = None
    
    def next(self):
        self.log(f'收盘价: {self.dataclose[0]:.2f}, 快线: {self.ma_fast[0]:.2f}, 慢线: {self.ma_slow[0]:.2f}')
        
        if not self.position:
            if self.crossover > 0:
                self.log(f'金叉买入信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.buy()
        else:
            if self.crossover < 0:
                self.log(f'死叉卖出信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.sell()

def create_sample_data():
    """创建模拟数据"""
    # 生成90天的模拟数据
    dates = pd.date_range(start='2024-07-01', periods=180, freq='D')
    
    # 过滤掉周末
    dates = dates[dates.weekday < 5]
    
    # 生成随机游走价格数据
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, len(dates))  # 日收益率
    prices = [100]  # 初始价格
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # 创建OHLCV数据
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        # 生成简单的OHLCV数据
        high = price * (1 + abs(np.random.normal(0, 0.01)))
        low = price * (1 - abs(np.random.normal(0, 0.01)))
        open_price = prices[i-1] if i > 0 else price
        volume = np.random.randint(1000, 10000)
        
        data.append({
            'datetime': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('datetime', inplace=True)
    
    return df

def run_backtest():
    """运行回测"""
    print("=== Backtrader 工作测试 ===")
    
    # 创建模拟数据
    print("生成模拟数据...")
    df = create_sample_data()
    print(f"数据范围: {df.index[0]} 到 {df.index[-1]}")
    print(f"数据点数: {len(df)}")
    
    # 创建数据源
    data_feed = bt.feeds.PandasData(
        dataname=df,
        datetime=None,
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=-1
    )
    
    # 创建Cerebro引擎
    cerebro = bt.Cerebro()
    
    # 添加数据
    cerebro.adddata(data_feed)
    
    # 添加策略
    cerebro.addstrategy(DualMovingAverageStrategy, ma_fast=5, ma_slow=20, printlog=True)
    
    # 设置初始资金
    cerebro.broker.setcash(100000)
    
    # 设置手续费
    cerebro.broker.setcommission(commission=0.001)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 打印初始资金
    print(f'初始资金: {cerebro.broker.getvalue():.2f}')
    
    # 运行回测
    print("开始回测...")
    results = cerebro.run()
    
    # 打印最终资金
    print(f'最终资金: {cerebro.broker.getvalue():.2f}')
    
    # 获取分析结果
    strat = results[0]
    
    # 计算收益率
    final_value = cerebro.broker.getvalue()
    total_return = (final_value - 100000) / 100000 * 100
    
    print(f'\n=== 回测结果 ===')
    print(f'总收益率: {total_return:.2f}%')
    
    # 获取分析器结果
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    trades = strat.analyzers.trades.get_analysis()
    
    sharpe_ratio = sharpe.get("sharperatio", 0)
    if sharpe_ratio is None:
        sharpe_ratio = 0
    print(f'夏普比率: {sharpe_ratio:.4f}')
    
    max_drawdown = drawdown.get("max", {}).get("drawdown", 0)
    if max_drawdown is None:
        max_drawdown = 0
    print(f'最大回撤: {max_drawdown:.2f}%')
    
    total_trades = trades.get("total", {}).get("total", 0)
    if total_trades is None:
        total_trades = 0
    print(f'总交易次数: {total_trades}')
    
    # 绘制结果
    try:
        print("生成图表...")
        cerebro.plot(style='candlestick', volume=False, iplot=False)
        plt.title('Backtrader 回测结果')
        plt.show()
    except Exception as e:
        print(f"绘图失败: {e}")
    
    print("回测完成！")

if __name__ == "__main__":
    run_backtest()
