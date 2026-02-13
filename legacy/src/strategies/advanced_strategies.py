"""
高级交易策略
包含更复杂的量化交易策略
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .technical_indicators import TechnicalIndicators

class MeanReversionStrategy(BaseStrategy):
    """均值回归策略"""
    def __init__(self, lookback=20, threshold=2.0, stop_loss=0.03, take_profit=0.06):
        super().__init__("均值回归策略")
        self.lookback = lookback
        self.threshold = threshold
        self.set_risk_management(stop_loss, take_profit)
        
    def calculate_signals(self, df):
        """计算均值回归信号"""
        df = df.copy()
        
        # 计算移动平均和标准差
        df['SMA'] = TechnicalIndicators.SMA(df['close'], self.lookback)
        df['STD'] = df['close'].rolling(window=self.lookback).std()
        
        # 计算Z-Score
        df['Z_Score'] = (df['close'] - df['SMA']) / df['STD']
        
        # 计算RSI作为过滤器
        df['RSI'] = TechnicalIndicators.RSI(df['close'])
        
        # 生成信号
        df['signal'] = 0
        
        for i in range(self.lookback, len(df)):
            z_score = df['Z_Score'].iloc[i]
            rsi = df['RSI'].iloc[i]
            
            # 价格过度偏离均值时买入（均值回归）
            if z_score < -self.threshold and rsi < 40:  # 超卖且偏离
                df.loc[df.index[i], 'signal'] = 1
            elif z_score > self.threshold and rsi > 60:  # 超买且偏离
                df.loc[df.index[i], 'signal'] = -1
            # 回归到均值附近时平仓
            elif abs(z_score) < 0.5:
                df.loc[df.index[i], 'signal'] = 0
        
        return df

class TrendFollowingStrategy(BaseStrategy):
    """趋势跟踪策略"""
    def __init__(self, atr_period=14, atr_multiplier=2.0, trend_period=50):
        super().__init__("趋势跟踪策略")
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.trend_period = trend_period
        
    def calculate_signals(self, df):
        """计算趋势跟踪信号"""
        df = df.copy()
        
        # 计算ATR和趋势指标
        df['ATR'] = TechnicalIndicators.ATR(df['high'], df['low'], df['close'], self.atr_period)
        df['SMA_trend'] = TechnicalIndicators.SMA(df['close'], self.trend_period)
        
        # 计算动态支撑阻力位
        df['Upper_Band'] = df['close'] + self.atr_multiplier * df['ATR']
        df['Lower_Band'] = df['close'] - self.atr_multiplier * df['ATR']
        
        # 计算MACD确认趋势
        macd, macd_signal, macd_hist = TechnicalIndicators.MACD(df['close'])
        df['MACD_hist'] = macd_hist
        
        # 生成信号
        df['signal'] = 0
        
        for i in range(1, len(df)):
            price = df['close'].iloc[i]
            trend = df['SMA_trend'].iloc[i]
            macd_momentum = df['MACD_hist'].iloc[i]
            
            # 趋势向上且有动量确认
            if (price > trend and 
                df['close'].iloc[i] > df['close'].iloc[i-1] and
                macd_momentum > 0):
                df.loc[df.index[i], 'signal'] = 1
                
            # 趋势向下且有动量确认  
            elif (price < trend and 
                  df['close'].iloc[i] < df['close'].iloc[i-1] and
                  macd_momentum < 0):
                df.loc[df.index[i], 'signal'] = -1
        
        return df

class IchimokuStrategy(BaseStrategy):
    """一目均衡表策略"""
    def __init__(self):
        super().__init__("一目均衡表策略")
        
    def calculate_signals(self, df):
        """计算一目均衡表信号"""
        df = df.copy()
        
        # 计算一目均衡表各线
        conversion, baseline, span_a, span_b, lagging = TechnicalIndicators.ICHIMOKU(
            df['high'], df['low'], df['close'])
        
        df['Conversion'] = conversion
        df['Baseline'] = baseline
        df['Span_A'] = span_a
        df['Span_B'] = span_b
        df['Lagging'] = lagging
        
        # 生成信号
        df['signal'] = 0
        
        for i in range(26, len(df)):  # 需要足够的历史数据
            price = df['close'].iloc[i]
            conv = df['Conversion'].iloc[i]
            base = df['Baseline'].iloc[i]
            
            # 多头信号：价格在云上方，转换线在基准线上方
            if (price > max(df['Span_A'].iloc[i], df['Span_B'].iloc[i]) and
                conv > base and
                df['Conversion'].iloc[i-1] <= df['Baseline'].iloc[i-1]):
                df.loc[df.index[i], 'signal'] = 1
                
            # 空头信号：价格在云下方，转换线在基准线下方
            elif (price < min(df['Span_A'].iloc[i], df['Span_B'].iloc[i]) and
                  conv < base and
                  df['Conversion'].iloc[i-1] >= df['Baseline'].iloc[i-1]):
                df.loc[df.index[i], 'signal'] = -1
        
        return df

class WilliamsRStrategy(BaseStrategy):
    """威廉指标策略"""
    def __init__(self, period=14, overbought=-20, oversold=-80):
        super().__init__("威廉指标策略")
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        
    def calculate_signals(self, df):
        """计算威廉指标信号"""
        df = df.copy()
        
        # 计算威廉指标
        df['Williams_R'] = TechnicalIndicators.Williams_R(
            df['high'], df['low'], df['close'], self.period)
        
        # 计算价格动量确认
        df['Price_Change'] = df['close'].pct_change()
        df['Volume_SMA'] = df['volume'].rolling(20).mean()
        
        # 生成信号
        df['signal'] = 0
        
        for i in range(1, len(df)):
            wr = df['Williams_R'].iloc[i]
            wr_prev = df['Williams_R'].iloc[i-1]
            volume_above_avg = df['volume'].iloc[i] > df['Volume_SMA'].iloc[i]
            
            # 从超卖区域向上突破
            if (wr_prev < self.oversold and wr > self.oversold and
                df['Price_Change'].iloc[i] > 0 and volume_above_avg):
                df.loc[df.index[i], 'signal'] = 1
                
            # 从超买区域向下突破
            elif (wr_prev > self.overbought and wr < self.overbought and
                  df['Price_Change'].iloc[i] < 0 and volume_above_avg):
                df.loc[df.index[i], 'signal'] = -1
        
        return df

class PairsTradingStrategy(BaseStrategy):
    """配对交易策略（简化版）"""
    def __init__(self, lookback=30, threshold=2.0):
        super().__init__("配对交易策略")
        self.lookback = lookback
        self.threshold = threshold
        
    def calculate_signals(self, df):
        """计算配对交易信号"""
        df = df.copy()
        
        # 使用价格与其移动平均的比值作为"配对"
        df['SMA'] = TechnicalIndicators.SMA(df['close'], self.lookback)
        df['Ratio'] = df['close'] / df['SMA']
        
        # 计算比值的移动平均和标准差
        df['Ratio_SMA'] = df['Ratio'].rolling(self.lookback).mean()
        df['Ratio_STD'] = df['Ratio'].rolling(self.lookback).std()
        
        # 计算Z-Score
        df['Z_Score'] = (df['Ratio'] - df['Ratio_SMA']) / df['Ratio_STD']
        
        # 生成信号
        df['signal'] = 0
        
        for i in range(self.lookback, len(df)):
            z_score = df['Z_Score'].iloc[i]
            
            # 比值偏离过大时进行配对交易
            if z_score > self.threshold:  # 价格相对过高，卖出
                df.loc[df.index[i], 'signal'] = -1
            elif z_score < -self.threshold:  # 价格相对过低，买入
                df.loc[df.index[i], 'signal'] = 1
            elif abs(z_score) < 0.5:  # 回归到正常水平，平仓
                df.loc[df.index[i], 'signal'] = 0
        
        return df 