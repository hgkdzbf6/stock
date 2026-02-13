#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtrader 策略适配器
将现有策略转换为 backtrader 格式
"""

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime

class BaseStrategy(bt.Strategy):
    """基础策略类"""
    
    params = (
        ('printlog', True),
    )
    
    def __init__(self):
        # 初始化指标
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.datavolume = self.datas[0].volume
        
        # 订单和价格跟踪
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # 添加指标到图表
        self.add_indicators()
    
    def add_indicators(self):
        """添加技术指标 - 子类需要重写"""
        pass
    
    def log(self, txt, dt=None):
        """日志记录"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}: {txt}')
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入执行, 价格: {order.executed.price:.2f}, '
                        f'成本: {order.executed.value:.2f}, 手续费: {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出执行, 价格: {order.executed.price:.2f}, '
                        f'成本: {order.executed.value:.2f}, 手续费: {order.executed.comm:.2f}')
            
            self.bar_executed = len(self)
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')
        
        self.order = None
    
    def notify_trade(self, trade):
        """交易通知"""
        if not trade.isclosed:
            return
        
        self.log(f'交易利润, 毛利润: {trade.pnl:.2f}, 净利润: {trade.pnlcomm:.2f}')
    
    def next(self):
        """策略主逻辑 - 子类需要重写"""
        self.log('收盘价', self.dataclose[0])
    
    def stop(self):
        """策略结束时的处理"""
        self.log(f'(策略结束) 期末资金: {self.broker.getvalue():.2f}', dt=self.datas[0].datetime.date(0))

class MovingAverageStrategy(BaseStrategy):
    """移动平均策略"""
    
    params = (
        ('ma_period', 20),
        ('printlog', True),
    )
    
    def add_indicators(self):
        self.ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.ma_period)
    
    def next(self):
        self.log(f'收盘价: {self.dataclose[0]:.2f}, MA: {self.ma[0]:.2f}')
        
        if not self.position:
            if self.dataclose[0] > self.ma[0]:
                self.log(f'买入信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.ma[0]:
                self.log(f'卖出信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.sell()

class DualMovingAverageStrategy(BaseStrategy):
    """双均线策略"""
    
    params = (
        ('ma_fast', 5),
        ('ma_slow', 20),
        ('printlog', True),
    )
    
    def add_indicators(self):
        self.ma_fast = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.ma_fast)
        self.ma_slow = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.ma_slow)
        self.crossover = bt.indicators.CrossOver(self.ma_fast, self.ma_slow)
    
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

class RSIStrategy(BaseStrategy):
    """RSI 策略"""
    
    params = (
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
        ('printlog', True),
    )
    
    def add_indicators(self):
        self.rsi = bt.indicators.RSI(self.datas[0], period=self.params.rsi_period)
    
    def next(self):
        self.log(f'收盘价: {self.dataclose[0]:.2f}, RSI: {self.rsi[0]:.2f}')
        
        if not self.position:
            if self.rsi[0] < self.params.rsi_lower:
                self.log(f'RSI超卖买入信号, 价格: {self.dataclose[0]:.2f}, RSI: {self.rsi[0]:.2f}')
                self.order = self.buy()
        else:
            if self.rsi[0] > self.params.rsi_upper:
                self.log(f'RSI超买卖出信号, 价格: {self.dataclose[0]:.2f}, RSI: {self.rsi[0]:.2f}')
                self.order = self.sell()

class MACDStrategy(BaseStrategy):
    """MACD 策略"""
    
    params = (
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('printlog', True),
    )
    
    def add_indicators(self):
        self.macd = bt.indicators.MACD(self.datas[0], 
                                      period_me1=self.params.macd_fast,
                                      period_me2=self.params.macd_slow,
                                      period_signal=self.params.macd_signal)
    
    def next(self):
        self.log(f'收盘价: {self.dataclose[0]:.2f}, MACD: {self.macd.macd[0]:.2f}, Signal: {self.macd.signal[0]:.2f}')
        
        if not self.position:
            if self.macd.macd[0] > self.macd.signal[0] and self.macd.macd[-1] <= self.macd.signal[-1]:
                self.log(f'MACD金叉买入信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.buy()
        else:
            if self.macd.macd[0] < self.macd.signal[0] and self.macd.macd[-1] >= self.macd.signal[-1]:
                self.log(f'MACD死叉卖出信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.sell()

class BollingerBandsStrategy(BaseStrategy):
    """布林带策略"""
    
    params = (
        ('bb_period', 20),
        ('bb_dev', 2),
        ('printlog', True),
    )
    
    def add_indicators(self):
        self.bb = bt.indicators.BollingerBands(self.datas[0], 
                                             period=self.params.bb_period,
                                             devfactor=self.params.bb_dev)
    
    def next(self):
        self.log(f'收盘价: {self.dataclose[0]:.2f}, 上轨: {self.bb.lines.top[0]:.2f}, 下轨: {self.bb.lines.bot[0]:.2f}')
        
        if not self.position:
            if self.dataclose[0] < self.bb.lines.bot[0]:
                self.log(f'布林带下轨买入信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.buy()
        else:
            if self.dataclose[0] > self.bb.lines.top[0]:
                self.log(f'布林带上轨卖出信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.sell()

class KDJStrategy(BaseStrategy):
    """KDJ 策略"""
    
    params = (
        ('kdj_period', 9),
        ('kdj_upper', 80),
        ('kdj_lower', 20),
        ('printlog', True),
    )
    
    def add_indicators(self):
        # KDJ 指标需要自定义实现
        self.kdj_k = bt.indicators.Stochastic(self.datas[0], period=self.params.kdj_period)
        self.kdj_d = bt.indicators.SmoothedMovingAverage(self.kdj_k, period=3)
        self.kdj_j = 3 * self.kdj_k - 2 * self.kdj_d
    
    def next(self):
        self.log(f'收盘价: {self.dataclose[0]:.2f}, K: {self.kdj_k[0]:.2f}, D: {self.kdj_d[0]:.2f}, J: {self.kdj_j[0]:.2f}')
        
        if not self.position:
            if self.kdj_k[0] < self.params.kdj_lower and self.kdj_d[0] < self.params.kdj_lower:
                self.log(f'KDJ超卖买入信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.buy()
        else:
            if self.kdj_k[0] > self.params.kdj_upper and self.kdj_d[0] > self.params.kdj_upper:
                self.log(f'KDJ超买卖出信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.sell()

class MeanReversionStrategy(BaseStrategy):
    """均值回归策略"""
    
    params = (
        ('lookback', 20),
        ('threshold', 2),
        ('printlog', True),
    )
    
    def add_indicators(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.lookback)
        self.std = bt.indicators.StandardDeviation(self.datas[0], period=self.params.lookback)
    
    def next(self):
        if len(self) < self.params.lookback:
            return
        
        upper_band = self.sma[0] + self.params.threshold * self.std[0]
        lower_band = self.sma[0] - self.params.threshold * self.std[0]
        
        self.log(f'收盘价: {self.dataclose[0]:.2f}, 上轨: {upper_band:.2f}, 下轨: {lower_band:.2f}')
        
        if not self.position:
            if self.dataclose[0] < lower_band:
                self.log(f'均值回归买入信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.buy()
        else:
            if self.dataclose[0] > upper_band:
                self.log(f'均值回归卖出信号, 价格: {self.dataclose[0]:.2f}')
                self.order = self.sell()

class GridTradingStrategy(BaseStrategy):
    """网格交易策略"""
    
    params = (
        ('grid_size', 0.02),  # 网格大小 2%
        ('max_position', 10),  # 最大持仓数量
        ('printlog', True),
    )
    
    def __init__(self):
        super().__init__()
        self.grid_levels = []
        self.position_count = 0
    
    def add_indicators(self):
        pass
    
    def next(self):
        if len(self) < 2:
            return
        
        current_price = self.dataclose[0]
        
        # 初始化网格
        if not self.grid_levels:
            base_price = current_price
            for i in range(-self.params.max_position//2, self.params.max_position//2 + 1):
                level = base_price * (1 + i * self.params.grid_size)
                self.grid_levels.append(level)
        
        # 检查网格交易信号
        for i, level in enumerate(self.grid_levels):
            if not self.position and current_price <= level * 0.99:  # 买入信号
                self.log(f'网格买入信号, 价格: {current_price:.2f}, 网格: {level:.2f}')
                self.order = self.buy()
                self.position_count += 1
                break
            elif self.position and current_price >= level * 1.01:  # 卖出信号
                self.log(f'网格卖出信号, 价格: {current_price:.2f}, 网格: {level:.2f}')
                self.order = self.sell()
                self.position_count -= 1
                break

class TestStrategy(BaseStrategy):
    """测试策略"""
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入执行, 价格: {order.executed.price:.2f}')
            else:
                self.log(f'卖出执行, 价格: {order.executed.price:.2f}')
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')
        self.order = None

    def next(self):
        self.log(f'收盘价: {self.dataclose[0]:.2f}')
        if self.order:
            return
        if not self.position:
            if self.dataclose[0] > self.dataclose[-1]:
                if self.dataclose[-1] > self.dataclose[-2]:
                    self.log(f'买入信号, 价格: {self.dataclose[0]:.2f}')
                    self.order = self.buy()
            if len(self) >= self.bar_executed + 5:
                self.log(f'持仓时间: {len(self) - self.bar_executed} 天')
                self.log(f'卖出信号, 价格: {self.dataclose[0]:.2f}')
                self.log(f'持仓利润: {self.broker.getvalue() - self.initial_capital:.2f}')
                self.order = self.sell()

# 策略工厂
STRATEGY_MAP = {
    'MA': MovingAverageStrategy,
    'DualMA': DualMovingAverageStrategy,
    'RSI': RSIStrategy,
    'MACD': MACDStrategy,
    'BOLL': BollingerBandsStrategy,
    'KDJ': KDJStrategy,
    'MeanReversion': MeanReversionStrategy,
    'Grid': GridTradingStrategy,
    'Test': TestStrategy,
}

def get_strategy(strategy_name):
    """获取策略类"""
    if strategy_name not in STRATEGY_MAP:
        raise ValueError(f"不支持的策略: {strategy_name}")
    
    return STRATEGY_MAP[strategy_name]

if __name__ == "__main__":
    """测试策略模块"""
    print("=== Backtrader 策略模块测试 ===")
    print(f"\n可用策略列表:")
    for i, (name, strategy_class) in enumerate(STRATEGY_MAP.items(), 1):
        print(f"{i}. {name}: {strategy_class.__name__}")
    
    print(f"\n共 {len(STRATEGY_MAP)} 个策略")
    print("\n策略模块加载成功！")
