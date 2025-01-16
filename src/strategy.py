import pandas as pd
import numpy as np

class MAStrategy:
    def __init__(self, short_window=5, long_window=20, stop_loss=0.20):
        self.short_window = short_window
        self.long_window = long_window
        self.stop_loss = stop_loss
        
    def calculate_signals(self, df):
        """计算交易信号"""
        # 计算移动平均线
        df['MA_short'] = df['close'].rolling(window=self.short_window).mean()
        df['MA_long'] = df['close'].rolling(window=self.long_window).mean()
        
        # 计算每日收益率
        df['daily_returns'] = df['close'].pct_change()
        
        # 计算从最高点的跌幅
        df['cummax'] = df['close'].cummax()
        df['drawdown'] = (df['close'] - df['cummax']) / df['cummax']
        
        # 生成交易信号
        df['signal'] = 0
        # 金叉买入信号
        df.loc[df['MA_short'] > df['MA_long'], 'signal'] = 1
        # 死叉卖出信号
        df.loc[df['MA_short'] < df['MA_long'], 'signal'] = -1
        
        # 止损信号（跌幅超过20%）
        df.loc[df['drawdown'] <= -self.stop_loss, 'signal'] = -1
        
        # T+1交易：买入信号后推一天
        df['signal'] = df['signal'].shift(1)
        
        return df 