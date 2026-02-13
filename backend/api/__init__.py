"""API模块"""
from fastapi import APIRouter
from api.stocks import router as stocks_router
from api.market import router as market_router
from api.auth import router as auth_router
from api.strategies import router as strategies_router

# 创建主路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(stocks_router, prefix="/stocks", tags=["stocks"])
api_router.include_router(market_router, prefix="/market", tags=["market"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(strategies_router, prefix="/strategies", tags=["strategies"])

__all__ = ['api_router']
