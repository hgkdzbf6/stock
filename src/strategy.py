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

class BaseStrategy:
    """策略基类"""
    def __init__(self, name="BaseStrategy"):
        self.name = name
    
    def calculate_signals(self, df):
        """计算交易信号，子类需要实现此方法"""
        raise NotImplementedError("子类必须实现calculate_signals方法")

class MAStrategy(BaseStrategy):
    """双均线策略"""
    def __init__(self, short_window=5, long_window=20, stop_loss=0.20):
        super().__init__("双均线策略")
        self.short_window = short_window
        self.long_window = long_window
        self.stop_loss = stop_loss
        
    def calculate_signals(self, df):
        """计算交易信号"""
        df = df.copy()
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
        
        # 止损信号（跌幅超过设定值）
        df.loc[df['drawdown'] <= -self.stop_loss, 'signal'] = -1
        
        return df

class EMAStrategy(BaseStrategy):
    """EMA指数移动平均策略"""
    def __init__(self, fast_window=5, slow_window=20, stop_loss=0.10):
        super().__init__("EMA指数移动平均策略")
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.stop_loss = stop_loss
        
    def calculate_signals(self, df):
        """计算EMA交易信号"""
        df = df.copy()
        
        # 计算EMA
        if HAS_TALIB:
            df['EMA_fast'] = talib.EMA(df['close'].values, timeperiod=self.fast_window)
            df['EMA_slow'] = talib.EMA(df['close'].values, timeperiod=self.slow_window)
        else:
            df['EMA_fast'] = TechnicalIndicators.EMA(df['close'], self.fast_window)
            df['EMA_slow'] = TechnicalIndicators.EMA(df['close'], self.slow_window)
        
        # 计算回撤
        df['cummax'] = df['close'].cummax()
        df['drawdown'] = (df['close'] - df['cummax']) / df['cummax']
        
        # 生成交易信号
        df['signal'] = 0
        
        # EMA金叉买入，死叉卖出
        for i in range(1, len(df)):
            if (df['EMA_fast'].iloc[i-1] <= df['EMA_slow'].iloc[i-1] and 
                df['EMA_fast'].iloc[i] > df['EMA_slow'].iloc[i]):
                df.loc[df.index[i], 'signal'] = 1  # 买入信号
            elif (df['EMA_fast'].iloc[i-1] >= df['EMA_slow'].iloc[i-1] and 
                  df['EMA_fast'].iloc[i] < df['EMA_slow'].iloc[i]):
                df.loc[df.index[i], 'signal'] = -1  # 卖出信号
        
        # 止损信号
        df.loc[df['drawdown'] <= -self.stop_loss, 'signal'] = -1
        
        return df

class RSIStrategy(BaseStrategy):
    """RSI相对强弱指标策略"""
    def __init__(self, rsi_window=14, oversold=30, overbought=70):
        super().__init__("RSI相对强弱指标策略")
        self.rsi_window = rsi_window
        self.oversold = oversold
        self.overbought = overbought
        
    def calculate_signals(self, df):
        """计算RSI交易信号"""
        df = df.copy()
        
        # 计算RSI
        if HAS_TALIB:
            df['RSI'] = talib.RSI(df['close'].values, timeperiod=self.rsi_window)
        else:
            df['RSI'] = TechnicalIndicators.RSI(df['close'], self.rsi_window)
        
        # 生成交易信号
        df['signal'] = 0
        
        # RSI超卖买入，超买卖出
        df.loc[df['RSI'] < self.oversold, 'signal'] = 1  # 超卖买入
        df.loc[df['RSI'] > self.overbought, 'signal'] = -1  # 超买卖出
        
        return df

class MACDStrategy(BaseStrategy):
    """MACD指标策略"""
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        super().__init__("MACD指标策略")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        
    def calculate_signals(self, df):
        """计算MACD交易信号"""
        df = df.copy()
        
        # 计算MACD
        if HAS_TALIB:
            macd, macdsignal, macdhist = talib.MACD(
                df['close'].values, 
                fastperiod=self.fast_period,
                slowperiod=self.slow_period, 
                signalperiod=self.signal_period
            )
            df['MACD'] = macd
            df['MACD_signal'] = macdsignal
            df['MACD_hist'] = macdhist
        else:
            macd, signal, histogram = TechnicalIndicators.MACD(
                df['close'], self.fast_period, self.slow_period, self.signal_period
            )
            df['MACD'] = macd
            df['MACD_signal'] = signal
            df['MACD_hist'] = histogram
        
        # 生成交易信号
        df['signal'] = 0
        
        # MACD金叉买入，死叉卖出
        for i in range(1, len(df)):
            if (df['MACD'].iloc[i-1] <= df['MACD_signal'].iloc[i-1] and 
                df['MACD'].iloc[i] > df['MACD_signal'].iloc[i]):
                df.loc[df.index[i], 'signal'] = 1  # 买入信号
            elif (df['MACD'].iloc[i-1] >= df['MACD_signal'].iloc[i-1] and 
                  df['MACD'].iloc[i] < df['MACD_signal'].iloc[i]):
                df.loc[df.index[i], 'signal'] = -1  # 卖出信号
        
        return df

class BOLLStrategy(BaseStrategy):
    """布林带策略"""
    def __init__(self, period=20, std_dev=2):
        super().__init__("布林带策略")
        self.period = period
        self.std_dev = std_dev
        
    def calculate_signals(self, df):
        """计算布林带交易信号"""
        df = df.copy()
        
        # 计算布林带
        if HAS_TALIB:
            upper, middle, lower = talib.BBANDS(
                df['close'].values,
                timeperiod=self.period,
                nbdevup=self.std_dev,
                nbdevdn=self.std_dev,
                matype=0
            )
            df['BOLL_upper'] = upper
            df['BOLL_middle'] = middle
            df['BOLL_lower'] = lower
        else:
            upper, middle, lower = TechnicalIndicators.BBANDS(
                df['close'], self.period, self.std_dev
            )
            df['BOLL_upper'] = upper
            df['BOLL_middle'] = middle
            df['BOLL_lower'] = lower
        
        # 生成交易信号
        df['signal'] = 0
        
        # 价格突破上轨买入，跌破下轨卖出
        df.loc[df['close'] > df['BOLL_upper'], 'signal'] = 1  # 突破上轨买入
        df.loc[df['close'] < df['BOLL_lower'], 'signal'] = -1  # 跌破下轨卖出
        
        return df

class KDJStrategy(BaseStrategy):
    """KDJ随机指标策略"""
    def __init__(self, k_period=9, d_period=3, j_period=3):
        super().__init__("KDJ随机指标策略")
        self.k_period = k_period
        self.d_period = d_period
        self.j_period = j_period
        
    def calculate_signals(self, df):
        """计算KDJ交易信号"""
        df = df.copy()
        
        # 计算KDJ
        if HAS_TALIB:
            slowk, slowd = talib.STOCH(
                df['high'].values,
                df['low'].values,
                df['close'].values,
                fastk_period=self.k_period,
                slowk_period=self.d_period,
                slowk_matype=0,
                slowd_period=self.j_period,
                slowd_matype=0
            )
            df['K'] = slowk
            df['D'] = slowd
            df['J'] = 3 * slowk - 2 * slowd
        else:
            k, d = TechnicalIndicators.STOCH(
                df['high'], df['low'], df['close'], self.k_period, self.d_period
            )
            df['K'] = k
            df['D'] = d
            df['J'] = 3 * k - 2 * d
        
        # 生成交易信号
        df['signal'] = 0
        
        # KDJ金叉买入，死叉卖出
        for i in range(1, len(df)):
            if (df['K'].iloc[i-1] <= df['D'].iloc[i-1] and 
                df['K'].iloc[i] > df['D'].iloc[i] and 
                df['K'].iloc[i] < 80):  # 金叉且不在超买区
                df.loc[df.index[i], 'signal'] = 1
            elif (df['K'].iloc[i-1] >= df['D'].iloc[i-1] and 
                  df['K'].iloc[i] < df['D'].iloc[i] and 
                  df['K'].iloc[i] > 20):  # 死叉且不在超卖区
                df.loc[df.index[i], 'signal'] = -1
        
        return df

class DualThrustStrategy(BaseStrategy):
    """Dual Thrust策略"""
    def __init__(self, window=5, k1=0.2, k2=0.5):
        super().__init__("Dual Thrust策略")
        self.window = window
        self.k1 = k1
        self.k2 = k2
        
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
        
        # 计算上下轨
        df['upper_bound'] = df['open'] + self.k1 * df['Range']
        df['lower_bound'] = df['open'] - self.k2 * df['Range']
        
        # 生成交易信号
        df['signal'] = 0
        
        # 价格突破上轨买入，跌破下轨卖出
        df.loc[df['close'] > df['upper_bound'], 'signal'] = 1
        df.loc[df['close'] < df['lower_bound'], 'signal'] = -1
        
        return df

class GridStrategy(BaseStrategy):
    """网格交易策略"""
    def __init__(self, grid_ratio=0.05, max_grids=10):
        super().__init__("网格交易策略")
        self.grid_ratio = grid_ratio  # 网格间距比例
        self.max_grids = max_grids
        
    def calculate_signals(self, df):
        """计算网格交易信号"""
        df = df.copy()
        
        # 计算基准价格（使用前N天的平均价）
        df['base_price'] = df['close'].rolling(window=20).mean()
        
        # 计算当前价格相对基准价格的偏离度
        df['price_deviation'] = (df['close'] - df['base_price']) / df['base_price']
        
        # 生成交易信号
        df['signal'] = 0
        
        # 价格下跌时买入，上涨时卖出
        for i in range(len(df)):
            deviation = df['price_deviation'].iloc[i]
            if deviation < -self.grid_ratio:  # 价格下跌超过网格间距，买入
                df.loc[df.index[i], 'signal'] = 1
            elif deviation > self.grid_ratio:  # 价格上涨超过网格间距，卖出
                df.loc[df.index[i], 'signal'] = -1
        
        return df

# 策略工厂
class StrategyFactory:
    """策略工厂类"""
    
    @staticmethod
    def create_strategy(strategy_name, **kwargs):
        """创建策略实例"""
        strategies = {
            'MA': MAStrategy,
            'EMA': EMAStrategy,
            'RSI': RSIStrategy,
            'MACD': MACDStrategy,
            'BOLL': BOLLStrategy,
            'KDJ': KDJStrategy,
            'DualThrust': DualThrustStrategy,
            'Grid': GridStrategy
        }
        
        if strategy_name not in strategies:
            raise ValueError(f"未知策略: {strategy_name}")
        
        return strategies[strategy_name](**kwargs)
    
    @staticmethod
    def get_available_strategies():
        """获取可用策略列表"""
        return ['MA', 'EMA', 'RSI', 'MACD', 'BOLL', 'KDJ', 'DualThrust', 'Grid'] 