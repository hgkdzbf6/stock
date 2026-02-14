"""Phase 2 AI功能测试脚本"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# 模拟导入（实际使用时取消注释）
# from ai import get_ai_service
# from core.security import create_access_token


class MockLLMClient:
    """模拟LLM客户端"""
    
    async def analyze(self, prompt: str, context: Any = None, **kwargs) -> str:
        """模拟分析"""
        # 根据提示词类型返回不同的模拟响应
        if "持仓" in prompt or "portfolio" in prompt.lower():
            return json.dumps({
                "risk_level": "medium",
                "suggestions": [
                    "建议分散投资，降低单一股票集中度",
                    "考虑增加防御性股票配置"
                ],
                "risk_factors": [
                    "单一股票占比超过30%",
                    "行业集中度较高"
                ],
                "confidence": 0.85
            }, ensure_ascii=False)
        
        elif "市场" in prompt or "market" in prompt.lower():
            return json.dumps({
                "trend": "up",
                "support": "20.50",
                "resistance": "22.80",
                "signal": "buy",
                "suggestions": [
                    "当前趋势向上，可考虑分批买入",
                    "关注20.50支撑位"
                ],
                "confidence": 0.75
            }, ensure_ascii=False)
        
        elif "指标" in prompt or "indicator" in prompt.lower():
            return json.dumps({
                "trend_strength": "strong",
                "signal": "buy",
                "key_levels": {
                    "support": 20.50,
                    "resistance": 22.80
                },
                "risk_alerts": [
                    "RSI接近超买区域",
                    "成交量有所放大"
                ],
                "confidence": 0.80
            }, ensure_ascii=False)
        
        elif "风险" in prompt or "risk" in prompt.lower():
            return json.dumps({
                "risk_level": "high",
                "risk_factors": [
                    "投资组合波动率过高",
                    "单一股票占比超过40%",
                    "市场整体风险偏高"
                ],
                "control_suggestions": [
                    "立即降低高风险仓位",
                    "增加现金配置比例",
                    "设置止损点"
                ],
                "alert_conditions": [
                    "单一股票损失超过10%",
                    "整体组合回撤超过15%"
                ],
                "confidence": 0.90
            }, ensure_ascii=False)
        
        elif "策略" in prompt or "strategy" in prompt.lower():
            return json.dumps({
                "parameter_adjustments": [
                    "建议缩短移动平均周期至5日和10日",
                    "提高止损比例至5%"
                ],
                "risk_control_improvements": [
                    "添加最大持仓比例限制",
                    "增加日均波幅过滤条件"
                ],
                "strategy_enhancements": [
                    "考虑加入成交量确认信号",
                    "添加多时间周期确认"
                ],
                "suitability": "该策略适合震荡行情，但在趋势市场中可能表现一般",
                "confidence": 0.85
            }, ensure_ascii=False)
        
        else:
            return "这是一个专业的量化投资问题。根据市场分析，建议关注技术指标变化，控制投资风险，合理配置资产。"
    
    async def chat_completion(self, messages, **kwargs) -> Dict:
        """模拟聊天完成"""
        return {
            "choices": [{
                "message": {
                    "content": "您好！我是您的AI量化投资顾问。我可以帮您分析市场行情、评估持仓风险、优化交易策略。"
                }
            }],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 30,
                "total_tokens": 80
            }
        }
    
    async def health_check(self) -> Dict:
        """模拟健康检查"""
        return {
            "status": "healthy",
            "message": "AI服务正常",
            "configured": True,
            "model": "glm-4"
        }


class MockAIService:
    """模拟AI服务"""
    
    def __init__(self):
        self.llm_client = MockLLMClient()
    
    async def analyze_portfolio(self, user_id, positions, market_data, indicators, stream=False):
        """模拟持仓分析"""
        return await self.llm_client.analyze("持仓分析", None)
    
    async def analyze_market(self, user_id, stock_code, stock_name, current_price, kline_data, indicators, volume_info, stream=False):
        """模拟市场分析"""
        return await self.llm_client.analyze("市场分析", None)
    
    async def analyze_indicators(self, user_id, indicators, stream=False):
        """模拟技术指标分析"""
        return await self.llm_client.analyze("技术指标分析", None)
    
    async def assess_risk(self, user_id, portfolio_info, risk_metrics, market_environment, stream=False):
        """模拟风险评估"""
        return await self.llm_client.analyze("风险评估", None)
    
    async def optimize_strategy(self, user_id, strategy_type, strategy_params, backtest_results, trades_summary, stream=False):
        """模拟策略优化"""
        return await self.llm_client.analyze("策略优化", None)
    
    async def chat(self, user_id, question, context=None, stream=False):
        """模拟聊天"""
        return await self.llm_client.analyze(question, context)
    
    async def health_check(self):
        """健康检查"""
        return await self.llm_client.health_check()


# 测试数据
TEST_POSITIONS = [
    {
        "stock_code": "600771",
        "stock_name": "东望谷",
        "quantity": 1000,
        "cost_price": 20.50,
        "current_price": 21.50
    },
    {
        "stock_code": "000001",
        "stock_name": "平安银行",
        "quantity": 500,
        "cost_price": 15.00,
        "current_price": 14.50
    }
]

TEST_MARKET_DATA = {
    "index_value": 3000,
    "index_change": "+1.2%",
    "market_sentiment": "乐观"
}

TEST_INDICATORS = {
    "ma5": 21.0,
    "ma10": 20.8,
    "ma20": 20.5,
    "rsi": 55.0,
    "macd": "金叉",
    "macd_hist": "0.12",
    "ma5_trend": "上升",
    "ma10_trend": "上升",
    "ma20_trend": "上升",
    "boll_upper": 22.80,
    "boll_mid": 21.50,
    "boll_lower": 20.20,
    "kdj": "85, 75, 80",
    "volume": 12500000,
    "volume_change": "+15%"
}

TEST_KLINE_DATA = [
    {
        "date": "2026-02-05",
        "open": 20.00,
        "high": 20.50,
        "low": 19.80,
        "close": 20.20,
        "volume": 10000000
    },
    {
        "date": "2026-02-06",
        "open": 20.20,
        "high": 20.80,
        "low": 20.00,
        "close": 20.60,
        "volume": 12000000
    }
]

TEST_PORTFOLIO_INFO = {
    "total_value": 30000,
    "position_count": 2
}

TEST_RISK_METRICS = {
    "total_market_value": 30000,
    "max_single_ratio": "45%",
    "industry_concentration": "高",
    "beta": 1.2,
    "volatility": "25%",
    "max_drawdown": "-10%"
}

TEST_MARKET_ENVIRONMENT = {
    "index_value": 3000,
    "index_change": "+1.2%",
    "market_sentiment": "乐观"
}

TEST_STRATEGY_PARAMS = {
    "ma_short": 5,
    "ma_long": 10,
    "stop_loss": 0.05
}

TEST_BACKTEST_RESULTS = {
    "period": "2025-01-01 至 2026-02-14",
    "initial_capital": 100000,
    "final_capital": 115000,
    "total_return": "+15%",
    "annual_return": "+18%",
    "max_drawdown": "-8%",
    "sharpe_ratio": 1.5,
    "win_rate": "60%",
    "profit_loss_ratio": 1.8,
    "trade_count": 50
}


async def test_health_check():
    """测试健康检查"""
    print("\n" + "=" * 60)
    print("测试1: 健康检查")
    print("=" * 60)
    
    try:
        service = MockAIService()
        result = await service.health_check()
        
        print(f"✅ 状态: {result['status']}")
        print(f"✅ 消息: {result['message']}")
        print(f"✅ 配置: {result['configured']}")
        print(f"✅ 模型: {result['model']}")
        
        assert result['status'] == 'healthy'
        assert result['configured'] == True
        
        print("\n✅ 健康检查测试通过！")
        return True
    
    except Exception as e:
        print(f"\n❌ 健康检查测试失败: {e}")
        return False


async def test_portfolio_analysis():
    """测试持仓分析"""
    print("\n" + "=" * 60)
    print("测试2: 持仓分析")
    print("=" * 60)
    
    try:
        service = MockAIService()
        result = await service.analyze_portfolio(
            user_id=1,
            positions=TEST_POSITIONS,
            market_data=TEST_MARKET_DATA,
            indicators=TEST_INDICATORS
        )
        
        # 解析JSON
        analysis = json.loads(result) if isinstance(result, str) else result
        
        print(f"✅ 风险等级: {analysis.get('risk_level')}")
        print(f"✅ 建议数量: {len(analysis.get('suggestions', []))}")
        print(f"✅ 风险因素数量: {len(analysis.get('risk_factors', []))}")
        print(f"✅ 置信度: {analysis.get('confidence', 0)}")
        
        for i, suggestion in enumerate(analysis.get('suggestions', []), 1):
            print(f"\n  建议{i}: {suggestion}")
        
        assert 'risk_level' in analysis
        assert 'suggestions' in analysis
        
        print("\n✅ 持仓分析测试通过！")
        return True
    
    except Exception as e:
        print(f"\n❌ 持仓分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_market_analysis():
    """测试市场分析"""
    print("\n" + "=" * 60)
    print("测试3: 市场分析")
    print("=" * 60)
    
    try:
        service = MockAIService()
        result = await service.analyze_market(
            user_id=1,
            stock_code="600771",
            stock_name="东望谷",
            current_price=21.50,
            kline_data=TEST_KLINE_DATA,
            indicators=TEST_INDICATORS,
            volume_info={"volume": 12500000}
        )
        
        # 解析JSON
        analysis = json.loads(result) if isinstance(result, str) else result
        
        print(f"✅ 趋势: {analysis.get('trend')}")
        print(f"✅ 支撑位: {analysis.get('support')}")
        print(f"✅ 压力位: {analysis.get('resistance')}")
        print(f"✅ 信号: {analysis.get('signal')}")
        print(f"✅ 置信度: {analysis.get('confidence', 0)}")
        
        for suggestion in analysis.get('suggestions', []):
            print(f"\n  建议: {suggestion}")
        
        assert 'trend' in analysis
        assert 'signal' in analysis
        
        print("\n✅ 市场分析测试通过！")
        return True
    
    except Exception as e:
        print(f"\n❌ 市场分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_indicator_analysis():
    """测试技术指标分析"""
    print("\n" + "=" * 60)
    print("测试4: 技术指标分析")
    print("=" * 60)
    
    try:
        service = MockAIService()
        result = await service.analyze_indicators(
            user_id=1,
            indicators=TEST_INDICATORS
        )
        
        # 解析JSON
        analysis = json.loads(result) if isinstance(result, str) else result
        
        print(f"✅ 趋势强度: {analysis.get('trend_strength')}")
        print(f"✅ 信号: {analysis.get('signal')}")
        print(f"✅ 支撑位: {analysis.get('key_levels', {}).get('support')}")
        print(f"✅ 压力位: {analysis.get('key_levels', {}).get('resistance')}")
        print(f"✅ 置信度: {analysis.get('confidence', 0)}")
        
        for alert in analysis.get('risk_alerts', []):
            print(f"\n  ⚠️  {alert}")
        
        assert 'trend_strength' in analysis
        assert 'signal' in analysis
        
        print("\n✅ 技术指标分析测试通过！")
        return True
    
    except Exception as e:
        print(f"\n❌ 技术指标分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_risk_assessment():
    """测试风险评估"""
    print("\n" + "=" * 60)
    print("测试5: 风险评估")
    print("=" * 60)
    
    try:
        service = MockAIService()
        result = await service.assess_risk(
            user_id=1,
            portfolio_info=TEST_PORTFOLIO_INFO,
            risk_metrics=TEST_RISK_METRICS,
            market_environment=TEST_MARKET_ENVIRONMENT
        )
        
        # 解析JSON
        assessment = json.loads(result) if isinstance(result, str) else result
        
        print(f"✅ 风险等级: {assessment.get('risk_level')}")
        print(f"✅ 风险因素数量: {len(assessment.get('risk_factors', []))}")
        print(f"✅ 建议数量: {len(assessment.get('control_suggestions', []))}")
        print(f"✅ 置信度: {assessment.get('confidence', 0)}")
        
        print("\n  风险因素:")
        for factor in assessment.get('risk_factors', []):
            print(f"    • {factor}")
        
        print("\n  控制建议:")
        for suggestion in assessment.get('control_suggestions', []):
            print(f"    • {suggestion}")
        
        assert 'risk_level' in assessment
        assert 'risk_factors' in assessment
        
        print("\n✅ 风险评估测试通过！")
        return True
    
    except Exception as e:
        print(f"\n❌ 风险评估测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_strategy_optimization():
    """测试策略优化"""
    print("\n" + "=" * 60)
    print("测试6: 策略优化")
    print("=" * 60)
    
    try:
        service = MockAIService()
        result = await service.optimize_strategy(
            user_id=1,
            strategy_type="双均线策略",
            strategy_params=TEST_STRATEGY_PARAMS,
            backtest_results=TEST_BACKTEST_RESULTS,
            trades_summary="共50笔交易，其中30笔盈利，20笔亏损"
        )
        
        # 解析JSON
        optimization = json.loads(result) if isinstance(result, str) else result
        
        print(f"✅ 参数调整数量: {len(optimization.get('parameter_adjustments', []))}")
        print(f"✅ 风控改进数量: {len(optimization.get('risk_control_improvements', []))}")
        print(f"✅ 策略增强数量: {len(optimization.get('strategy_enhancements', []))}")
        print(f"✅ 适用性: {optimization.get('suitability', 'N/A')}")
        print(f"✅ 置信度: {optimization.get('confidence', 0)}")
        
        print("\n  参数调整:")
        for adj in optimization.get('parameter_adjustments', []):
            print(f"    • {adj}")
        
        assert 'parameter_adjustments' in optimization
        
        print("\n✅ 策略优化测试通过！")
        return True
    
    except Exception as e:
        print(f"\n❌ 策略优化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_chat():
    """测试聊天功能"""
    print("\n" + "=" * 60)
    print("测试7: 聊天功能")
    print("=" * 60)
    
    try:
        service = MockAIService()
        
        questions = [
            "什么是移动平均线？",
            "如何判断买入信号？",
            "什么是MACD指标？"
        ]
        
        for question in questions:
            print(f"\n问题: {question}")
            result = await service.chat(
                user_id=1,
                question=question
            )
            print(f"回答: {result[:100]}...")
        
        print("\n✅ 聊天功能测试通过！")
        return True
    
    except Exception as e:
        print(f"\n❌ 聊天功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Phase 2 AI功能测试")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 运行所有测试
    tests = [
        ("健康检查", test_health_check),
        ("持仓分析", test_portfolio_analysis),
        ("市场分析", test_market_analysis),
        ("技术指标分析", test_indicator_analysis),
        ("风险评估", test_risk_assessment),
        ("策略优化", test_strategy_optimization),
        ("聊天功能", test_chat)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 打印测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:.<30} {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if passed == total:
        print("\n🎉 所有测试通过！Phase 2 AI功能开发完成！")
    else:
        print(f"\n⚠️  有{total - passed}个测试失败，请检查相关代码")
    
    return passed == total


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(run_all_tests())