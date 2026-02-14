"""BaoStock数据源适配器"""
import baostock as bs
from typing import List, Optional
from datetime import datetime
from loguru import logger
from .base import BaseAdapter
from .models import StockQuote, KlineData


class BaoStockAdapter(BaseAdapter):
    """BaoStock数据源适配器"""
    
    def __init__(self):
        super().__init__()
        self.bs_lg = None
        self._connect()
    
    def _connect(self):
        """连接BaoStock"""
        try:
            self.bs_lg = bs.login()
            if self.bs_lg.error_code != '0':
                logger.warning(f"BaoStock登录失败: {self.bs_lg.error_msg}")
                self.bs_lg = None
        except Exception as e:
            logger.error(f"BaoStock连接失败: {e}")
            self.bs_lg = None
    
    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None
    ) -> List[StockQuote]:
        """获取股票列表"""
        try:
            if not self.bs_lg:
                raise Exception("BaoStock未连接")
            
            logger.info(f"[BaoStock] 获取股票列表: page={page}, page_size={page_size}")
            
            # 获取交易日
            from utils.trading_days import get_latest_trading_day
            trading_day = get_latest_trading_day(days_back=7)
            day_str = trading_day.strftime('%Y-%m-%d')
            
            logger.info(f"[BaoStock] 使用交易日: {day_str}")
            
            # 查询股票列表
            rs = bs.query_all_stock(day=day_str)
            
            if rs.error_code != '0':
                raise Exception(f"BaoStock查询失败: {rs.error_msg}")
            
            stocks = []
            count = 0
            start_index = (page - 1) * page_size
            
            # 跳过前面的数据
            while (rs.error_code == '0') & rs.next():
                if count < start_index:
                    count += 1
                    continue
                
                if len(stocks) >= page_size:
                    break
                
                try:
                    row = rs.get_row_data()
                    if len(row) < 5:
                        continue
                    
                    code = row[0].replace('sh.', '').replace('sz.', '')
                    name = row[1]
                    
                    # 只获取正常交易的股票
                    if row[4] == '1':  # 1=正常交易
                        # 过滤关键词
                        if keyword:
                            if keyword.lower() not in code.lower() and keyword.lower() not in name:
                                continue
                        
                        stocks.append(StockQuote(
                            code=code,
                            name=name,
                            price=0.0,
                            change=0.0,
                            change_pct=0.0,
                            volume=0,
                            amount=0.0,
                            market_cap=0.0
                        ))
                except Exception as e:
                    logger.warning(f"[BaoStock] 解析股票行数据失败: {e}")
                    continue
            
            logger.info(f"[BaoStock] 获取成功: {len(stocks)} 只股票")
            return stocks
            
        except Exception as e:
            logger.error(f"[BaoStock] 获取股票列表失败: {e}")
            raise
    
    async def get_stock_quote(self, code: str) -> Optional[StockQuote]:
        """获取单只股票实时行情"""
        try:
            logger.info(f"[BaoStock] 获取股票行情: {code}")
            
            # BaoStock主要提供历史数据，这里返回0值
            return StockQuote(
                code=code,
                name="",
                price=0.0,
                change=0.0,
                change_pct=0.0,
                volume=0,
                amount=0.0,
                market_cap=0.0
            )
        except Exception as e:
            logger.error(f"[BaoStock] 获取股票行情失败: {e}")
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
            if not self.bs_lg:
                raise Exception("BaoStock未连接")
            
            logger.info(f"[BaoStock] 获取K线数据: {code}, {start_date} 到 {end_date}, 频率: {freq}")
            
            # 转换代码格式
            bs_code = self.add_market_suffix(code)
            
            # 频率映射
            freq_map = {
                '1d': 'd',
                '1w': 'w',
                '1m': 'm'
            }
            
            bs_freq = freq_map.get(freq, 'd')
            
            # 获取数据
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,open,high,low,close,volume,amount",
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                frequency=bs_freq,
                adjustflag="3"  # 不复权
            )
            
            if rs.error_code != '0':
                raise Exception(f"BaoStock查询失败: {rs.error_msg}")
            
            # 解析数据
            kline_list = []
            while (rs.error_code == '0') & rs.next():
                try:
                    row = rs.get_row_data()
                    if len(row) < 7:
                        continue
                    
                    kline_list.append(KlineData(
                        date=datetime.strptime(row[0], '%Y-%m-%d'),
                        open=float(row[1]) if row[1] else 0.0,
                        high=float(row[2]) if row[2] else 0.0,
                        low=float(row[3]) if row[3] else 0.0,
                        close=float(row[4]) if row[4] else 0.0,
                        volume=int(float(row[5])) if row[5] else 0,
                        amount=float(row[6]) if row[6] else 0.0
                    ))
                except Exception as e:
                    logger.warning(f"[BaoStock] 解析K线行数据失败: {e}")
                    continue
            
            logger.info(f"[BaoStock] 获取成功: {len(kline_list)} 条K线数据")
            return kline_list
            
        except Exception as e:
            logger.error(f"[BaoStock] 获取K线数据失败: {e}")
            raise
    
    async def search_stocks(self, keyword: str, limit: int = 20) -> List[StockQuote]:
        """搜索股票"""
        try:
            logger.info(f"[BaoStock] 搜索股票: {keyword}")
            
            # 使用get_stock_list并过滤
            stocks = await self.get_stock_list(page=1, page_size=limit * 2)
            
            results = [
                stock for stock in stocks
                if keyword.lower() in stock.code.lower()
                or keyword.lower() in stock.name.lower()
            ]
            
            return results[:limit]
        except Exception as e:
            logger.error(f"[BaoStock] 搜索股票失败: {e}")
            return []
    
    def __del__(self):
        """析构时断开连接"""
        if self.bs_lg:
            try:
                bs.logout()
            except:
                pass