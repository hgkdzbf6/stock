"""
波动率策略
基于价格波动率的交易策略
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .technical_indicators import TechnicalIndicators

class BOLLStrategy(BaseStrategy):
    """布林带策略 - 改进版"""
    def __init__(self, period=20, std_dev=2, stop_loss=0.04, take_profit=0.08):
        super().__init__("布林带策略")
        self.period = period
        self.std_dev = std_dev
        self.set_risk_management(stop_loss, take_profit)
        
    def calculate_signals(self, df):
        """计算布林带交易信号"""
        df = df.copy()
        
        # 计算布林带
        upper, middle, lower = TechnicalIndicators.BBANDS(
            df['close'], self.period, self.std_dev
        )
        df['BOLL_upper'] = upper
        df['BOLL_middle'] = middle
        df['BOLL_lower'] = lower
        
        # 计算带宽和位置
        df['BB_width'] = (df['BOLL_upper'] - df['BOLL_lower']) / df['BOLL_middle']
        df['BB_position'] = (df['close'] - df['BOLL_lower']) / (df['BOLL_upper'] - df['BOLL_lower'])
        
        # 计算RSI作为确认指标
        df['RSI'] = TechnicalIndicators.RSI(df['close'])
        
        # 生成交易信号
        df['signal'] = 0
        
        for i in range(1, len(df)):
            bb_pos = df['BB_position'].iloc[i]
            bb_width = df['BB_width'].iloc[i]
            rsi = df['RSI'].iloc[i]
            
            # 价格接近下轨且RSI超卖，带宽不过窄（避免横盘）
            if (bb_pos < 0.2 and rsi < 35 and bb_width > 0.02 and
                df['close'].iloc[i] > df['close'].iloc[i-1]):  # 价格开始反弹
                df.loc[df.index[i], 'signal'] = 1
                
            # 价格接近上轨且RSI超买
            elif (bb_pos > 0.8 and rsi > 65 and
                  df['close'].iloc[i] < df['close'].iloc[i-1]):  # 价格开始回落
                df.loc[df.index[i], 'signal'] = -1
                
            # 价格回归中轨附近时考虑平仓
            elif 0.4 < bb_pos < 0.6:
                # 根据持仓方向决定是否平仓
                if hasattr(self, 'position') and self.position != 0:
                    df.loc[df.index[i], 'signal'] = 0
        
        return df 