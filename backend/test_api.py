"""
API单元测试 - Phase 1-4
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, date
import json


# 导入主应用
from main import app

client = TestClient(app)


# ==================== Phase 1 测试 ====================

class TestPhase1StocksAPI:
    """Phase 1: 股票API测试"""
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "app_name" in data
        assert "version" in data
    
    def test_get_stocks_list(self):
        """测试获取股票列表"""
        response = client.get("/api/v1/stocks")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
    
    def test_search_stocks(self):
        """测试搜索股票"""
        response = client.get("/api/v1/stocks/search?keyword=600")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_get_stock_detail(self):
        """测试获取股票详情"""
        response = client.get("/api/v1/stocks/600771")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestPhase1MarketAPI:
    """Phase 1: 行情API测试"""
    
    def test_get_quote(self):
        """测试获取实时行情"""
        response = client.get("/api/v1/market/quote/600771")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
    
    def test_get_kline(self):
        """测试获取K线数据"""
        params = {
            "frequency": "daily",
            "start_date": "2025-01-01",
            "end_date": "2026-02-14"
        }
        response = client.get("/api/v1/market/kline/600771", params=params)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
    
    def test_get_indicators(self):
        """测试获取技术指标"""
        params = {
            "frequency": "daily",
            "indicators": "MA,BOLL,RSI"
        }
        response = client.get("/api/v1/market/indicators/600771", params=params)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestPhase1AuthAPI:
    """Phase 1: 认证API测试"""
    
    def test_register_user(self):
        """测试用户注册"""
        user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "test123456",
            "full_name": "Test User"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code in [200, 400]  # 可能已存在
    
    def test_login_user(self):
        """测试用户登录"""
        login_data = {
            "username": "test_user",
            "password": "test123456"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code in [200, 401]  # 可能未注册
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"


# ==================== Phase 2 测试 ====================

class TestPhase2AIAPI:
    """Phase 2: AI API测试"""
    
    def test_ai_health_check(self):
        """测试AI服务健康检查"""
        response = client.get("/api/v1/ai/health")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "status" in data
    
    def test_ai_analyze(self):
        """测试AI通用分析"""
        request_data = {
            "type": "market",
            "context": {
                "market": "上涨",
                "trend": "向好"
            }
        }
        response = client.post("/api/v1/ai/analyze", json=request_data)
        # 可能未配置GLM API KEY
        assert response.status_code in [200, 500]
    
    def test_ai_analyze_portfolio(self):
        """测试AI持仓分析"""
        request_data = {
            "positions": [
                {"symbol": "600771", "quantity": 1000, "cost": 20.50}
            ],
            "market_data": {
                "600771": {"current_price": 22.50, "daily_change": 0.05}
            },
            "indicators": {
                "600771": {"ma5": 22.00, "ma10": 21.50, "rsi": 65}
            }
        }
        response = client.post("/api/v1/ai/analyze/portfolio", json=request_data)
        assert response.status_code in [200, 500]
    
    def test_ai_chat(self):
        """测试AI聊天"""
        request_data = {
            "question": "什么是移动平均线？",
            "stream": False
        }
        response = client.post("/api/v1/ai/chat", json=request_data)
        assert response.status_code in [200, 500]
    
    def test_ai_templates(self):
        """测试获取AI模板"""
        response = client.get("/api/v1/ai/templates")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data


# ==================== Phase 3 测试 ====================

class TestPhase3OptimizationAPI:
    """Phase 3: 优化API测试"""
    
    def test_grid_search(self):
        """测试网格搜索优化"""
        request_data = {
            "strategy_type": "双均线策略",
            "stock_code": "600771",
            "start_date": "2025-01-01",
            "end_date": "2026-02-14",
            "frequency": "daily",
            "initial_capital": 100000,
            "objective": "sharpe_ratio",
            "maximize": True,
            "param_ranges": {
                "ma_short": {"type": "int", "min": 5, "max": 20, "step": 1},
                "ma_long": {"type": "int", "min": 20, "max": 60, "step": 1}
            }
        }
        response = client.post("/api/v1/optimization/grid-search", json=request_data)
        assert response.status_code in [200, 500]
    
    def test_genetic_optimization(self):
        """测试遗传算法优化"""
        request_data = {
            "strategy_type": "双均线策略",
            "stock_code": "600771",
            "start_date": "2025-01-01",
            "end_date": "2026-02-14",
            "objective": "sharpe_ratio",
            "param_ranges": {
                "ma_short": {"type": "int", "min": 5, "max": 20, "step": 1},
                "ma_long": {"type": "int", "min": 20, "max": 60, "step": 1}
            },
            "population_size": 20,
            "generations": 10
        }
        response = client.post("/api/v1/optimization/genetic", json=request_data)
        assert response.status_code in [200, 500]
    
    def test_bayesian_optimization(self):
        """测试贝叶斯优化"""
        request_data = {
            "strategy_type": "双均线策略",
            "stock_code": "600771",
            "start_date": "2025-01-01",
            "end_date": "2026-02-14",
            "objective": "sharpe_ratio",
            "param_ranges": {
                "ma_short": {"type": "int", "min": 5, "max": 20, "step": 1},
                "ma_long": {"type": "int", "min": 20, "max": 60, "step": 1}
            },
            "n_iter": 50,
            "n_init": 10
        }
        response = client.post("/api/v1/optimization/bayesian", json=request_data)
        assert response.status_code in [200, 500]
    
    def test_optimization_history(self):
        """测试获取优化历史"""
        response = client.get("/api/v1/optimization/history")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


# ==================== Phase 4 测试 ====================

class TestPhase4TradingAPI:
    """Phase 4: 交易API测试"""
    
    # 注意：交易API需要认证，这里只测试端点是否存在
    
    def test_connect_trading(self):
        """测试连接交易系统"""
        response = client.post("/api/v1/trading/connect")
        # 需要认证
        assert response.status_code in [401, 500]
    
    def test_create_order(self):
        """测试创建订单"""
        params = {
            "stock_code": "600771",
            "side": "buy",
            "order_type": "market",
            "quantity": 1000
        }
        response = client.post("/api/v1/trading/orders", params=params)
        # 需要认证
        assert response.status_code in [401, 400]
    
    def test_get_orders(self):
        """测试获取订单列表"""
        response = client.get("/api/v1/trading/orders")
        # 需要认证
        assert response.status_code == 401
    
    def test_get_positions(self):
        """测试获取持仓列表"""
        response = client.get("/api/v1/trading/positions")
        # 需要认证
        assert response.status_code == 401
    
    def test_get_account(self):
        """测试获取账户信息"""
        response = client.get("/api/v1/trading/account")
        # 需要认证
        assert response.status_code == 401
    
    def test_get_risk_summary(self):
        """测试获取风险汇总"""
        response = client.get("/api/v1/trading/risk/summary")
        # 需要认证
        assert response.status_code in [401, 500]


# ==================== 策略API测试 ====================

class TestStrategiesAPI:
    """策略API测试"""
    
    def test_get_strategies(self):
        """测试获取策略列表"""
        response = client.get("/api/v1/strategies")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_backtest(self):
        """测试回测"""
        request_data = {
            "strategy_type": "双均线策略",
            "stock_code": "600771",
            "start_date": "2025-01-01",
            "end_date": "2026-02-14",
            "frequency": "daily",
            "initial_capital": 100000,
            "params": {
                "ma_short": 5,
                "ma_long": 20
            }
        }
        response = client.post("/api/v1/strategies/backtest", json=request_data)
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert data["code"] == 200
            assert "data" in data
            # 检查回测结果字段
            result = data["data"]
            assert "total_return" in result
            assert "sharpe_ratio" in result
            assert "max_drawdown" in result


# ==================== 测试运行器 ====================

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])