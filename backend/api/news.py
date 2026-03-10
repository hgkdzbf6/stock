"""
新闻获取API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from core.security import get_current_user
from models.user import User
from services.news_fetcher import NewsFetcher, get_news_fetcher
from ai.sentiment_service import SentimentService, get_sentiment_service


# Pydantic 模型
class FetchStockNewsRequest(BaseModel):
    """获取股票新闻请求"""
    stock_code: Optional[str] = Field("", description="股票代码")
    stock_name: Optional[str] = Field("", description="股票名称")
    sector_name: Optional[str] = Field(None, description="板块名称")
    market: Optional[str] = Field(None, description="市场类型: domestic(国内) 或 international(国外)")
    sources: Optional[List[str]] = Field(None, description="数据来源列表")
    limit: int = Field(10, description="最大新闻数量")


class FetchSectorNewsRequest(BaseModel):
    """获取板块新闻请求"""
    sector_name: str = Field(..., description="板块名称")
    limit: int = Field(20, description="最大新闻数量")


class FundamentalsData(BaseModel):
    """基本面数据"""
    market_cap: Optional[str] = Field(None, description="市值")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    roe: Optional[float] = Field(None, description="净资产收益率")
    revenue: Optional[str] = Field(None, description="营收")
    net_profit: Optional[str] = Field(None, description="净利润")
    revenue_growth: Optional[float] = Field(None, description="营收增长率")
    profit_growth: Optional[float] = Field(None, description="净利润增长率")
    dividend_yield: Optional[float] = Field(None, description="股息率")
    industry: Optional[str] = Field(None, description="所属行业")


class SummarizeFundamentalsRequest(BaseModel):
    """总结基本面请求"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    fundamentals: FundamentalsData = Field(..., description="基本面数据")


class FormatNewsRequest(BaseModel):
    """格式化新闻请求"""
    news_list: List[dict] = Field(..., description="新闻列表")
    fundamentals: Optional[FundamentalsData] = Field(None, description="基本面数据")


class AnalyzeSentimentRequest(BaseModel):
    """情绪分析请求"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    sector_name: Optional[str] = Field(None, description="板块名称")
    news_list: List[dict] = Field(..., description="新闻数据列表")


# 公共路由（不需要认证）
public_router = APIRouter(prefix="/public/news", tags=["公共新闻"])


# ========== 公共API端点（不需要认证） ==========


@public_router.get("/health")
async def public_health_check():
    """公共健康检查"""
    try:
        fetcher = get_news_fetcher()
        
        # 检查新浪财经API可用性
        sina_available = await fetcher.check_sina_api()
        
        # 构建源列表
        sources = []
        for category, urls in fetcher.default_rss_sources.items():
            for url in urls:
                source_info = fetcher.rss_source_info.get(url, {})
                sources.append({
                    "name": source_info.get("name_cn", url),
                    "name_en": source_info.get("name", ""),
                    "url": url,
                    "category": category,
                    "country": source_info.get("country_cn", ""),
                    "available": True  # RSS源通常可用
                })
        
        # 添加新浪财经状态
        sources.append({
            "name": "新浪财经",
            "name_en": "Sina Finance",
            "url": "https://finance.sina.com.cn",
            "category": "A股",
            "country": "中国",
            "available": sina_available
        })
        
        return {
            "code": 200,
            "message": "服务正常",
            "data": {
                "status": "healthy",
                "sources": sources
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务异常: {str(e)}"
        )


@public_router.post("/fetch/stock")
async def public_fetch_stock_news(request: FetchStockNewsRequest):
    """
    获取股票相关新闻（公共端点，不需要认证）
    
    Args:
        request: 获取股票新闻请求
        
    Returns:
        新闻列表
    """
    try:
        fetcher = get_news_fetcher()
        
        # 检查新浪财经API可用性
        if request.sources and ("新浪财经" in request.sources or "Sina Finance" in request.sources):
            sina_available = await fetcher.check_sina_api()
            if not sina_available:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="新浪财经API端点目前不可用，请稍后再试或选择其他数据来源"
                )
        
        news_list = await fetcher.fetch_stock_news(
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            sector_name=request.sector_name,
            market=request.market,
            sources=request.sources,
            limit=request.limit
        )
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "news": news_list,
                "total": len(news_list)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取新闻失败: {str(e)}"
        )


@public_router.post("/fetch/sector")
async def public_fetch_sector_news(request: FetchSectorNewsRequest):
    """
    获取板块相关新闻（公共端点，不需要认证）
    
    Args:
        request: 获取板块新闻请求
        
    Returns:
        新闻列表
    """
    try:
        fetcher = get_news_fetcher()
        
        news_list = await fetcher.fetch_sector_news(
            sector_name=request.sector_name,
            limit=request.limit
        )
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "news": news_list,
                "total": len(news_list)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取新闻失败: {str(e)}"
        )


@public_router.post("/format")
async def public_format_news(request: FormatNewsRequest):
    """
    格式化新闻用于舆情分析（公共端点，不需要认证）
    
    Args:
        request: 格式化新闻请求
        
    Returns:
        格式化后的新闻列表
    """
    try:
        fetcher = get_news_fetcher()
        
        formatted_news = fetcher.format_news_for_sentiment(
            news_list=request.news_list,
            fundamentals=request.fundamentals.dict() if request.fundamentals else None
        )
        
        return {
            "code": 200,
            "message": "格式化成功",
            "data": {
                "news": formatted_news,
                "total": len(formatted_news)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"格式化失败: {str(e)}"
        )


@public_router.post("/analyze/sentiment")
async def public_analyze_sentiment(request: AnalyzeSentimentRequest):
    """
    一键情绪分析（公共端点，不需要认证）
    
    Args:
        request: 情绪分析请求
        
    Returns:
        情绪分析结果
    """
    try:
        service = get_sentiment_service()
        
        # 转换新闻数据为字典列表
        news_data_list = request.news_list if request.news_list else []
        
        # 调用服务分析
        result_generator = service.analyze_news(
            user_id=0,  # 公共端点使用0作为用户ID
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


# ========== 受保护API端点（需要认证） ==========


# 受保护路由（需要认证）
router = APIRouter(prefix="/news", tags=["新闻获取"])


@router.get("/health")
async def health_check(current_user: User = Depends(get_current_user)):
    """健康检查"""
    try:
        fetcher = get_news_fetcher()
        return {
            "code": 200,
            "message": "服务正常",
            "data": {
                "status": "healthy",
                "sources": list(fetcher.default_rss_sources.keys())
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务异常: {str(e)}"
        )


@router.post("/fetch/stock")
async def fetch_stock_news(
    request: FetchStockNewsRequest,
    current_user: User = Depends(get_current_user),
):
    """
    获取股票相关新闻
    
    Args:
        request: 获取股票新闻请求
        
    Returns:
        新闻列表
    """
    try:
        fetcher = get_news_fetcher()
        
        news_list = await fetcher.fetch_stock_news(
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            sector_name=request.sector_name,
            limit=request.limit
        )
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "news": news_list,
                "total": len(news_list)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取新闻失败: {str(e)}"
        )


@router.post("/fetch/sector")
async def fetch_sector_news(
    request: FetchSectorNewsRequest,
    current_user: User = Depends(get_current_user),
):
    """
    获取板块相关新闻
    
    Args:
        request: 获取板块新闻请求
        
    Returns:
        新闻列表
    """
    try:
        fetcher = get_news_fetcher()
        
        news_list = await fetcher.fetch_sector_news(
            sector_name=request.sector_name,
            limit=request.limit
        )
        
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "news": news_list,
                "total": len(news_list)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取新闻失败: {str(e)}"
        )


@router.post("/summarize/fundamentals")
async def summarize_fundamentals(
    request: SummarizeFundamentalsRequest,
    current_user: User = Depends(get_current_user),
):
    """
    总结基本面信息
    
    Args:
        request: 总结基本面请求
        
    Returns:
        基本面总结
    """
    try:
        fetcher = get_news_fetcher()
        
        summary = await fetcher.summarize_fundamentals(
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            fundamentals=request.fundamentals.dict()
        )
        
        return {
            "code": 200,
            "message": "总结成功",
            "data": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"总结失败: {str(e)}"
        )


@router.post("/format")
async def format_news(
    request: FormatNewsRequest,
    current_user: User = Depends(get_current_user),
):
    """
    格式化新闻用于舆情分析
    
    Args:
        request: 格式化新闻请求
        
    Returns:
        格式化后的新闻列表
    """
    try:
        fetcher = get_news_fetcher()
        
        formatted_news = fetcher.format_news_for_sentiment(
            news_list=request.news_list,
            fundamentals=request.fundamentals.dict() if request.fundamentals else None
        )
        
        return {
            "code": 200,
            "message": "格式化成功",
            "data": {
                "news": formatted_news,
                "total": len(formatted_news)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"格式化失败: {str(e)}"
        )