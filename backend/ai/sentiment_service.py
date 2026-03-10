"""舆情分析服务"""
import json
import asyncio
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime, timedelta
from loguru import logger

from .llm_client import LLMClient, get_llm_client
from .prompt_templates import PromptTemplates


class SentimentService:
    """舆情分析服务"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """初始化舆情服务
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm_client = llm_client or get_llm_client()
        self.templates = PromptTemplates()
        logger.info("舆情分析服务初始化完成")
    
    async def analyze_news(
        self,
        user_id: int,
        news_data: List[Dict[str, Any]],
        stock_code: str,
        stock_name: str,
        sector_name: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any] | AsyncIterator[str]:
        """分析新闻舆情
        
        Args:
            user_id: 用户ID
            news_data: 新闻数据列表
            stock_code: 股票代码
            stock_name: 股票名称
            sector_name: 板块名称（可选）
            stream: 是否流式响应
            
        Returns:
            舆情分析结果或流式响应
        """
        logger.info(f"用户 {user_id} 请求舆情分析: {stock_code} - {stock_name}")
        
        # 构建提示词
        prompt = self.templates.format_sentiment_analysis(
            news_data=news_data,
            stock_code=stock_code,
            stock_name=stock_name,
            sector_name=sector_name
        )
        
        if stream:
            # 流式响应
            async for chunk in self.llm_client.chat_stream(
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的舆情分析师。你需要分析新闻对股票走势的影响，给出明确的评分和判断。"
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
                    "overall_sentiment": 0,
                    "confidence": 0.5
                }
            
            yield analysis
    
    async def analyze_news_batch(
        self,
        user_id: int,
        news_items: List[Dict[str, Any]],
        stock_code: str,
        stock_name: str
    ) -> List[Dict[str, Any]]:
        """批量分析新闻舆情
        
        Args:
            user_id: 用户ID
            news_items: 新闻项列表
            stock_code: 股票代码
            stock_name: 股票名称
            
        Returns:
            每条新闻的舆情分析结果列表
        """
        logger.info(f"用户 {user_id} 批量分析 {len(news_items)} 条新闻")
        
        results = []
        for news_item in news_items:
            try:
                result = await self.analyze_single_news(
                    news_item,
                    stock_code,
                    stock_name
                )
                results.append(result)
            except Exception as e:
                logger.error(f"分析新闻失败: {e}")
                results.append({
                    "news_id": news_item.get("id", ""),
                    "error": str(e),
                    "sentiment_score": 0,
                    "confidence": 0
                })
        
        return results
    
    async def analyze_single_news(
        self,
        news_item: Dict[str, Any],
        stock_code: str,
        stock_name: str
    ) -> Dict[str, Any]:
        """分析单条新闻
        
        Args:
            news_item: 新闻项
            stock_code: 股票代码
            stock_name: 股票名称
            
        Returns:
            舆情分析结果
        """
        # 构建单条新闻分析提示词
        prompt = self.templates.format_single_news_analysis(
            news_item=news_item,
            stock_code=stock_code,
            stock_name=stock_name
        )
        
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
            analysis["news_id"] = news_item.get("id", "")
            return analysis
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"JSON解析失败: {e}")
            return {
                "news_id": news_item.get("id", ""),
                "sentiment_score": 0,
                "confidence": 0,
                "impact_level": "neutral",
                "analysis": result
            }
    
    async def aggregate_sentiment(
        self,
        sentiment_scores: List[float],
        weights: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """聚合舆情分数
        
        Args:
            sentiment_scores: 舆情分数列表
            weights: 权重列表（可选）
            
        Returns:
            聚合结果
        """
        if not sentiment_scores:
            return {
                "overall_score": 0,
                "trend": "neutral",
                "confidence": 0,
                "count": 0
            }
        
        if weights is None:
            weights = [1.0] * len(sentiment_scores)
        
        # 加权平均
        weighted_sum = sum(s * w for s, w in zip(sentiment_scores, weights))
        total_weight = sum(weights)
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        # 确定趋势
        if overall_score > 50:
            trend = "strongly_positive"
        elif overall_score > 20:
            trend = "positive"
        elif overall_score > -20:
            trend = "neutral"
        elif overall_score > -50:
            trend = "negative"
        else:
            trend = "strongly_negative"
        
        # 计算置信度
        count = len(sentiment_scores)
        confidence = min(count / 10, 1.0)  # 最多10条新闻时置信度为1
        
        return {
            "overall_score": round(overall_score, 2),
            "trend": trend,
            "confidence": round(confidence, 2),
            "count": count
        }
    
    async def backtest_sentiment_impact(
        self,
        user_id: int,
        stock_code: str,
        stock_name: str,
        sentiment_history: List[Dict[str, Any]],
        price_data: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """回测舆情影响
        
        Args:
            user_id: 用户ID
            stock_code: 股票代码
            stock_name: 股票名称
            sentiment_history: 舆情历史记录
            price_data: 价格数据
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            回测结果
        """
        logger.info(f"用户 {user_id} 请求舆情影响回测: {stock_code}")
        
        # 构建提示词
        prompt = self.templates.format_sentiment_backtest(
            stock_code=stock_code,
            stock_name=stock_name,
            sentiment_history=sentiment_history,
            price_data=price_data,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
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
            
            backtest_result = json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"JSON解析失败: {e}")
            backtest_result = {
                "correlation": 0,
                "accuracy": 0,
                "insights": result
            }
        
        return backtest_result


# 单例模式
_sentiment_service: Optional[SentimentService] = None


def get_sentiment_service() -> SentimentService:
    """获取舆情服务单例
    
    Returns:
        舆情服务实例
    """
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = SentimentService()
    return _sentiment_service