"""数据下载服务单元测试"""
import unittest
import asyncio
from datetime import datetime
from pathlib import Path
import sys

sys.path.append('..')

from services.data_download_service import DataDownloadService
from services.duckdb_storage_service import DuckDBStorageService


class TestDataDownloadService(unittest.TestCase):
    """数据下载服务测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.test_db_path = 'data/test_download.duckdb'
        
    def setUp(self):
        """每个测试前初始化"""
        # 删除测试数据库
        if Path(self.test_db_path).exists():
            Path(self.test_db_path).unlink()
        
        # 初始化服务
        self.download_service = DataDownloadService(use_duckdb=True)
    
    def tearDown(self):
        """每个测试后清理"""
        self.download_service.storage.close()
        
        # 删除测试数据库
        if Path(self.test_db_path).exists():
            Path(self.test_db_path).unlink()
    
    def test_init_with_duckdb(self):
        """测试使用DuckDB初始化"""
        self.assertIsInstance(self.download_service.storage, DuckDBStorageService)
        self.assertTrue(self.download_service.use_duckdb)
    
    def test_download_stock_data(self):
        """测试下载股票数据"""
        async def run_test():
            result = await self.download_service.download_stock_data(
                stock_code='600519.SH',
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 5),
                frequency='daily',
                source='ashare'
            )
            
            # 验证
            self.assertEqual(result['status'], 'completed')
            self.assertEqual(result['stock_code'], '600519.SH')
            self.assertIsNotNone(result.get('data_count'))
            self.assertIsNotNone(result.get('record_id'))
        
        asyncio.run(run_test())
    
    def test_download_data_exists(self):
        """测试数据缓存复用"""
        async def run_test():
            # 测试真实数据的缓存复用
            # 下载600519.SH数据
            result1 = await self.download_service.download_stock_data(
                stock_code='600519.SH',
                start_date=datetime(2025, 1, 6),
                end_date=datetime(2025, 1, 8),
                frequency='daily',
                source='ashare'
            )
            
            self.assertEqual(result1['status'], 'completed')
            self.assertEqual(result1['stock_code'], '600519.SH')
            
            # 再次下载相同数据，应该使用缓存
            result2 = await self.download_service.download_stock_data(
                stock_code='600519.SH',
                start_date=datetime(2025, 1, 6),
                end_date=datetime(2025, 1, 8),
                frequency='daily',
                source='ashare'
            )
            
            # 验证状态（exists或partial_overlap都表示使用了已有数据）
            self.assertIn(result2['status'], ['exists', 'partial_overlap'])
            self.assertIsNotNone(result2.get('message'))
        
        asyncio.run(run_test())
    
    def test_check_data_availability(self):
        """测试检查数据可用性"""
        async def run_test():
            # 使用不同的股票和日期避免冲突
            # 下载数据
            await self.download_service.download_stock_data(
                stock_code='000002.SZ',  # 不同的股票
                start_date=datetime(2024, 12, 20),  # 不同的日期
                end_date=datetime(2024, 12, 25),
                frequency='daily',
                source='ashare'
            )
            
            # 检查数据
            result = await self.download_service.check_data_availability(
                stock_code='000002.SZ',
                start_date=datetime(2024, 12, 20),
                end_date=datetime(2024, 12, 25),
                frequency='daily'
            )
            
            # 验证
            self.assertTrue(result['available'])
            self.assertEqual(result['overlap_type'], 'exact')
        
        asyncio.run(run_test())
    
    def test_get_downloaded_data_list(self):
        """测试获取已下载数据列表"""
        async def run_test():
            # 下载多个股票
            for stock_code in ['600519.SH', '600000.SH']:
                await self.download_service.download_stock_data(
                    stock_code=stock_code,
                    start_date=datetime(2025, 1, 1),
                    end_date=datetime(2025, 1, 3),
                    frequency='daily',
                    source='ashare'
                )
            
            # 获取列表
            result = await self.download_service.get_downloaded_data_list(limit=10)
            
            # 验证
            self.assertGreaterEqual(result['total'], 2)
            self.assertGreaterEqual(len(result['downloads']), 2)
        
        asyncio.run(run_test())
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        async def run_test():
            # 下载数据
            await self.download_service.download_stock_data(
                stock_code='600519.SH',
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 3),
                frequency='daily',
                source='ashare'
            )
            
            # 获取统计
            stats = self.download_service.get_statistics()
            
            # 验证
            self.assertGreater(stats['total_records'], 0)
            self.assertGreater(stats['total_stocks'], 0)
        
        asyncio.run(run_test())
    
    def test_load_data_for_backtest(self):
        """测试为回测加载数据"""
        async def run_test():
            # 下载数据
            await self.download_service.download_stock_data(
                stock_code='600519.SH',
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 5),
                frequency='daily',
                source='ashare'
            )
            
            # 加载数据
            data = await self.download_service.load_data_for_backtest(
                stock_code='600519.SH',
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 5),
                frequency='daily'
            )
            
            # 验证
            self.assertIsNotNone(data)
            self.assertGreater(len(data), 0)
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main(verbosity=2)