"""Mock数据源适配器 - 已禁用，仅保留用于内部兼容性"""
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger
import random
import numpy as np
import pandas as pd

from .base import BaseAdapter
from .models import StockQuote, KlineData


class MockAdapter(BaseAdapter):
    """Mock数据源适配器 - 已禁用，不允许使用"""
    
    def __init__(self):
        """初始化Mock适配器"""
        self.stock_cache = {}
        # 不再允许初始化，直接抛出异常
        raise RuntimeError("Mock数据源已被禁用，系统仅使用真实市场数据")
    
    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None
    ) -> List[StockQuote]:
        """获取股票列表 - 已禁用"""
        raise RuntimeError("Mock数据源已被禁用，系统仅使用真实市场数据")
    
    async def get_stock_quote(self, code: str) -> Optional[StockQuote]:
        """获取单只股票实时行情 - 已禁用"""
        raise RuntimeError("Mock数据源已被禁用，系统仅使用真实市场数据")
    
    async def get_kline_data(
        self,
        code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str = '1d'
    ) -> List[KlineData]:
        """获取K线数据 - 已禁用"""
        raise RuntimeError("Mock数据源已被禁用，系统仅使用真实市场数据")
    
    async def search_stocks(self, keyword: str, limit: int = 20) -> List[StockQuote]:
        """搜索股票 - 已禁用"""
        raise RuntimeError("Mock数据源已被禁用，系统仅使用真实市场数据")