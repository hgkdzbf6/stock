"""东方财富数据源适配器"""
import requests
from typing import List, Optional
from datetime import datetime
from loguru import logger
from .base import BaseAdapter
from .models import StockQuote, KlineData


class EastmoneyAdapter(BaseAdapter):
    """东方财富数据源适配器"""
    
    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None
    ) -> List[StockQuote]:
        """获取股票列表"""
        try:
            logger.info(f"[东方财富] 获取股票列表: page={page}, page_size={page_size}")
            # 东方财富不提供完整股票列表API
            logger.warning("[东方财富] 不提供完整股票列表API")
            return []
        except Exception as e:
            logger.error(f"[东方财富] 获取股票列表失败: {e}")
            raise
    
    async def get_stock_quote(self, code: str) -> Optional[StockQuote]:
        """获取单只股票实时行情"""
        try:
            logger.info(f"[东方财富] 获取股票行情: {code}")
            
            # 格式: 1.000001 (1=沪市, 0=深市)
            if code.startswith('6'):
                secid = f"1.{code}"
            else:
                secid = f"0.{code}"
            
            url = "http://push2.eastmoney.com/api/qt/stock/get"
            params = {
                'secid': secid,
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58',
                'klt': '101',  # 日线
                'fqt': '1',     # 前复权
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return None
            
            result = response.json()
            if result.get('rc') != 0 or not result.get('data'):
                return None
            
            data = result['data']
            
            return StockQuote(
                code=code,
                name=data.get('f58', ''),
                price=float(data.get('f43', 0)) / 100,
                change=float(data.get('f169', 0)) / 100,
                change_pct=float(data.get('f170', 0)),
                open=float(data.get('f46', 0)) / 100,
                high=float(data.get('f44', 0)) / 100,
                low=float(data.get('f45', 0)) / 100,
                pre_close=float(data.get('f60', 0)) / 100,
                volume=int(data.get('f47', 0)),
                amount=float(data.get('f48', 0)) / 10000,
                market_cap=0.0
            )
        except Exception as e:
            logger.error(f"[东方财富] 获取股票行情失败: {e}")
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
            logger.info(f"[东方财富] 获取K线数据: {code}, {start_date} 到 {end_date}, 频率: {freq}")
            
            if freq != '1d':
                logger.warning("[东方财富] 只提供日线数据")
                return []
            
            # 格式: 1.000001 (1=沪市, 0=深市)
            if code.startswith('6'):
                secid = f"1.{code}"
            else:
                secid = f"0.{code}"
            
            url = "http://push2.eastmoney.com/api/qt/stock/klt"
            params = {
                'secid': secid,
                'fields1': 'f1,f2,f3,f4,f5',
                'fields2': 'f51,f52,f53,f54,f55',
                'klt': '101',  # 日线
                'fqt': '1',     # 前复权
                'beg': start_date.strftime('%Y%m%d'),
                'end': end_date.strftime('%Y%m%d')
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                raise Exception(f"东方财富API返回错误: {response.status_code}")
            
            result = response.json()
            if result.get('rc') != 0 or not result.get('data'):
                raise Exception("东方财富返回空数据")
            
            # 解析数据
            data_list = result['data']['klines']
            kline_list = []
            for item in data_list:
                parts = item.split(',')
                if len(parts) < 6:
                    continue
                
                kline_list.append(KlineData(
                    date=datetime.strptime(parts[0], '%Y-%m-%d'),
                    open=float(parts[1]),
                    close=float(parts[2]),
                    high=float(parts[3]),
                    low=float(parts[4]),
                    volume=int(float(parts[5]))
                ))
            
            logger.info(f"[东方财富] 获取成功: {len(kline_list)} 条K线数据")
            return kline_list
        except Exception as e:
            logger.error(f"[东方财富] 获取K线数据失败: {e}")
            raise
    
    async def search_stocks(self, keyword: str, limit: int = 20) -> List[StockQuote]:
        """搜索股票"""
        try:
            logger.info(f"[东方财富] 搜索股票: {keyword}")
            # 东方财富不提供搜索API
            return []
        except Exception as e:
            logger.error(f"[东方财富] 搜索股票失败: {e}")
            return []