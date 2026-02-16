"""股票代码映射服务使用示例"""
import asyncio
from services.stock_code_service import stock_code_service
from services.data_fetcher import DataFetcher


async def example_download():
    """示例1: 下载股票列表"""
    print("=" * 60)
    print("示例1: 下载股票列表")
    print("=" * 60)
    
    # 初始化数据获取器
    data_fetcher = DataFetcher(source='ashare')
    
    # 分批下载前2页股票
    all_stocks = []
    for page in range(1, 3):
        stocks = await data_fetcher.get_stock_list(
            page=page,
            page_size=100
        )
        if not stocks:
            break
        all_stocks.extend(stocks)
        print(f"已获取第{page}页: {len(stocks)}只股票")
    
    # 保存到本地
    success = stock_code_service.save_stock_list(all_stocks)
    if success:
        print(f"✅ 成功保存 {len(all_stocks)} 只股票到 data/stock_list.csv\n")
    
    return all_stocks


def example_search_by_name():
    """示例2: 根据名称搜索股票"""
    print("=" * 60)
    print("示例2: 根据名称搜索股票")
    print("=" * 60)
    
    # 搜索包含"银行"的股票
    results = stock_code_service.search_by_name('银行', limit=5)
    print(f"找到 {len(results)} 只包含'银行'的股票:")
    for stock in results:
        print(f"  {stock['code']} {stock['name']} ({stock['market']}) - {stock['price']}元")
    
    print()


def example_search_by_code():
    """示例3: 根据代码搜索股票"""
    print("=" * 60)
    print("示例3: 根据代码搜索股票")
    print("=" * 60)
    
    # 搜索代码包含"600"的股票
    results = stock_code_service.search_by_code('600', limit=5)
    print(f"找到 {len(results)} 只代码包含'600'的股票:")
    for stock in results:
        print(f"  {stock['code']} {stock['name']} ({stock['market']}) - {stock['price']}元")
    
    print()


def example_search_by_prefix():
    """示例4: 根据前缀搜索（自动补全）"""
    print("=" * 60)
    print("示例4: 根据前缀搜索（自动补全）")
    print("=" * 60)
    
    # 搜索名称以"贵州"开头的股票
    results = stock_code_service.search_by_prefix('贵州', search_field='name', limit=5)
    print(f"找到 {len(results)} 只名称以'贵州'开头的股票:")
    for stock in results:
        print(f"  {stock['code']} {stock['name']}")
    
    print()


def example_fuzzy_search():
    """示例5: 模糊搜索"""
    print("=" * 60)
    print("示例5: 模糊搜索（同时搜索代码和名称）")
    print("=" * 60)
    
    # 搜索"茅台"
    results = stock_code_service.fuzzy_search('茅台', limit=5)
    print(f"找到 {len(results)} 只包含'茅台'的股票:")
    for stock in results:
        print(f"  {stock['code']} {stock['name']} ({stock['market']})")
    
    print()


def example_get_stock_info():
    """示例6: 获取股票详细信息"""
    print("=" * 60)
    print("示例6: 获取股票详细信息")
    print("=" * 60)
    
    # 获取股票信息
    stock_info = stock_code_service.get_stock_info('600519.SH')
    if stock_info:
        print(f"股票代码: {stock_info['code']}")
        print(f"股票名称: {stock_info['name']}")
        print(f"所属市场: {stock_info['market']}")
        print(f"最新价格: {stock_info['price']}元")
        print(f"涨跌额: {stock_info['change']}元")
        print(f"涨跌幅: {stock_info['change_pct']}%")
        print(f"开盘价: {stock_info['open']}元")
        print(f"最高价: {stock_info['high']}元")
        print(f"最低价: {stock_info['low']}元")
        print(f"昨收价: {stock_info['pre_close']}元")
        print(f"成交量: {stock_info['volume']}手")
        print(f"成交额: {stock_info['amount']}元")
        print(f"市值: {stock_info['market_cap']}元")
    
    print()


def example_get_stocks_by_market():
    """示例7: 根据市场获取股票"""
    print("=" * 60)
    print("示例7: 根据市场获取股票")
    print("=" * 60)
    
    markets = ['沪市主板', '科创板', '深市主板', '创业板']
    for market in markets:
        results = stock_code_service.get_stocks_by_market(market, limit=5)
        print(f"{market}: 找到 {len(results)} 只股票")
        for stock in results[:3]:
            print(f"  {stock['code']} {stock['name']} - {stock['price']}元")
        print()


def example_statistics():
    """示例8: 获取统计信息"""
    print("=" * 60)
    print("示例8: 获取统计信息")
    print("=" * 60)
    
    stats = stock_code_service.get_statistics()
    print(f"总股票数: {stats['total']}只")
    print("\n各市场分布:")
    for market, count in sorted(stats['by_market'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {market}: {count}只")
    
    print()


def example_name_to_code():
    """示例9: 根据名称查找代码"""
    print("=" * 60)
    print("示例9: 根据名称查找代码")
    print("=" * 60)
    
    # 用户只知道股票名称
    stock_names = ['贵州茅台', '平安银行', '特锐德']
    
    for name in stock_names:
        results = stock_code_service.search_by_name(name, limit=1)
        if results:
            stock = results[0]
            print(f"{stock['name']} -> {stock['code']} ({stock['market']})")
    
    print()


def example_code_to_name():
    """示例10: 根据代码查找名称"""
    print("=" * 60)
    print("示例10: 根据代码查找名称")
    print("=" * 60)
    
    # 用户只知道股票代码
    stock_codes = ['600519.SH', '000001.SZ', '300001.SZ']
    
    for code in stock_codes:
        stock_info = stock_code_service.get_stock_info(code)
        if stock_info:
            print(f"{stock_info['code']} -> {stock_info['name']} ({stock_info['market']})")
    
    print()


async def main():
    """主函数"""
    print("\n")
    print("🎯 股票代码映射服务使用示例")
    print("=" * 60)
    
    # 检查是否已下载股票列表
    stats = stock_code_service.get_statistics()
    if stats['total'] == 0:
        print("\n⚠️  股票列表为空，正在下载...")
        await example_download()
    else:
        print(f"\n✅ 已加载 {stats['total']} 只股票\n")
    
    # 运行示例
    example_search_by_name()
    example_search_by_code()
    example_search_by_prefix()
    example_fuzzy_search()
    example_get_stock_info()
    example_get_stocks_by_market()
    example_statistics()
    example_name_to_code()
    example_code_to_name()
    
    print("=" * 60)
    print("✅ 所有示例运行完成！")
    print("=" * 60)
    print("\n📚 更多使用方法请查看: backend/STOCK_CODE_USAGE.md")
    print()


if __name__ == '__main__':
    asyncio.run(main())