"""新浪财经数据源适配器"""
import requests
from typing import List, Optional
from datetime import datetime
from loguru import logger
from .base import BaseAdapter
from .models import StockQuote, KlineData


class SinaAdapter(BaseAdapter):
    """新浪财经数据源适配器"""
    
    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None
    ) -> List[StockQuote]:
        """获取股票列表"""
        try:
            logger.info(f"[新浪] 获取股票列表: page={page}, page_size={page_size}")
            # 新浪财经不提供完整股票列表API
            logger.warning("[新浪] 不提供完整股票列表API")
            return []
        except Exception as e:
            logger.error(f"[新浪] 获取股票列表失败: {e}")
            raise
    
    async def get_stock_quote(self, code: str) -> Optional[StockQuote]:
        """获取单只股票实时行情"""
        try:
            logger.info(f"[新浪] 获取股票行情: {code}")
            
            # 格式: sh600000 或 sz000001
            if code.startswith('6'):
                symbol_code = f"sh{code}"
            else:
                symbol_code = f"sz{code}"
            
            url = f"http://hq.sinajs.cn/list={symbol_code}"
            response = requests.get(url, timeout=5)
            response.encoding = 'gbk'
            
            if response.status_code != 200:
                return None
            
            # 解析数据
            data_str = response.text.strip()
            if not data_str or '=' not in data_str:
                return None
            
            # 提取数据部分
            data_part = data_str.split('=')[1].strip('";')
            parts = data_part.split(',')
            
            if len(parts) < 32:
                return None
            
            # 解析字段
            name = parts[0]
            open_price = float(parts[1]) if parts[1] else 0.0
            pre_close = float(parts[2]) if parts[2] else 0.0
            current = float(parts[3]) if parts[3] else 0.0
            high = float(parts[4]) if parts[4] else 0.0
            low = float(parts[5]) if parts[5] else 0.0
            volume = float(parts[8]) if parts[8] else 0
            amount = float(parts[9]) if parts[9] else 0.0
            
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
            logger.error(f"[新浪] 获取股票行情失败: {e}")
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
            logger.info(f"[新浪] 获取K线数据: {code}, {start_date} 到 {end_date}, 频率: {freq}")
            
            if freq != '1d':
                logger.warning("[新浪] 只提供日线数据")
                return []
            
            # 格式: sh600000 或 sz000001
            if code.startswith('6'):
                symbol_code = f"sh{code}"
            else:
                symbol_code = f"sz{code}"
            
            # 新浪财经历史数据API
            url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
            params = {
                'symbol': symbol_code,
                'scale': 240,  # 240=日线
                'ma': 'no',
                'datalen': '2000'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                raise Exception(f"新浪API返回错误: {response.status_code}")
            
            data = response.json()
            if not data:
                raise Exception("新浪返回空数据")
            
            # 转换为KlineData
            kline_list = []
            for item in data:
                date = datetime.strptime(item['day'], '%Y-%m-%d')
                if date < start_date or date > end_date:
                    continue
                
                kline_list.append(KlineData(
                    date=date,
                    open=float(item['open']),
                    high=float(item['high']),
                    low=float(item['low']),
                    close=float(item['close']),
                    volume=int(float(item['volume'])),
                    amount=float(item['amount']) if 'amount' in item else None
                ))
            
            logger.info(f"[新浪] 获取成功: {len(kline_list)} 条K线数据")
            return kline_list
        except Exception as e:
            logger.error(f"[新浪] 获取K线数据失败: {e}")
            raise
    
    async def search_stocks(self, keyword: str, limit: int = 20) -> List[StockQuote]:
        """搜索股票"""
        try:
            logger.info(f"[新浪] 搜索股票: {keyword}")
            # 新浪财经不提供搜索API
            return []
        except Exception as e:
            logger.error(f"[新浪] 搜索股票失败: {e}")
            return []