"""Tushare数据源适配器"""
import tushare as ts
import pandas as pd
from typing import List, Optional
from datetime import datetime
from loguru import logger
from .base import BaseAdapter
from .models import StockQuote, KlineData


class TushareAdapter(BaseAdapter):
    """Tushare数据源适配器"""
    
    def __init__(self, token: Optional[str] = None):
        super().__init__()
        self.pro = None
        self._connect(token)
    
    def _connect(self, token: Optional[str]):
        """连接Tushare"""
        try:
            if token:
                ts.set_token(token)
                self.pro = ts.pro_api()
                logger.info("[Tushare] 连接成功")
            else:
                logger.warning("[Tushare] 未提供token")
        except Exception as e:
            logger.error(f"[Tushare] 连接失败: {e}")
            self.pro = None
    
    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None
    ) -> List[StockQuote]:
        """获取股票列表"""
        try:
            if not self.pro:
                raise Exception("Tushare未连接")
            
            logger.info(f"[Tushare] 获取股票列表: page={page}, page_size={page_size}")
            
            # Tushare的股票列表需要token且有积分限制
            # 这里返回空列表，实际使用需要配置token
            logger.warning("[Tushare] 需要配置token才能获取股票列表")
            return []
            
        except Exception as e:
            logger.error(f"[Tushare] 获取股票列表失败: {e}")
            raise
    
    async def get_stock_quote(self, code: str) -> Optional[StockQuote]:
        """获取单只股票实时行情"""
        try:
            logger.info(f"[Tushare] 获取股票行情: {code}")
            # Tushare需要高级权限
            return None
        except Exception as e:
            logger.error(f"[Tushare] 获取股票行情失败: {e}")
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
            if not self.pro:
                raise Exception("Tushare未连接")
            
            logger.info(f"[Tushare] 获取K线数据: {code}, {start_date} 到 {end_date}, 频率: {freq}")
            
            # 转换代码格式
            if code.startswith('6'):
                ts_code = f"{code}.SH"
            else:
                ts_code = f"{code}.SZ"
            
            if freq == '1d':
                df = self.pro.daily(
                    ts_code=ts_code,
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d')
                )
            else:
                logger.warning("[Tushare] 分钟数据需要高级权限")
                return []
            
            if df.empty:
                return []
            
            # 转换为KlineData
            kline_list = []
            for _, row in df.iterrows():
                kline_list.append(KlineData(
                    date=pd.to_datetime(row['trade_date']),
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['vol']),
                    amount=float(row['amount']) if 'amount' in row else None
                ))
            
            logger.info(f"[Tushare] 获取成功: {len(kline_list)} 条K线数据")
            return kline_list
            
        except Exception as e:
            logger.error(f"[Tushare] 获取K线数据失败: {e}")
            raise
    
    async def search_stocks(self, keyword: str, limit: int = 20) -> List[StockQuote]:
        """搜索股票"""
        try:
            logger.info(f"[Tushare] 搜索股票: {keyword}")
            # Tushare搜索需要高级权限
            return []
        except Exception as e:
            logger.error(f"[Tushare] 搜索股票失败: {e}")
            return []