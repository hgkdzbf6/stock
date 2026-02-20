"""API模块"""
from fastapi import APIRouter
from api.stocks import router as stocks_router
from api.market import router as market_router
from api.auth import router as auth_router
from api.strategies import router as strategies_router
from api.ai import router as ai_router
from api.optimization import router as optimization_router
from api.trading import router as trading_router
from api.data_download import router as data_download_router
from api.stock_code import router as stock_code_router
from api.sector import router as sector_router
from api.backtest_reports import router as backtest_reports_router

# 创建主路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(stocks_router, prefix="/stocks", tags=["stocks"])
api_router.include_router(market_router, prefix="/market", tags=["market"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(strategies_router, prefix="/strategies", tags=["strategies"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(optimization_router, tags=["optimization"])
api_router.include_router(trading_router, tags=["trading"])
api_router.include_router(data_download_router, prefix="/data", tags=["data-download"])
api_router.include_router(stock_code_router, tags=["stock-code"])
api_router.include_router(sector_router, tags=["sector"])
api_router.include_router(backtest_reports_router, prefix="/backtest-reports", tags=["backtest-reports"])

__all__ = ['api_router']
