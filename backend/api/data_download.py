"""数据下载API - 提供数据下载和管理接口"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from loguru import logger

from services.data_download_service import DataDownloadService


router = APIRouter(tags=["数据下载"])


# 初始化服务
download_service = DataDownloadService()


# 请求模型
class DownloadRequest(BaseModel):
    """数据下载请求"""
    stock_code: str = Field(..., description="股票代码")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    frequency: str = Field("daily", description="数据频率: daily, 1d, 1min, 5min, 15min, 30min, 60min")
    source: str = Field("auto", description="数据源: auto, tushare, akshare, baostock, sina, tencent, eastmoney")
    force_download: bool = Field(False, description="是否强制重新下载")


class BatchDownloadRequest(BaseModel):
    """批量下载请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    frequency: str = Field("daily", description="数据频率")
    source: str = Field("auto", description="数据源")


class CheckDataRequest(BaseModel):
    """检查数据请求"""
    stock_code: str = Field(..., description="股票代码")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    frequency: str = Field("daily", description="数据频率")


# 响应模型
class DownloadResponse(BaseModel):
    """下载响应"""
    status: str  # completed, exists, partial_overlap, failed
    message: str
    download_id: str
    stock_code: str
    stock_name: Optional[str] = None
    data_count: Optional[int] = None
    record_id: Optional[int] = None
    existing_data: Optional[dict] = None


class BatchDownloadResponse(BaseModel):
    """批量下载响应"""
    total: int
    success: int
    failed: int
    results: List[dict]


class DownloadedListResponse(BaseModel):
    """已下载数据列表响应"""
    downloads: List[dict]
    total: int


class CheckDataResponse(BaseModel):
    """检查数据响应"""
    available: bool
    overlap_type: Optional[str] = None  # exact, partial
    existing_data: Optional[dict] = None


class DeleteDataResponse(BaseModel):
    """删除数据响应"""
    status: str
    message: str
    record_id: int


class StatisticsResponse(BaseModel):
    """统计信息响应"""
    total_downloads: int
    unique_stocks: int
    total_data_points: int
    total_file_size: int
    total_file_size_str: str
    frequency_distribution: dict


@router.post("/download", response_model=DownloadResponse)
async def download_stock_data(request: DownloadRequest):
    """
    下载股票数据
    
    - 如果数据已存在且完全匹配，返回已有数据
    - 如果数据部分重叠，提示用户
    - 如果数据不存在，下载数据并保存
    """
    try:
        # 解析日期
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        logger.info(f"下载请求: {request.stock_code}, {request.start_date} - {request.end_date}")
        
        # 调用下载服务
        result = await download_service.download_stock_data(
            stock_code=request.stock_code,
            start_date=start_date,
            end_date=end_date,
            frequency=request.frequency,
            source=request.source,
            force_download=request.force_download
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"日期格式错误: {e}")
        raise HTTPException(status_code=400, detail=f"日期格式错误，请使用YYYY-MM-DD格式: {str(e)}")
    except Exception as e:
        logger.error(f"下载失败: {e}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.post("/batch-download", response_model=BatchDownloadResponse)
async def batch_download_stock_data(request: BatchDownloadRequest):
    """批量下载股票数据"""
    try:
        # 解析日期
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        logger.info(f"批量下载请求: {len(request.stock_codes)}只股票")
        
        # 调用批量下载服务
        result = await download_service.batch_download(
            stock_codes=request.stock_codes,
            start_date=start_date,
            end_date=end_date,
            frequency=request.frequency,
            source=request.source
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"日期格式错误: {e}")
        raise HTTPException(status_code=400, detail=f"日期格式错误: {str(e)}")
    except Exception as e:
        logger.error(f"批量下载失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量下载失败: {str(e)}")


@router.get("/check", response_model=CheckDataResponse)
async def check_data_availability(
    stock_code: str,
    start_date: str,
    end_date: str,
    frequency: str = "daily"
):
    """
    检查数据是否可用
    
    返回数据是否存在以及重叠类型
    """
    try:
        # 解析日期
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        logger.info(f"检查数据: {stock_code}, {start_date} - {end_date}")
        
        # 调用检查服务
        result = await download_service.check_data_availability(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"日期格式错误: {e}")
        raise HTTPException(status_code=400, detail=f"日期格式错误: {str(e)}")
    except Exception as e:
        logger.error(f"检查数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"检查数据失败: {str(e)}")


@router.get("/downloads", response_model=DownloadedListResponse)
async def get_downloaded_data_list(
    stock_code: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    获取已下载数据列表
    
    - stock_code: 可选，过滤指定股票
    - limit: 返回数量限制
    - offset: 偏移量
    """
    try:
        logger.info(f"获取已下载数据列表: stock_code={stock_code}, limit={limit}")
        
        # 调用服务
        result = await download_service.get_downloaded_data_list(
            stock_code=stock_code,
            limit=limit,
            offset=offset
        )
        
        return result
        
    except Exception as e:
        logger.error(f"获取数据列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据列表失败: {str(e)}")


@router.delete("/downloads/{record_id}", response_model=DeleteDataResponse)
async def delete_downloaded_data(record_id: int):
    """删除已下载数据"""
    try:
        logger.info(f"删除数据: record_id={record_id}")
        
        # 调用服务
        result = await download_service.delete_downloaded_data(record_id)
        
        return result
        
    except Exception as e:
        logger.error(f"删除数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除数据失败: {str(e)}")


@router.get("/statistics", response_model=StatisticsResponse)
async def get_download_statistics():
    """获取下载统计信息"""
    try:
        logger.info("获取下载统计信息")
        
        # 调用服务
        result = download_service.get_statistics()
        
        return result
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/status/{download_id}")
async def get_download_status(download_id: str):
    """获取下载状态"""
    try:
        logger.info(f"获取下载状态: {download_id}")
        
        # 调用服务
        result = await download_service.get_download_status(download_id)
        
        return result
        
    except Exception as e:
        logger.error(f"获取下载状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取下载状态失败: {str(e)}")