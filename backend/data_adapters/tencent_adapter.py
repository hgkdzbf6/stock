"""腾讯财经数据源适配器"""
import requests
from typing import List, Optional
from datetime import datetime
from loguru import logger
from .base import BaseAdapter
from .models import StockQuote, KlineData


class TencentAdapter(BaseAdapter):
    """腾讯财经数据源适配器"""
    
    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None
    ) -> List[StockQuote]:
        """获取股票列表"""
        try:
            logger.info(f"[腾讯] 获取股票列表: page={page}, page_size={page_size}")
            # 腾讯财经不提供完整股票列表API
            logger.warning("[腾讯] 不提供完整股票列表API")
            return []
        except Exception as e:
            logger.error(f"[腾讯] 获取股票列表失败: {e}")
            raise
    
    async def get_stock_quote(self, code: str) -> Optional[StockQuote]:
        """获取单只股票实时行情"""
        try:
            logger.info(f"[腾讯] 获取股票行情: {code}")
            
            # 格式: sz000001 或 sh600519
            if code.startswith('6'):
                symbol_code = f"sh{code}"
            else:
                symbol_code = f"sz{code}"
            
            url = f"http://qt.gtimg.cn/q={symbol_code}"
            response = requests.get(url, timeout=5)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return None
            
            # 解析数据
            data_str = response.text.strip('~').strip()
            if not data_str:
                return None
            
            parts = data_str.split(',')
            if len(parts) < 44:
                return None
            
            # 提取数据
            name = parts[1]
            current = float(parts[3]) if parts[3] else 0.0
            open_price = float(parts[5]) if parts[5] else 0.0
            high = float(parts[33]) if parts[33] else 0.0
            low = float(parts[34]) if parts[34] else 0.0
            pre_close = float(parts[4]) if parts[4] else 0.0
            volume = float(parts[36]) if parts[36] else 0
            amount = float(parts[37]) if parts[37] else 0.0
            
            change = current - pre_close
            change_pct = (change / pre_close * 100) if pre_close > 0 else 0.0
            
            return StockQuote(
                code=code,
                name=name,
                price=current,
                change=change,
                change_pct=change_pct,
                open=open_price,
                high=high,
                low=low,
                pre_close=pre_close,
                volume=int(volume),
                amount=amount,
                market_cap=0.0
            )
        except Exception as e:
            logger.error(f"[腾讯] 获取股票行情失败: {e}")
            return None
    
    async def get_kline_data(
        self,
        code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str = '1d'
    ) -> List[KlineData]:
        """获取K线数据"""
        try:
            logger.info(f"[腾讯] 获取K线数据: {code}, {start_date} 到 {end_date}, 频率: {freq}")
            # 腾讯财经主要提供实时行情，历史数据有限
            logger.warning("[腾讯] 不提供历史K线数据API")
            return []
        except Exception as e:
            logger.error(f"[腾讯] 获取K线数据失败: {e}")
            raise
    
    async def search_stocks(self, keyword: str, limit: int = 20) -> List[StockQuote]:
        """搜索股票"""
        try:
            logger.info(f"[腾讯] 搜索股票: {keyword}")
            # 腾讯财经不提供搜索API
            return []
        except Exception as e:
            logger.error(f"[腾讯] 搜索股票失败: {e}")
            return []