"""
技术指标计算类
提供各种技术指标的计算方法，作为talib的替代实现
"""

from .base_strategy import BaseStrategy
class TestStrategy(BaseStrategy):
    """测试策略"""
    def __init__(self, lookback=20, threshold=2.0, stop_loss=0.03, take_profit=0.06):
        super().__init__("测试策略")
        self.lookback = lookback
        self.threshold = threshold
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def calculate_signals(self, df):
        """计算测试信号"""
        df = df.copy()