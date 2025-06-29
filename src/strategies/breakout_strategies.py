"""
突破策略
基于价格突破的交易策略
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .technical_indicators import TechnicalIndicators

class DualThrustStrategy(BaseStrategy):
    """Dual Thrust策略 - 改进版"""
    def __init__(self, window=10, k1=0.4, k2=0.6, stop_loss=0.05, take_profit=0.10):
        super().__init__("Dual Thrust策略")
        self.window = window
        self.k1 = k1
        self.k2 = k2
        self.set_risk_management(stop_loss, take_profit)
        
    def calculate_signals(self, df):
        """计算Dual Thrust交易信号"""
        df = df.copy()
        
        # 计算HH, HC, LC, LL
        df['HH'] = df['high'].rolling(window=self.window).max()
        df['HC'] = df['close'].rolling(window=self.window).max()
        df['LC'] = df['close'].rolling(window=self.window).min()
        df['LL'] = df['low'].rolling(window=self.window).min()
        
        # 计算Range
        df['Range'] = np.maximum(df['HH'] - df['LC'], df['HC'] - df['LL'])
        
        # 计算上下轨，使用前一日的开盘价
        df['upper_bound'] = df['open'] + self.k1 * df['Range'].shift(1)
        df['lower_bound'] = df['open'] - self.k2 * df['Range'].shift(1)
        
        # 计算ATR用于过滤小幅突破
        df['ATR'] = TechnicalIndicators.ATR(df['high'], df['low'], df['close'])
        
        # 计算成交量确认
        df['Volume_SMA'] = df['volume'].rolling(20).mean()
        
        # 生成交易信号
        df['signal'] = 0
        
        for i in range(self.window, len(df)):
            # 确保有足够的历史数据
            if pd.isna(df['upper_bound'].iloc[i]) or pd.isna(df['lower_bound'].iloc[i]):
                continue
                
            price = df['close'].iloc[i]
            upper = df['upper_bound'].iloc[i]
            lower = df['lower_bound'].iloc[i]
            atr = df['ATR'].iloc[i]
            volume_confirm = df['volume'].iloc[i] > df['Volume_SMA'].iloc[i] * 1.2
            
            # 向上突破且有成交量确认
            if (price > upper and 
                (price - upper) > atr * 0.5 and  # 突破幅度足够大
                volume_confirm):
                df.loc[df.index[i], 'signal'] = 1
                
            # 向下突破且有成交量确认
            elif (price < lower and 
                  (lower - price) > atr * 0.5 and  # 突破幅度足够大
                  volume_confirm):
                df.loc[df.index[i], 'signal'] = -1
        
        return df 