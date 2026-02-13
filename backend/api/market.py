"""行情API"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from services.market_service import market_service
from loguru import logger

router = APIRouter()


class QuoteResponse(BaseModel):
    """行情响应"""
    stock_code: str
    price: float
    change: float
    change_pct: float
    open: float
    high: float
    low: float
    volume: int
    timestamp: str


class KlineData(BaseModel):
    """K线数据"""
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int


@router.get("/quote/{code}", response_model=QuoteResponse)
async def get_quote(code: str):
    """
    获取实时行情

    Args:
        code: 股票代码
    """
    try:
        logger.info(f"获取实时行情: {code}")

        quote = await market_service.get_realtime_quote(code)

        if not quote:
            raise HTTPException(
                status_code=404,
                detail="未找到行情数据"
            )

        return quote

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取实时行情失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取实时行情失败"
        )


@router.get("/kline/{code}")
async def get_kline(
    code: str,
    freq: str = Query("daily", regex="^(1min|5min|15min|30min|60min|daily)$"),
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD")
):
    """
    获取K线数据

    Args:
        code: 股票代码
        freq: 频率 (1min, 5min, 15min, 30min, 60min, daily)
        start_date: 开始日期
        end_date: 结束日期
    """
    try:
        logger.info(f"获取K线数据: {code}, freq={freq}")

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        kline_data = await market_service.get_kline_data(
            code, start_dt, end_dt, freq
        )

        return {
            "code": 200,
            "message": "success",
            "data": kline_data
        }

    except ValueError as e:
        logger.error(f"日期格式错误: {e}")
        raise HTTPException(
            status_code=400,
            detail="日期格式错误，请使用 YYYY-MM-DD 格式"
        )
    except Exception as e:
        logger.error(f"获取K线数据失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取K线数据失败"
        )


@router.get("/indicators/{code}")
async def get_indicators(
    code: str,
    freq: str = Query("daily", regex="^(1min|5min|15min|30min|60min|daily)$"),
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    indicators: List[str] = Query(
        ["MA", "BOLL"],
        description="指标列表: MA, BOLL, RSI, MACD, KDJ"
    )
):
    """
    获取技术指标

    Args:
        code: 股票代码
        freq: 频率
        start_date: 开始日期
        end_date: 结束日期
        indicators: 指标列表
    """
    try:
        logger.info(f"获取技术指标: {code}, indicators={indicators}")

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        indicator_data = await market_service.get_indicators(
            code, start_dt, end_dt, freq, indicators
        )

        return {
            "code": 200,
            "message": "success",
            "data": indicator_data
        }

    except ValueError as e:
        logger.error(f"日期格式错误: {e}")
        raise HTTPException(
            status_code=400,
            detail="日期格式错误，请使用 YYYY-MM-DD 格式"
        )
    except Exception as e:
        logger.error(f"获取技术指标失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取技术指标失败"
        )


@router.get("/batch")
async def get_batch_quotes(codes: str = Query(..., description="股票代码，逗号分隔")):
    """
    批量获取实时行情

    Args:
        codes: 股票代码，逗号分隔，如 600771,000001
    """
    try:
        logger.info(f"批量获取行情: {codes}")

        code_list = codes.split(',')
        quotes = []

        for code in code_list:
            code = code.strip()
            try:
                quote = await market_service.get_realtime_quote(code)
                if quote:
                    quotes.append(quote)
            except Exception as e:
                logger.warning(f"获取股票 {code} 行情失败: {e}")
                continue

        return {
            "code": 200,
            "message": "success",
            "data": quotes
        }

    except Exception as e:
        logger.error(f"批量获取行情失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="批量获取行情失败"
        )
