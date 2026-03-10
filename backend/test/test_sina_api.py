"""
测试新浪财经API
"""
import asyncio
import httpx
import json


async def test_sina_api():
    """测试新浪财经API"""
    print("=" * 60)
    print("测试新浪财经API")
    print("=" * 60)
    
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, connect=10.0),
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/",
            "Accept": "application/json, text/plain, */*"
        }
    )
    
    base_url = "https://feed.sina.com.cn/api/roll/get"
    
    # 测试1: 使用"财经"关键词
    print("\n测试1: 使用'财经'关键词")
    print("-" * 60)
    params = {
        "page": "1",
        "num": "10",
        "length": "120",
        "keyword": "财经"
    }
    
    try:
        response = await client.get(base_url, params=params)
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)}")
        
        data = response.json()
        print(f"\n响应结构:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
        
        if data and "result" in data:
            result = data["result"]
            if "data" in result:
                news_count = len(result["data"])
                print(f"\n获取到 {news_count} 条新闻")
                
                if news_count > 0:
                    print(f"\n第一条新闻:")
                    first_news = result["data"][0]
                    print(f"  标题: {first_news.get('title', '')}")
                    print(f"  URL: {first_news.get('url', '')}")
                    print(f"  时间: {first_news.get('ctime', '')}")
            else:
                print("  响应中没有'data'字段")
        else:
            print("  响应中没有'result'字段")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试2: 不使用关键词
    print("\n测试2: 不使用关键词")
    print("-" * 60)
    params = {
        "page": "1",
        "num": "10",
        "length": "120",
    }
    
    try:
        response = await client.get(base_url, params=params)
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)}")
        
        data = response.json()
        print(f"\n响应结构:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
        
        if data and "result" in data:
            result = data["result"]
            if "data" in result:
                news_count = len(result["data"])
                print(f"\n获取到 {news_count} 条新闻")
                
                if news_count > 0:
                    print(f"\n第一条新闻:")
                    first_news = result["data"][0]
                    print(f"  标题: {first_news.get('title', '')}")
            else:
                print("  响应中没有'data'字段")
        else:
            print("  响应中没有'result'字段")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试3: 尝试不同的API端点
    print("\n测试3: 尝试新浪财经滚动新闻API")
    print("-" * 60)
    
    # 尝试新浪财经的另一个API
    api_url = "https://finance.sina.com.cn/realstock/company/"
    
    try:
        response = await client.get("https://finance.sina.com.cn/7x24/")
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)}")
        
        # 检查是否有新闻数据
        if "7x24" in response.text or "快讯" in response.text:
            print("  响应包含快讯内容")
    except Exception as e:
        print(f"请求失败: {e}")
    
    await client.aclose()
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_sina_api())