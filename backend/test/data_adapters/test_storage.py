"""DuckDB存储服务单元测试"""
import unittest
import pandas as pd
import duckdb
from datetime import datetime
from pathlib import Path
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.duckdb_storage_service import DuckDBStorageService


class TestDuckDBStorageService(unittest.TestCase):
    """DuckDB存储服务测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.test_db_path = 'data/test_stock_data.duckdb'
        
    def setUp(self):
        """每个测试前初始化"""
        # 删除测试数据库
        if Path(self.test_db_path).exists():
            Path(self.test_db_path).unlink()
        
        # 初始化服务
        self.storage = DuckDBStorageService(self.test_db_path)
    
    def tearDown(self):
        """每个测试后清理"""
        self.storage.close()
        
        # 删除测试数据库
        if Path(self.test_db_path).exists():
            Path(self.test_db_path).unlink()
    
    def test_init_tables(self):
        """测试表初始化"""
        # 检查表是否存在
        tables = self.storage.con.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'main'
        """).fetchall()
        
        table_names = [t[0] for t in tables]
        
        self.assertIn('kline_data', table_names)
        self.assertIn('stock_info', table_names)
    
    def test_save_kline_data(self):
        """测试保存K线数据"""
        # 创建测试数据
        data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=5, freq='D'),
            'open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'high': [105.0, 106.0, 107.0, 108.0, 109.0],
            'low': [95.0, 96.0, 97.0, 98.0, 99.0],
            'close': [100.0, 101.0, 102.0, 103.0, 104.0],
            'volume': [1000000, 1100000, 1200000, 1300000, 1400000],
            'amount': [100000000, 111000000, 122000000, 133000000, 144000000]
        })
        
        # 保存数据
        count = self.storage.save_kline_data(data, '600519.SH', 'daily')
        
        # 验证
        self.assertEqual(count, 5)
        
        # 查询验证
        result = self.storage.con.execute(
            "SELECT COUNT(*) FROM kline_data WHERE stock_code = '600519.SH'"
        ).fetchone()
        self.assertEqual(result[0], 5)
    
    def test_load_kline_data(self):
        """测试加载K线数据"""
        # 先保存数据
        data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=3, freq='D'),
            'open': [100.0, 101.0, 102.0],
            'high': [105.0, 106.0, 107.0],
            'low': [95.0, 96.0, 97.0],
            'close': [100.0, 101.0, 102.0],
            'volume': [1000000, 1100000, 1200000],
            'amount': [100000000, 111000000, 122000000]
        })
        
        self.storage.save_kline_data(data, '600519.SH', 'daily')
        
        # 加载数据
        loaded_data = self.storage.load_kline_data(
            '600519.SH',
            datetime(2025, 1, 1),
            datetime(2025, 1, 3),
            'daily'
        )
        
        # 验证
        self.assertIsNotNone(loaded_data)
        self.assertEqual(len(loaded_data), 3)
        self.assertIn('close', loaded_data.columns)
        self.assertIn('volume', loaded_data.columns)
    
    def test_update_kline_fields(self):
        """测试更新K线字段"""
        # 先保存数据
        data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=1, freq='D'),
            'open': [100.0],
            'high': [105.0],
            'low': [95.0],
            'close': [100.0],
            'volume': [1000000],
            'amount': [100000000]
        })
        
        self.storage.save_kline_data(data, '600519.SH', 'daily')
        
        # 更新字段
        success = self.storage.update_kline_fields(
            '600519.SH',
            datetime(2025, 1, 1),
            {'pe_ratio': 25.5, 'turnover_rate': 2.3}
        )
        
        # 验证
        self.assertTrue(success)
        
        result = self.storage.con.execute("""
            SELECT pe_ratio, turnover_rate FROM kline_data
            WHERE stock_code = '600519.SH' AND date = '2025-01-01'
        """).fetchone()
        
        self.assertEqual(result[0], 25.5)
        self.assertEqual(result[1], 2.3)
    
    def test_add_kline_column(self):
        """测试添加列"""
        # 添加列
        success = self.storage.add_kline_column('test_column', 'DOUBLE', 0.0)
        
        # 验证
        self.assertTrue(success)
        
        columns = self.storage.con.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'kline_data'
        """).fetchall()
        
        column_names = [c[0] for c in columns]
        self.assertIn('test_column', column_names)
        
        # 测试重复添加
        success = self.storage.add_kline_column('test_column', 'DOUBLE', 0.0)
        self.assertFalse(success)
    
    def test_get_downloaded_data_list(self):
        """测试获取下载数据列表"""
        # 保存多个股票数据
        for i, stock_code in enumerate(['600519.SH', '600000.SH', '000001.SZ']):
            data = pd.DataFrame({
                'date': pd.date_range('2025-01-01', periods=2, freq='D'),
                'open': [100.0 + i, 101.0 + i],
                'high': [105.0 + i, 106.0 + i],
                'low': [95.0 + i, 96.0 + i],
                'close': [100.0 + i, 101.0 + i],
                'volume': [1000000, 1100000],
                'amount': [100000000, 111000000]
            })
            self.storage.save_kline_data(data, stock_code, 'daily')
        
        # 获取列表
        result = self.storage.get_downloaded_data_list(limit=10)
        
        # 验证
        self.assertEqual(result['total'], 3)
        self.assertEqual(len(result['downloads']), 3)
        
        # 验证数据结构
        download = result['downloads'][0]
        self.assertIn('stock_code', download)
        self.assertIn('start_date', download)
        self.assertIn('end_date', download)
        self.assertIn('data_count', download)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        # 保存数据
        data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=5, freq='D'),
            'open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'high': [105.0, 106.0, 107.0, 108.0, 109.0],
            'low': [95.0, 96.0, 97.0, 98.0, 99.0],
            'close': [100.0, 101.0, 102.0, 103.0, 104.0],
            'volume': [1000000, 1100000, 1200000, 1300000, 1400000],
            'amount': [100000000, 111000000, 122000000, 133000000, 144000000]
        })
        
        self.storage.save_kline_data(data, '600519.SH', 'daily')
        
        # 获取统计
        stats = self.storage.get_statistics()
        
        # 验证
        self.assertEqual(stats['total_records'], 5)
        self.assertEqual(stats['total_stocks'], 1)
        self.assertEqual(stats['total_data_points'], 5)
        self.assertIn('daily', stats['frequency_distribution'])
    
    def test_delete_data(self):
        """测试删除数据"""
        # 保存数据
        data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=5, freq='D'),
            'open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'high': [105.0, 106.0, 107.0, 108.0, 109.0],
            'low': [95.0, 96.0, 97.0, 98.0, 99.0],
            'close': [100.0, 101.0, 102.0, 103.0, 104.0],
            'volume': [1000000, 1100000, 1200000, 1300000, 1400000],
            'amount': [100000000, 111000000, 122000000, 133000000, 144000000]
        })
        
        self.storage.save_kline_data(data, '600519.SH', 'daily')
        
        # 删除数据
        deleted = self.storage.delete_data(
            '600519.SH',
            datetime(2025, 1, 1),
            datetime(2025, 1, 5),
            'daily'
        )
        
        # 验证
        self.assertEqual(deleted, 5)
        
        result = self.storage.con.execute(
            "SELECT COUNT(*) FROM kline_data WHERE stock_code = '600519.SH'"
        ).fetchone()
        self.assertEqual(result[0], 0)
    
    def test_check_data_exists(self):
        """测试检查数据是否存在"""
        # 保存数据
        data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=5, freq='D'),
            'open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'high': [105.0, 106.0, 107.0, 108.0, 109.0],
            'low': [95.0, 96.0, 97.0, 98.0, 99.0],
            'close': [100.0, 101.0, 102.0, 103.0, 104.0],
            'volume': [1000000, 1100000, 1200000, 1300000, 1400000],
            'amount': [100000000, 111000000, 122000000, 133000000, 144000000]
        })
        
        self.storage.save_kline_data(data, '600519.SH', 'daily')
        
        # 检查数据
        exists = self.storage.check_data_exists(
            '600519.SH',
            datetime(2025, 1, 1),
            datetime(2025, 1, 5),
            'daily'
        )
        
        # 验证
        self.assertIsNotNone(exists)
        self.assertEqual(exists['stock_code'], '600519.SH')
        self.assertEqual(exists['data_count'], 5)
        self.assertEqual(exists['overlap_type'], 'exact')
        
        # 检查不存在的数据
        not_exists = self.storage.check_data_exists(
            '000000.SZ',
            datetime(2025, 1, 1),
            datetime(2025, 1, 5),
            'daily'
        )
        
        self.assertIsNone(not_exists)
    
    def test_chinese_column_mapping(self):
        """测试中文列名映射"""
        # 创建带中文列名的数据
        data = pd.DataFrame({
            '日期': pd.date_range('2025-01-01', periods=2, freq='D'),
            '开盘': [100.0, 101.0],
            '最高': [105.0, 106.0],
            '最低': [95.0, 96.0],
            '收盘': [100.0, 101.0],
            '成交量': [1000000, 1100000],
            '成交额': [100000000, 111000000]
        })
        
        # 保存数据
        count = self.storage.save_kline_data(data, '600519.SH', 'daily')
        
        # 验证
        self.assertEqual(count, 2)
        
        # 加载验证
        loaded_data = self.storage.load_kline_data(
            '600519.SH',
            datetime(2025, 1, 1),
            datetime(2025, 1, 2),
            'daily'
        )
        
        self.assertIsNotNone(loaded_data)
        self.assertEqual(len(loaded_data), 2)

    def test_incremental_save_no_duplicate(self):
        """测试增量保存不会产生重复数据"""
        data_a = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=3, freq='D'),
            'open': [10.0, 11.0, 12.0],
            'high': [11.0, 12.0, 13.0],
            'low': [9.0, 10.0, 11.0],
            'close': [10.5, 11.5, 12.5],
            'volume': [100, 110, 120],
            'amount': [1000, 1100, 1200],
        })
        data_b = pd.DataFrame({
            'date': pd.date_range('2025-01-03', periods=3, freq='D'),
            'open': [12.0, 13.0, 14.0],
            'high': [13.0, 14.0, 15.0],
            'low': [11.0, 12.0, 13.0],
            'close': [12.8, 13.8, 14.8],  # 2025-01-03 将被更新
            'volume': [121, 130, 140],
            'amount': [1210, 1300, 1400],
        })

        self.storage.save_kline_data(data_a, '600519.SH', 'daily')
        self.storage.save_kline_data(data_b, '600519.SH', 'daily')

        loaded = self.storage.load_kline_data(
            '600519.SH',
            datetime(2025, 1, 1),
            datetime(2025, 1, 5),
            'daily',
        )

        self.assertIsNotNone(loaded)
        self.assertEqual(len(loaded), 5)
        self.assertAlmostEqual(float(loaded.loc['2025-01-03']['close']), 12.8)

    def test_aggregate_30min_to_daily(self):
        """测试30分钟线聚合日线"""
        timestamps = pd.to_datetime([
            '2025-01-01 09:30:00', '2025-01-01 10:00:00', '2025-01-01 10:30:00',
            '2025-01-02 09:30:00', '2025-01-02 10:00:00',
        ])
        data = pd.DataFrame({
            'date': timestamps,
            'open': [10.0, 10.2, 10.3, 11.0, 11.2],
            'high': [10.5, 10.6, 10.7, 11.5, 11.6],
            'low': [9.9, 10.1, 10.2, 10.8, 11.0],
            'close': [10.2, 10.3, 10.4, 11.2, 11.4],
            'volume': [100, 120, 140, 150, 160],
            'amount': [1000, 1200, 1400, 1500, 1600],
        })

        self.storage.save_kline_data(data, '000001.SZ', '30min')
        daily = self.storage.aggregate_30min_to_daily(
            '000001.SZ',
            datetime(2025, 1, 1),
            datetime(2025, 1, 2),
        )

        self.assertIsNotNone(daily)
        self.assertEqual(len(daily), 2)
        self.assertAlmostEqual(float(daily.iloc[0]['open']), 10.0)
        self.assertAlmostEqual(float(daily.iloc[0]['close']), 10.4)
        self.assertEqual(int(daily.iloc[0]['volume']), 360)


if __name__ == '__main__':
    unittest.main(verbosity=2)
