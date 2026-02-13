"""股票API"""
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from services.market_service import market_service
from loguru import logger

router = APIRouter()


class StockInfo(BaseModel):
    """股票信息"""
    id: int
    code: str
    name: str
    market: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    list_date: Optional[str] = None


class StockListResponse(BaseModel):
    """股票列表响应"""
    items: List[dict]
    total: int
    page: int
    page_size: int


@router.get("", response_model=StockListResponse)
async def get_stocks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sector: Optional[str] = None,
    keyword: Optional[str] = None
):
    """
    获取股票列表

    Args:
        page: 页码
        page_size: 每页数量
        sector: 板块过滤
        keyword: 关键词搜索
    """
    try:
        logger.info(f"获取股票列表: page={page}, page_size={page_size}")

        # TODO: 从数据库获取股票列表
        # 这里临时使用模拟数据
        if keyword:
            # 搜索股票
            stocks = await market_service.data_fetcher.search_stocks(keyword)
            items = stocks[:page_size]
        else:
            # 获取全部股票列表
            stocks = await market_service.data_fetcher.get_stock_list()
            # 分页
            start = (page - 1) * page_size
            end = start + page_size
            items = stocks[start:end]

        return StockListResponse(
            items=items,
            total=len(stocks) if not keyword else len(items),
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取股票列表失败"
        )


@router.get("/{code}")
async def get_stock(code: str):
    """
    获取股票详情

    Args:
        code: 股票代码
    """
    try:
        logger.info(f"获取股票详情: {code}")

        # TODO: 从数据库获取股票详情
        # 这里临时返回模拟数据
        stocks = await market_service.data_fetcher.get_stock_list()
        stock = None

        for s in stocks:
            if str(s.get('代码')) == code or str(s.get('代码')) == code.replace('.SH', '').replace('.SZ', ''):
                stock = s
                break

        if not stock:
            raise HTTPException(
                status_code=404,
                detail="股票不存在"
            )

        return {
            "code": 200,
            "message": "success",
            "data": stock
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票详情失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取股票详情失败"
        )


@router.get("/search/{keyword}")
async def search_stocks(keyword: str, limit: int = Query(20, ge=1, le=100)):
    """
    搜索股票

    Args:
        keyword: 搜索关键词
        limit: 返回数量限制
    """
    try:
        logger.info(f"搜索股票: {keyword}")

        stocks = await market_service.data_fetcher.search_stocks(keyword)

        return {
            "code": 200,
            "message": "success",
            "data": stocks[:limit]
        }

    except Exception as e:
        logger.error(f"搜索股票失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="搜索股票失败"
        )
