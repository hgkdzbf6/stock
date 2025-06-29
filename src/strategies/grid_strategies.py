"""
网格策略
基于网格交易的策略
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .technical_indicators import TechnicalIndicators

class GridStrategy(BaseStrategy):
    """网格交易策略 - 改进版"""
    def __init__(self, grid_ratio=0.03, max_grids=8, base_period=30):
        super().__init__("网格交易策略")
        self.grid_ratio = grid_ratio  # 网格间距比例
        self.max_grids = max_grids
        self.base_period = base_period
        
    def calculate_signals(self, df):
        """计算网格交易信号"""
        df = df.copy()
        
        # 计算基准价格（使用VWAP或移动平均）
        if 'volume' in df.columns:
            # 使用VWAP作为基准
            df['base_price'] = TechnicalIndicators.VWAP(
                df['high'], df['low'], df['close'], df['volume']
            ).rolling(self.base_period).mean()
        else:
            # 使用移动平均作为基准
            df['base_price'] = TechnicalIndicators.SMA(df['close'], self.base_period)
        
        # 计算价格相对基准的偏离度
        df['price_deviation'] = (df['close'] - df['base_price']) / df['base_price']
        
        # 计算波动率过滤器
        df['volatility'] = df['close'].rolling(20).std() / df['close'].rolling(20).mean()
        
        # 生成交易信号
        df['signal'] = 0
        
        for i in range(self.base_period, len(df)):
            deviation = df['price_deviation'].iloc[i]
            volatility = df['volatility'].iloc[i]
            
            # 只在适度波动的市场中使用网格策略
            if 0.01 < volatility < 0.05:
                # 计算网格层级
                grid_level = int(abs(deviation) / self.grid_ratio)
                
                if grid_level > 0 and grid_level <= self.max_grids:
                    if deviation < -self.grid_ratio:  # 价格下跌，分批买入
                        df.loc[df.index[i], 'signal'] = 1
                    elif deviation > self.grid_ratio:  # 价格上涨，分批卖出
                        df.loc[df.index[i], 'signal'] = -1
        
        return df 