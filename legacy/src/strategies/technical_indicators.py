"""
技术指标计算类
提供各种技术指标的计算方法，作为talib的替代实现
"""

import pandas as pd
import numpy as np

# 尝试导入talib，如果失败则使用自定义实现
try:
    import talib
    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False
    print("警告：未安装talib库，使用内置技术指标实现")

class TechnicalIndicators:
    """技术指标计算类 - talib的替代实现"""
    
    @staticmethod
    def SMA(prices, period):
        """简单移动平均"""
        return prices.rolling(window=period).mean()
    
    @staticmethod
    def EMA(prices, period):
        """指数移动平均"""
        return prices.ewm(span=period).mean()
    
    @staticmethod
    def RSI(prices, period=14):
        """相对强弱指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def MACD(prices, fast_period=12, slow_period=26, signal_period=9):
        """MACD指标"""
        ema_fast = TechnicalIndicators.EMA(prices, fast_period)
        ema_slow = TechnicalIndicators.EMA(prices, slow_period)
        macd = ema_fast - ema_slow
        signal = TechnicalIndicators.EMA(macd, signal_period)
        histogram = macd - signal
        return macd, signal, histogram
    
    @staticmethod
    def BBANDS(prices, period=20, std_dev=2):
        """布林带"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
    
    @staticmethod
    def STOCH(high, low, close, k_period=9, d_period=3):
        """随机指标KDJ"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        k_percent = k_percent.rolling(window=d_period).mean()
        d_percent = k_percent.rolling(window=d_period).mean()
        return k_percent, d_percent
    
    @staticmethod
    def ATR(high, low, close, period=14):
        """平均真实波幅"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def CCI(high, low, close, period=20):
        """商品通道指数"""
        tp = (high + low + close) / 3
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (tp - sma) / (0.015 * mad)
        return cci
    
    @staticmethod
    def Williams_R(high, low, close, period=14):
        """威廉指标"""
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        wr = -100 * (highest_high - close) / (highest_high - lowest_low)
        return wr
    
    @staticmethod
    def ICHIMOKU(high, low, close):
        """一目均衡表"""
        # 转换线 (9日高低点平均)
        conversion = (high.rolling(9).max() + low.rolling(9).min()) / 2
        
        # 基准线 (26日高低点平均)
        baseline = (high.rolling(26).max() + low.rolling(26).min()) / 2
        
        # 先行带A (转换线+基准线)/2，向前移26日
        span_a = ((conversion + baseline) / 2).shift(26)
        
        # 先行带B (52日高低点平均)，向前移26日
        span_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
        
        # 滞后线 (收盘价向后移26日)
        lagging = close.shift(-26)
        
        return conversion, baseline, span_a, span_b, lagging
    
    @staticmethod
    def VWAP(high, low, close, volume):
        """成交量加权平均价"""
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap
    
    @staticmethod
    def OBV(close, volume):
        """能量潮"""
        obv = volume.copy()
        obv[close < close.shift()] *= -1
        obv[close == close.shift()] = 0
        return obv.cumsum()
    
    @staticmethod
    def AROON(high, low, period=14):
        """阿隆指标"""
        aroon_up = 100 * (period - high.rolling(period).apply(lambda x: period - 1 - x.argmax())) / period
        aroon_down = 100 * (period - low.rolling(period).apply(lambda x: period - 1 - x.argmin())) / period
        return aroon_up, aroon_down 