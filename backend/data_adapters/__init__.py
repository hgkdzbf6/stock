"""数据源适配器"""
from typing import Optional
import asyncio
from .base import BaseAdapter
from .models import StockQuote, KlineData, StockInfo
from .ashare_adapter import AshareAdapter
from .baostock_adapter import BaoStockAdapter
from .akshare_adapter import AkShareAdapter
from .tushare_adapter import TushareAdapter
from .sina_adapter import SinaAdapter
from .tencent_adapter import TencentAdapter
from .eastmoney_adapter import EastmoneyAdapter
from .mock_adapter import MockAdapter
from loguru import logger


class AdapterFactory:
    """适配器工厂"""
    
    # 数据源请求超时时间（秒）
    REQUEST_TIMEOUT = 5
    
    def __init__(self, tushare_token: str = None):
        """初始化工厂
        
        Args:
            tushare_token: Tushare API token
        """
        self.tushare_token = tushare_token
        self._adapters = {}
        # 数据源优先级：按响应速度和稳定性排序
        # Ashare优先，因为它支持双数据源（新浪+腾讯）自动切换
        self._priority_order = {
            'stock_list': ['ashare', 'akshare', 'sina', 'tencent', 'eastmoney', 'baostock', 'tushare', 'mock'],
            'stock_quote': ['ashare', 'akshare', 'sina', 'tencent', 'eastmoney', 'baostock', 'tushare', 'mock'],
            'kline_data': ['ashare', 'akshare', 'sina', 'tencent', 'eastmoney', 'baostock', 'tushare', 'mock'],
            'search_stocks': ['akshare', 'sina', 'tencent', 'eastmoney', 'baostock', 'tushare', 'mock']  # Ashare不支持搜索
        }
    
    def get_adapter(self, source: str = 'auto') -> BaseAdapter:
        """获取适配器实例
        
        Args:
            source: 数据源名称 (auto/baostock/akshare/tushare/sina/tencent/eastmoney/mock)
            
        Returns:
            适配器实例
        """
        if source == 'auto':
            return None
        
        if source not in self._adapters:
            self._create_adapter(source)
        
        return self._adapters[source]
    
    def _create_adapter(self, source: str):
        """创建适配器实例"""
        if source == 'ashare':
            self._adapters[source] = AshareAdapter()
        elif source == 'baostock':
            self._adapters[source] = BaoStockAdapter()
        elif source == 'akshare':
            self._adapters[source] = AkShareAdapter()
        elif source == 'tushare':
            self._adapters[source] = TushareAdapter(self.tushare_token)
        elif source == 'sina':
            self._adapters[source] = SinaAdapter()
        elif source == 'tencent':
            self._adapters[source] = TencentAdapter()
        elif source == 'eastmoney':
            self._adapters[source] = EastmoneyAdapter()
        elif source == 'mock':
            self._adapters[source] = MockAdapter()
        else:
            logger.warning(f"未知的数据源: {source}，使用ashare")
            self._adapters[source] = AshareAdapter()
    
    async def auto_get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: str = None
    ) -> tuple[list[StockQuote], str]:
        """自动获取股票列表（按优先级尝试，每个数据源超时5秒）
        
        Returns:
            (股票列表, 使用的数据源名称)
        """
        priority_list = self._priority_order.get('stock_list', ['mock'])
        last_error = None
        
        for source in priority_list:
            try:
                adapter = self.get_adapter(source)
                logger.info(f"[Auto] 尝试使用 {source} 获取股票列表...")
                # 使用超时包装器
                result = await asyncio.wait_for(
                    adapter.get_stock_list(page, page_size, keyword),
                    timeout=self.REQUEST_TIMEOUT
                )
                if result:
                    logger.info(f"[Auto] 使用 {source} 获取股票列表成功，共{len(result)}只股票")
                    return result, source
                else:
                    logger.warning(f"[Auto] {source} 返回空结果，切换数据源")
                    last_error = f"{source}返回空结果"
            except asyncio.TimeoutError:
                logger.warning(f"[Auto] {source} 获取股票列表超时（>{self.REQUEST_TIMEOUT}秒），切换数据源")
                last_error = f"{source}超时"
                continue
            except Exception as e:
                logger.warning(f"[Auto] {source} 获取股票列表失败: {e}")
                last_error = f"{source}失败: {str(e)}"
                continue
        
        # 所有数据源都失败，使用mock（但mock也有超时）
        logger.warning(f"[Auto] 所有数据源都失败，使用mock数据。最后错误: {last_error}")
        try:
            adapter = self.get_adapter('mock')
            result = await asyncio.wait_for(
                adapter.get_stock_list(page, page_size, keyword),
                timeout=self.REQUEST_TIMEOUT
            )
            if result:
                logger.info(f"[Auto] mock数据获取成功，共{len(result)}只股票")
                return result, 'mock'
            else:
                raise ValueError("mock返回空结果")
        except asyncio.TimeoutError:
            logger.error(f"[Auto] mock数据源也超时，返回超时错误")
            raise TimeoutError(f"所有数据源都超时（>{self.REQUEST_TIMEOUT}秒）")
        except Exception as e:
            logger.error(f"[Auto] mock数据源失败: {e}")
            raise TimeoutError(f"所有数据源都失败: {last_error}")
    
    async def auto_get_stock_quote(self, code: str) -> tuple[Optional[StockQuote], str]:
        """自动获取股票行情（按优先级尝试，每个数据源超时5秒）
        
        Returns:
            (股票行情, 使用的数据源名称)
        """
        priority_list = self._priority_order.get('stock_quote', ['mock'])
        last_error = None
        
        for source in priority_list:
            try:
                adapter = self.get_adapter(source)
                logger.info(f"[Auto] 尝试使用 {source} 获取股票行情 {code}...")
                result = await asyncio.wait_for(
                    adapter.get_stock_quote(code),
                    timeout=self.REQUEST_TIMEOUT
                )
                if result:
                    logger.info(f"[Auto] 使用 {source} 获取股票行情成功")
                    return result, source
                else:
                    logger.warning(f"[Auto] {source} 返回空结果，切换数据源")
                    last_error = f"{source}返回空结果"
            except asyncio.TimeoutError:
                logger.warning(f"[Auto] {source} 获取股票行情超时（>{self.REQUEST_TIMEOUT}秒），切换数据源")
                last_error = f"{source}超时"
                continue
            except Exception as e:
                logger.warning(f"[Auto] {source} 获取股票行情失败: {e}")
                last_error = f"{source}失败: {str(e)}"
                continue
        
        logger.warning(f"[Auto] 所有数据源都失败，返回None。最后错误: {last_error}")
        return None, 'none'
    
    async def auto_get_kline_data(
        self,
        code: str,
        start_date,
        end_date,
        freq: str = '1d'
    ) -> tuple[list[KlineData], str]:
        """自动获取K线数据（按优先级尝试，每个数据源超时5秒）
        
        Returns:
            (K线数据列表, 使用的数据源名称)
        """
        priority_list = self._priority_order.get('kline_data', ['mock'])
        last_error = None
        
        for source in priority_list:
            try:
                adapter = self.get_adapter(source)
                logger.info(f"[Auto] 尝试使用 {source} 获取K线数据 {code}...")
                result = await asyncio.wait_for(
                    adapter.get_kline_data(code, start_date, end_date, freq),
                    timeout=self.REQUEST_TIMEOUT
                )
                if result:
                    logger.info(f"[Auto] 使用 {source} 获取K线数据成功，共{len(result)}条记录")
                    return result, source
                else:
                    logger.warning(f"[Auto] {source} 返回空结果，切换数据源")
                    last_error = f"{source}返回空结果"
            except asyncio.TimeoutError:
                logger.warning(f"[Auto] {source} 获取K线数据超时（>{self.REQUEST_TIMEOUT}秒），切换数据源")
                last_error = f"{source}超时"
                continue
            except Exception as e:
                logger.warning(f"[Auto] {source} 获取K线数据失败: {e}")
                last_error = f"{source}失败: {str(e)}"
                continue
        
        logger.warning(f"[Auto] 所有数据源都失败，使用mock数据。最后错误: {last_error}")
        try:
            adapter = self.get_adapter('mock')
            result = await asyncio.wait_for(
                adapter.get_kline_data(code, start_date, end_date, freq),
                timeout=self.REQUEST_TIMEOUT
            )
            if result:
                logger.info(f"[Auto] mock数据获取成功，共{len(result)}条记录")
                return result, 'mock'
            else:
                raise ValueError("mock返回空结果")
        except asyncio.TimeoutError:
            logger.error(f"[Auto] mock数据源也超时，返回超时错误")
            raise TimeoutError(f"所有数据源都超时（>{self.REQUEST_TIMEOUT}秒）")
        except Exception as e:
            logger.error(f"[Auto] mock数据源失败: {e}")
            raise TimeoutError(f"所有数据源都失败: {last_error}")
    
    async def auto_search_stocks(self, keyword: str, limit: int = 20) -> tuple[list[StockQuote], str]:
        """自动搜索股票（按优先级尝试，每个数据源超时5秒）
        
        Returns:
            (股票列表, 使用的数据源名称)
        """
        priority_list = self._priority_order.get('search_stocks', ['mock'])
        last_error = None
        
        for source in priority_list:
            try:
                adapter = self.get_adapter(source)
                logger.info(f"[Auto] 尝试使用 {source} 搜索股票 {keyword}...")
                result = await asyncio.wait_for(
                    adapter.search_stocks(keyword, limit),
                    timeout=self.REQUEST_TIMEOUT
                )
                if result:
                    logger.info(f"[Auto] 使用 {source} 搜索股票成功，共{len(result)}只股票")
                    return result, source
                else:
                    logger.warning(f"[Auto] {source} 返回空结果，切换数据源")
                    last_error = f"{source}返回空结果"
            except asyncio.TimeoutError:
                logger.warning(f"[Auto] {source} 搜索股票超时（>{self.REQUEST_TIMEOUT}秒），切换数据源")
                last_error = f"{source}超时"
                continue
            except Exception as e:
                logger.warning(f"[Auto] {source} 搜索股票失败: {e}")
                last_error = f"{source}失败: {str(e)}"
                continue
        
        logger.warning(f"[Auto] 所有数据源都失败，使用mock数据。最后错误: {last_error}")
        try:
            adapter = self.get_adapter('mock')
            result = await asyncio.wait_for(
                adapter.search_stocks(keyword, limit),
                timeout=self.REQUEST_TIMEOUT
            )
            if result:
                logger.info(f"[Auto] mock数据获取成功，共{len(result)}只股票")
                return result, 'mock'
            else:
                raise ValueError("mock返回空结果")
        except asyncio.TimeoutError:
            logger.error(f"[Auto] mock数据源也超时，返回超时错误")
            raise TimeoutError(f"所有数据源都超时（>{self.REQUEST_TIMEOUT}秒）")
        except Exception as e:
            logger.error(f"[Auto] mock数据源失败: {e}")
            raise TimeoutError(f"所有数据源都失败: {last_error}")


__all__ = [
    'AdapterFactory',
    'BaseAdapter',
    'StockQuote',
    'KlineData',
    'StockInfo',
    'AshareAdapter',
    'BaoStockAdapter',
    'AkShareAdapter',
    'TushareAdapter',
    'SinaAdapter',
    'TencentAdapter',
    'EastmoneyAdapter',
    'MockAdapter'
]
