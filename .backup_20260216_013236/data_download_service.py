"""数据下载服务 - 管理股票数据下载和去重"""
import asyncio
from datetime import datetime
from typing import Dict, Optional
from loguru import logger
import pandas as pd

from .data_fetcher import DataFetcher
from .data_storage_service import DataStorageService
from .duckdb_storage_service import DuckDBStorageService
from .stock_code_service import stock_code_service


class DataDownloadService:
    """数据下载服务"""
    
    def __init__(self, storage_service: Optional[DataStorageService] = None, use_duckdb: bool = True):
        """
        初始化数据下载服务
        
        Args:
            storage_service: 数据存储服务实例（优先使用DuckDB）
            use_duckdb: 是否使用DuckDB存储（默认True）
        """
        # 优先使用DuckDB存储
        if use_duckdb:
            try:
                self.storage = DuckDBStorageService()
                self.use_duckdb = True
                logger.info("使用DuckDB存储服务")
            except Exception as e:
                logger.warning(f"DuckDB初始化失败，使用CSV存储: {e}")
                self.storage = storage_service or DataStorageService()
                self.use_duckdb = False
        else:
            self.storage = storage_service or DataStorageService()
            self.use_duckdb = False
        
        self.data_fetcher = DataFetcher(source='ashare')  # 使用Ashare作为默认数据源
        self.download_progress = {}  # 存储下载进度
        
        logger.info("数据下载服务初始化完成")
    
    async def download_stock_data(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'daily',
        source: str = 'auto',
        force_download: bool = False
    ) -> Dict:
        """
        下载股票数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            source: 数据源
            force_download: 是否强制重新下载
            
        Returns:
            下载结果字典
        """
        try:
            download_id = f"{stock_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            logger.info(f"开始下载数据: {stock_code}, {start_date} - {end_date}")
            
            # 从本地stock_list获取股票名称
            stock_name = None
            try:
                stock_info = stock_code_service.get_stock_info(stock_code)
                if stock_info:
                    stock_name = stock_info.get('name') or stock_info.get('名称')
                    logger.info(f"获取股票名称: {stock_code} -> {stock_name}")
            except Exception as e:
                logger.warning(f"获取股票名称失败: {e}")
            
            # 如果不是强制下载，检查数据是否存在
            if not force_download and self.use_duckdb:
                check_result = self.storage.check_data_exists(
                    stock_code, start_date, end_date, frequency
                )
                
                if check_result:
                    overlap_type = check_result['overlap_type']
                    
                    if overlap_type == 'exact':
                        # 数据已存在且完全匹配
                        data = self.storage.load_kline_data(
                            stock_code, start_date, end_date, frequency
                        )
                        
                        if data is not None:
                            logger.info(f"数据已存在，使用已有数据: {len(data)}条记录")
                            return {
                                'status': 'exists',
                                'message': '数据已存在，使用已有数据',
                                'download_id': download_id,
                                'stock_code': stock_code,
                                'stock_name': stock_name,
                                'data_count': len(data),
                                'data': data,
                                'existing_data': check_result
                            }
                    
                    elif overlap_type in ['partial_start', 'partial_end']:
                        # 数据部分重叠
                        logger.warning(f"数据部分重叠: {check_result['start_date']} - {check_result['end_date']}")
                        return {
                            'status': 'partial_overlap',
                            'message': f'数据部分重叠，已存在数据范围: {check_result["start_date"]} 至 {check_result["end_date"]}',
                            'download_id': download_id,
                            'stock_code': stock_code,
                            'stock_name': stock_name,
                            'existing_data': check_result
                        }
            
            # 开始下载数据
            logger.info(f"从数据源下载数据: {source}")
            
            # 转换频率格式
            freq_map = {
                'daily': '1d',
                '1d': '1d',
                'weekly': '1w',
                '1w': '1w',
                '1min': '1min',
                '5min': '5min',
                '15min': '15min',
                '30min': '30min',
                '60min': '60min'
            }
            freq = freq_map.get(frequency, 'daily')
            
            # 下载数据（临时创建使用指定source的fetcher）
            temp_fetcher = DataFetcher(source=source)
            data = await temp_fetcher.get_data(
                code=stock_code,
                start_date=start_date,
                end_date=end_date,
                freq=freq
            )
            
            if data is None or len(data) == 0:
                logger.error(f"下载数据失败: 未获取到数据")
                return {
                    'status': 'failed',
                    'message': '下载数据失败：未获取到数据',
                    'download_id': download_id,
                    'stock_code': stock_code
                }
            
            logger.info(f"数据下载成功: {len(data)}条记录")
            logger.info(f"Storage类型: {type(self.storage).__name__}, use_duckdb: {self.use_duckdb}")
            
            # 保存数据
            if self.use_duckdb:
                # 使用DuckDB存储，传入股票名称
                record_id = self.storage.save_kline_data(
                    df=data,
                    stock_code=stock_code,
                    frequency=frequency,
                    stock_name=stock_name
                )
                logger.info(f"使用DuckDB保存成功: record_id={record_id}")
            else:
                # 使用CSV存储，传入股票名称
                record_id = self.storage.save_downloaded_data(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    start_date=start_date,
                    end_date=end_date,
                    frequency=frequency,
                    data=data,
                    source=source
                )
                logger.info(f"使用CSV保存成功: record_id={record_id}")
            
            logger.info(f"数据保存成功: 记录ID={record_id}")
            
            return {
                'status': 'completed',
                'message': '下载完成',
                'download_id': download_id,
                'stock_code': stock_code,
                'stock_name': stock_name,
                'data_count': len(data),
                'record_id': record_id,
                'data': data
            }
            
        except Exception as e:
            logger.error(f"下载数据失败: {e}")
            return {
                'status': 'failed',
                'message': f'下载数据失败: {str(e)}',
                'download_id': download_id,
                'stock_code': stock_code
            }
    
    async def batch_download(
        self,
        stock_codes: list,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'daily',
        source: str = 'auto'
    ) -> Dict:
        """
        批量下载股票数据
        
        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            source: 数据源
            
        Returns:
            批量下载结果
        """
        logger.info(f"开始批量下载: {len(stock_codes)}只股票")
        
        results = []
        success_count = 0
        failed_count = 0
        
        for i, stock_code in enumerate(stock_codes):
            logger.info(f"正在下载 ({i+1}/{len(stock_codes)}): {stock_code}")
            
            result = await self.download_stock_data(
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                source=source
            )
            
            results.append(result)
            
            if result['status'] == 'completed':
                success_count += 1
            else:
                failed_count += 1
            
            # 稍作延迟，避免请求过快
            await asyncio.sleep(0.5)
        
        return {
            'total': len(stock_codes),
            'success': success_count,
            'failed': failed_count,
            'results': results
        }
    
    async def get_download_status(self, download_id: str) -> Dict:
        """
        获取下载状态
        
        Args:
            download_id: 下载ID
            
        Returns:
            下载状态信息
        """
        if download_id in self.download_progress:
            return self.download_progress[download_id]
        else:
            return {
                'status': 'not_found',
                'message': '下载任务不存在'
            }
    
    async def get_downloaded_data_list(
        self,
        stock_code: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        获取已下载数据列表
        
        Args:
            stock_code: 股票代码（可选）
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            数据列表
        """
        return self.storage.get_downloaded_data_list(
            stock_code=stock_code,
            limit=limit,
            offset=offset
        )
    
    async def delete_downloaded_data(self, record_id: int) -> Dict:
        """
        删除已下载数据
        
        Args:
            record_id: 数据库记录ID
            
        Returns:
            删除结果
        """
        success = self.storage.delete_downloaded_data(record_id)
        
        if success:
            return {
                'status': 'success',
                'message': '数据删除成功',
                'record_id': record_id
            }
        else:
            return {
                'status': 'failed',
                'message': '数据删除失败',
                'record_id': record_id
            }
    
    async def check_data_availability(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'daily'
    ) -> Dict:
        """
        检查数据是否可用
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            
        Returns:
            可用性检查结果
        """
        if self.use_duckdb:
            check_result = self.storage.check_data_exists(
                stock_code, start_date, end_date, frequency
            )
            
            if check_result:
                return {
                    'available': True,
                    'overlap_type': check_result.get('overlap_type'),
                    'existing_data': check_result
                }
            else:
                return {
                    'available': False,
                    'overlap_type': None,
                    'existing_data': None
                }
        else:
            check_result = self.storage.check_data_exists(
                stock_code, start_date, end_date, frequency
            )
            
            return {
                'available': check_result['exists'],
                'overlap_type': check_result.get('overlap_type'),
                'existing_data': check_result.get('data')
            }
    
    async def load_data_for_backtest(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'daily'
    ) -> Optional[pd.DataFrame]:
        """
        为回测加载数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            
        Returns:
            数据DataFrame，如果数据不存在返回None
        """
        logger.info(f"为回测加载数据: {stock_code}, {start_date} - {end_date}")
        
        # 加载数据
        if self.use_duckdb:
            data = self.storage.load_kline_data(
                stock_code, start_date, end_date, frequency
            )
        else:
            data = self.storage.load_downloaded_data(
                stock_code, start_date, end_date, frequency
            )
        
        if data is not None:
            logger.info(f"回测数据加载成功: {len(data)}条记录")
        else:
            logger.error(f"回测数据加载失败")
        
        return data
    
    def get_statistics(self) -> Dict:
        """
        获取下载统计信息
        
        Returns:
            统计信息
        """
        try:
            if self.use_duckdb:
                # 使用DuckDB统计
                return self.storage.get_statistics()
            else:
                # 使用CSV统计
                result = self.storage.get_downloaded_data_list(limit=10000)
                
                downloads = result.get('downloads', [])
                total = result.get('total', 0)
                
                # 统计信息
                stock_count = len(set(d['stock_code'] for d in downloads))
                total_data_points = sum(d['data_count'] for d in downloads)
                total_file_size = sum(d['file_size'] for d in downloads)
                
                # 按频率统计
                freq_stats = {}
                for d in downloads:
                    freq = d['frequency']
                    freq_stats[freq] = freq_stats.get(freq, 0) + 1
                
                return {
                    'total_downloads': total,
                    'unique_stocks': stock_count,
                    'total_data_points': total_data_points,
                    'total_file_size': total_file_size,
                    'total_file_size_str': self.storage._format_file_size(total_file_size),
                    'frequency_distribution': freq_stats
                }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}