"""AI分析服务"""
import json
import asyncio
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime
from loguru import logger

from .llm_client import LLMClient, get_llm_client
from .prompt_templates import PromptTemplates


class AIService:
    """AI分析服务"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """初始化AI服务
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm_client = llm_client or get_llm_client()
        self.templates = PromptTemplates()
        logger.info("AI服务初始化完成")
    
    async def analyze_portfolio(
        self,
        user_id: int,
        positions: List[Dict[str, Any]],
        market_data: Dict[str, Any],
        indicators: Dict[str, Any],
        stream: bool = False
    ) -> Dict[str, Any] | AsyncIterator[str]:
        """分析持仓
        
        Args:
            user_id: 用户ID
            positions: 持仓列表
            market_data: 市场数据
            indicators: 技术指标
            stream: 是否流式响应
            
        Returns:
            分析结果或流式响应
        """
        logger.info(f"用户 {user_id} 请求持仓分析")
        
        # 构建提示词
        prompt = self.templates.format_portfolio_analysis(
            positions=positions,
            market_data=market_data,
            indicators=indicators
        )
        
        if stream:
            # 流式响应
            async for chunk in self.llm_client.chat_stream(
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的量化投资顾问。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            ):
                yield chunk
        else:
            # 非流式响应
            result = await self.llm_client.analyze(prompt, context=None)
            
            # 尝试解析JSON
            try:
                # 提取JSON部分
                if "```json" in result:
                    json_start = result.find("```json") + 7
                    json_end = result.find("```", json_start)
                    json_str = result[json_start:json_end].strip()
                elif "```" in result:
                    json_start = result.find("```") + 3
                    json_end = result.find("```", json_start)
                    json_str = result[json_start:json_end].strip()
                else:
                    json_str = result
                
                analysis = json.loads(json_str)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON解析失败: {e}")
                analysis = {
                    "raw_response": result,
                    "confidence": 0.5
                }
            
            # 不使用return，直接作为生成器返回单个值
            yield analysis
    
    async def analyze_market(
        self,
        user_id: int,
        stock_code: str,
        stock_name: str,
        current_price: float,
        kline_data: List[Dict[str, Any]],
        indicators: Dict[str, Any],
        volume_info: Dict[str, Any],
        stream: bool = False
    ) -> Dict[str, Any] | AsyncIterator[str]:
        """分析市场行情
        
        Args:
            user_id: 用户ID
            stock_code: 股票代码
            stock_name: 股票名称
            current_price: 当前价格
            kline_data: K线数据
            indicators: 技术指标
            volume_info: 成交量信息
            stream: 是否流式响应
            
        Returns:
            分析结果或流式响应
        """
        logger.info(f"用户 {user_id} 请求市场分析: {stock_code}")
        
        # 构建提示词
        prompt = self.templates.format_market_analysis(
            stock_code=stock_code,
            stock_name=stock_name,
            current_price=current_price,
            kline_data=kline_data,
            indicators=indicators,
            volume_info=volume_info
        )
        
        if stream:
            async for chunk in self.llm_client.chat_stream(
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的市场分析师。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            ):
                yield chunk
        else:
            result = await self.llm_client.analyze(prompt, context=None)
            
            try:
                if "```json" in result:
                    json_start = result.find("```json") + 7
                    json_end = result.find("```", json_start)
                    json_str = result[json_start:json_end].strip()
                elif "```" in result:
                    json_start = result.find("```") + 3
                    json_end = result.find("```", json_start)
                    json_str = result[json_start:json_end].strip()
                else:
                    json_str = result
                
                analysis = json.loads(json_str)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON解析失败: {e}")
                analysis = {
                    "raw_response": result,
                    "confidence": 0.5
                }
            
            yield analysis
    
    async def analyze_indicators(
        self,
        user_id: int,
        indicators: Dict[str, Any],
        stream: bool = False
    ) -> Dict[str, Any] | AsyncIterator[str]:
        """分析技术指标
        
        Args:
            user_id: 用户ID
            indicators: 技术指标
            stream: 是否流式响应
            
        Returns:
            分析结果或流式响应
        """
        logger.info(f"用户 {user_id} 请求技术指标分析")
        
        # 构建提示词
        prompt = self.templates.format_indicator_analysis(
            indicators=indicators
        )
        
        if stream:
            async for chunk in self.llm_client.chat_stream(
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的技术分析专家。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            ):
                yield chunk
        else:
            result = await self.llm_client.analyze(prompt, context=None)
            
            try:
                if "```json" in result:
                    json_start = result.find("```json") + 7
                    json_end = result.find("```", json_start)
                    json_str = result[json_start:json_end].strip()
                elif "```" in result:
                    json_start = result.find("```") + 3
                    json_end = result.find("```", json_start)
                    json_str = result[json_start:json_end].strip()
                else:
                    json_str = result
                
                analysis = json.loads(json_str)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON解析失败: {e}")
                analysis = {
                    "raw_response": result,
                    "confidence": 0.5
                }
            
            yield analysis
    
    async def assess_risk(
        self,
        user_id: int,
        portfolio_info: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        market_environment: Dict[str, Any],
        stream: bool = False
    ) -> Dict[str, Any] | AsyncIterator[str]:
        """评估风险
        
        Args:
            user_id: 用户ID
            portfolio_info: 持仓信息
            risk_metrics: 风险指标
            market_environment: 市场环境
            stream: 是否流式响应
            
        Returns:
            风险评估结果或流式响应
        """
        logger.info(f"用户 {user_id} 请求风险评估")
        
        # 构建提示词
        prompt = self.templates.format_risk_assessment(
            portfolio_info=portfolio_info,
            risk_metrics=risk_metrics,
            market_environment=market_environment
        )
        
        if stream:
            async for chunk in self.llm_client.chat_stream(
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的风险控制专家。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            ):
                yield chunk
        else:
            result = await self.llm_client.analyze(prompt, context=None)
            
            try:
                if "```json" in result:
                    json_start = result.find("```json") + 7
                    json_end = result.find("```", json_start)
                    json_str = result[json_start:json_end].strip()
                elif "```" in result:
                    json_start = result.find("```") + 3
                    json_end = result.find("```", json_start)
                    json_str = result[json_start:json_end].strip()
                else:
                    json_str = result
                
                assessment = json.loads(json_str)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON解析失败: {e}")
                assessment = {
                    "raw_response": result,
                    "confidence": 0.5
                }
            
            yield assessment
    
    async def optimize_strategy(
        self,
        user_id: int,
        strategy_type: str,
        strategy_params: Dict[str, Any],
        backtest_results: Dict[str, Any],
        trades_summary: str,
        stream: bool = False
    ) -> Dict[str, Any] | AsyncIterator[str]:
        """策略优化建议
        
        Args:
            user_id: 用户ID
            strategy_type: 策略类型
            strategy_params: 策略参数
            backtest_results: 回测结果
            trades_summary: 交易摘要
            stream: 是否流式响应
            
        Returns:
            优化建议或流式响应
        """
        logger.info(f"用户 {user_id} 请求策略优化: {strategy_type}")
        
        # 构建提示词
        prompt = self.templates.format_strategy_optimization(
            strategy_type=strategy_type,
            strategy_params=strategy_params,
            backtest_results=backtest_results,
            trades_summary=trades_summary
        )
        
        if stream:
            async for chunk in self.llm_client.chat_stream(
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的策略优化专家。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            ):
                yield chunk
        else:
            result = await self.llm_client.analyze(prompt, context=None)
            
            try:
                if "```json" in result:
                    json_start = result.find("```json") + 7
                    json_end = result.find("```", json_start)
                    json_str = result[json_start:json_end].strip()
                elif "```" in result:
                    json_start = result.find("```") + 3
                    json_end = result.find("```", json_start)
                    json_str = result[json_start:json_end].strip()
                else:
                    json_str = result
                
                optimization = json.loads(json_str)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON解析失败: {e}")
                optimization = {
                    "raw_response": result,
                    "confidence": 0.5
                }
            
            yield optimization
    
    async def chat(
        self,
        user_id: int,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> AsyncIterator[str] | str:
        """快速问答
        
        Args:
            user_id: 用户ID
            question: 问题
            context: 上下文
            stream: 是否流式响应
            
        Returns:
            回答或流式响应
        """
        logger.info(f"用户 {user_id} 提问: {question[:50]}...")
        
        # 构建提示词
        prompt = self.templates.format_quick_question(
            question=question,
            context=context
        )
        
        if stream:
            async for chunk in self.llm_client.chat_stream(
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的量化投资顾问。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            ):
                yield chunk
        else:
            result = await self.llm_client.analyze(prompt, context=context)
            yield result
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查
        
        Returns:
            健康状态
        """
        try:
            # 检查API Key是否配置
            if not self.llm_client.api_key:
                return {
                    "status": "warning",
                    "message": "GLM_API_KEY未配置",
                    "configured": False
                }
            
            # 简单测试
            result = await self.llm_client.analyze(
                "请回复'OK'",
                context=None,
                max_tokens=10
            )
            
            if "OK" in result or "ok" in result:
                return {
                    "status": "healthy",
                    "message": "AI服务正常",
                    "configured": True,
                    "model": self.llm_client.model
                }
            else:
                return {
                    "status": "error",
                    "message": f"AI响应异常: {result}",
                    "configured": True
                }
        
        except Exception as e:
            logger.error(f"AI服务健康检查失败: {e}")
            return {
                "status": "error",
                "message": f"AI服务异常: {str(e)}",
                "configured": False
            }


# 单例模式
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """获取AI服务单例
    
    Returns:
        AI服务实例
    """
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service