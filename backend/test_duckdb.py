"""测试DuckDB存储功能"""
import asyncio
from datetime import datetime
from services.data_download_service import DataDownloadService
from services.duckdb_storage_service import DuckDBStorageService

async def test():
    print('=== 测试DuckDB存储 ===\n')
    
    # 1. 初始化服务
    print('1. 初始化DuckDBStorageService...')
    try:
        storage = DuckDBStorageService()
        print(f'✅ DuckDBStorageService初始化成功\n')
    except Exception as e:
        print(f'❌ DuckDBStorageService初始化失败: {e}\n')
        return
    
    # 2. 初始化下载服务
    print('2. 初始化DataDownloadService...')
    try:
        download_service = DataDownloadService(use_duckdb=True)
        print(f'✅ Storage类型: {type(download_service.storage).__name__}')
        print(f'✅ use_duckdb: {download_service.use_duckdb}\n')
    except Exception as e:
        print(f'❌ DataDownloadService初始化失败: {e}\n')
        return
    
    # 3. 下载数据
    print('3. 下载600519.SH数据...')
    result = await download_service.download_stock_data(
        stock_code='600519.SH',
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 5),
        frequency='daily',
        source='ashare'
    )
    print(f'状态: {result["status"]}')
    print(f'数据量: {result.get("data_count")}条')
    print(f'记录ID: {result.get("record_id")}\n')
    
    # 4. 查询统计
    print('4. 查询DuckDB统计信息...')
    stats = storage.get_statistics()
    print(f'总记录数: {stats["total_records"]}')
    print(f'股票数: {stats["total_stocks"]}')
    
    # 5. 读取数据
    print('\n5. 从DuckDB读取数据...')
    data = storage.load_kline_data(
        stock_code='600519.SH',
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 5),
        frequency='daily'
    )
    if data is not None:
        print(f'✅ 读取成功: {len(data)}条记录')
        print(f'数据列: {list(data.columns)}')
    else:
        print('❌ 读取失败')
    
    print('\n=== 测试完成 ===')

if __name__ == '__main__':
    asyncio.run(test())