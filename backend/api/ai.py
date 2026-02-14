"""AI分析API"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from loguru import logger

from ai import get_ai_service
from core.security import get_current_user, User

router = APIRouter()


# ==================== 请求模型 ====================

class AIAnalyzeRequest(BaseModel):
    """AI分析请求"""
    type: str = Field(..., description="分析类型: portfolio, market, indicators, risk, strategy")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文数据")
    stream: bool = Field(default=False, description="是否流式响应")


class ChatRequest(BaseModel):
    """聊天请求"""
    question: str = Field(..., description="问题")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文")
    stream: bool = Field(default=False, description="是否流式响应")


class PortfolioAnalysisRequest(BaseModel):
    """持仓分析请求"""
    positions: List[Dict[str, Any]] = Field(..., description="持仓列表")
    market_data: Dict[str, Any] = Field(default_factory=dict, description="市场数据")
    indicators: Dict[str, Any] = Field(default_factory=dict, description="技术指标")
    stream: bool = Field(default=False, description="是否流式响应")


class MarketAnalysisRequest(BaseModel):
    """市场分析请求"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    current_price: float = Field(..., description="当前价格")
    kline_data: List[Dict[str, Any]] = Field(..., description="K线数据")
    indicators: Dict[str, Any] = Field(default_factory=dict, description="技术指标")
    volume_info: Dict[str, Any] = Field(default_factory=dict, description="成交量信息")
    stream: bool = Field(default=False, description="是否流式响应")


class IndicatorAnalysisRequest(BaseModel):
    """技术指标分析请求"""
    indicators: Dict[str, Any] = Field(..., description="技术指标")
    stream: bool = Field(default=False, description="是否流式响应")


class RiskAssessmentRequest(BaseModel):
    """风险评估请求"""
    portfolio_info: Dict[str, Any] = Field(..., description="持仓信息")
    risk_metrics: Dict[str, Any] = Field(..., description="风险指标")
    market_environment: Dict[str, Any] = Field(default_factory=dict, description="市场环境")
    stream: bool = Field(default=False, description="是否流式响应")


class StrategyOptimizationRequest(BaseModel):
    """策略优化请求"""
    strategy_type: str = Field(..., description="策略类型")
    strategy_params: Dict[str, Any] = Field(..., description="策略参数")
    backtest_results: Dict[str, Any] = Field(..., description="回测结果")
    trades_summary: str = Field(default="", description="交易摘要")
    stream: bool = Field(default=False, description="是否流式响应")


# ==================== 通用分析端点 ====================

@router.post("/analyze")
async def analyze(
    request: AIAnalyzeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    AI分析 - 通用接口
    
    支持的分析类型:
    - portfolio: 持仓分析
    - market: 市场分析
    - indicators: 技术指标分析
    - risk: 风险评估
    - strategy: 策略优化
    """
    try:
        ai_service = get_ai_service()
        analysis_type = request.type
        
        logger.info(f"用户 {current_user.username} 请求AI分析: {analysis_type}")
        
        if analysis_type == "portfolio":
            result = await ai_service.analyze_portfolio(
                user_id=current_user.id,
                positions=request.context.get("positions", []),
                market_data=request.context.get("market_data", {}),
                indicators=request.context.get("indicators", {}),
                stream=request.stream
            )
        elif analysis_type == "market":
            result = await ai_service.analyze_market(
                user_id=current_user.id,
                stock_code=request.context.get("stock_code", ""),
                stock_name=request.context.get("stock_name", ""),
                current_price=request.context.get("current_price", 0),
                kline_data=request.context.get("kline_data", []),
                indicators=request.context.get("indicators", {}),
                volume_info=request.context.get("volume_info", {}),
                stream=request.stream
            )
        elif analysis_type == "indicators":
            result = await ai_service.analyze_indicators(
                user_id=current_user.id,
                indicators=request.context,
                stream=request.stream
            )
        elif analysis_type == "risk":
            result = await ai_service.assess_risk(
                user_id=current_user.id,
                portfolio_info=request.context.get("portfolio_info", {}),
                risk_metrics=request.context.get("risk_metrics", {}),
                market_environment=request.context.get("market_environment", {}),
                stream=request.stream
            )
        elif analysis_type == "strategy":
            result = await ai_service.optimize_strategy(
                user_id=current_user.id,
                strategy_type=request.context.get("strategy_type", ""),
                strategy_params=request.context.get("strategy_params", {}),
                backtest_results=request.context.get("backtest_results", {}),
                trades_summary=request.context.get("trades_summary", ""),
                stream=request.stream
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的分析类型: {analysis_type}"
            )
        
        # 流式响应
        if request.stream:
            async def generate():
                async for chunk in result:
                    yield chunk
            
            return StreamingResponse(
                generate(),
                media_type="text/plain"
            )
        
        # 非流式响应
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI分析失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI分析失败: {str(e)}"
        )


# ==================== 专用分析端点 ====================

@router.post("/analyze/portfolio")
async def analyze_portfolio(
    request: PortfolioAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """持仓分析"""
    try:
        ai_service = get_ai_service()
        
        logger.info(f"用户 {current_user.username} 请求持仓分析")
        
        result = await ai_service.analyze_portfolio(
            user_id=current_user.id,
            positions=request.positions,
            market_data=request.market_data,
            indicators=request.indicators,
            stream=request.stream
        )
        
        if request.stream:
            async def generate():
                async for chunk in result:
                    yield chunk
            
            return StreamingResponse(
                generate(),
                media_type="text/plain"
            )
        
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"持仓分析失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"持仓分析失败: {str(e)}"
        )


@router.post("/analyze/market")
async def analyze_market(
    request: MarketAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """市场分析"""
    try:
        ai_service = get_ai_service()
        
        logger.info(f"用户 {current_user.username} 请求市场分析: {request.stock_code}")
        
        result = await ai_service.analyze_market(
            user_id=current_user.id,
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            current_price=request.current_price,
            kline_data=request.kline_data,
            indicators=request.indicators,
            volume_info=request.volume_info,
            stream=request.stream
        )
        
        if request.stream:
            async def generate():
                async for chunk in result:
                    yield chunk
            
            return StreamingResponse(
                generate(),
                media_type="text/plain"
            )
        
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"市场分析失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"市场分析失败: {str(e)}"
        )


@router.post("/analyze/indicators")
async def analyze_indicators(
    request: IndicatorAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """技术指标分析"""
    try:
        ai_service = get_ai_service()
        
        logger.info(f"用户 {current_user.username} 请求技术指标分析")
        
        result = await ai_service.analyze_indicators(
            user_id=current_user.id,
            indicators=request.indicators,
            stream=request.stream
        )
        
        if request.stream:
            async def generate():
                async for chunk in result:
                    yield chunk
            
            return StreamingResponse(
                generate(),
                media_type="text/plain"
            )
        
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"技术指标分析失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"技术指标分析失败: {str(e)}"
        )


@router.post("/assess/risk")
async def assess_risk(
    request: RiskAssessmentRequest,
    current_user: User = Depends(get_current_user)
):
    """风险评估"""
    try:
        ai_service = get_ai_service()
        
        logger.info(f"用户 {current_user.username} 请求风险评估")
        
        result = await ai_service.assess_risk(
            user_id=current_user.id,
            portfolio_info=request.portfolio_info,
            risk_metrics=request.risk_metrics,
            market_environment=request.market_environment,
            stream=request.stream
        )
        
        if request.stream:
            async def generate():
                async for chunk in result:
                    yield chunk
            
            return StreamingResponse(
                generate(),
                media_type="text/plain"
            )
        
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"风险评估失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"风险评估失败: {str(e)}"
        )


@router.post("/optimize/strategy")
async def optimize_strategy(
    request: StrategyOptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """策略优化"""
    try:
        ai_service = get_ai_service()
        
        logger.info(f"用户 {current_user.username} 请求策略优化: {request.strategy_type}")
        
        result = await ai_service.optimize_strategy(
            user_id=current_user.id,
            strategy_type=request.strategy_type,
            strategy_params=request.strategy_params,
            backtest_results=request.backtest_results,
            trades_summary=request.trades_summary,
            stream=request.stream
        )
        
        if request.stream:
            async def generate():
                async for chunk in result:
                    yield chunk
            
            return StreamingResponse(
                generate(),
                media_type="text/plain"
            )
        
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"策略优化失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"策略优化失败: {str(e)}"
        )


# ==================== 聊天端点 ====================

@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """快速问答"""
    try:
        ai_service = get_ai_service()
        
        logger.info(f"用户 {current_user.username} 提问: {request.question[:50]}...")
        
        result = await ai_service.chat(
            user_id=current_user.id,
            question=request.question,
            context=request.context,
            stream=request.stream
        )
        
        if request.stream:
            async def generate():
                async for chunk in result:
                    yield chunk
            
            return StreamingResponse(
                generate(),
                media_type="text/plain"
            )
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "answer": result
            }
        }
    
    except Exception as e:
        logger.error(f"问答失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"问答失败: {str(e)}"
        )


# ==================== 健康检查端点 ====================

@router.get("/health")
async def health_check(current_user: User = Depends(get_current_user)):
    """AI服务健康检查"""
    try:
        ai_service = get_ai_service()
        result = await ai_service.health_check()
        
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"健康检查失败: {str(e)}"
        )


# ==================== 获取提示词模板 ====================

@router.get("/templates")
async def get_templates(current_user: User = Depends(get_current_user)):
    """获取可用的提示词模板"""
    from ai import PromptTemplates
    
    templates = {
        "portfolio_analysis": "持仓分析",
        "market_analysis": "市场分析",
        "indicator_analysis": "技术指标分析",
        "risk_assessment": "风险评估",
        "strategy_optimization": "策略优化",
        "quick_question": "快速问答"
    }
    
    return {
        "code": 200,
        "message": "success",
        "data": templates
    }