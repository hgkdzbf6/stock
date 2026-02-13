"""数据获取服务 - 复用并适配原有代码"""
import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

import akshare as ak


class DataFetcher:
    """数据获取器 - 异步版本"""

    def __init__(self, token: Optional[str] = None, source: str = 'akshare'):
        """
        初始化数据获取器

        Args:
            token: tushare API token
            source: 数据源 ('tushare' 或 'akshare')
        """
        self.source = source
        if source == 'tushare' and token:
            ts.set_token(token)
            self.pro = ts.pro_api()
        elif source == 'akshare':
            # akshare不需要token
            pass
        else:
            logger.warning(f"无效的数据源配置: {source}, 使用默认值")
            self.source = 'akshare'

    async def get_data(
        self,
        code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str = '1min'
    ) -> pd.DataFrame:
        """
        获取股票数据

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            freq: 数据频率 ('1min', '5min', '15min', '30min', '60min', '1d')

        Returns:
            DataFrame包含OHLCV数据
        """
        logger.info(f"获取股票数据: {code}, {start_date} 到 {end_date}, 频率: {freq}")

        if self.source == 'tushare':
            return self._get_tushare_data(code, start_date, end_date, freq)
        elif self.source == 'akshare':
            return self._get_akshare_data(code, start_date, end_date, freq)
        else:
            raise ValueError(f"不支持的数据源: {self.source}")

    def _get_tushare_data(
        self,
        code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str
    ) -> pd.DataFrame:
        """使用tushare获取数据"""
        # 将代码转换为tushare格式
        if code.startswith('6'):
            ts_code = f"{code}.SH"
        else:
            ts_code = f"{code}.SZ"

        if freq == '1d':
            # 日线数据
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d')
            )
        else:
            # 分钟数据（tushare分钟数据需要权限）
            logger.warning("tushare分钟数据需要高级权限，使用模拟数据")
            return self._generate_mock_minute_data(code, start_date, end_date, freq)

        # 数据处理
        df = df.sort_values('trade_date')
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.set_index('trade_date', inplace=True)

        return df

    def _get_akshare_data(
        self,
        code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str
    ) -> pd.DataFrame:
        """使用akshare获取数据"""
        try:
            logger.info(f"从akshare获取数据: {code}, {freq}")

            if freq == '1d':
                # 日线数据
                df = ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d'),
                    adjust=""
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

                logger.info("akshare分钟数据通常只提供最近几天的数据")
                df = ak.stock_zh_a_hist_min_em(
                    symbol=code,
                    period=period_map.get(freq, '30'),
                    start_date=start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    end_date=end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    adjust=""
                )

            if df.empty:
                logger.warning("akshare返回空数据，使用模拟数据")
                return self._generate_mock_minute_data(code, start_date, end_date, freq)

            # 统一列名
            df.columns = [
                'date', 'code', 'open', 'close', 'high', 'low',
                'volume', 'amount', 'amplitude', 'pct_chg', 'change', 'turnover_rate'
            ]
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

            logger.info(f"akshare获取成功: {len(df)}条记录")

            return df

        except Exception as e:
            logger.error(f"akshare获取数据失败: {e}")
            logger.info("使用模拟数据")
            return self._generate_mock_minute_data(code, start_date, end_date, freq)

    def _generate_mock_minute_data(
        self,
        code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str
    ) -> pd.DataFrame:
        """生成模拟分钟数据用于测试"""
        logger.info(f"生成模拟数据: {code}, {start_date} 到 {end_date}, 频率: {freq}")

        # 生成时间序列
        freq_minutes = {
            '1min': 1,
            '5min': 5,
            '15min': 15,
            '30min': 30,
            '60min': 60
        }

        interval_minutes = freq_minutes.get(freq, 30)

        # 生成完整的日期范围
        date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')

        all_data = []
        all_timestamps = []
        base_price = 10.0  # 基础价格

        for date in date_range:
            # 跳过周末
            if date.weekday() >= 5:
                continue

            # 模拟akshare的实际时间点：10:00, 10:30, 11:00, 11:30, 13:30, 14:00, 14:30, 15:00 (8个点)
            day_times = []

            if interval_minutes == 30:
                # 30分钟间隔的特定时间点（与akshare一致）
                time_points = [
                    (10, 0), (10, 30), (11, 0), (11, 30),  # 上午4个点
                    (13, 30), (14, 0), (14, 30), (15, 0)   # 下午4个点
                ]
                for hour, minute in time_points:
                    day_times.append(date.replace(hour=hour, minute=minute, second=0, microsecond=0))
            else:
                # 上午时段：9:30-11:30
                morning_times = []
                current_time = date.replace(hour=9, minute=30, second=0, microsecond=0)
                end_morning = date.replace(hour=11, minute=30, second=0, microsecond=0)

                while current_time <= end_morning:
                    morning_times.append(current_time)
                    current_time += timedelta(minutes=interval_minutes)

                # 下午时段：13:00-15:00
                afternoon_times = []
                current_time = date.replace(hour=13, minute=0, second=0, microsecond=0)
                end_afternoon = date.replace(hour=15, minute=0, second=0, microsecond=0)

                while current_time <= end_afternoon:
                    afternoon_times.append(current_time)
                    current_time += timedelta(minutes=interval_minutes)

                day_times = morning_times + afternoon_times

            for timestamp in day_times:
                # 生成更真实的价格数据
                price_change = np.random.normal(0, 0.015)  # 1.5%的标准差
                base_price *= (1 + price_change)
                base_price = max(base_price, 1.0)  # 价格不能低于1元

                # 生成OHLC数据
                volatility = abs(np.random.normal(0, 0.008))  # 0.8%波动率
                high = base_price * (1 + volatility)
                low = base_price * (1 - volatility)

                # 开盘价基于前一个收盘价
                if all_data:
                    open_price = all_data[-1]['close'] * (1 + np.random.normal(0, 0.003))
                else:
                    open_price = base_price

                close_price = base_price

                # 确保OHLC逻辑正确
                high = max(high, open_price, close_price)
                low = min(low, open_price, close_price)

                # 生成成交量
                volume = np.random.randint(5000, 50000)

                all_data.append({
                    'open': round(open_price, 2),
                    'high': round(high, 2),
                    'low': round(low, 2),
                    'close': round(close_price, 2),
                    'volume': volume
                })
                all_timestamps.append(timestamp)

        df = pd.DataFrame(all_data, index=all_timestamps)
        df.index.name = 'date'

        logger.info(f"生成模拟数据完成: {len(df)}条记录")

        return df

    async def get_stock_list(self) -> list:
        """获取股票列表"""
        try:
            logger.info("获取股票列表")
            # 使用akshare获取股票列表
            stocks = ak.stock_zh_a_spot_em()
            return stocks.to_dict('records')
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []

    async def search_stocks(self, keyword: str) -> list:
        """搜索股票"""
        try:
            logger.info(f"搜索股票: {keyword}")
            stocks = await self.get_stock_list()

            # 简单的搜索逻辑
            results = [
                stock for stock in stocks
                if keyword.lower() in str(stock.get('代码', '')).lower()
                or keyword.lower() in str(stock.get('名称', '')).lower()
            ]

            return results[:20]  # 返回前20个结果
        except Exception as e:
            logger.error(f"搜索股票失败: {e}")
            return []
