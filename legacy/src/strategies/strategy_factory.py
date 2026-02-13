"""
策略工厂
用于创建和管理各种交易策略
"""

from .moving_average_strategies import MAStrategy, EMAStrategy
from .momentum_strategies import RSIStrategy, MACDStrategy, KDJStrategy
from .volatility_strategies import BOLLStrategy
from .breakout_strategies import DualThrustStrategy
from .grid_strategies import GridStrategy
from .advanced_strategies import (
    MeanReversionStrategy, 
    TrendFollowingStrategy,
    IchimokuStrategy,
    WilliamsRStrategy,
    PairsTradingStrategy
)
from .test_strategies import TestStrategy

class StrategyFactory:
    """策略工厂类"""
    
    # 策略映射表
    STRATEGIES = {
        # 基础策略
        'MA': MAStrategy,
        'EMA': EMAStrategy,
        'RSI': RSIStrategy,
        'MACD': MACDStrategy,
        'KDJ': KDJStrategy,
        'BOLL': BOLLStrategy,
        'DualThrust': DualThrustStrategy,
        'Grid': GridStrategy,
        'Test': TestStrategy,

        # 高级策略
        'MeanReversion': MeanReversionStrategy,
        'TrendFollowing': TrendFollowingStrategy,
        'Ichimoku': IchimokuStrategy,
        'WilliamsR': WilliamsRStrategy,
        'PairsTrading': PairsTradingStrategy,
    }
    
    @classmethod
    def create_strategy(cls, strategy_name, **kwargs):
        """创建策略实例"""
        if strategy_name not in cls.STRATEGIES:
            raise ValueError(f"未知策略: {strategy_name}. 可用策略: {list(cls.STRATEGIES.keys())}")
        
        strategy_class = cls.STRATEGIES[strategy_name]
        return strategy_class(**kwargs)
    
    @classmethod
    def get_available_strategies(cls):
        """获取可用策略列表"""
        return list(cls.STRATEGIES.keys())
    
    @classmethod
    def get_strategy_info(cls):
        """获取策略信息"""
        info = {}
        for name, strategy_class in cls.STRATEGIES.items():
            info[name] = {
                'name': name,
                'class': strategy_class.__name__,
                'description': strategy_class.__doc__ or "无描述",
            }
        return info
    
    @classmethod
    def get_default_params(cls):
        """获取各策略的默认参数"""
        return {
            # 基础策略参数
            'MA': {'short_window': 5, 'long_window': 20, 'stop_loss': 0.05, 'take_profit': 0.10},
            'EMA': {'fast_window': 12, 'slow_window': 26, 'signal_window': 9, 'stop_loss': 0.05, 'take_profit': 0.10},
            'RSI': {'rsi_window': 14, 'oversold': 30, 'overbought': 70, 'stop_loss': 0.04, 'take_profit': 0.08},
            'MACD': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9, 'stop_loss': 0.04, 'take_profit': 0.08},
            'KDJ': {'k_period': 9, 'd_period': 3, 'j_period': 3, 'stop_loss': 0.03, 'take_profit': 0.06},
            'BOLL': {'period': 20, 'std_dev': 2, 'stop_loss': 0.04, 'take_profit': 0.08},
            'DualThrust': {'window': 10, 'k1': 0.4, 'k2': 0.6, 'stop_loss': 0.05, 'take_profit': 0.10},
            'Grid': {'grid_ratio': 0.03, 'max_grids': 8, 'base_period': 30},
            
            # 高级策略参数
            'MeanReversion': {'lookback': 20, 'threshold': 2.0, 'stop_loss': 0.03, 'take_profit': 0.06},
            'TrendFollowing': {'atr_period': 14, 'atr_multiplier': 2.0, 'trend_period': 50},
            'Ichimoku': {},
            'WilliamsR': {'period': 14, 'overbought': -20, 'oversold': -80},
            'PairsTrading': {'lookback': 30, 'threshold': 2.0},
            'Test': {},
        } 