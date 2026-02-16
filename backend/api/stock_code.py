"""股票代码搜索API"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from loguru import logger

from services.stock_code_service import stock_code_service
from services.data_fetcher import DataFetcher

router = APIRouter(prefix="/stock-code", tags=["股票代码"])

# 初始化数据获取器（使用akshare获取完整股票列表）
data_fetcher = DataFetcher(source='akshare')


@router.post("/download")
async def download_stock_list(page: int = 1, page_size: int = 5000):
    """
    下载股票列表到本地
    
    Args:
        page: 页码（默认1）
        page_size: 每页数量（默认5000）
        
    Returns:
        下载结果
    """
    try:
        logger.info(f"下载股票列表: page={page}, page_size={page_size}")
        
        # 分批获取所有股票
        all_stocks = []
        current_page = page
        total_count = 0
        
        while True:
            # 获取一页数据
            stocks = await data_fetcher.get_stock_list(
                page=current_page,
                page_size=page_size
            )
            
            if not stocks:
                break
            
            all_stocks.extend(stocks)
            total_count = len(all_stocks)
            logger.info(f"已获取 {total_count} 只股票")
            
            # 如果获取的数据少于请求的数量，说明已经获取完所有数据
            if len(stocks) < page_size:
                break
            
            current_page += 1
            
            # 防止无限循环
            if current_page > 100:
                logger.warning("已达到最大页数限制")
                break
        
        # 保存到本地
        success = stock_code_service.save_stock_list(all_stocks)
        
        return {
            "success": success,
            "message": f"成功下载并保存 {len(all_stocks)} 只股票",
            "total": len(all_stocks),
            "data_file": "data/stock_list.csv"
        }
        
    except Exception as e:
        logger.error(f"下载股票列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_stocks(
    keyword: str,
    search_type: str = "fuzzy",
    limit: int = 10
):
    """
    搜索股票
    
    Args:
        keyword: 搜索关键词
        search_type: 搜索类型 ('fuzzy', 'code', 'name', 'prefix')
        limit: 返回数量限制
        
    Returns:
        搜索结果
    """
    try:
        logger.info(f"搜索股票: keyword={keyword}, type={search_type}, limit={limit}")
        
        if search_type == "code":
            results = stock_code_service.search_by_code(keyword, limit)
        elif search_type == "name":
            results = stock_code_service.search_by_name(keyword, limit)
        elif search_type == "prefix":
            results = stock_code_service.search_by_prefix(keyword, limit)
        else:  # fuzzy
            results = stock_code_service.fuzzy_search(keyword, limit)
        
        return {
            "success": True,
            "keyword": keyword,
            "search_type": search_type,
            "total": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"搜索股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{code}")
async def get_stock_info(code: str):
    """
    获取股票详细信息
    
    Args:
        code: 股票代码
        
    Returns:
        股票信息
    """
    try:
        logger.info(f"获取股票信息: {code}")
        
        stock_info = stock_code_service.get_stock_info(code)
        
        if not stock_info:
            raise HTTPException(status_code=404, detail=f"未找到股票: {code}")
        
        return {
            "success": True,
            "data": stock_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/{market}")
async def get_stocks_by_market(market: str, limit: int = 100):
    """
    根据市场获取股票列表
    
    Args:
        market: 市场名称 ('沪市主板', '深市主板', '科创板', '创业板', '北交所')
        limit: 返回数量限制
        
    Returns:
        股票列表
    """
    try:
        logger.info(f"获取市场股票: market={market}, limit={limit}")
        
        results = stock_code_service.get_stocks_by_market(market, limit)
        
        return {
            "success": True,
            "market": market,
            "total": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"获取市场股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics():
    """
    获取股票列表统计信息
    
    Returns:
        统计信息
    """
    try:
        logger.info("获取股票统计信息")
        
        stats = stock_code_service.get_statistics()
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_stock_list():
    """
    刷新股票列表（重新加载）
    
    Returns:
        刷新结果
    """
    try:
        logger.info("刷新股票列表")
        
        success = stock_code_service.refresh()
        
        return {
            "success": success,
            "message": "股票列表已刷新" if success else "刷新失败"
        }
        
    except Exception as e:
        logger.error(f"刷新股票列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prefix")
async def search_by_prefix(
    prefix: str,
    search_field: str = "name",
    limit: int = 10
):
    """
    根据前缀搜索股票
    
    Args:
        prefix: 前缀字符
        search_field: 搜索字段 ('name' 或 'code')
        limit: 返回数量限制
        
    Returns:
        搜索结果
    """
    try:
        logger.info(f"前缀搜索: prefix={prefix}, field={search_field}, limit={limit}")
        
        results = stock_code_service.search_by_prefix(prefix, limit, search_field)
        
        return {
            "success": True,
            "prefix": prefix,
            "search_field": search_field,
            "total": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"前缀搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/name/{name}")
async def search_by_name(name: str, limit: int = 10):
    """
    根据名称搜索股票
    
    Args:
        name: 股票名称
        limit: 返回数量限制
        
    Returns:
        搜索结果
    """
    try:
        logger.info(f"名称搜索: name={name}, limit={limit}")
        
        results = stock_code_service.search_by_name(name, limit)
        
        return {
            "success": True,
            "name": name,
            "total": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"名称搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/code/{code}")
async def search_by_code(code: str, limit: int = 10):
    """
    根据代码搜索股票
    
    Args:
        code: 股票代码
        limit: 返回数量限制
        
    Returns:
        搜索结果
    """
    try:
        logger.info(f"代码搜索: code={code}, limit={limit}")
        
        results = stock_code_service.search_by_code(code, limit)
        
        return {
            "success": True,
            "code": code,
            "total": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"代码搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))