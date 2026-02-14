"""数据获取服务 - 使用适配器模式支持多种数据源"""
from typing import Optional, List
from datetime import datetime
from loguru import logger
import pandas as pd
from data_adapters import AdapterFactory, StockQuote, KlineData


class DataFetcher:
    """数据获取器 - 使用适配器模式支持多种数据源"""

    def __init__(self, token: Optional[str] = None, source: str = 'ashare'):
        """
        初始化数据获取器

        Args:
            token: tushare API token
            source: 数据源 ('ashare', 'tushare', 'akshare', 'baostock', 'sina', 'tencent', 'eastmoney', 'mock', 'auto')
        """
        self.source = source
        self.adapter_factory = AdapterFactory(tushare_token=token)
        logger.info(f"数据源: {source}")

    async def get_data(
        self,
        code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str = '1min'
    ) -> pd.DataFrame:
        """
        获取股票数据（返回DataFrame格式，保持向后兼容）

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            freq: 数据频率 ('1min', '5min', '15min', '30min', '60min', '1d')

        Returns:
            DataFrame包含OHLCV数据
        """
        logger.info(f"获取股票数据: {code}, {start_date} 到 {end_date}, 频率: {freq}")

        # 获取K线数据
        kline_data_list, used_source = await self._get_kline_with_source(
            code, start_date, end_date, freq
        )
        
        if not kline_data_list:
            logger.warning(f"未获取到数据，使用mock")
            return self._generate_mock_dataframe(code, start_date, end_date, freq)

        # 转换为DataFrame
        data = []
        for kline in kline_data_list:
            data.append({
                'open': kline.open,
                'high': kline.high,
                'low': kline.low,
                'close': kline.close,
                'volume': kline.volume
            })
        
        df = pd.DataFrame(data)
        df.index = [kline.date for kline in kline_data_list]
        df.index.name = 'date'
        df = df.sort_index()
        
        logger.info(f"获取成功: {len(df)}条记录，数据源: {used_source}")
        return df

    async def _get_kline_with_source(
        self,
        code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str
    ) -> tuple[List[KlineData], str]:
        """获取K线数据并返回使用的数据源"""
        if self.source == 'auto':
            return await self.adapter_factory.auto_get_kline_data(
                code, start_date, end_date, freq
            )
        else:
            adapter = self.adapter_factory.get_adapter(self.source)
            if adapter:
                return await adapter.get_kline_data(code, start_date, end_date, freq), self.source
            else:
                # 降级到auto模式
                return await self.adapter_factory.auto_get_kline_data(
                    code, start_date, end_date, freq
                )

    def _generate_mock_dataframe(
        self,
        code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str
    ) -> pd.DataFrame:
        """生成模拟DataFrame数据"""
        import numpy as np
        
        logger.info(f"生成模拟数据: {code}, {start_date} 到 {end_date}, {freq}")

        freq_minutes = {
            '1min': 1,
            '5min': 5,
            '15min': 15,
            '30min': 30,
            '60min': 60
        }
        interval_minutes = freq_minutes.get(freq, 30)

        date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')

        all_data = []
        base_price = 10.0

        for date in date_range:
            if date.weekday() >= 5:
                continue

            if interval_minutes == 30:
                time_points = [
                    (10, 0), (10, 30), (11, 0), (11, 30),
                    (13, 30), (14, 0), (14, 30), (15, 0)
                ]
                timestamps = [date.replace(hour=hour, minute=minute, second=0) for hour, minute in time_points]
            elif freq == '1d':
                timestamps = [date]
            else:
                morning_times = []
                current_time = date.replace(hour=9, minute=30, second=0)
                end_morning = date.replace(hour=11, minute=30, second=0)
                while current_time <= end_morning:
                    morning_times.append(current_time)
                    current_time += pd.Timedelta(minutes=interval_minutes)

                afternoon_times = []
                current_time = date.replace(hour=13, minute=0, second=0)
                end_afternoon = date.replace(hour=15, minute=0, second=0)
                while current_time <= end_afternoon:
                    afternoon_times.append(current_time)
                    current_time += pd.Timedelta(minutes=interval_minutes)

                timestamps = morning_times + afternoon_times

            for timestamp in timestamps:
                price_change = np.random.normal(0, 0.015)
                base_price *= (1 + price_change)
                base_price = max(base_price, 1.0)

                volatility = abs(np.random.normal(0, 0.008))
                high = base_price * (1 + volatility)
                low = base_price * (1 - volatility)

                if all_data:
                    open_price = all_data[-1]['close'] * (1 + np.random.normal(0, 0.003))
                else:
                    open_price = base_price

                close_price = base_price
                high = max(high, open_price, close_price)
                low = min(low, open_price, close_price)
                volume = np.random.randint(5000, 50000)

                all_data.append({
                    'date': timestamp,
                    'open': round(open_price, 2),
                    'high': round(high, 2),
                    'low': round(low, 2),
                    'close': round(close_price, 2),
                    'volume': volume
                })

        df = pd.DataFrame(all_data)
        df.set_index('date', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']]

        logger.info(f"生成模拟数据完成: {len(df)}条记录")
        return df

    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: str = None
    ) -> list:
        """
        获取股票列表（返回字典格式，保持向后兼容）
        
        Args:
            page: 页码
            page_size: 每页数量
            keyword: 搜索关键词
        """
        try:
            logger.info(f"获取股票列表: page={page}, page_size={page_size}, 数据源: {self.source}")
            
            # 使用适配器获取数据
            try:
                if self.source == 'auto':
                    stocks, used_source = await self.adapter_factory.auto_get_stock_list(
                        page, page_size, keyword
                    )
                else:
                    adapter = self.adapter_factory.get_adapter(self.source)
                    if adapter:
                        stocks = await adapter.get_stock_list(page, page_size, keyword)
                        used_source = self.source
                    else:
                        stocks, used_source = await self.adapter_factory.auto_get_stock_list(
                            page, page_size, keyword
                        )
            except Exception as e:
                logger.warning(f"使用数据源 {self.source} 失败，尝试auto模式: {e}")
                stocks, used_source = await self.adapter_factory.auto_get_stock_list(
                    page, page_size, keyword
                )
            
            # 转换为字典格式（向后兼容）
            stocks_dict = []
            for stock in stocks:
                stocks_dict.append({
                    '代码': stock.code,
                    '名称': stock.name,
                    '最新价': stock.price,
                    '涨跌额': stock.change,
                    '涨跌幅': stock.change_pct,
                    '成交量': stock.volume,
                    '成交额': stock.amount,
                    '市值': stock.market_cap,
                    '开盘': stock.open,
                    '最高': stock.high,
                    '最低': stock.low,
                    '昨收': stock.pre_close
                })
            
            logger.info(f"获取成功: {len(stocks_dict)} 只股票，数据源: {used_source}")
            return stocks_dict
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            raise

    async def search_stocks(self, keyword: str, limit: int = 20) -> list:
        """
        搜索股票（返回字典格式，保持向后兼容）
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
        """
        try:
            logger.info(f"搜索股票: {keyword}")
            
            # 使用适配器搜索
            if self.source == 'auto':
                stocks, used_source = await self.adapter_factory.auto_search_stocks(keyword, limit)
            else:
                adapter = self.adapter_factory.get_adapter(self.source)
                if adapter:
                    stocks = await adapter.search_stocks(keyword, limit)
                    used_source = self.source
                else:
                    stocks, used_source = await self.adapter_factory.auto_search_stocks(keyword, limit)
            
            # 转换为字典格式（向后兼容）
            stocks_dict = []
            for stock in stocks:
                stocks_dict.append({
                    '代码': stock.code,
                    '名称': stock.name,
                    '最新价': stock.price,
                    '涨跌额': stock.change,
                    '涨跌幅': stock.change_pct,
                    '成交量': stock.volume,
                    '市值': stock.market_cap
                })
            
            logger.info(f"搜索成功: {len(stocks_dict)} 只股票，数据源: {used_source}")
            return stocks_dict
            
        except Exception as e:
            logger.error(f"搜索股票失败: {e}")
            return []