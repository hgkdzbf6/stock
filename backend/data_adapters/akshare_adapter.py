"""AkShare数据源适配器"""
import akshare as ak
import pandas as pd
from typing import List, Optional
from datetime import datetime
import time
from loguru import logger
from .base import BaseAdapter
from .models import StockQuote, KlineData


class AkShareAdapter(BaseAdapter):
    """AkShare数据源适配器"""
    
    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None
    ) -> List[StockQuote]:
        """获取股票列表"""
        try:
            logger.info(f"[AkShare] 获取股票列表: page={page}, page_size={page_size}")
            
            df = ak.stock_zh_a_spot_em()
            time.sleep(5)  # 避免频繁请求
            
            if df.empty:
                raise Exception("AkShare返回空数据")
            
            # 关键词过滤
            if keyword:
                df = df[
                    df['代码'].str.contains(keyword, case=False) |
                    df['名称'].str.contains(keyword, case=False)
                ]
            
            # 分页
            total = len(df)
            start = (page - 1) * page_size
            end = start + page_size
            df = df.iloc[start:end]
            
            # 转换为StockQuote
            stocks = []
            for _, row in df.iterrows():
                stocks.append(StockQuote(
                    code=str(row['代码']),
                    name=str(row['名称']),
                    price=float(row['最新价']) if row['最新价'] else 0.0,
                    change=float(row['涨跌额']) if row['涨跌额'] else 0.0,
                    change_pct=float(row['涨跌幅']) if row['涨跌幅'] else 0.0,
                    open=float(row['今开']) if row['今开'] else None,
                    high=float(row['最高']) if row['最高'] else None,
                    low=float(row['最低']) if row['最低'] else None,
                    pre_close=float(row['昨收']) if row['昨收'] else None,
                    volume=int(float(row['成交量'])) if row['成交量'] else 0,
                    amount=float(row['成交额']) if row['成交额'] else 0.0,
                    market_cap=float(row['总市值']) / 100000000 if row['总市值'] else 0.0,
                    turnover_rate=float(row['换手率']) if row['换手率'] else None,
                    pe=float(row['市盈率-动态']) if row['市盈率-动态'] else None,
                    pb=float(row['市净率']) if row['市净率'] else None
                ))
            
            logger.info(f"[AkShare] 获取成功: {len(stocks)} 只股票，总计: {total}")
            return stocks
            
        except Exception as e:
            logger.error(f"[AkShare] 获取股票列表失败: {e}")
            raise
    
    async def get_stock_quote(self, code: str) -> Optional[StockQuote]:
        """获取单只股票实时行情"""
        try:
            logger.info(f"[AkShare] 获取股票行情: {code}")
            
            df = ak.stock_zh_a_spot_em()
            
            if df.empty:
                return None
            
            row = df[df['代码'] == code]
            if row.empty:
                return None
            
            row = row.iloc[0]
            
            return StockQuote(
                code=str(row['代码']),
                name=str(row['名称']),
                price=float(row['最新价']) if row['最新价'] else 0.0,
                change=float(row['涨跌额']) if row['涨跌额'] else 0.0,
                change_pct=float(row['涨跌幅']) if row['涨跌幅'] else 0.0,
                open=float(row['今开']) if row['今开'] else None,
                high=float(row['最高']) if row['最高'] else None,
                low=float(row['最低']) if row['最低'] else None,
                pre_close=float(row['昨收']) if row['昨收'] else None,
                volume=int(float(row['成交量'])) if row['成交量'] else 0,
                amount=float(row['成交额']) if row['成交额'] else 0.0,
                market_cap=float(row['总市值']) / 100000000 if row['总市值'] else 0.0
            )
        except Exception as e:
            logger.error(f"[AkShare] 获取股票行情失败: {e}")
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
            logger.info(f"[AkShare] 获取K线数据: {code}, {start_date} 到 {end_date}, 频率: {freq}")
            
            if freq == '1d':
                # 日线数据
                df = ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d'),
                    adjust="qfq"  # 前复权
                )
            else:
                # 分钟数据
                period_map = {
                    '1min': '1',
                    '5min': '5',
                    '15min': '15',
                    '30min': '30',
                    '60min': '60'
                }
                
                df = ak.stock_zh_a_hist_min_em(
                    symbol=code,
                    period=period_map.get(freq, '30'),
                    start_date=start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    end_date=end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    adjust="qfq"
                )
            
            if df.empty:
                return []
            
            # 转换为KlineData
            kline_list = []
            for _, row in df.iterrows():
                kline_list.append(KlineData(
                    date=pd.to_datetime(row['日期']) if freq == '1d' else pd.to_datetime(row['时间']),
                    open=float(row['开盘']) if row['开盘'] else 0.0,
                    high=float(row['最高']) if row['最高'] else 0.0,
                    low=float(row['最低']) if row['最低'] else 0.0,
                    close=float(row['收盘']) if row['收盘'] else 0.0,
                    volume=int(float(row['成交量'])) if row['成交量'] else 0,
                    amount=float(row['成交额']) if row['成交额'] else None
                ))
            
            logger.info(f"[AkShare] 获取成功: {len(kline_list)} 条K线数据")
            return kline_list
            
        except Exception as e:
            logger.error(f"[AkShare] 获取K线数据失败: {e}")
            raise
    
    async def search_stocks(self, keyword: str, limit: int = 20) -> List[StockQuote]:
        """搜索股票"""
        try:
            logger.info(f"[AkShare] 搜索股票: {keyword}")
            
            stocks = await self.get_stock_list(page=1, page_size=limit, keyword=keyword)
            
            return stocks[:limit]
        except Exception as e:
            logger.error(f"[AkShare] 搜索股票失败: {e}")
            return []