"""股票代码服务测试"""
import unittest
import sys
from pathlib import Path

sys.path.append('.')

from services.stock_code_service import StockCodeService
from services.data_fetcher import DataFetcher
import asyncio


class TestStockCodeService(unittest.TestCase):
    """股票代码服务测试"""
    
    def setUp(self):
        """测试前初始化"""
        # 使用测试数据目录
        self.service = StockCodeService(data_dir='data')
        self.data_fetcher = DataFetcher(source='ashare')
        
        # 创建测试股票列表
        self.test_stocks = [
            {
                '代码': '600519.SH',
                '名称': '贵州茅台',
                '最新价': 1500.00,
                '涨跌额': 10.00,
                '涨跌幅': 0.67,
                '成交量': 1000000,
                '成交额': 1500000000,
                '市值': 2000000000000,
                '开盘': 1490.00,
                '最高': 1510.00,
                '最低': 1485.00,
                '昨收': 1490.00
            },
            {
                '代码': '000001.SZ',
                '名称': '平安银行',
                '最新价': 10.50,
                '涨跌额': 0.20,
                '涨跌幅': 1.94,
                '成交量': 50000000,
                '成交额': 525000000,
                '市值': 200000000000,
                '开盘': 10.30,
                '最高': 10.60,
                '最低': 10.25,
                '昨收': 10.30
            },
            {
                '代码': '688111.SH',
                '名称': '金山办公',
                '最新价': 200.00,
                '涨跌额': 5.00,
                '涨跌幅': 2.56,
                '成交量': 100000,
                '成交额': 20000000,
                '市值': 50000000000,
                '开盘': 195.00,
                '最高': 202.00,
                '最低': 194.00,
                '昨收': 195.00
            },
            {
                '代码': '300001.SZ',
                '名称': '特锐德',
                '最新价': 20.00,
                '涨跌额': 0.50,
                '涨跌幅': 2.56,
                '成交量': 1000000,
                '成交额': 20000000,
                '市值': 4000000000,
                '开盘': 19.50,
                '最高': 20.50,
                '最低': 19.30,
                '昨收': 19.50
            }
        ]
    
    def test_detect_market(self):
        """测试市场检测"""
        # 沪市主板
        market = StockCodeService._detect_market('600519.SH')
        self.assertEqual(market, '沪市主板')
        
        # 科创板
        market = StockCodeService._detect_market('688111.SH')
        self.assertEqual(market, '科创板')
        
        # 深市主板
        market = StockCodeService._detect_market('000001.SZ')
        self.assertEqual(market, '深市主板')
        
        # 创业板
        market = StockCodeService._detect_market('300001.SZ')
        self.assertEqual(market, '创业板')
        
        print("✅ 市场检测测试通过")
    
    def test_save_stock_list(self):
        """测试保存股票列表"""
        success = self.service.save_stock_list(self.test_stocks)
        self.assertTrue(success)
        
        # 验证文件存在
        self.assertTrue(self.service.stock_list_file.exists())
        
        print("✅ 保存股票列表测试通过")
    
    def test_search_by_code(self):
        """测试根据代码搜索"""
        # 先保存测试数据
        self.service.save_stock_list(self.test_stocks)
        
        # 精确搜索
        results = self.service.search_by_code('600519')
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['code'], '600519.SH')
        self.assertEqual(results[0]['name'], '贵州茅台')
        
        # 部分搜索
        results = self.service.search_by_code('6005')
        self.assertGreater(len(results), 0)
        
        print("✅ 根据代码搜索测试通过")
    
    def test_search_by_name(self):
        """测试根据名称搜索"""
        # 先保存测试数据
        self.service.save_stock_list(self.test_stocks)
        
        # 精确搜索
        results = self.service.search_by_name('贵州茅台')
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['code'], '600519.SH')
        
        # 部分搜索
        results = self.service.search_by_name('贵州')
        self.assertGreater(len(results), 0)
        
        # 部分搜索
        results = self.service.search_by_name('银行')
        self.assertGreater(len(results), 0)
        
        print("✅ 根据名称搜索测试通过")
    
    def test_search_by_prefix(self):
        """测试根据前缀搜索"""
        # 先保存测试数据
        self.service.save_stock_list(self.test_stocks)
        
        # 名称前缀
        results = self.service.search_by_prefix('贵州', search_field='name')
        self.assertGreater(len(results), 0)
        
        # 代码前缀
        results = self.service.search_by_prefix('6005', search_field='code')
        self.assertGreater(len(results), 0)
        
        print("✅ 根据前缀搜索测试通过")
    
    def test_fuzzy_search(self):
        """测试模糊搜索"""
        # 先保存测试数据
        self.service.save_stock_list(self.test_stocks)
        
        # 搜索代码
        results = self.service.fuzzy_search('600519')
        self.assertGreater(len(results), 0)
        
        # 搜索名称
        results = self.service.fuzzy_search('茅台')
        self.assertGreater(len(results), 0)
        
        # 搜索关键词
        results = self.service.fuzzy_search('银行')
        self.assertGreater(len(results), 0)
        
        print("✅ 模糊搜索测试通过")
    
    def test_get_stock_info(self):
        """测试获取股票信息"""
        # 先保存测试数据
        self.service.save_stock_list(self.test_stocks)
        
        # 获取股票信息
        stock_info = self.service.get_stock_info('600519.SH')
        self.assertIsNotNone(stock_info)
        self.assertEqual(stock_info['code'], '600519.SH')
        self.assertEqual(stock_info['name'], '贵州茅台')
        self.assertEqual(stock_info['market'], '沪市主板')
        
        # 测试不存在的股票
        stock_info = self.service.get_stock_info('999999.SH')
        self.assertIsNone(stock_info)
        
        print("✅ 获取股票信息测试通过")
    
    def test_get_stocks_by_market(self):
        """测试根据市场获取股票"""
        # 先保存测试数据
        self.service.save_stock_list(self.test_stocks)
        
        # 获取沪市主板股票
        results = self.service.get_stocks_by_market('沪市主板')
        self.assertGreater(len(results), 0)
        
        # 获取科创板股票
        results = self.service.get_stocks_by_market('科创板')
        self.assertGreater(len(results), 0)
        
        # 获取创业板股票
        results = self.service.get_stocks_by_market('创业板')
        self.assertGreater(len(results), 0)
        
        print("✅ 根据市场获取股票测试通过")
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        # 先保存测试数据
        self.service.save_stock_list(self.test_stocks)
        
        # 获取统计信息
        stats = self.service.get_statistics()
        self.assertGreater(stats['total'], 0)
        self.assertIn('沪市主板', stats['by_market'])
        self.assertIn('深市主板', stats['by_market'])
        self.assertIn('科创板', stats['by_market'])
        self.assertIn('创业板', stats['by_market'])
        
        print("✅ 获取统计信息测试通过")
    
    def test_refresh(self):
        """测试刷新"""
        # 先保存测试数据
        self.service.save_stock_list(self.test_stocks)
        
        # 刷新
        success = self.service.refresh()
        self.assertTrue(success)
        
        print("✅ 刷新测试通过")
    
    async def test_download_real_stock_list(self):
        """测试下载真实股票列表（可选，需要网络）"""
        try:
            print("\n开始下载真实股票列表...")
            
            # 分批下载
            all_stocks = []
            for page in range(1, 4):  # 下载前3页
                stocks = await self.data_fetcher.get_stock_list(
                    page=page,
                    page_size=100
                )
                if not stocks:
                    break
                all_stocks.extend(stocks)
                print(f"已获取 {len(all_stocks)} 只股票")
            
            if all_stocks:
                # 保存到本地
                success = self.service.save_stock_list(all_stocks)
                self.assertTrue(success)
                print(f"✅ 成功下载并保存 {len(all_stocks)} 只股票")
                
                # 测试搜索
                results = self.service.search_by_name('银行', limit=5)
                print(f"✅ 搜索'银行'找到 {len(results)} 只股票")
                if results:
                    for stock in results[:3]:
                        print(f"   - {stock['code']} {stock['name']} ({stock['market']})")
            else:
                print("⚠️ 未获取到股票数据")
                
        except Exception as e:
            print(f"⚠️ 下载真实股票列表失败: {e}")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("股票代码服务测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStockCodeService)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 运行异步测试
    if result.wasSuccessful():
        print("\n" + "=" * 60)
        print("是否下载真实股票列表？(需要网络连接)")
        print("=" * 60)
        print("运行: python -m unittest test_stock_code_service.TestStockCodeService.test_download_real_stock_list")


if __name__ == '__main__':
    run_tests()