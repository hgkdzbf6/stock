"""板块API"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import csv
import pandas as pd
import akshare as ak
from loguru import logger
from services.market_service import market_service

router = APIRouter(prefix="/sector", tags=["板块"])


def load_sectors_from_csv():
    """
    从CSV文件加载板块数据
    
    Returns:
        板块数据列表
    """
    csv_path = Path(__file__).parent.parent / "data" / "sectors.csv"
    
    try:
        if not csv_path.exists():
            logger.warning(f"板块数据文件不存在: {csv_path}")
            return []
        
        sectors = []
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sectors.append({
                    "code": row.get('code', ''),
                    "name": row.get('name', ''),
                    "type": row.get('type', ''),
                    "market": row.get('market', ''),
                    "description": row.get('description', '')
                })
        
        logger.info(f"从CSV加载了 {len(sectors)} 个板块")
        return sectors
        
    except Exception as e:
        logger.error(f"从CSV加载板块数据失败: {e}")
        return []


@router.get("/list")
async def get_sector_list():
    """
    获取板块列表
    
    Returns:
        板块列表
    """
    try:
        logger.info("获取板块列表")
        
        # 从CSV文件加载板块数据
        sectors = load_sectors_from_csv()
        
        # 如果CSV为空或不存在，使用默认板块
        if not sectors:
            logger.warning("CSV板块数据为空，使用默认板块")
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
        sector_code: 板块代码（板块名称）
        page: 页码
        page_size: 每页数量
    """
    try:
        logger.info(f"获取板块股票: sector={sector_code}")
        
        # 从AkShare获取板块股票列表
        try:
            # 尝试获取行业板块股票
            df = ak.stock_board_industry_cons_em(symbol=sector_code)
        except Exception as e:
            try:
                # 如果行业板块失败，尝试获取概念板块股票
                df = ak.stock_board_concept_cons_em(symbol=sector_code)
            except Exception as e2:
                logger.warning(f"从AkShare获取板块 {sector_code} 的股票失败: {e}, {e2}")
                df = None
        
        if df is None or df.empty:
            logger.warning(f"板块 {sector_code} 没有找到股票列表")
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "items": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size
                }
            }
        
        # 转换为标准格式
        stocks = []
        for _, row in df.iterrows():
            try:
                volume_val = row.get("成交量", 0)
                if volume_val is None or (isinstance(volume_val, float) and pd.isna(volume_val)):
                    volume_val = 0
                else:
                    volume_val = int(float(volume_val))
                
                stock = {
                    "code": str(row.get("代码", "")),
                    "name": str(row.get("名称", "")),
                    "price": float(row.get("最新价", 0)) if row.get("最新价") and not pd.isna(row.get("最新价")) else 0,
                    "change": float(row.get("涨跌额", 0)) if row.get("涨跌额") and not pd.isna(row.get("涨跌额")) else 0,
                    "change_pct": float(row.get("涨跌幅", 0)) if row.get("涨跌幅") and not pd.isna(row.get("涨跌幅")) else 0,
                    "open": float(row.get("今开", 0)) if row.get("今开") and not pd.isna(row.get("今开")) else None,
                    "high": float(row.get("最高", 0)) if row.get("最高") and not pd.isna(row.get("最高")) else None,
                    "low": float(row.get("最低", 0)) if row.get("最低") and not pd.isna(row.get("最低")) else None,
                    "pre_close": float(row.get("昨收", 0)) if row.get("昨收") and not pd.isna(row.get("昨收")) else None,
                    "volume": volume_val,
                    "amount": float(row.get("成交额", 0)) if row.get("成交额") and not pd.isna(row.get("成交额")) else 0,
                    "market_cap": float(row.get("总市值", 0)) / 100000000 if row.get("总市值") and not pd.isna(row.get("总市值")) else 0,
                    "pe": float(row.get("市盈率-动态", 0)) if row.get("市盈率-动态") and not pd.isna(row.get("市盈率-动态")) else None,
                    "pb": float(row.get("市净率", 0)) if row.get("市净率") and not pd.isna(row.get("市净率")) else None,
                }
                stocks.append(stock)
            except Exception as e:
                logger.warning(f"处理股票数据失败: {e}, 跳过该股票")
                continue
        
        # 分页
        total = len(stocks)
        start = (page - 1) * page_size
        end = start + page_size
        paged_stocks = stocks[start:end]
        
        logger.info(f"获取板块 {sector_code} 股票成功: {len(paged_stocks)} 只，总计: {total}")
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": paged_stocks,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }
        
    except Exception as e:
        logger.error(f"获取板块股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sector_code}/kline")
async def get_sector_kline(
    sector_code: str,
    freq: str = Query("daily", pattern="^(1min|5min|15min|30min|60min|daily)$"),
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD")
):
    """
    获取板块K线数据
    
    Args:
        sector_code: 板块代码
        freq: 频率 (1min, 5min, 15min, 30min, 60min, daily)
        start_date: 开始日期
        end_date: 结束日期
    """
    try:
        logger.info(f"获取板块K线数据: {sector_code}, freq={freq}")
        
        # 转换日期格式为YYYYMMDD
        start_date_yyyymmdd = start_date.replace("-", "")
        end_date_yyyymmdd = end_date.replace("-", "")
        
        # 使用AkShare获取真实的板块历史数据
        try:
            # 尝试获取行业板块历史数据
            df = ak.stock_board_industry_hist_em(
                symbol=sector_code,
                start_date=start_date_yyyymmdd,
                end_date=end_date_yyyymmdd,
                adjust="qfq"
            )
            data_source = "行业板块历史"
        except Exception as e:
            try:
                # 如果行业板块失败，尝试获取概念板块历史数据
                df = ak.stock_board_concept_hist_em(
                    symbol=sector_code,
                    start_date=start_date_yyyymmdd,
                    end_date=end_date_yyyymmdd,
                    adjust="qfq"
                )
                data_source = "概念板块历史"
            except Exception as e2:
                logger.warning(f"从AkShare获取板块 {sector_code} 的K线失败: {e}, {e2}")
                df = None
                data_source = None
        
        if df is None or df.empty:
            # 如果AkShare没有板块历史数据，尝试使用板块代码作为股票代码
            logger.warning(f"板块 {sector_code} 没有找到历史数据，尝试使用股票代码")
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                kline_data = await market_service.get_kline_data(
                    sector_code, start_dt, end_dt, freq
                )
                logger.info(f"使用股票代码 {sector_code} 获取K线数据成功")
                return {
                    "code": 200,
                    "message": "success",
                    "data": kline_data
                }
            except Exception as e:
                # 如果都失败，使用上证指数作为替代
                logger.warning(f"使用板块代码获取K线失败，使用上证指数作为替代: {e}")
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                kline_data = await market_service.get_kline_data(
                    "SH000001", start_dt, end_dt, freq
                )
                return {
                    "code": 200,
                    "message": "success",
                    "data": kline_data
                }
        
        # 转换为标准格式
        kline_data = []
        for _, row in df.iterrows():
            try:
                kline_point = {
                    "date": row.get("日期"),
                    "open": float(row.get("开盘", 0)) if row.get("开盘") and not pd.isna(row.get("开盘")) else 0,
                    "high": float(row.get("最高", 0)) if row.get("最高") and not pd.isna(row.get("最高")) else 0,
                    "low": float(row.get("最低", 0)) if row.get("最低") and not pd.isna(row.get("最低")) else 0,
                    "close": float(row.get("收盘", 0)) if row.get("收盘") and not pd.isna(row.get("收盘")) else 0,
                    "volume": int(float(row.get("成交量", 0))) if row.get("成交量") and not pd.isna(row.get("成交量")) else 0,
                }
                kline_data.append(kline_point)
            except Exception as e:
                logger.warning(f"处理K线数据失败: {e}, 跳过该数据点")
                continue
        
        # 按日期排序
        kline_data.sort(key=lambda x: x["date"])
        
        logger.info(f"获取板块 {sector_code} K线数据成功: {len(kline_data)} 条（来源: {data_source}）")
        
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
        logger.error(f"获取板块K线数据失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取板块K线数据失败"
        )


def convert_sector_to_index_code(sector_code: str) -> Optional[str]:
    """
    将板块代码转换为指数代码
    
    Args:
        sector_code: 板块代码
    
    Returns:
        指数代码（如果有的话）
    """
    # 一些常见板块的指数代码映射
    sector_index_map = {
        "银行": "SH399986",  # 中证银行指数
        "医药": "SH000932",  # 医药生物指数
        "白酒": "SZ399997",  # 中证白酒指数
        "房地产": "SH000932",  # 房地产指数
        "科技": "SZ399615",  # 创业板指
        "消费": "SH000932",  # 消费指数
        "金融": "SH000016",  # 上证50（金融权重高）
        "新能源": "SZ399976",  # 中证新能源指数
        "军工": "SZ399967",  # 中证军工指数
        "汽车": "SZ399006",  # 汽车指数
    }
    
    return sector_index_map.get(sector_code)


async def calculate_sector_index(
    sector_code: str,
    start_date: datetime,
    end_date: datetime,
    freq: str
) -> List[dict]:
    """
    计算板块指数（基于板块内股票）
    
    Args:
        sector_code: 板块代码
        start_date: 开始日期
        end_date: 结束日期
        freq: 频率
    
    Returns:
        板块指数K线数据
    """
    try:
        # TODO: 实现从数据库或股票代码服务获取板块内股票列表
        # 这里暂时返回空数据，等待板块-股票映射表完善
        
        # 暂时使用市场指数作为替代
        logger.warning(f"板块 {sector_code} 暂无对应指数，使用上证指数作为替代")
        return await market_service.get_kline_data(
            "SH000001", start_date, end_date, freq
        )
        
    except Exception as e:
        logger.error(f"计算板块指数失败: {e}")
        raise
