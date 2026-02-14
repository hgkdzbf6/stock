"""数据下载服务 - 管理股票数据下载和去重"""
import asyncio
from datetime import datetime
from typing import Dict, Optional
from loguru import logger
import pandas as pd

from .data_fetcher import DataFetcher
from .data_storage_service import DataStorageService


class DataDownloadService:
    """数据下载服务"""
    
    def __init__(self, storage_service: Optional[DataStorageService] = None):
        """
        初始化数据下载服务
        
        Args:
            storage_service: 数据存储服务实例
        """
        self.storage = storage_service or DataStorageService()
        self.data_fetcher = DataFetcher(source='sina')  # 优先使用新浪API
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
            
            # 如果不是强制下载，检查数据是否存在
            if not force_download:
                check_result = self.storage.check_data_exists(
                    stock_code, start_date, end_date, frequency
                )
                
                if check_result['exists']:
                    overlap_type = check_result['overlap_type']
                    
                    if overlap_type == 'exact':
                        # 数据已存在且完全匹配
                        existing_data = check_result['data']
                        data = self.storage.load_downloaded_data(
                            stock_code, start_date, end_date, frequency
                        )
                        
                        if data is not None:
                            logger.info(f"数据已存在，使用已有数据: {len(data)}条记录")
                            return {
                                'status': 'exists',
                                'message': '数据已存在，使用已有数据',
                                'download_id': download_id,
                                'stock_code': stock_code,
                                'data_count': len(data),
                                'data': data,
                                'existing_data': existing_data
                            }
                    
                    elif overlap_type == 'partial':
                        # 数据部分重叠
                        existing_data = check_result['data']
                        logger.warning(f"数据部分重叠: {existing_data['start_date']} - {existing_data['end_date']}")
                        return {
                            'status': 'partial_overlap',
                            'message': f'数据部分重叠，已存在数据范围: {existing_data["start_date"]} 至 {existing_data["end_date"]}',
                            'download_id': download_id,
                            'stock_code': stock_code,
                            'existing_data': existing_data
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
            
            # 保存数据（股票名称作为可选，不阻塞下载）
            record_id = self.storage.save_downloaded_data(
                stock_code=stock_code,
                stock_name=None,  # 先不获取名称，避免阻塞
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                data=data,
                source=source
            )
            
            logger.info(f"数据保存成功: 记录ID={record_id}")
            
            return {
                'status': 'completed',
                'message': '下载完成',
                'download_id': download_id,
                'stock_code': stock_code,
                'stock_name': None,  # 股票名称暂不提供
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
        
        # 检查数据是否存在
        check_result = self.storage.check_data_exists(
            stock_code, start_date, end_date, frequency
        )
        
        if not check_result['exists']:
            logger.warning(f"回测数据不存在: {stock_code}")
            return None
        
        if check_result['overlap_type'] == 'partial':
            logger.warning(f"数据部分重叠，可能影响回测结果")
        
        # 加载数据
        data = self.storage.load_downloaded_data(
            stock_code, start_date, end_date, frequency
        )
        
        if data is not None:
            logger.info(f"回测数据加载成功: {len(data)}条记录")
        else:
            logger.error(f"回测数据加载失败")
        
        return data
    
    async def _get_stock_name(self, stock_code: str) -> Optional[str]:
        """
        获取股票名称
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股票名称
        """
        try:
            # 从股票列表中搜索
            stocks = await self.data_fetcher.search_stocks(stock_code, limit=1)
            if stocks and len(stocks) > 0:
                return stocks[0].get('名称')
            return None
        except Exception as e:
            logger.warning(f"获取股票名称失败: {e}")
            return None
    
    def get_statistics(self) -> Dict:
        """
        获取下载统计信息
        
        Returns:
            统计信息
        """
        try:
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