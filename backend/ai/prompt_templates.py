"""提示词模板系统"""
from typing import Dict, Any, List, Optional


class PromptTemplates:
    """提示词模板类"""
    
    # ==================== 持仓分析 ====================
    
    PORTFOLIO_ANALYSIS = """
你是一个专业的量化投资顾问。请分析以下持仓数据：

## 持仓信息
{position_info}

## 市场环境
{market_info}

## 技术指标
{indicators}

请提供以下分析：

1. **整体风险评估**（低/中/高）
2. **持仓配置建议**
3. **风险控制建议**
4. **优化建议**

请以JSON格式返回，包含以下字段：
```json
{{
  "risk_level": "风险等级（low/medium/high）",
  "suggestions": [
    "建议1",
    "建议2"
  ],
  "risk_factors": [
    "风险因素1",
    "风险因素2"
  ],
  "confidence": 0.85
}}
```
"""
    
    # ==================== 市场行情分析 ====================
    
    MARKET_ANALYSIS = """
你是一个专业的市场分析师。请分析以下股票的市场行情：

## 股票基本信息
股票代码: {stock_code}
股票名称: {stock_name}
当前价格: {current_price}

## K线数据（最近10天）
{kline_data}

## 技术指标
- MA5: {ma5}
- MA10: {ma10}
- MA20: {ma20}
- RSI: {rsi}
- MACD: {macd}

## 成交量
{volume_info}

请提供以下分析：

1. **趋势判断**（上涨/下跌/震荡）
2. **支撑位和压力位**
3. **买卖信号**
4. **操作建议**

请以JSON格式返回：
```json
{{
  "trend": "趋势（up/down/sideways）",
  "support": "支撑位价格",
  "resistance": "压力位价格",
  "signal": "信号（buy/sell/hold）",
  "suggestions": [
    "建议1",
    "建议2"
  ],
  "confidence": 0.75
}}
```
"""
    
    # ==================== 技术指标分析 ====================
    
    INDICATOR_ANALYSIS = """
你是一个专业的技术分析专家。请综合分析以下技术指标：

## 趋势指标
- MA5: {ma5}（{ma5_trend}）
- MA10: {ma10}（{ma10_trend}）
- MA20: {ma20}（{ma20_trend}）

## 动量指标
- RSI: {rsi}
- MACD金叉/死叉: {macd_signal}
- MACD柱状图: {macd_hist}

## 波动指标
- 布林带上轨: {boll_upper}
- 布林带中轨: {boll_mid}
- 布林带下轨: {boll_lower}
- KDJ: {kdj}

## 成交量指标
- 成交量: {volume}
- 成交量变化: {volume_change}

请综合以上指标，提供：

1. **趋势强度**（强/中/弱）
2. **买卖信号**（强烈买入/买入/持有/卖出/强烈卖出）
3. **关键点位**
4. **风险提示**

请以JSON格式返回：
```json
{{
  "trend_strength": "趋势强度（strong/medium/weak）",
  "signal": "交易信号（strong_buy/buy/hold/sell/strong_sell）",
  "key_levels": {{
    "support": "支撑位",
    "resistance": "压力位"
  }},
  "risk_alerts": [
    "风险提示1",
    "风险提示2"
  ],
  "confidence": 0.80
}}
```
"""
    
    # ==================== 风险评估 ====================
    
    RISK_ASSESSMENT = """
你是一个专业的风险控制专家。请评估以下投资组合的风险：

## 持仓信息
{portfolio_info}

## 风险指标
- 总市值: {total_market_value}
- 单一股票最大占比: {max_single_ratio}
- 行业集中度: {industry_concentration}
- Beta系数: {beta}
- 波动率: {volatility}
- 最大回撤: {max_drawdown}

## 市场环境
- 大盘指数: {index_value}
- 大盘涨跌: {index_change}
- 市场情绪: {market_sentiment}

请提供以下风险评估：

1. **整体风险等级**（低/中/高）
2. **主要风险因素**
3. **风险控制建议**
4. **预警条件**

请以JSON格式返回：
```json
{{
  "risk_level": "风险等级（low/medium/high）",
  "risk_factors": [
    "风险因素1",
    "风险因素2"
  ],
  "control_suggestions": [
    "风控建议1",
    "风控建议2"
  ],
  "alert_conditions": [
    "预警条件1",
    "预警条件2"
  ],
  "confidence": 0.90
}}
```
"""
    
    # ==================== 策略优化建议 ====================
    
    STRATEGY_OPTIMIZATION = """
你是一个专业的策略优化专家。请分析以下策略的回测结果，提供优化建议：

## 策略信息
策略类型: {strategy_type}
策略参数: {strategy_params}

## 回测结果
- 回测期间: {backtest_period}
- 初始资金: {initial_capital}
- 最终资金: {final_capital}
- 总收益率: {total_return}
- 年化收益率: {annual_return}
- 最大回撤: {max_drawdown}
- 夏普比率: {sharpe_ratio}
- 胜率: {win_rate}
- 盈亏比: {profit_loss_ratio}
- 交易次数: {trade_count}

## 交易明细
{trades_summary}

请提供以下优化建议：

1. **参数调整建议**
2. **风险控制改进**
3. **策略增强建议**
4. **适用性分析**

请以JSON格式返回：
```json
{{
  "parameter_adjustments": [
    "参数调整建议1",
    "参数调整建议2"
  ],
  "risk_control_improvements": [
    "风控改进建议1",
    "风控改进建议2"
  ],
  "strategy_enhancements": [
    "策略增强建议1",
    "策略增强建议2"
  ],
  "suitability": "适用性分析",
  "confidence": 0.85
}}
```
"""
    
    # ==================== 快速问答 ====================
    
    QUICK_QUESTION = """
用户提问: {question}

上下文信息:
{context}

请简洁明了地回答用户的问题，控制在200字以内。
如果涉及具体股票或策略，请提供具体的建议。
"""
    
    # ==================== 工具方法 ====================
    
    @classmethod
    def format_portfolio_analysis(
        cls,
        positions: List[Dict[str, Any]],
        market_data: Dict[str, Any],
        indicators: Dict[str, Any]
    ) -> str:
        """格式化持仓分析提示词"""
        return cls.PORTFOLIO_ANALYSIS.format(
            position_info=cls._format_dict(positions),
            market_info=cls._format_dict(market_data),
            indicators=cls._format_dict(indicators)
        )
    
    @classmethod
    def format_market_analysis(
        cls,
        stock_code: str,
        stock_name: str,
        current_price: float,
        kline_data: List[Dict[str, Any]],
        indicators: Dict[str, Any],
        volume_info: Dict[str, Any]
    ) -> str:
        """格式化市场分析提示词"""
        return cls.MARKET_ANALYSIS.format(
            stock_code=stock_code,
            stock_name=stock_name,
            current_price=current_price,
            kline_data=cls._format_list(kline_data),
            ma5=indicators.get("ma5", "N/A"),
            ma10=indicators.get("ma10", "N/A"),
            ma20=indicators.get("ma20", "N/A"),
            rsi=indicators.get("rsi", "N/A"),
            macd=indicators.get("macd", "N/A"),
            volume_info=cls._format_dict(volume_info)
        )
    
    @classmethod
    def format_indicator_analysis(
        cls,
        indicators: Dict[str, Any]
    ) -> str:
        """格式化技术指标分析提示词"""
        return cls.INDICATOR_ANALYSIS.format(**indicators)
    
    @classmethod
    def format_risk_assessment(
        cls,
        portfolio_info: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        market_environment: Dict[str, Any]
    ) -> str:
        """格式化风险评估提示词"""
        return cls.RISK_ASSESSMENT.format(
            portfolio_info=cls._format_dict(portfolio_info),
            total_market_value=risk_metrics.get("total_market_value", "N/A"),
            max_single_ratio=risk_metrics.get("max_single_ratio", "N/A"),
            industry_concentration=risk_metrics.get("industry_concentration", "N/A"),
            beta=risk_metrics.get("beta", "N/A"),
            volatility=risk_metrics.get("volatility", "N/A"),
            max_drawdown=risk_metrics.get("max_drawdown", "N/A"),
            index_value=market_environment.get("index_value", "N/A"),
            index_change=market_environment.get("index_change", "N/A"),
            market_sentiment=market_environment.get("market_sentiment", "N/A")
        )
    
    @classmethod
    def format_strategy_optimization(
        cls,
        strategy_type: str,
        strategy_params: Dict[str, Any],
        backtest_results: Dict[str, Any],
        trades_summary: str
    ) -> str:
        """格式化策略优化提示词"""
        return cls.STRATEGY_OPTIMIZATION.format(
            strategy_type=strategy_type,
            strategy_params=cls._format_dict(strategy_params),
            backtest_period=backtest_results.get("period", "N/A"),
            initial_capital=backtest_results.get("initial_capital", "N/A"),
            final_capital=backtest_results.get("final_capital", "N/A"),
            total_return=backtest_results.get("total_return", "N/A"),
            annual_return=backtest_results.get("annual_return", "N/A"),
            max_drawdown=backtest_results.get("max_drawdown", "N/A"),
            sharpe_ratio=backtest_results.get("sharpe_ratio", "N/A"),
            win_rate=backtest_results.get("win_rate", "N/A"),
            profit_loss_ratio=backtest_results.get("profit_loss_ratio", "N/A"),
            trade_count=backtest_results.get("trade_count", "N/A"),
            trades_summary=trades_summary
        )
    
    @classmethod
    def format_quick_question(
        cls,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """格式化快速问答提示词"""
        context_str = cls._format_dict(context) if context else "无"
        return cls.QUICK_QUESTION.format(
            question=question,
            context=context_str
        )
    
    @staticmethod
    def _format_dict(data: Dict[str, Any], indent: int = 0) -> str:
        """格式化字典为字符串"""
        if not data:
            return "无"
        
        lines = []
        for key, value in data.items():
            lines.append(f"{'  ' * indent}- {key}: {value}")
        return "\n".join(lines)
    
    @staticmethod
    def _format_list(data: List[Dict[str, Any]], limit: int = 10) -> str:
        """格式化列表为字符串"""
        if not data:
            return "无"
        
        lines = []
        for i, item in enumerate(data[:limit]):
            lines.append(f"{i+1}. {item}")
        if len(data) > limit:
            lines.append(f"... 还有 {len(data) - limit} 条数据")
        return "\n".join(lines)