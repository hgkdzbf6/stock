"""Ashare数据适配器 - 使用Ashare库获取A股数据"""
import sys
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, List
from loguru import logger
import pandas as pd
from datetime import datetime
from .models import KlineData, StockQuote

# 添加Ashare库路径
ashare_path = Path(__file__).parent.parent / "3rdparty" / "Ashare"
sys.path.insert(0, str(ashare_path))

try:
    from Ashare import get_price
    ASHARE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Ashare库不可用: {e}")
    ASHARE_AVAILABLE = False


class AshareAdapter:
    """Ashare数据适配器"""
    
    def __init__(self):
        """初始化Ashare适配器"""
        self.name = "Ashare"
        self.available = ASHARE_AVAILABLE
        if not self.available:
            logger.error("Ashare库未安装或不可用")
        
        logger.info(f"[Ashare] 初始化完成: {'可用' if self.available else '不可用'}")
    
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
            code: 股票代码（如 sh600519, sz000001）
            start_date: 开始日期
            end_date: 结束日期
            freq: 频率（1d日线, 1w周线, 1M月线, 1m/5m/15m/30m/60m分钟线）
            
        Returns:
            K线数据列表
        """
        if not self.available:
            logger.error("[Ashare] 库不可用")
            return []
        
        try:
            # 转换股票代码格式
            ashare_code = self._convert_code_format(code)
            logger.info(f"[Ashare] 获取K线数据: {code} ({ashare_code}), {start_date} - {end_date}, 频率: {freq}")
            
            # 计算需要获取的数据条数
            days_diff = (end_date - start_date).days + 10  # 多取一些以确保覆盖
            count = max(days_diff, 10)
            
            # 如果是分钟线，需要计算分钟数
            if freq in ['1m', '5m', '15m', '30m', '60m']:
                minutes_per_day = 240  # 4小时交易时间
                count = max(days_diff * minutes_per_day // int(freq[0]), 10)
            
            # 在线程池中执行同步的get_price函数
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: get_price(
                    code=ashare_code,
                    end_date=end_date,
                    count=count,
                    frequency=freq
                )
            )
            
            if df is None or len(df) == 0:
                logger.warning(f"[Ashare] 未获取到数据: {code}")
                return []
            
            # 过滤日期范围
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            
            if len(df) == 0:
                logger.warning(f"[Ashare] 过滤后无数据: {code}")
                return []
            
            # 确保列名标准化
            df = self._standardize_columns(df)
            
            # 转换为KlineData列表
            kline_list = []
            for idx, row in df.iterrows():
                kline = KlineData(
                    date=idx,
                    code=code,
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['volume']),
                    amount=0.0  # Ashare没有成交额数据
                )
                kline_list.append(kline)
            
            logger.info(f"[Ashare] 获取成功: {len(kline_list)}条K线数据")
            return kline_list
            
        except Exception as e:
            logger.error(f"[Ashare] 获取K线数据失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def search_stocks(
        self,
        keyword: str,
        limit: int = 20
    ) -> List[StockQuote]:
        """
        搜索股票（Ashare不支持搜索，返回空列表）
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            股票列表
        """
        logger.warning("[Ashare] 不支持股票搜索功能")
        return []
    
    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 100,
        keyword: Optional[str] = None
    ) -> List[StockQuote]:
        """
        获取股票列表（Ashare不支持获取全量列表，返回空列表）
        
        Args:
            page: 页码
            page_size: 每页数量
            keyword: 搜索关键词
            
        Returns:
            股票列表
        """
        logger.warning("[Ashare] 不支持获取全量股票列表")
        return []
    
    async def get_stock_quote(self, code: str) -> Optional[StockQuote]:
        """
        获取单只股票实时行情（Ashare不支持此功能）
        
        Args:
            code: 股票代码
            
        Returns:
            股票行情数据
        """
        logger.warning("[Ashare] 不支持获取单只股票实时行情")
        return None
    
    def _convert_code_format(self, stock_code: str) -> str:
        """
        转换股票代码格式为Ashare兼容格式
        
        Args:
            stock_code: 股票代码（如 600519.SH, 600771.SH, sh600519, sz000001）
            
        Returns:
            Ashare格式的股票代码（sh600519 或 sz000001）
        """
        code = stock_code.replace('.SH', '').replace('.SZ', '')
        code = code.replace('.XSHG', '').replace('.XSHE', '')
        code = code.replace('sh.', '').replace('sz.', '')
        
        # 判断市场
        if code.isdigit():
            if code.startswith('6') or code.startswith('5'):
                return f'sh{code}'
            else:
                return f'sz{code}'
        else:
            # 已经是sh或sz开头的格式
            return code.lower()
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化DataFrame列名
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        # Ashare返回的列名已经是标准格式：open, close, high, low, volume
        # 直接返回
        return df


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test():
        adapter = AshareAdapter()
        
        if adapter.available:
            # 测试获取K线数据
            kline_list = await adapter.get_kline_data(
                code="600519.SH",
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 10),
                freq="1d"
            )
            
            if kline_list:
                print(f"数据形状: {len(kline_list)}条")
                if kline_list:
                    print("\n第一条数据:")
                    print(kline_list[0])
            else:
                print("获取数据失败")
        else:
            print("Ashare不可用")
    
    asyncio.run(test())