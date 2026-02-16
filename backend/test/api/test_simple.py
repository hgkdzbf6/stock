"""
简单的API端点测试
"""
import requests
import json
from typing import Dict, Any

# 基础URL
BASE_URL = "http://localhost:8000"


def print_result(test_name: str, response: requests.Response):
    """打印测试结果"""
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"响应: {response.text}")
    print(f"{'='*60}\n")


def test_health_check():
    """测试健康检查"""
    print("✅ 测试健康检查端点...")
    response = requests.get(f"{BASE_URL}/health")
    print_result("健康检查", response)
    return response.status_code == 200


def test_get_stocks():
    """测试获取股票列表"""
    print("✅ 测试获取股票列表...")
    response = requests.get(f"{BASE_URL}/api/v1/stocks")
    print_result("获取股票列表", response)
    return response.status_code == 200


def test_search_stocks():
    """测试搜索股票"""
    print("✅ 测试搜索股票...")
    response = requests.get(f"{BASE_URL}/api/v1/stocks/search?keyword=600")
    print_result("搜索股票", response)
    return response.status_code == 200


def test_get_stock_detail():
    """测试获取股票详情"""
    print("✅ 测试获取股票详情...")
    response = requests.get(f"{BASE_URL}/api/v1/stocks/600771")
    print_result("获取股票详情", response)
    return response.status_code == 200


def test_get_quote():
    """测试获取实时行情"""
    print("✅ 测试获取实时行情...")
    response = requests.get(f"{BASE_URL}/api/v1/market/quote/600771")
    print_result("获取实时行情", response)
    return response.status_code == 200


def test_get_kline():
    """测试获取K线数据"""
    print("✅ 测试获取K线数据...")
    params = {
        "frequency": "daily",
        "start_date": "2025-01-01",
        "end_date": "2026-02-14"
    }
    response = requests.get(f"{BASE_URL}/api/v1/market/kline/600771", params=params)
    print_result("获取K线数据", response)
    return response.status_code == 200


def test_get_strategies():
    """测试获取策略列表"""
    print("✅ 测试获取策略列表...")
    response = requests.get(f"{BASE_URL}/api/v1/strategies")
    print_result("获取策略列表", response)
    return response.status_code == 200


def test_ai_health_check():
    """测试AI服务健康检查"""
    print("✅ 测试AI服务健康检查...")
    response = requests.get(f"{BASE_URL}/api/v1/ai/health")
    print_result("AI服务健康检查", response)
    return response.status_code == 200


def test_optimization_history():
    """测试获取优化历史"""
    print("✅ 测试获取优化历史...")
    response = requests.get(f"{BASE_URL}/api/v1/optimization/history")
    print_result("获取优化历史", response)
    return response.status_code == 200


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始API端点测试")
    print("="*60 + "\n")
    
    results = {}
    
    # Phase 1 测试
    results["健康检查"] = test_health_check()
    results["获取股票列表"] = test_get_stocks()
    results["搜索股票"] = test_search_stocks()
    results["获取股票详情"] = test_get_stock_detail()
    results["获取实时行情"] = test_get_quote()
    results["获取K线数据"] = test_get_kline()
    results["获取策略列表"] = test_get_strategies()
    
    # Phase 2 测试
    results["AI服务健康检查"] = test_ai_health_check()
    
    # Phase 3 测试
    results["获取优化历史"] = test_optimization_history()
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    print(f"通过率: {passed/total*100:.1f}%")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器")
        print("请确保后端服务正在运行: cd backend && python main.py")
        exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        exit(1)