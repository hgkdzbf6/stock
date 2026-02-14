"""Mock数据源适配器"""
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger
from .base import BaseAdapter
from .models import StockQuote, KlineData


class MockAdapter(BaseAdapter):
    """Mock数据源适配器（用于测试和降级）"""
    
    # 模拟股票数据
    MOCK_STOCKS = [
        {
            'code': '000001', 'name': '平安银行', 'price': 12.50,
            'change': 0.15, 'change_pct': 1.25,
            'open': 12.35, 'high': 12.60, 'low': 12.30, 'pre_close': 12.35,
            'volume': 1000000, 'amount': 12450000, 'market_cap': 2425.0
        },
        {
            'code': '000002', 'name': '万科A', 'price': 8.75,
            'change': -0.03, 'change_pct': -0.34,
            'open': 8.80, 'high': 8.85, 'low': 8.70, 'pre_close': 8.78,
            'volume': 800000, 'amount': 7000000, 'market_cap': 962.5
        },
        {
            'code': '000858', 'name': '五粮液', 'price': 158.50,
            'change': 2.35, 'change_pct': 1.50,
            'open': 156.20, 'high': 159.80, 'low': 155.90, 'pre_close': 156.15,
            'volume': 500000, 'amount': 79250000, 'market_cap': 6120.0
        },
        {
            'code': '600000', 'name': '浦发银行', 'price': 7.35,
            'change': 0.08, 'change_pct': 1.10,
            'open': 7.28, 'high': 7.40, 'low': 7.25, 'pre_close': 7.27,
            'volume': 1200000, 'amount': 8820000, 'market_cap': 2148.0
        },
        {
            'code': '600519', 'name': '贵州茅台', 'price': 1680.00,
            'change': 25.50, 'change_pct': 1.54,
            'open': 1655.00, 'high': 1690.00, 'low': 1650.00, 'pre_close': 1654.50,
            'volume': 200000, 'amount': 336000000, 'market_cap': 210000.0
        },
        {
            'code': '600036', 'name': '招商银行', 'price': 32.50,
            'change': 0.65, 'change_pct': 2.04,
            'open': 31.90, 'high': 32.80, 'low': 31.85, 'pre_close': 31.85,
            'volume': 600000, 'amount': 19500000, 'market_cap': 8125.0
        },
        {
            'code': '000333', 'name': '美的集团', 'price': 62.80,
            'change': -0.70, 'change_pct': -1.10,
            'open': 63.50, 'high': 63.80, 'low': 62.50, 'pre_close': 63.50,
            'volume': 450000, 'amount': 28260000, 'market_cap': 4396.0
        },
        {
            'code': '601318', 'name': '中国平安', 'price': 45.20,
            'change': 0.90, 'change_pct': 2.03,
            'open': 44.35, 'high': 45.50, 'low': 44.20, 'pre_close': 44.30,
            'volume': 800000, 'amount': 36160000, 'market_cap': 8266.0
        },
        {
            'code': '000651', 'name': '格力电器', 'price': 35.80,
            'change': 0.42, 'change_pct': 1.19,
            'open': 35.40, 'high': 36.00, 'low': 35.30, 'pre_close': 35.38,
            'volume': 550000, 'amount': 19690000, 'market_cap': 2026.0
        },
        {
            'code': '600900', 'name': '长江电力', 'price': 24.50,
            'change': 0.18, 'change_pct': 0.74,
            'open': 24.35, 'high': 24.60, 'low': 24.30, 'pre_close': 24.32,
            'volume': 300000, 'amount': 7350000, 'market_cap': 5625.0
        }
    ]
    
    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None
    ) -> List[StockQuote]:
        """获取股票列表"""
        try:
            logger.info(f"[Mock] 获取股票列表: page={page}, page_size={page_size}")
            
            # 过滤关键词
            stocks_data = self.MOCK_STOCKS
            if keyword:
                stocks_data = [
                    s for s in stocks_data
                    if keyword.lower() in s['code'].lower()
                    or keyword.lower() in s['name'].lower()
                ]
            
            # 分页
            start = (page - 1) * page_size
            end = start + page_size
            stocks_data = stocks_data[start:end]
            
            # 转换为StockQuote
            stocks = [
                StockQuote(**stock) for stock in stocks_data
            ]
            
            logger.info(f"[Mock] 返回 {len(stocks)} 只模拟股票")
            return stocks
        except Exception as e:
            logger.error(f"[Mock] 获取股票列表失败: {e}")
            return []
    
    async def get_stock_quote(self, code: str) -> Optional[StockQuote]:
        """获取单只股票实时行情"""
        try:
            logger.info(f"[Mock] 获取股票行情: {code}")
            
            for stock in self.MOCK_STOCKS:
                if stock['code'] == code:
                    return StockQuote(**stock)
            
            return None
        except Exception as e:
            logger.error(f"[Mock] 获取股票行情失败: {e}")
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
            logger.info(f"[Mock] 获取K线数据: {code}, {start_date} 到 {end_date}, 频率: {freq}")
            
            # 查找股票
            stock = None
            for s in self.MOCK_STOCKS:
                if s['code'] == code:
                    stock = s
                    break
            
            if not stock:
                return []
            
            # 生成模拟K线数据
            kline_list = []
            current_date = start_date
            base_price = stock['price']
            
            while current_date <= end_date:
                # 跳过周末
                if current_date.weekday() < 5:
                    # 随机波动
                    import random
                    open_price = base_price * (1 + random.uniform(-0.02, 0.02))
                    close_price = open_price * (1 + random.uniform(-0.03, 0.03))
                    high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))
                    low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))
                    volume = random.randint(500000, 2000000)
                    amount = volume * close_price
                    
                    kline_list.append(KlineData(
                        date=current_date,
                        open=round(open_price, 2),
                        high=round(high_price, 2),
                        low=round(low_price, 2),
                        close=round(close_price, 2),
                        volume=volume,
                        amount=round(amount, 2)
                    ))
                
                current_date += timedelta(days=1)
                # 调整基础价格
                base_price = base_price * (1 + random.uniform(-0.005, 0.005))
            
            logger.info(f"[Mock] 生成 {len(kline_list)} 条模拟K线数据")
            return kline_list
        except Exception as e:
            logger.error(f"[Mock] 获取K线数据失败: {e}")
            return []
    
    async def search_stocks(self, keyword: str, limit: int = 20) -> List[StockQuote]:
        """搜索股票"""
        try:
            logger.info(f"[Mock] 搜索股票: {keyword}")
            
            results = [
                StockQuote(**stock) for stock in self.MOCK_STOCKS
                if keyword.lower() in stock['code'].lower()
                or keyword.lower() in stock['name'].lower()
            ]
            
            return results[:limit]
        except Exception as e:
            logger.error(f"[Mock] 搜索股票失败: {e}")
            return []