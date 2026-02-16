"""
测试分钟数据下载功能
"""
import asyncio
from datetime import datetime, timedelta
from services.data_fetcher import DataFetcher
from loguru import logger
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_minute_download():
    """测试分钟数据下载"""
    print("=== 分钟数据下载测试 ===\n")
    
    # 配置测试参数
    test_stock_code = "000001.SZ"  # 平安银行
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)  # 最近3天
    
    test_frequencies = [
        '1min',  # 1分钟
        '5min',  # 5分钟
        '15min', # 15分钟
        '30min', # 30分钟
        '60min',  # 60分钟
        'daily'   # 日线
    ]
    
    print(f"测试股票: {test_stock_code}")
    print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    print("")
    
    # 测试不同的数据源
    test_sources = ['mock', 'auto']
    
    for source in test_sources:
        print(f"=== 测试数据源: {source} ===")
        
        try:
            # 初始化数据获取器
            fetcher = DataFetcher(source=source)
            
            # 测试不同频率
            for freq in test_frequencies:
                print(f"\n测试频率: {freq}")
                
                try:
                    # 获取数据
                    data = await fetcher.get_data(
                        code=test_stock_code,
                        start_date=start_date,
                        end_date=end_date,
                        freq=freq
                    )
                    
                    if data is not None and len(data) > 0:
                        print(f"  ✓ 成功获取 {len(data)} 条记录")
                        print(f"    日期范围: {data.index.min()} 到 {data.index.max()}")
                        print(f"    数据列: {list(data.columns)}")
                        print(f"    前3条数据:")
                        print(f"    {data.head(3).to_string()}")
                    else:
                        print(f"  ✗ 未获取到数据")
                
                except Exception as e:
                    print(f"  ✗ 错误: {e}")
            
        except Exception as e:
            print(f"数据源 {source} 测试失败: {e}")
            import traceback
            traceback.print_exc()

async def test_multiple_stocks():
    """测试多只股票的分钟数据下载"""
    print("\n\n=== 多只股票分钟数据测试 ===\n")
    
    # 测试股票列表
    test_stocks = [
        '000001.SZ',  # 平安银行
        '600519.SH',  # 贵州茅台
        '000002.SZ',  # 万科A
        '601318.SH',  # 中国平安
    ]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)  # 最近1天
    
    print(f"测试股票: {test_stocks}")
    print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    print(f"频率: 30min")
    print("")
    
    try:
        fetcher = DataFetcher(source='mock')
        
        for stock_code in test_stocks:
            print(f"\n下载 {stock_code}...")
            
            try:
                data = await fetcher.get_data(
                    code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    freq='30min'
                )
                
                if data is not None and len(data) > 0:
                    print(f"  ✓ {stock_code}: {len(data)} 条记录")
                else:
                    print(f"  ✗ {stock_code}: 未获取到数据")
            
            except Exception as e:
                print(f"  ✗ {stock_code}: {e}")
    
    except Exception as e:
        print(f"批量测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_data_download_service():
    """测试数据下载服务的分钟数据下载"""
    print("\n\n=== 数据下载服务测试 ===\n")
    
    try:
        from services.data_download_service import DataDownloadService
        
        # 初始化服务
        service = DataDownloadService(use_duckdb=False)  # 使用CSV存储测试
        
        # 测试参数
        test_stock_code = "000001.SZ"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        print(f"测试股票: {test_stock_code}")
        print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
        print("")
        
        # 测试不同频率
        test_frequencies = ['30min', 'daily']
        
        for freq in test_frequencies:
            print(f"\n测试频率: {freq}")
            
            try:
                result = await service.download_stock_data(
                    stock_code=test_stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    frequency=freq,
                    source='mock',
                    force_download=True  # 强制重新下载
                )
                
                print(f"  状态: {result['status']}")
                print(f"  消息: {result['message']}")
                
                if result.get('data_count'):
                    print(f"  数据量: {result['data_count']}")
                
                if result.get('record_id'):
                    print(f"  记录ID: {result['record_id']}")
                
                if result.get('data') is not None and len(result['data']) > 0:
                    print(f"  数据样本:")
                    print(f"  {result['data'].head(3).to_string()}")
            
            except Exception as e:
                print(f"  ✗ 错误: {e}")
                import traceback
                traceback.print_exc()
    
    except Exception as e:
        print(f"数据下载服务测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主测试函数"""
    try:
        # 配置日志
        logger.add(sys.stdout, format="{time} | {level} | {message}", level="INFO")
        
        # 1. 测试直接的数据获取
        await test_minute_download()
        
        # 2. 测试多只股票
        await test_multiple_stocks()
        
        # 3. 测试数据下载服务
        await test_data_download_service()
        
        print("\n\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # 运行测试
    asyncio.run(main())