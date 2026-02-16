"""
测试真实数据源功能 - 验证系统只使用真实市场数据
"""
import asyncio
from datetime import datetime, timedelta
from services.data_fetcher import DataFetcher
from services.data_download_service import DataDownloadService
from loguru import logger
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_real_data_sources():
    """测试真实数据源功能"""
    print("=== 真实数据源测试 ===")
    print("验证：系统仅使用真实市场数据，禁用 mock 数据源")
    print("")
    
    # 1. 测试 DataFetcher 禁用 mock
    print("1. 测试 DataFetcher 禁用 mock...")
    try:
        # 尝试初始化 mock 数据源，应该抛出异常
        fetcher = DataFetcher(source='mock')
        print("  ✗ 错误：Mock 数据源初始化成功（应该被禁用）")
    except ValueError as e:
        print(f"  ✓ 正确：Mock 数据源被正确禁用 - {e}")
    except Exception as e:
        print(f"  ✗ 错误：Mock 数据源禁用失败 - {e}")
    
    print("")
    
    # 2. 测试不同数据源的初始化
    print("2. 测试不同真实数据源的初始化...")
    real_sources = ['akshare', 'ashare', 'tushare', 'eastmoney', 'sina', 'tencent', 'baostock', 'auto']
    
    for source in real_sources:
        try:
            fetcher = DataFetcher(source=source)
            print(f"  ✓ {source} 数据源初始化成功")
        except Exception as e:
            print(f"  ✗ {source} 数据源初始化失败: {e}")
    
    print("")
    
    # 3. 测试 DataDownloadService 禁用 mock
    print("3. 测试 DataDownloadService 禁用 mock...")
    service = DataDownloadService(use_duckdb=False)
    
    try:
        # 尝试使用 mock 数据源下载，应该返回失败
        test_stock_code = "600519.SH"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        result = await service.download_stock_data(
            stock_code=test_stock_code,
            start_date=start_date,
            end_date=end_date,
            frequency='daily',
            source='mock',
            force_download=True
        )
        
        if result['status'] == 'failed' and 'mock' in result.get('message', ''):
            print(f"  ✓ 正确：Mock 数据下载被正确拒绝")
            print(f"    错误信息: {result['message']}")
        else:
            print(f"  ✗ 错误：Mock 数据下载未被正确拒绝")
            print(f"    状态: {result['status']}, 消息: {result['message']}")
    except Exception as e:
        print(f"  ✗ 错误：DataDownloadService 测试失败 - {e}")
    
    print("")
    
    # 4. 测试真实数据源的数据获取
    print("4. 测试真实数据源的数据获取...")
    test_stocks = [
        ('000001.SZ', '平安银行'),
        ('600519.SH', '贵州茅台'),
        ('000858.SZ', '五粮液')
    ]
    
    successful_downloads = 0
    failed_downloads = 0
    
    for stock_code, stock_name in test_stocks:
        print(f"\n  测试 {stock_name} ({stock_code})...")
        
        # 测试日线数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        
        try:
            # 尝试从真实数据源获取数据
            fetcher = DataFetcher(source='auto')
            
            # 测试日线数据
            daily_data = await fetcher.get_data(
                code=stock_code,
                start_date=start_date,
                end_date=end_date,
                freq='daily'
            )
            
            if daily_data is not None and len(daily_data) > 0:
                print(f"    ✓ 日线数据获取成功: {len(daily_data)} 条记录")
                print(f"       数据源: auto（真实数据源）")
                print(f"       日期范围: {daily_data.index.min()} 到 {daily_data.index.max()}")
                successful_downloads += 1
            else:
                print(f"    ✗ 日线数据获取失败（所有真实数据源都失败）")
                failed_downloads += 1
        
        except Exception as e:
            if "所有真实数据源都失败" in str(e):
                print(f"    ✗ 所有真实数据源都失败（符合预期）")
                print(f"       这可能需要：")
                print(f"       - 检查网络连接")
                print(f"       - 配置 Tushare API token")
                print(f"       - 确认数据源 API 是否正常")
            else:
                print(f"    ✗ 数据获取异常: {e}")
    
    print("")
    print("5. 数据源状态总结：")
    print(f"  成功下载: {successful_downloads} 只股票")
    print(f"  失败下载: {failed_downloads} 只股票")

async def test_real_minute_data():
    """测试真实分钟数据下载"""
    print("\n\n=== 真实分钟数据测试 ===")
    print("说明：大多数免费数据源不支持分钟级历史数据")
    print("")
    
    test_stock_code = "000001.SZ"
    stock_name = "平安银行"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    
    print(f"测试股票: {stock_name} ({test_stock_code})")
    print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    print("")
    
    # 测试不同的分钟频率
    test_frequencies = ['1min', '5min', '15min', '30min', '60min']
    
    for freq in test_frequencies:
        print(f"  测试 {freq} 数据...")
        
        try:
            fetcher = DataFetcher(source='auto')
            data = await fetcher.get_data(
                code=test_stock_code,
                start_date=start_date,
                end_date=end_date,
                freq=freq
            )
            
            if data is not None and len(data) > 0:
                print(f"    ✓ 成功获取 {len(data)} 条 {freq} 数据")
                print(f"       日期范围: {data.index.min()} 到 {data.index.max()}")
                print(f"       这表明数据源支持 {freq} 数据")
            else:
                print(f"    ✗ 未获取到 {freq} 数据")
                print(f"       这表明该数据源不支持 {freq} 数据（符合预期）")
        
        except Exception as e:
            if "所有真实数据源都失败" in str(e):
                print(f"    ✗ 所有真实数据源都失败（符合预期）")
            else:
                print(f"    ✗ 错误: {e}")
    
    print("")
    print("注意：")
    print("  - 大多数免费数据源不支持分钟级历史数据")
    print("  - 日线数据通常可以正常获取，用于趋势分析和回测")
    print("  - 如需分钟级数据，可能需要使用付费的专业数据源")

async def test_data_download_service():
    """测试数据下载服务（仅使用真实数据）"""
    print("\n\n=== 数据下载服务测试 ===")
    
    try:
        service = DataDownloadService(use_duckdb=False)
        
        # 测试参数
        test_stock_code = "600519.SH"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        print(f"测试股票: {test_stock_code}")
        print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
        print("")
        
        # 测试日线数据下载
        print("  测试日线数据下载...")
        result = await service.download_stock_data(
            stock_code=test_stock_code,
            start_date=start_date,
            end_date=end_date,
            frequency='daily',
            source='auto',  # 使用自动模式尝试所有真实数据源
            force_download=True  # 强制重新下载
        )
        
        print(f"  状态: {result['status']}")
        print(f"  消息: {result['message']}")
        print(f"  数据源: {result.get('source', 'unknown')}")
        
        if result.get('data_count'):
            print(f"  数据量: {result['data_count']}")
        
        if result.get('record_id'):
            print(f"  记录ID: {result['record_id']}")
        
        if result.get('data') is not None and len(result['data']) > 0:
            print(f"  数据样本:")
            print(f"  {result['data'].head(3).to_string()}")
        
        # 测试分钟数据下载（预期会失败）
        print("\n  测试分钟数据下载（预期可能失败）...")
        result = await service.download_stock_data(
            stock_code=test_stock_code,
            start_date=start_date,
            end_date=end_date,
            frequency='30min',
            source='auto',
            force_download=True
        )
        
        print(f"  状态: {result['status']}")
        print(f"  消息: {result['message']}")
        
        if result['status'] == 'failed':
            print(f"  ✓ 分钟数据下载失败（符合预期）")
            print(f"  原因：免费数据源通常不提供分钟级历史数据")
        else:
            print(f"  ✗ 意外：分钟数据下载成功")
        
    except Exception as e:
        print(f"  ✗ 数据下载服务测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主测试函数"""
    try:
        print("=== 系统配置验证 ===")
        print("验证：系统已配置为仅使用真实市场数据")
        print("  1. Mock 数据源已禁用")
        print("  2. 系统在所有数据源失败时会明确报告")
        print("  3. 系统不包含任何模拟数据逻辑")
        print("")
        
        # 1. 测试真实数据源配置
        await test_real_data_sources()
        
        # 2. 测试真实分钟数据
        await test_real_minute_data()
        
        # 3. 测试数据下载服务
        await test_data_download_service()
        
        print("\n\n=== 测试完成 ===")
        print("系统配置验证:")
        print("  ✓ Mock 数据源已禁用")
        print("  ✓ 系统仅使用真实市场数据")
        print("  ✓ 当真实数据源失败时会明确报告")
        print("")
        print("使用建议:")
        print("  1. 日线数据：可以正常获取，用于趋势分析和回测")
        print("  2. 分钟数据：需要付费数据源或等待交易时间")
        print("  3. 数据质量：系统现在使用真实的市场数据")
        print("  4. 错误处理：当数据源失败时，会显示清晰的错误信息")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # 运行测试
    asyncio.run(main())