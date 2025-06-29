"""
动量策略
基于价格动量和技术指标的交易策略
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .technical_indicators import TechnicalIndicators, HAS_TALIB

if HAS_TALIB:
    import talib

class RSIStrategy(BaseStrategy):
    """RSI相对强弱指标策略 - 改进版"""
    def __init__(self, rsi_window=14, oversold=30, overbought=70, stop_loss=0.04, take_profit=0.08):
        super().__init__("RSI相对强弱指标策略")
        self.rsi_window = rsi_window
        self.oversold = oversold
        self.overbought = overbought
        self.set_risk_management(stop_loss, take_profit)
        
    def calculate_signals(self, df):
        """计算RSI交易信号"""
        df = df.copy()
        
        # 计算RSI
        df['RSI'] = TechnicalIndicators.RSI(df['close'], self.rsi_window)
        
        # 计算价格动量确认
        df['Price_SMA'] = TechnicalIndicators.SMA(df['close'], 10)
        df['Volume_SMA'] = df['volume'].rolling(20).mean()
        
        # 生成交易信号
        df['signal'] = 0
        
        for i in range(1, len(df)):
            rsi_curr = df['RSI'].iloc[i]
            rsi_prev = df['RSI'].iloc[i-1]
            price_trend = df['close'].iloc[i] > df['Price_SMA'].iloc[i]
            volume_confirm = df['volume'].iloc[i] > df['Volume_SMA'].iloc[i]
            
            # RSI从超卖区域向上突破，且有价格和成交量确认
            if (rsi_prev <= self.oversold and rsi_curr > self.oversold and 
                price_trend and volume_confirm):
                df.loc[df.index[i], 'signal'] = 1
                
            # RSI从超买区域向下突破，且有价格确认
            elif (rsi_prev >= self.overbought and rsi_curr < self.overbought and 
                  not price_trend):
                df.loc[df.index[i], 'signal'] = -1
        
        return df

class MACDStrategy(BaseStrategy):
    """MACD指标策略 - 改进版"""
    def __init__(self, fast_period=12, slow_period=26, signal_period=9, stop_loss=0.04, take_profit=0.08):
        super().__init__("MACD指标策略")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.set_risk_management(stop_loss, take_profit)
        
    def calculate_signals(self, df):
        """计算MACD交易信号"""
        df = df.copy()
        
        # 计算MACD
        macd, macd_signal, macd_hist = TechnicalIndicators.MACD(
            df['close'], self.fast_period, self.slow_period, self.signal_period
        )
        df['MACD'] = macd
        df['MACD_signal'] = macd_signal
        df['MACD_hist'] = macd_hist
        
        # 计算趋势确认指标
        df['EMA_50'] = TechnicalIndicators.EMA(df['close'], 50)
        
        # 生成交易信号
        df['signal'] = 0
        
        for i in range(1, len(df)):
            # MACD金叉且柱状图增长，价格在长期趋势上方
            macd_bullish = (df['MACD'].iloc[i-1] <= df['MACD_signal'].iloc[i-1] and 
                           df['MACD'].iloc[i] > df['MACD_signal'].iloc[i])
            hist_growing = df['MACD_hist'].iloc[i] > df['MACD_hist'].iloc[i-1]
            above_trend = df['close'].iloc[i] > df['EMA_50'].iloc[i]
            
            if macd_bullish and hist_growing and above_trend:
                df.loc[df.index[i], 'signal'] = 1
                
            # MACD死叉且柱状图下降
            macd_bearish = (df['MACD'].iloc[i-1] >= df['MACD_signal'].iloc[i-1] and 
                           df['MACD'].iloc[i] < df['MACD_signal'].iloc[i])
            hist_declining = df['MACD_hist'].iloc[i] < df['MACD_hist'].iloc[i-1]
            
            if macd_bearish and hist_declining:
                df.loc[df.index[i], 'signal'] = -1
        
        return df

class KDJStrategy(BaseStrategy):
    """KDJ随机指标策略 - 改进版"""
    def __init__(self, k_period=9, d_period=3, j_period=3, stop_loss=0.03, take_profit=0.06):
        super().__init__("KDJ随机指标策略")
        self.k_period = k_period
        self.d_period = d_period
        self.j_period = j_period
        self.set_risk_management(stop_loss, take_profit)
        
    def calculate_signals(self, df):
        """计算KDJ交易信号"""
        df = df.copy()
        
        # 计算KDJ
        k, d = TechnicalIndicators.STOCH(
            df['high'], df['low'], df['close'], self.k_period, self.d_period
        )
        df['K'] = k
        df['D'] = d
        df['J'] = 3 * k - 2 * d
        
        # 计算价格趋势确认
        df['Price_Trend'] = df['close'].rolling(5).mean()
        
        # 生成交易信号，减少交易频率
        df['signal'] = 0
        
        for i in range(max(self.k_period, 10), len(df)):
            k_val = df['K'].iloc[i]
            d_val = df['D'].iloc[i]
            j_val = df['J'].iloc[i]
            
            k_prev = df['K'].iloc[i-1]
            d_prev = df['D'].iloc[i-1]
            
            price_rising = df['close'].iloc[i] > df['Price_Trend'].iloc[i-3]
            
            # 限制交易频率：只在超买超卖区域交易
            # KDJ金叉且在超卖区域，价格有上涨趋势
            if (k_prev <= d_prev and k_val > d_val and 
                k_val < 30 and j_val < 20 and price_rising):
                df.loc[df.index[i], 'signal'] = 1
                
            # KDJ死叉且在超买区域
            elif (k_prev >= d_prev and k_val < d_val and 
                  k_val > 70 and j_val > 80):
                df.loc[df.index[i], 'signal'] = -1
        
        return df 