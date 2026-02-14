#!/usr/bin/env python3
"""
前后端集成测试脚本
测试所有主要API端点和功能
"""
import requests
import json
import time
import sys
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # 30秒超时

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def test_endpoint(method, path, data=None, description=""):
    """测试API端点"""
    url = f"{BASE_URL}{path}"
    print_info(f"测试: {description or path}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=TIMEOUT)
        elif method == "DELETE":
            response = requests.delete(url, timeout=TIMEOUT)
        
        if response.status_code < 400:
            print_success(f"{description or path} - 状态码: {response.status_code}")
            return True, response.json()
        else:
            print_error(f"{description or path} - 状态码: {response.status_code}")
            return False, None
    except requests.exceptions.Timeout:
        print_error(f"{description or path} - 请求超时 ({TIMEOUT}秒)")
        return False, None
    except requests.exceptions.ConnectionError:
        print_error(f"{description or path} - 连接失败，服务未启动")
        return False, None
    except Exception as e:
        print_error(f"{description or path} - 错误: {str(e)}")
        return False, None

def main():
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"前后端集成测试")
    print(f"{'='*60}{Colors.END}\n")
    
    print_info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"后端地址: {BASE_URL}")
    print_info(f"超时设置: {TIMEOUT}秒\n")
    
    # 测试结果统计
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    # 1. 健康检查
    print(f"\n{Colors.BOLD}1. 健康检查{Colors.END}")
    success, data = test_endpoint("GET", "/health", description="健康检查端点")
    results['total'] += 1
    if success:
        results['passed'] += 1
        results['tests'].append(('健康检查', 'PASS'))
        print(f"  - 应用名称: {data.get('app_name', 'N/A')}")
        print(f"  - 版本: {data.get('version', 'N/A')}")
    else:
        results['failed'] += 1
        results['tests'].append(('健康检查', 'FAIL'))
        print_warning("健康检查失败，后端服务可能未正常启动")
        return
    
    # 2. 股票列表
    print(f"\n{Colors.BOLD}2. 股票数据API{Colors.END}")
    success, data = test_endpoint("GET", "/api/v1/stocks/?page=1&page_size=5", description="获取股票列表")
    results['total'] += 1
    if success and data:
        results['passed'] += 1
        results['tests'].append(('股票列表', 'PASS'))
        print(f"  - 获取到 {len(data.get('data', []))} 只股票")
    else:
        results['failed'] += 1
        results['tests'].append(('股票列表', 'FAIL'))
    
    # 3. 市场概览
    print(f"\n{Colors.BOLD}3. 市场数据API{Colors.END}")
    success, data = test_endpoint("GET", "/api/v1/market/overview", description="市场概览")
    results['total'] += 1
    if success and data:
        results['passed'] += 1
        results['tests'].append(('市场概览', 'PASS'))
    else:
        results['failed'] += 1
        results['tests'].append(('市场概览', 'FAIL'))
    
    # 4. 策略列表
    print(f"\n{Colors.BOLD}4. 策略回测API{Colors.END}")
    success, data = test_endpoint("GET", "/api/v1/strategies/", description="获取策略列表")
    results['total'] += 1
    if success and data:
        results['passed'] += 1
        results['tests'].append(('策略列表', 'PASS'))
        strategies = data.get('data', [])
        print(f"  - 获取到 {len(strategies)} 个策略")
    else:
        results['failed'] += 1
        results['tests'].append(('策略列表', 'FAIL'))
    
    # 5. 执行回测
    if success and strategies:
        print_info("执行策略回测...")
        strategy_id = strategies[0].get('id', 1)
        backtest_data = {
            "stock_code": "600771",
            "start_date": "2025-08-14",
            "end_date": "2026-02-14",
            "frequency": "daily",
            "initial_capital": 100000,
            "strategy_type": "MA",
            "custom_params": {
                "short_window": 5,
                "long_window": 20
            }
        }
        success, data = test_endpoint("POST", f"/api/v1/strategies/{strategy_id}/backtest", 
                                  backtest_data, description="执行回测")
        results['total'] += 1
        if success and data:
            results['passed'] += 1
            results['tests'].append(('执行回测', 'PASS'))
            metrics = data.get('data', {}).get('metrics', {})
            print(f"  - 总收益率: {metrics.get('total_return', 0)*100:.2f}%")
            print(f"  - 交易次数: {metrics.get('trade_count', 0)}")
            print(f"  - 胜率: {metrics.get('win_rate', 0)*100:.2f}%")
        else:
            results['failed'] += 1
            results['tests'].append(('执行回测', 'FAIL'))
    
    # 6. API文档
    print(f"\n{Colors.BOLD}5. API文档{Colors.END}")
    success, _ = test_endpoint("GET", "/docs", description="Swagger文档")
    results['total'] += 1
    if success:
        results['passed'] += 1
        results['tests'].append(('API文档', 'PASS'))
    else:
        results['failed'] += 1
        results['tests'].append(('API文档', 'FAIL'))
    
    # 测试结果汇总
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"测试结果汇总")
    print(f"{'='*60}{Colors.END}\n")
    
    print(f"总测试数: {results['total']}")
    print(f"{Colors.GREEN}通过: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}失败: {results['failed']}{Colors.END}")
    pass_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"通过率: {pass_rate:.1f}%\n")
    
    print(f"{Colors.BOLD}详细测试结果:{Colors.END}")
    for test_name, result in results['tests']:
        if result == 'PASS':
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}{'='*60}\n")
    
    # 返回退出码
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\n测试被用户中断")
        sys.exit(1)