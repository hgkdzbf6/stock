"""
舆情分析API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from core.security import get_current_user
from models.user import User
from ai.sentiment_service import SentimentService, get_sentiment_service


def _resolve_current_user_id(current_user: User) -> int:
    """兼容不同用户模型字段，解析当前用户ID。"""
    raw_user_id = getattr(current_user, "id", None)
    if raw_user_id is None:
        raw_user_id = getattr(current_user, "user_id", None)

    if raw_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户身份信息",
        )

    try:
        return int(raw_user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户ID",
        )


# Pydantic 模型
class NewsItem(BaseModel):
    """新闻项"""
    id: str
    title: str
    content: str
    source: str
    publish_time: str
    url: Optional[str] = None


class AnalyzeSentimentRequest(BaseModel):
    """舆情分析请求"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    sector_name: Optional[str] = Field(None, description="板块名称")
    news_data: Optional[List[NewsItem]] = Field(None, description="新闻数据列表（必须为真实新闻）")


class BatchAnalyzeRequest(BaseModel):
    """批量分析请求"""
    news_items: List[NewsItem] = Field(..., description="新闻项列表")
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")


class BacktestRequest(BaseModel):
    """回测请求"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    start_date: str = Field(..., description="开始日期（ISO格式）")
    end_date: str = Field(..., description="结束日期（ISO格式）")
    sentiment_history: Optional[List[dict]] = Field(None, description="舆情历史记录（必须为真实历史数据）")
    price_data: Optional[List[dict]] = Field(None, description="价格数据（必须为真实历史数据）")


class AggregateRequest(BaseModel):
    """聚合请求"""
    sentiment_scores: List[float] = Field(..., description="舆情分数列表")
    weights: Optional[List[float]] = Field(None, description="权重列表")


router = APIRouter(prefix="/sentiment", tags=["舆情分析"])


@router.get("/health")
async def health_check(current_user: User = Depends(get_current_user)):
    """健康检查"""
    try:
        service = get_sentiment_service()
        result = await service.health_check() if hasattr(service, 'health_check') else {
            "status": "healthy",
            "configured": True
        }
        return {
            "code": 200,
            "message": "服务正常",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务异常: {str(e)}"
        )


@router.post("/analyze")
async def analyze_news(
    request: AnalyzeSentimentRequest,
    current_user: User = Depends(get_current_user),
):
    """
    分析新闻舆情
    
    Args:
        request: 舆情分析请求
        
    Returns:
        舆情分析结果
    """
    try:
        service = get_sentiment_service()
        user_id = _resolve_current_user_id(current_user)

        news_data = request.news_data
        if not news_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="news_data 不能为空，请提供真实新闻数据",
            )
        
        # 转换为字典列表
        news_data_list = [item.model_dump() for item in news_data] if news_data else []
        
        # 调用服务分析
        result_generator = service.analyze_news(
            user_id=user_id,
            news_data=news_data_list,
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            sector_name=request.sector_name,
            stream=False
        )
        
        # 提取结果
        result = None
        async for item in result_generator:
            result = item
            break
        
        return {
            "code": 200,
            "message": "分析成功",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.post("/analyze/batch")
async def analyze_news_batch(
    request: BatchAnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    """
    批量分析新闻舆情
    
    Args:
        request: 批量分析请求
        
    Returns:
        每条新闻的舆情分析结果列表
    """
    try:
        service = get_sentiment_service()
        user_id = _resolve_current_user_id(current_user)

        # 转换为字典列表
        news_items_list = [item.model_dump() for item in request.news_items]

        results = await service.analyze_news_batch(
            user_id=user_id,
            news_items=news_items_list,
            stock_code=request.stock_code,
            stock_name=request.stock_name
        )
        
        return {
            "code": 200,
            "message": "批量分析成功",
            "data": {
                "results": results,
                "total": len(results)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量分析失败: {str(e)}"
        )


@router.post("/backtest")
async def backtest_sentiment_impact(
    request: BacktestRequest,
    current_user: User = Depends(get_current_user),
):
    """
    回测舆情影响
    
    Args:
        request: 回测请求
        
    Returns:
        回测结果
    """
    try:
        service = get_sentiment_service()
        user_id = _resolve_current_user_id(current_user)

        # 解析日期
        try:
            start_dt = datetime.fromisoformat(request.start_date)
            end_dt = datetime.fromisoformat(request.end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date/end_date 格式错误，请使用 ISO 日期格式",
            )

        if start_dt > end_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date 不能晚于 end_date",
            )

        sentiment_history = request.sentiment_history
        if not sentiment_history:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sentiment_history 不能为空，请提供真实舆情历史数据",
            )

        price_data = request.price_data
        if not price_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="price_data 不能为空，请提供真实价格数据",
            )

        # 调用服务回测
        result = await service.backtest_sentiment_impact(
            user_id=user_id,
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            sentiment_history=sentiment_history,
            price_data=price_data,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return {
            "code": 200,
            "message": "回测成功",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"回测失败: {str(e)}"
        )


@router.post("/aggregate")
async def aggregate_sentiment(
    request: AggregateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    聚合舆情分数
    
    Args:
        request: 聚合请求
        
    Returns:
        聚合结果
    """
    try:
        service = get_sentiment_service()
        
        result = await service.aggregate_sentiment(
            sentiment_scores=request.sentiment_scores,
            weights=request.weights
        )
        
        return {
            "code": 200,
            "message": "聚合成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"聚合失败: {str(e)}"
        )
