"""
移动平均策略
包含各种基于移动平均线的交易策略
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .technical_indicators import TechnicalIndicators, HAS_TALIB

if HAS_TALIB:
    import talib

class MAStrategy(BaseStrategy):
    """双均线策略 - 改进版"""
    def __init__(self, short_window=5, long_window=20, stop_loss=0.05, take_profit=0.10):
        super().__init__("双均线策略")
        self.short_window = short_window
        self.long_window = long_window
        self.set_risk_management(stop_loss, take_profit)
        
    def calculate_signals(self, df):
        """计算交易信号"""
        df = df.copy()
        
        # 计算移动平均线
        df['MA_short'] = TechnicalIndicators.SMA(df['close'], self.short_window)
        df['MA_long'] = TechnicalIndicators.SMA(df['close'], self.long_window)
        
        # 计算ATR用于动态止损
        df['ATR'] = TechnicalIndicators.ATR(df['high'], df['low'], df['close'])
        
        # 生成交易信号
        df['signal'] = 0
        
        # 改进的信号生成：增加趋势确认
        for i in range(1, len(df)):
            # 金叉买入条件：短期均线向上突破长期均线，且有一定的分离度
            if (df['MA_short'].iloc[i-1] <= df['MA_long'].iloc[i-1] and 
                df['MA_short'].iloc[i] > df['MA_long'].iloc[i] and
                (df['MA_short'].iloc[i] - df['MA_long'].iloc[i]) / df['MA_long'].iloc[i] > 0.005):  # 0.5%分离度
                df.loc[df.index[i], 'signal'] = 1
                
            # 死叉卖出条件：短期均线向下跌破长期均线
            elif (df['MA_short'].iloc[i-1] >= df['MA_long'].iloc[i-1] and 
                  df['MA_short'].iloc[i] < df['MA_long'].iloc[i]):
                df.loc[df.index[i], 'signal'] = -1
        
        return df

class EMAStrategy(BaseStrategy):
    """EMA指数移动平均策略 - 改进版"""
    def __init__(self, fast_window=12, slow_window=26, signal_window=9, stop_loss=0.05, take_profit=0.10):
        super().__init__("EMA指数移动平均策略")
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.signal_window = signal_window
        self.set_risk_management(stop_loss, take_profit)
        
    def calculate_signals(self, df):
        """计算EMA交易信号"""
        df = df.copy()
        
        # 计算EMA
        df['EMA_fast'] = TechnicalIndicators.EMA(df['close'], self.fast_window)
        df['EMA_slow'] = TechnicalIndicators.EMA(df['close'], self.slow_window)
        df['EMA_signal'] = TechnicalIndicators.EMA(df['close'], self.signal_window)
        
        # 计算MACD作为辅助确认
        macd, macd_signal, macd_hist = TechnicalIndicators.MACD(df['close'])
        df['MACD'] = macd
        df['MACD_signal'] = macd_signal
        df['MACD_hist'] = macd_hist
        
        # 生成交易信号
        df['signal'] = 0
        
        for i in range(1, len(df)):
            # 多重确认买入信号
            ema_bullish = (df['EMA_fast'].iloc[i-1] <= df['EMA_slow'].iloc[i-1] and 
                          df['EMA_fast'].iloc[i] > df['EMA_slow'].iloc[i])
            macd_bullish = (df['MACD_hist'].iloc[i] > 0 and 
                           df['MACD_hist'].iloc[i] > df['MACD_hist'].iloc[i-1])
            price_above_signal = df['close'].iloc[i] > df['EMA_signal'].iloc[i]
            
            if ema_bullish and macd_bullish and price_above_signal:
                df.loc[df.index[i], 'signal'] = 1
                
            # 多重确认卖出信号
            ema_bearish = (df['EMA_fast'].iloc[i-1] >= df['EMA_slow'].iloc[i-1] and 
                          df['EMA_fast'].iloc[i] < df['EMA_slow'].iloc[i])
            macd_bearish = (df['MACD_hist'].iloc[i] < 0 and 
                           df['MACD_hist'].iloc[i] < df['MACD_hist'].iloc[i-1])
            price_below_signal = df['close'].iloc[i] < df['EMA_signal'].iloc[i]
            
            if ema_bearish and (macd_bearish or price_below_signal):
                df.loc[df.index[i], 'signal'] = -1
        
        return df 