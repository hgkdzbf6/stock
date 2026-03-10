"""
测试新闻来源过滤功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.news_fetcher import NewsFetcher


async def test_source_filter():
    """测试来源过滤功能"""
    print("=" * 60)
    print("测试新闻来源过滤功能")
    print("=" * 60)
    
    fetcher = NewsFetcher()
    
    # 测试1: 只选择新浪财经
    print("\n测试1: 只选择新浪财经")
    print("-" * 60)
    try:
        news = await fetcher.fetch_stock_news(
            stock_code="",
            stock_name="",
            sector_name=None,
            market=None,
            sources=["新浪财经"],
            limit=10
        )
        print(f"获取到 {len(news)} 条新闻")
        
        # 检查来源
        sources = set([n.get('source', '') for n in news])
        print(f"新闻来源: {sources}")
        
        if len(news) > 0:
            first_news = news[0]
            print(f"第一条新闻来源: {first_news.get('source', '')}")
            print(f"第一条新闻标题: {first_news.get('title', '')[:50]}...")
        
        # 验证
        if len(news) > 0:
            all_sina = all(n.get('source') == '新浪财经' for n in news)
            if all_sina:
                print("✅ 测试通过: 所有新闻都来自新浪财经")
            else:
                print("❌ 测试失败: 存在其他来源的新闻")
                for n in news:
                    if n.get('source') != '新浪财经':
                        print(f"  发现非新浪财经新闻: {n.get('source')}")
        else:
            print("⚠️ 警告: 未获取到任何新闻")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试2: 只选择CNBC国际商业新闻
    print("\n测试2: 只选择CNBC国际商业新闻")
    print("-" * 60)
    try:
        news = await fetcher.fetch_stock_news(
            stock_code="",
            stock_name="",
            sector_name=None,
            market=None,
            sources=["CNBC国际商业新闻"],
            limit=5
        )
        print(f"获取到 {len(news)} 条新闻")
        
        # 检查来源
        sources = set([n.get('source', '') for n in news])
        print(f"新闻来源: {sources}")
        
        if len(news) > 0:
            first_news = news[0]
            print(f"第一条新闻来源: {first_news.get('source', '')}")
            print(f"第一条新闻标题: {first_news.get('title', '')[:50]}...")
        
        # 验证
        if len(news) > 0:
            # CNBC新闻的source可能是CNBC或其他名称
            print(f"所有新闻来源详情:")
            for n in news:
                print(f"  - 来源: {n.get('source')}")
                source_info = n.get('source_info', {})
                if source_info:
                    print(f"    中文名称: {source_info.get('name_cn')}")
                    print(f"    英文名称: {source_info.get('name')}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试3: 国内市场
    print("\n测试3: 国内市场")
    print("-" * 60)
    try:
        news = await fetcher.fetch_stock_news(
            stock_code="",
            stock_name="",
            sector_name=None,
            market="domestic",
            sources=None,
            limit=10
        )
        print(f"获取到 {len(news)} 条新闻")
        
        # 检查来源
        sources = set([n.get('source', '') for n in news])
        print(f"新闻来源: {sources}")
        
        if len(news) > 0:
            first_news = news[0]
            print(f"第一条新闻来源: {first_news.get('source', '')}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试4: 国外市场
    print("\n测试4: 国外市场")
    print("-" * 60)
    try:
        news = await fetcher.fetch_stock_news(
            stock_code="",
            stock_name="",
            sector_name=None,
            market="international",
            sources=None,
            limit=10
        )
        print(f"获取到 {len(news)} 条新闻")
        
        # 检查来源
        sources = set([n.get('source', '') for n in news])
        print(f"新闻来源: {sources}")
        print(f"新闻来源数量: {len(sources)}")
        
        if len(news) > 0:
            first_news = news[0]
            print(f"第一条新闻来源: {first_news.get('source')}")
            source_info = first_news.get('source_info', {})
            if source_info:
                print(f"  中文名称: {source_info.get('name_cn')}")
                print(f"  国家: {source_info.get('country_cn')}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试5: 检查RSS源配置
    print("\n测试5: 检查RSS源配置")
    print("-" * 60)
    print(f"配置的RSS源类别: {list(fetcher.default_rss_sources.keys())}")
    for category, urls in fetcher.default_rss_sources.items():
        print(f"\n{category}:")
        for url in urls:
            source_info = fetcher.rss_source_info.get(url, {})
            print(f"  URL: {url}")
            print(f"    中文名称: {source_info.get('name_cn', 'N/A')}")
            print(f"    英文名称: {source_info.get('name', 'N/A')}")
    
    await fetcher.close()
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_source_filter())