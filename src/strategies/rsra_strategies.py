"""
RSRS策略
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .technical_indicators import TechnicalIndicators, HAS_TALIB

if HAS_TALIB:
    import talib

class RSRSStrategy(BaseStrategy):
