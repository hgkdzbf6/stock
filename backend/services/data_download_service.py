"""数据下载服务 - 管理股票数据下载和去重"""
import asyncio
from datetime import datetime
from datetime import timedelta
from typing import Dict, Optional, List, Tuple
import uuid
import json
from loguru import logger
import pandas as pd

from .data_fetcher import DataFetcher
from .data_storage_service import DataStorageService
from .duckdb_storage_service import DuckDBStorageService
from .stock_code_service import stock_code_service


class DataDownloadService:
    """数据下载服务 - 仅使用真实数据源"""
    
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
        
        # 使用 ashare 作为默认数据源（真实数据）
        self.data_fetcher = DataFetcher(source='ashare')  
        self.download_progress = {}  # 存储下载进度
        
        logger.info("数据下载服务初始化完成（仅使用真实数据源）")

    def _normalize_frequency(self, frequency: str) -> str:
        mapping = {
            '1d': 'daily',
            'daily': 'daily',
            'day': 'daily',
            '30m': '30min',
            '30min': '30min',
            '60m': '60min',
            '60min': '60min',
            '15m': '15min',
            '15min': '15min',
            '5m': '5min',
            '5min': '5min',
            '1m': '1min',
            '1min': '1min',
            '1w': 'weekly',
            'weekly': 'weekly',
        }
        return mapping.get((frequency or '').lower(), frequency)

    def _to_fetch_frequency(self, frequency: str) -> str:
        frequency = self._normalize_frequency(frequency)
        mapping = {
            'daily': '1d',
            'weekly': '1w',
            '1min': '1min',
            '5min': '5min',
            '15min': '15min',
            '30min': '30min',
            '60min': '60min',
        }
        return mapping.get(frequency, '1d')

    def _step_by_frequency(self, frequency: str) -> timedelta:
        frequency = self._normalize_frequency(frequency)
        mapping = {
            '1min': timedelta(minutes=1),
            '5min': timedelta(minutes=5),
            '15min': timedelta(minutes=15),
            '30min': timedelta(minutes=30),
            '60min': timedelta(minutes=60),
            'daily': timedelta(days=1),
            'weekly': timedelta(days=7),
        }
        return mapping.get(frequency, timedelta(days=1))

    def _compute_missing_ranges(
        self,
        requested_start: datetime,
        requested_end: datetime,
        coverage: Optional[Dict],
        frequency: str,
    ) -> List[Tuple[datetime, datetime]]:
        if coverage is None:
            return [(requested_start, requested_end)]

        step = self._step_by_frequency(frequency)
        missing: List[Tuple[datetime, datetime]] = []
        existing_start = coverage.get('start_date')
        existing_end = coverage.get('end_date')

        if existing_start is None or existing_end is None:
            return [(requested_start, requested_end)]

        if requested_start < existing_start:
            missing.append((requested_start, min(requested_end, existing_start - step)))

        if requested_end > existing_end:
            missing.append((max(requested_start, existing_end + step), requested_end))

        # 清理无效区间
        valid_missing = []
        for missing_start, missing_end in missing:
            if missing_start <= missing_end:
                valid_missing.append((missing_start, missing_end))

        return valid_missing
    
    async def download_stock_data(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'daily',
        source: str = 'ashare',
        force_download: bool = False
    ) -> Dict:
        """
        下载股票数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            source: 数据源（仅真实数据源）
            force_download: 是否强制重新下载
            
        Returns:
            下载结果字典
        """
        frequency = self._normalize_frequency(frequency)

        # 明确禁止 mock 数据源
        if source and source.lower() == 'mock':
            error_msg = f"Mock数据源已被禁用，仅允许使用真实数据源。请求的源: {source}"
            logger.error(error_msg)
            return {
                'status': 'failed',
                'message': error_msg,
                'stock_code': stock_code,
                'source': source
            }
        
        try:
            download_id = f"{stock_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            logger.info(f"开始下载数据: {stock_code}, {start_date} - {end_date}, 频率: {frequency}, 数据源: {source}")
            
            # 从本地stock_list获取股票名称
            stock_name = None
            try:
                stock_info = stock_code_service.get_stock_info(stock_code)
                if stock_info:
                    stock_name = stock_info.get('name') or stock_info.get('名称')
                    logger.info(f"获取股票名称: {stock_code} -> {stock_name}")
            except Exception as e:
                logger.warning(f"获取股票名称失败: {e}")
            
            # 如果请求日线且已有30分钟线，优先从30分钟线聚合（不重复下载日线）
            if self.use_duckdb and frequency == 'daily' and not force_download:
                intraday_coverage = self.storage.get_coverage_range(stock_code, '30min')
                if intraday_coverage:
                    coverage_start = intraday_coverage.get('start_date')
                    coverage_end = intraday_coverage.get('end_date')
                    if coverage_start and coverage_end and coverage_start <= start_date and coverage_end >= end_date:
                        daily_df = self.storage.aggregate_30min_to_daily(stock_code, start_date, end_date)
                        if daily_df is not None and len(daily_df) > 0:
                            saved_count = self.storage.save_kline_data(
                                df=daily_df,
                                stock_code=stock_code,
                                frequency='daily',
                                stock_name=stock_name,
                            )
                            loaded_data = self.storage.load_kline_data(stock_code, start_date, end_date, 'daily')
                            return {
                                'status': 'derived',
                                'message': '已从30分钟线聚合生成日线，无需单独下载日线',
                                'download_id': download_id,
                                'stock_code': stock_code,
                                'stock_name': stock_name,
                                'data_count': len(loaded_data) if loaded_data is not None else saved_count,
                                'record_id': saved_count,
                                'source': source,
                                'derived_from': '30min'
                            }

            coverage = None
            if self.use_duckdb and not force_download:
                coverage = self.storage.get_coverage_range(stock_code, frequency)
                missing_ranges = self._compute_missing_ranges(start_date, end_date, coverage, frequency)
            else:
                missing_ranges = [(start_date, end_date)]

            if not missing_ranges:
                existing = self.storage.load_kline_data(stock_code, start_date, end_date, frequency) if self.use_duckdb else None
                return {
                    'status': 'exists',
                    'message': '请求区间已被本地数据覆盖，无需重复下载',
                    'download_id': download_id,
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'data_count': len(existing) if existing is not None else 0,
                    'source': source,
                    'existing_data': coverage,
                }

            logger.info(f"增量下载缺失区间: {missing_ranges}")
            freq = self._to_fetch_frequency(frequency)
            temp_fetcher = DataFetcher(source=source)
            downloaded_segments = []
            total_new_rows = 0

            for seg_start, seg_end in missing_ranges:
                try:
                    data = await temp_fetcher.get_data(
                        code=stock_code,
                        start_date=seg_start,
                        end_date=seg_end,
                        freq=freq,
                    )
                except Exception as e:
                    logger.error(f"数据源 {source} 下载区间失败: {seg_start}~{seg_end}, error={e}")
                    return {
                        'status': 'failed',
                        'message': f'下载数据失败: {seg_start.strftime("%Y-%m-%d")}~{seg_end.strftime("%Y-%m-%d")} 区间失败: {str(e)}',
                        'download_id': download_id,
                        'stock_code': stock_code,
                        'source': source
                    }

                if data is None or len(data) == 0:
                    logger.warning(f"区间未返回数据: {seg_start}~{seg_end}")
                    continue

                if self.use_duckdb:
                    saved_count = self.storage.save_kline_data(
                        df=data,
                        stock_code=stock_code,
                        frequency=frequency,
                        stock_name=stock_name,
                    )
                    total_new_rows += int(saved_count)
                else:
                    record_id = self.storage.save_downloaded_data(
                        stock_code=stock_code,
                        stock_name=stock_name,
                        start_date=seg_start,
                        end_date=seg_end,
                        frequency=frequency,
                        data=data,
                        source=source,
                    )
                    total_new_rows += int(record_id or 0)

                downloaded_segments.append({
                    'start_date': seg_start.strftime('%Y-%m-%d'),
                    'end_date': seg_end.strftime('%Y-%m-%d'),
                    'rows': len(data),
                })

            if len(downloaded_segments) == 0:
                return {
                    'status': 'failed',
                    'message': '下载数据失败: 缺失区间未获取到有效数据',
                    'download_id': download_id,
                    'stock_code': stock_code,
                    'source': source,
                }

            data = self.storage.load_kline_data(stock_code, start_date, end_date, frequency) if self.use_duckdb else None
            if data is None:
                return {
                    'status': 'failed',
                    'message': '增量下载后未能加载目标区间数据',
                    'download_id': download_id,
                    'stock_code': stock_code,
                    'source': source,
                }

            logger.info(f"数据下载成功: stock={stock_code}, total={len(data)}, new_segments={len(downloaded_segments)}")
            logger.info(f"Storage类型: {type(self.storage).__name__}, use_duckdb: {self.use_duckdb}")

            return {
                'status': 'completed',
                'message': '下载完成',
                'download_id': download_id,
                'stock_code': stock_code,
                'stock_name': stock_name,
                'data_count': len(data),
                'record_id': total_new_rows,
                'data': data,
                'source': source,
                'downloaded_segments': downloaded_segments,
            }
            
        except Exception as e:
            logger.error(f"下载数据失败: {e}")
            return {
                'status': 'failed',
                'message': f'下载数据失败: {str(e)}',
                'download_id': download_id,
                'stock_code': stock_code,
                'source': source
            }

    async def download_data_package(
        self,
        stock_codes: List[str],
        start_date: datetime,
        end_date: datetime,
        base_frequency: str = '30min',
        source: str = 'ashare',
        include_daily: bool = True,
        package_name: Optional[str] = None,
        force_download: bool = False,
    ) -> Dict:
        """打包下载某时间段内多只股票数据，并可由30分钟线自动合成日线。"""
        if not self.use_duckdb:
            return {
                'status': 'failed',
                'message': '打包下载仅支持DuckDB存储模式',
            }

        base_frequency = self._normalize_frequency(base_frequency)
        package_id = f"pkg_{uuid.uuid4().hex[:12]}"
        package_name = package_name or f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{base_frequency}"

        self.storage.upsert_download_package(
            package_id=package_id,
            package_name=package_name,
            start_date=start_date,
            end_date=end_date,
            base_frequency=base_frequency,
            include_daily=include_daily,
            source=source,
            stock_count=len(stock_codes),
            metadata=json.dumps({'stock_codes': stock_codes}, ensure_ascii=False),
        )

        results = []
        success = 0
        failed = 0

        for stock_code in stock_codes:
            stock_name = None
            try:
                stock_info = stock_code_service.get_stock_info(stock_code)
                if stock_info:
                    stock_name = stock_info.get('name') or stock_info.get('名称')
            except Exception:
                pass

            result = await self.download_stock_data(
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                frequency=base_frequency,
                source=source,
                force_download=force_download,
            )

            has_daily = False
            daily_count = 0
            if include_daily and base_frequency == '30min' and result.get('status') in ('completed', 'exists', 'derived'):
                daily_df = self.storage.aggregate_30min_to_daily(stock_code, start_date, end_date)
                if daily_df is not None and len(daily_df) > 0:
                    daily_count = self.storage.save_kline_data(
                        df=daily_df,
                        stock_code=stock_code,
                        frequency='daily',
                        stock_name=stock_name,
                    )
                    has_daily = True

            self.storage.upsert_package_stock_sync(
                package_id=package_id,
                stock_code=stock_code,
                stock_name=stock_name,
                base_frequency=base_frequency,
                has_daily=has_daily,
                base_data_points=int(result.get('data_count') or 0),
                daily_data_points=int(daily_count),
                range_start=start_date,
                range_end=end_date,
                status='success' if result.get('status') in ('completed', 'exists', 'derived') else 'failed',
                message=result.get('message', ''),
            )

            if result.get('status') in ('completed', 'exists', 'derived'):
                success += 1
            else:
                failed += 1

            result['daily_derived'] = has_daily
            result['daily_data_count'] = daily_count
            results.append(result)

        return {
            'status': 'completed' if failed == 0 else 'partial',
            'package_id': package_id,
            'package_name': package_name,
            'base_frequency': base_frequency,
            'include_daily': include_daily,
            'total': len(stock_codes),
            'success': success,
            'failed': failed,
            'results': results,
        }
    
    async def batch_download(
        self,
        stock_codes: list,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'daily',
        source: str = 'ashare'
    ) -> Dict:
        """
        批量下载股票数据
        
        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            source: 数据源（仅真实数据源）
            
        Returns:
            批量下载结果
        """
        # 明确禁止 mock 数据源
        if source and source.lower() == 'mock':
            return {
                'status': 'failed',
                'message': 'Mock数据源已被禁用',
                'total': len(stock_codes),
                'success': 0,
                'failed': len(stock_codes)
            }
        
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
            'results': results,
            'source': source
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
        
        frequency = self._normalize_frequency(frequency)

        # 加载数据
        if self.use_duckdb:
            data = self.storage.load_kline_data(
                stock_code, start_date, end_date, frequency
            )

            # 若请求日线且日线未落库，则尝试由30分钟线聚合
            if (data is None or len(data) == 0) and frequency == 'daily':
                daily_df = self.storage.aggregate_30min_to_daily(stock_code, start_date, end_date)
                if daily_df is not None and len(daily_df) > 0:
                    self.storage.save_kline_data(
                        df=daily_df,
                        stock_code=stock_code,
                        frequency='daily',
                    )
                    data = self.storage.load_kline_data(stock_code, start_date, end_date, 'daily')
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
                    'frequency_distribution': freq_stats,
                    'data_sources': 'ashare (仅真实数据)'
                }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
