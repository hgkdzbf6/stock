"""数据下载服务增量与30分钟聚合测试"""

import unittest
from unittest.mock import patch
from datetime import datetime
from pathlib import Path
import sys
import os

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.data_download_service import DataDownloadService
from services.duckdb_storage_service import DuckDBStorageService


class _FakeFetcher:
    """可控假的数据抓取器（仅用于单元测试服务流程）"""

    def __init__(self, source='auto'):
        self.source = source

    async def get_data(self, code, start_date, end_date, freq='1d'):
        if freq == '1d':
            dates = pd.date_range(start_date, end_date, freq='D')
        elif freq == '30min':
            dates = pd.date_range(start_date, end_date, freq='30min')
        else:
            dates = pd.date_range(start_date, end_date, freq='D')

        if len(dates) == 0:
            return pd.DataFrame()

        return pd.DataFrame({
            'date': dates,
            'open': [10.0 + i for i in range(len(dates))],
            'high': [10.5 + i for i in range(len(dates))],
            'low': [9.5 + i for i in range(len(dates))],
            'close': [10.2 + i for i in range(len(dates))],
            'volume': [1000 + i for i in range(len(dates))],
            'amount': [10000 + i for i in range(len(dates))],
        })


class TestDataPackageIncremental(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = 'data/test_incremental_package.duckdb'

    def setUp(self):
        if Path(self.test_db_path).exists():
            Path(self.test_db_path).unlink()
        self.service = DataDownloadService(use_duckdb=False)
        self.service.storage = DuckDBStorageService(self.test_db_path)
        self.service.use_duckdb = True

    def tearDown(self):
        self.service.storage.close()
        if Path(self.test_db_path).exists():
            Path(self.test_db_path).unlink()

    def test_incremental_gap_download(self):
        async def run_test():
            with patch('services.data_download_service.DataFetcher', _FakeFetcher):
                await self.service.download_stock_data(
                    stock_code='600519.SH',
                    start_date=datetime(2025, 1, 1),
                    end_date=datetime(2025, 1, 5),
                    frequency='daily',
                    source='ashare',
                )

                result = await self.service.download_stock_data(
                    stock_code='600519.SH',
                    start_date=datetime(2025, 1, 3),
                    end_date=datetime(2025, 1, 8),
                    frequency='daily',
                    source='ashare',
                )

            self.assertEqual(result['status'], 'completed')
            self.assertEqual(len(result.get('downloaded_segments', [])), 1)
            seg = result['downloaded_segments'][0]
            self.assertEqual(seg['start_date'], '2025-01-06')
            self.assertEqual(seg['end_date'], '2025-01-08')

            loaded = self.service.storage.load_kline_data(
                '600519.SH',
                datetime(2025, 1, 1),
                datetime(2025, 1, 8),
                'daily',
            )
            self.assertIsNotNone(loaded)
            self.assertEqual(len(loaded), 8)

        import asyncio
        asyncio.run(run_test())

    def test_daily_derived_from_30min(self):
        async def run_test():
            with patch('services.data_download_service.DataFetcher', _FakeFetcher):
                await self.service.download_stock_data(
                    stock_code='000001.SZ',
                    start_date=datetime(2025, 1, 1),
                    end_date=datetime(2025, 1, 2),
                    frequency='30min',
                    source='ashare',
                )

                result = await self.service.download_stock_data(
                    stock_code='000001.SZ',
                    start_date=datetime(2025, 1, 1),
                    end_date=datetime(2025, 1, 2),
                    frequency='daily',
                    source='ashare',
                )

            self.assertEqual(result['status'], 'derived')
            self.assertEqual(result.get('derived_from'), '30min')

            daily = self.service.storage.load_kline_data(
                '000001.SZ',
                datetime(2025, 1, 1),
                datetime(2025, 1, 2),
                'daily',
            )
            self.assertIsNotNone(daily)
            self.assertGreaterEqual(len(daily), 2)

        import asyncio
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main(verbosity=2)
