"""数据获取服务 - 使用适配器模式支持多种数据源"""
from typing import Optional, List
from datetime import datetime
from loguru import logger
import pandas as pd
from data_adapters import AdapterFactory, StockQuote, KlineData


class DataFetcher:
    """数据获取器 - 仅使用真实数据源，不使用 mock"""

    def __init__(self, token: Optional[str] = None, source: str = 'auto'):
        """
        初始化数据获取器

        Args:
            token: tushare API token
            source: 数据源 ('ashare', 'tushare', 'akshare', 'baostock', 'sina', 'tencent', 'eastmoney', 'auto')
                    注意：不支持 'mock'，明确要求只使用真实数据
        """
        self.source = source
        self.adapter_factory = AdapterFactory(tushare_token=token)
        
        # 明确禁止使用 mock 数据源
        if source.lower() == 'mock':
            logger.error("明确禁止使用 mock 数据源")
            raise ValueError("Mock 数据源已被禁用，系统仅使用真实市场数据")
        
        logger.info(f"数据源: {source} (仅真实数据)")

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
            DataFrame包含OHLCV数据，如果所有数据源失败则返回None

        Raises:
            Exception: 当所有数据源都失败时抛出异常
        """
        logger.info(f"获取股票数据: {code}, {start_date} 到 {end_date}, 频率: {freq}")

        # 获取K线数据
        kline_data_list, used_source = await self._get_kline_with_source(
            code, start_date, end_date, freq
        )
        
        if not kline_data_list or len(kline_data_list) == 0:
            error_msg = f"所有真实数据源都失败，无法获取 {code} 的 {freq} 数据"
            logger.error(error_msg)
            raise Exception(error_msg)
        
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
        """
        获取K线数据并返回使用的数据源
        
        仅尝试真实数据源，不使用 mock
        """
        logger.info(f"尝试从真实数据源获取K线数据: {code}, {freq}")
        
        if self.source == 'auto':
            # auto 模式：按优先级尝试真实数据源
            # 优先级：akshare > ashare > tushare > eastmoney > sina > tencent > baostock
            sources_to_try = ['akshare', 'ashare', 'tushare', 'eastmoney', 'sina', 'tencent', 'baostock']
        else:
            # 指定数据源
            sources_to_try = [self.source]
        
        last_error = None
        
        for source in sources_to_try:
            try:
                logger.info(f"尝试数据源: {source}")
                adapter = self.adapter_factory.get_adapter(source)
                
                if adapter:
                    kline_data = await adapter.get_kline_data(code, start_date, end_date, freq)
                    
                    if kline_data and len(kline_data) > 0:
                        logger.info(f"数据源 {source} 成功返回 {len(kline_data)} 条数据")
                        return kline_data, source
                    else:
                        logger.warning(f"数据源 {source} 未返回数据")
                        last_error = f"{source} 未返回数据"
                else:
                    logger.warning(f"无法获取 {source} 适配器")
                    last_error = f"{source} 适配器不可用"
            
            except Exception as e:
                logger.warning(f"数据源 {source} 失败: {e}")
                last_error = f"{source} 错误: {str(e)}"
                continue
        
        # 所有数据源都失败
        error_msg = f"所有真实数据源都失败，最后错误: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

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
            
            # 确定要尝试的数据源
            if self.source == 'auto':
                sources_to_try = ['akshare', 'ashare', 'tushare', 'eastmoney']
            else:
                sources_to_try = [self.source]
            
            last_error = None
            
            # 尝试数据源
            for source in sources_to_try:
                try:
                    logger.info(f"尝试从 {source} 获取股票列表")
                    adapter = self.adapter_factory.get_adapter(source)
                    
                    if adapter:
                        stocks = await adapter.get_stock_list(page, page_size, keyword)
                        
                        if stocks and len(stocks) > 0:
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
                            
                            logger.info(f"从 {source} 获取成功: {len(stocks_dict)} 只股票")
                            return stocks_dict
                        else:
                            last_error = f"{source} 未返回数据"
                    
                except Exception as e:
                    logger.warning(f"从 {source} 获取股票列表失败: {e}")
                    last_error = str(e)
                    continue
            
            # 所有数据源都失败
            error_msg = f"所有真实数据源都失败: {last_error}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
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
            
            # 确定要尝试的数据源
            if self.source == 'auto':
                sources_to_try = ['akshare', 'ashare', 'tushare', 'eastmoney']
            else:
                sources_to_try = [self.source]
            
            last_error = None
            
            # 尝试数据源
            for source in sources_to_try:
                try:
                    logger.info(f"尝试从 {source} 搜索股票")
                    adapter = self.adapter_factory.get_adapter(source)
                    
                    if adapter:
                        stocks = await adapter.search_stocks(keyword, limit)
                        
                        if stocks and len(stocks) > 0:
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
                            
                            logger.info(f"从 {source} 搜索成功: {len(stocks_dict)} 只股票")
                            return stocks_dict
                        else:
                            last_error = f"{source} 未返回结果"
                    
                except Exception as e:
                    logger.warning(f"从 {source} 搜索股票失败: {e}")
                    last_error = str(e)
                    continue
            
            # 所有数据源都失败
            error_msg = f"所有真实数据源都失败: {last_error}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"搜索股票失败: {e}")
            raise