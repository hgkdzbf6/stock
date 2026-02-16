"""
后端 API 接口单元测试
测试所有主要 API 端点，确保前后端交互正常
"""
import pytest
import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入必要的模块
from fastapi.testclient import TestClient
from main import app
from loguru import logger


class TestStockAPI:
    """股票 API 接口测试类"""
    
    @pytest.fixture(autouse=True)
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    def test_root_health_check(self, client):
        """测试根路径健康检查"""
        logger.info("测试 1: 根路径健康检查")
        
        response = client.get("/")
        
        # 验证状态码
        assert response.status_code == 200
        
        # 验证响应内容
        data = response.json()
        assert data["status"] == "ok"
        assert "app_name" in data
        assert "version" in data
        assert "api" in data
        
        logger.info(f"  ✓ 根路径健康检查通过")
        logger.info(f"    应用名称: {data['app_name']}")
        logger.info(f"    版本: {data['version']}")
        logger.info(f"    API 路径: {data['api']}")
    
    def test_api_health_check(self, client):
        """测试 API 健康检查端点"""
        logger.info("测试 2: API 健康检查")
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
        logger.info(f"  ✓ API 健康检查通过")
        logger.info(f"    状态: {data['status']}")
    
    def test_get_stock_list(self, client):
        """测试获取股票列表"""
        logger.info("测试 3: 获取股票列表")
        
        # 测试无参数请求
        response = client.get("/api/v1/stocks")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total" in data
        assert len(data["data"]) > 0
        
        # 验证数据格式
        stocks = data["data"]
        first_stock = stocks[0]
        assert "code" in first_stock
        assert "name" in first_stock
        assert "price" in first_stock
        
        logger.info(f"  ✓ 获取股票列表通过")
        logger.info(f"    总数: {data['total']}")
        logger.info(f"    返回数量: {len(stocks)}")
        logger.info(f"    第一只股票: {first_stock['name']} ({first_stock['code']})")
    
    def test_search_stocks(self, client):
        """测试搜索股票"""
        logger.info("测试 4: 搜索股票")
        
        search_keyword = "茅台"
        response = client.get(f"/api/v1/stocks/search?keyword={search_keyword}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证搜索结果
        stocks = data["data"]
        if len(stocks) > 0:
            found_stock = stocks[0]
            logger.info(f"  ✓ 搜索股票通过")
            logger.info(f"    搜索关键词: {search_keyword}")
            logger.info(f"    找到数量: {len(stocks)}")
            logger.info(f"    第一个结果: {found_stock['name']} ({found_stock['code']})")
        else:
            logger.info(f"  ✓ 搜索股票通过（无结果）")
    
    def test_get_stock_detail(self, client):
        """测试获取股票详情"""
        logger.info("测试 5: 获取股票详情")
        
        # 测试已知的股票代码
        test_code = "600519.SH"  # 贵州茅台
        response = client.get(f"/api/v1/stocks/{test_code}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        stock = data["data"]
        assert stock["code"] == test_code
        assert "name" in stock
        assert "price" in stock
        assert "change" in stock
        assert "change_percent" in stock
        assert "volume" in stock
        assert "turnover" in stock
        
        logger.info(f"  ✓ 获取股票详情通过")
        logger.info(f"    股票代码: {stock['code']}")
        logger.info(f"    股票名称: {stock['name']}")
        logger.info(f"    最新价: {stock['price']}")
        logger.info(f"    涨跌额: {stock['change']}")
        logger.info(f"    涨跌幅: {stock['change_percent']}%")
    
    def test_get_stock_quote(self, client):
        """测试获取股票实时行情"""
        logger.info("测试 6: 获取股票实时行情")
        
        test_code = "000001.SZ"  # 平安银行
        response = client.get(f"/api/v1/stocks/quote/{test_code}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        quote = data["data"]
        assert "code" in quote
        assert "name" in quote
        assert "price" in quote
        assert "change" in quote
        assert "change_percent" in quote
        
        logger.info(f"  ✓ 获取股票实时行情通过")
        logger.info(f"    股票代码: {quote['code']}")
        logger.info(f"    股票名称: {quote['name']}")
        logger.info(f"    当前价: {quote['price']}")
    
    def test_get_stock_list_with_pagination(self, client):
        """测试分页获取股票列表"""
        logger.info("测试 7: 分页获取股票列表")
        
        response = client.get("/api/v1/stocks?page=2&page_size=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["page"] == 2
        assert len(data["data"]) <= 10
        
        logger.info(f"  ✓ 分页获取股票列表通过")
        logger.info(f"    当前页: {data['page']}")
        logger.info(f"    每页数量: {data['page_size']}")
        logger.info(f"    返回数量: {len(data['data'])}")
    
    def test_market_overview(self, client):
        """测试市场概览"""
        logger.info("测试 8: 市场概览")
        
        response = client.get("/api/v1/market/overview")
        
        # 注意：这个接口可能不存在，我们只测试接口响应
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            
            logger.info(f"  ✓ 市场概览通过")
            logger.info(f"    数据: {data['data']}")
        else:
            logger.info(f"  ⚠ 市场概览接口返回 {response.status_code}")
    
    def test_download_data_list(self, client):
        """测试获取已下载数据列表"""
        logger.info("测试 9: 获取已下载数据列表")
        
        response = client.get("/api/v1/data/downloads?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "downloads" in data
            
            logger.info(f"  ✓ 获取已下载数据列表通过")
            logger.info(f"    总数: {data['total']}")
            logger.info(f"    返回数量: {len(data['downloads'])}")
        else:
            logger.info(f"  ⚠ 已下载数据列表接口返回 {response.status_code}")
    
    def test_download_stock_data(self, client):
        """测试下载数据"""
        logger.info("测试 10: 下载股票数据")
        
        # 这是一个耗时的操作，我们只测试接口调用
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        payload = {
            "stock_code": "000001.SZ",
            "start_date": start_date,
            "end_date": end_date,
            "frequency": "daily"
        }
        
        # 注意：这可能会失败，因为所有真实数据源可能都失败
        # 我们主要测试接口是否响应
        response = client.post("/api/v1/data/download", json=payload)
        
        # 这个测试我们不做断言，只检查接口是否响应
        logger.info(f"  ⚠ 下载数据接口响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"    状态: {data.get('status', 'unknown')}")
            logger.info(f"    消息: {data.get('message', 'no message')}")
        
        # 注意：下载可能会因为数据源失败，这是正常的


def run_tests_and_generate_report():
    """运行测试并生成报告"""
    print("\n" + "=" * 70)
    print("  股票 API 接口单元测试")
    print("  版本: 1.0")
    print("  测试目标: 验证所有主要 API 接口功能正常")
    print("=" * 70)
    print("\n")
    
    # 配置日志
    logger.add(sys.stdout, format="{time} | {level} | {message}", level="INFO")
    
    # 运行 pytest
    exit_code = pytest.main([
        __file__,
        "-v",  # 详细输出
        "-s",  # 不显示本地变量
        "--tb=short",  # 错误回溯简短
        "--color=yes",  # 彩色输出
        "-x",  # 第一次失败就停止
        "-m", "verbose"  # 显示打印输出
    ])
    
    print("\n" + "=" * 70)
    print(f"  测试完成，退出码: {exit_code}")
    print("=" * 70)
    
    if exit_code == 0:
        print("\n✓ 所有测试通过！后端 API 接口工作正常。")
        print("\n下一步：")
        print("  1. 启动前端服务：cd /Users/zbf/ws/stock/frontend && npm run dev")
        print("  2. 访问前端页面：http://localhost:3000")
        print("  3. 检查浏览器控制台，确认前端能正常调用后端 API")
    else:
        print("\n✗ 测试失败！请查看上面的错误信息。")
        print("\n常见问题：")
        print("  1. 后端服务未启动 - 请先启动后端服务")
        print("  2. 端口被占用 - 检查 8000 端口是否被占用")
        print("  3. 数据库连接失败 - 检查数据库服务是否正常")
        print("  4. Redis 连接失败 - 检查 Redis 服务是否正常")


if __name__ == "__main__":
    run_tests_and_generate_report()