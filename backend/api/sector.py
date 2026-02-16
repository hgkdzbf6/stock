"""板块API"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from loguru import logger

router = APIRouter(prefix="/sector", tags=["板块"])


@router.get("/list")
async def get_sector_list():
    """
    获取板块列表
    
    Returns:
        板块列表
    """
    try:
        logger.info("获取板块列表")
        
        # 提供常用板块
        sectors = [
            {"code": "医药", "name": "医药", "description": "医药生物板块"},
            {"code": "银行", "name": "银行", "description": "银行板块"},
            {"code": "白酒", "name": "白酒", "description": "白酒板块"},
            {"code": "房地产", "name": "房地产", "description": "房地产板块"},
            {"code": "科技", "name": "科技", "description": "科技板块"},
            {"code": "消费", "name": "消费", "description": "消费板块"},
            {"code": "金融", "name": "金融", "description": "金融板块"},
            {"code": "新能源", "name": "新能源", "description": "新能源板块"},
            {"code": "军工", "name": "军工", "description": "军工板块"},
            {"code": "汽车", "name": "汽车", "description": "汽车板块"},
            {"code": "化工", "name": "化工", "description": "化工板块"},
            {"code": "钢铁", "name": "钢铁", "description": "钢铁板块"},
            {"code": "有色金属", "name": "有色金属", "description": "有色金属板块"},
            {"code": "煤炭", "name": "煤炭", "description": "煤炭板块"},
            {"code": "电力", "name": "电力", "description": "电力板块"},
        ]
        
        return {
            "code": 200,
            "message": "success",
            "data": sectors
        }
        
    except Exception as e:
        logger.error(f"获取板块列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sector_code}/stocks")
async def get_stocks_by_sector(
    sector_code: str,
    page: int = 1,
    page_size: int = 20
):
    """
    根据板块获取股票列表
    
    Args:
        sector_code: 板块代码
        page: 页码
        page_size: 每页数量
    """
    try:
        logger.info(f"获取板块股票: sector={sector_code}")
        
        # TODO: 从股票代码服务或数据库获取板块下的股票
        # 这里可以扩展，根据板块名称从stock_list中筛选
        # 或者维护一个板块-股票映射表
        
        stocks = []
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": stocks,
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        }
        
    except Exception as e:
        logger.error(f"获取板块股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))