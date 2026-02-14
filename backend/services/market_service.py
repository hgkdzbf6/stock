"""市场行情服务"""
from typing import Optional, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from services.data_fetcher import DataFetcher
from core.config import settings
from loguru import logger


class MarketService:
    """市场行情服务"""

    def __init__(self):
        # 从环境变量读取配置
        data_source = getattr(settings, 'DATA_SOURCE', 'akshare')
        tushare_token = getattr(settings, 'TUSHARE_TOKEN', None)
        
        logger.info(f"初始化MarketService，数据源: {data_source}")
        logger.info(f"Tushare Token: {'已配置' if tushare_token else '未配置'}")
        
        self.data_fetcher = DataFetcher(
            token=tushare_token,
            source=data_source
        )
    
    def _ensure_data_fetcher(self):
        """确保data_fetcher使用最新配置"""
        from core.config import settings
        current_source = getattr(settings, 'DATA_SOURCE', 'akshare')
        current_token = getattr(settings, 'TUSHARE_TOKEN', None)
        
        # 如果配置有变化，重新初始化data_fetcher
        if (self.data_fetcher.source != current_source or 
            (current_source == 'tushare' and current_token and 
             not hasattr(self.data_fetcher, 'pro'))):
            logger.info(f"重新初始化data_fetcher，数据源: {current_source}")
            self.data_fetcher = DataFetcher(
                token=current_token,
                source=current_source
            )
        
        return self.data_fetcher

    async def get_realtime_quote(self, stock_code: str) -> dict:
        """
        获取实时行情

        Args:
            stock_code: 股票代码

        Returns:
            实时行情数据
        """
        try:
            # 获取最新数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)

            df = await self.data_fetcher.get_data(
                stock_code, start_date, end_date, freq='1d'
            )

            if df.empty:
                logger.warning(f"未获取到股票 {stock_code} 的行情数据")
                return {}

            latest = df.iloc[-1]

            # 计算涨跌幅
            if len(df) > 1:
                prev_close = df.iloc[-2]['close']
                change = latest['close'] - prev_close
                change_pct = (change / prev_close) * 100 if prev_close > 0 else 0
            else:
                change = 0
                change_pct = 0

            return {
                'stock_code': stock_code,
                'price': float(latest['close']),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'open': float(latest['open']),
                'high': float(latest['high']),
                'low': float(latest['low']),
                'volume': int(latest['volume']),
                'timestamp': latest.name.isoformat()
            }

        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            raise

    async def get_kline_data(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str = 'daily'
    ) -> List[dict]:
        """
        获取K线数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            freq: 频率 ('1min', '5min', '15min', '30min', '60min', 'daily')

        Returns:
            K线数据列表
        """
        try:
            logger.info(f"获取K线数据: {stock_code}, {freq}")

            # 映射频率
            freq_map = {
                '1min': '1min',
                '5min': '5min',
                '15min': '15min',
                '30min': '30min',
                '60min': '60min',
                'daily': '1d'
            }

            freq_value = freq_map.get(freq, 'daily')

            df = await self.data_fetcher.get_data(
                stock_code, start_date, end_date, freq=freq_value
            )

            if df.empty:
                return []

            # 转换为列表格式
            kline_data = []
            for timestamp, row in df.iterrows():
                kline_data.append({
                    'timestamp': timestamp.isoformat(),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume'])
                })

            return kline_data

        except Exception as e:
            logger.error(f"获取K线数据失败: {e}")
            raise

    async def get_indicators(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str = 'daily',
        indicators: List[str] = None
    ) -> dict:
        """
        获取技术指标

        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            freq: 频率
            indicators: 指标列表 ['MA', 'BOLL', 'RSI', 'MACD', 'KDJ']

        Returns:
            技术指标数据
        """
        try:
            if indicators is None:
                indicators = ['MA', 'BOLL', 'RSI', 'MACD']

            df = await self.data_fetcher.get_data(
                stock_code, start_date, end_date, freq=freq
            )

            if df.empty:
                return {}

            result = {}

            # MA指标
            if 'MA' in indicators:
                result['MA'] = {
                    'MA5': df['close'].rolling(window=5).mean().fillna('').tolist(),
                    'MA10': df['close'].rolling(window=10).mean().fillna('').tolist(),
                    'MA20': df['close'].rolling(window=20).mean().fillna('').tolist(),
                    'MA60': df['close'].rolling(window=60).mean().fillna('').tolist()
                }

            # BOLL指标
            if 'BOLL' in indicators:
                rolling_mean = df['close'].rolling(window=20)
                rolling_std = df['close'].rolling(window=20).std()
                result['BOLL'] = {
                    'upper': (rolling_mean + 2 * rolling_std).fillna('').tolist(),
                    'middle': rolling_mean.fillna('').tolist(),
                    'lower': (rolling_mean - 2 * rolling_std).fillna('').tolist()
                }

            # RSI指标
            if 'RSI' in indicators:
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                result['RSI'] = rsi.fillna('').tolist()

            # MACD指标
            if 'MACD' in indicators:
                ema12 = df['close'].ewm(span=12, adjust=False).mean()
                ema26 = df['close'].ewm(span=26, adjust=False).mean()
                dif = ema12 - ema26
                dea = dif.ewm(span=9, adjust=False).mean()
                macd = (dif - dea) * 2
                result['MACD'] = {
                    'DIF': dif.fillna('').tolist(),
                    'DEA': dea.fillna('').tolist(),
                    'MACD': macd.fillna('').tolist()
                }

            return result

        except Exception as e:
            logger.error(f"获取技术指标失败: {e}")
            raise


# 全局实例
market_service = MarketService()
