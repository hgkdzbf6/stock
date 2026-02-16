"""数据源适配器基类"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .models import StockQuote, KlineData, StockInfo


class BaseAdapter(ABC):
    """数据源适配器基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None
    ) -> List[StockQuote]:
        """
        获取股票列表
        
        Args:
            page: 页码
            page_size: 每页数量
            keyword: 搜索关键词
            
        Returns:
            股票行情列表
        """
        pass
    
    @abstractmethod
    async def get_stock_quote(self, code: str) -> Optional[StockQuote]:
        """
        获取单只股票实时行情
        
        Args:
            code: 股票代码
            
        Returns:
            股票行情数据
        """
        pass
    
    @abstractmethod
    async def get_kline_data(
        self,
        code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str = '1d'
    ) -> List[KlineData]:
        """
        获取K线数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            freq: 数据频率 (1min, 5min, 15min, 30min, 60min, 1d)
            
        Returns:
            K线数据列表
        """
        pass
    
    @abstractmethod
    async def search_stocks(self, keyword: str, limit: int = 20) -> List[StockQuote]:
        """
        搜索股票
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            股票列表
        """
        pass
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            数据源是否可用
        """
        try:
            await self.get_stock_list(page=1, page_size=1)
            return True
        except Exception:
            return False
    
    @staticmethod
    def normalize_code(code: str) -> str:
        """
        标准化股票代码（去除市场前缀和后缀）
        
        Args:
            code: 原始代码 (支持格式: sh600771, sz000001, sh600771.SZ, sz000001.SH, sh.600771, sz.000001)
            
        Returns:
            标准化后的代码 (纯数字)
        """
        result = code
        # 去除 .SH 和 .SZ 后缀
        result = result.replace('.SH', '').replace('.SZ', '')
        # 去除 sh. 和 sz. 前缀
        result = result.replace('sh.', '').replace('sz.', '')
        # 去除 sh 和 sz 前缀 (不带点的)
        if result.startswith('sh') and len(result) > 2 and result[2].isdigit():
            result = result[2:]
        if result.startswith('sz') and len(result) > 2 and result[2].isdigit():
            result = result[2:]
        return result
    
    def add_market_suffix(self, code: str) -> str:
        """
        添加市场后缀
        
        Args:
            code: 原始代码
            
        Returns:
            带市场后缀的代码 (格式: sh.600771 或 sz.000001)
        """
        code = self.normalize_code(code)
        if code.startswith('6'):
            return f"sh.{code}"
        else:
            return f"sz.{code}"