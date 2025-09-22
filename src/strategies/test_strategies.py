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

class TestStrategy(BaseStrategy):
    """测试策略"""
    def __init__(self):
        super().__init__("测试策略")
        
    def calculate_signals(self, df):
        """计算交易信号"""
        df = df.copy()
        df['signal'] = 0
        return df
        