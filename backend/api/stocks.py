"""股票API"""
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from services.market_service import market_service
from services.data_download_service import DataDownloadService
from services.data_storage_service import DataStorageService
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


@router.get("")
async def get_stocks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sector: Optional[str] = None,
    keyword: Optional[str] = None,
    data_source: Optional[str] = None,
    use_local: bool = Query(True, description="是否使用本地已下载数据")
):
    """
    获取股票列表

    Args:
        page: 页码
        page_size: 每页数量
        sector: 板块过滤
        keyword: 关键词搜索
        data_source: 数据源 (auto/baostock/akshare/tushare/sina/tencent/eastmoney)
        use_local: 是否使用本地已下载数据（默认True）
    """
    try:
        logger.info(f"获取股票列表: page={page}, page_size={page_size}, use_local={use_local}, data_source={data_source}")
        
        # 优先使用本地数据
        if use_local:
            try:
                storage = DataStorageService()
                result = storage.get_downloaded_data_list(
                    stock_code=None,
                    limit=page_size,
                    offset=(page - 1) * page_size
                )
                
                if result['total'] > 0:
                    logger.info(f"使用本地数据: {result['total']}条记录")
                    
                    # 转换为股票列表格式
                    items = []
                    for record in result['downloads']:
                        # 读取最新一条数据作为价格信息
                        try:
                            data = storage.load_downloaded_data(
                                stock_code=record['stock_code'],
                                start_date=datetime.strptime(record['start_date'], '%Y-%m-%d'),
                                end_date=datetime.strptime(record['end_date'], '%Y-%m-%d'),
                                frequency=record['frequency']
                            )
                            
                            if data is not None and len(data) > 0:
                                latest = data.iloc[-1]
                                items.append({
                                    'code': record['stock_code'],
                                    'name': record['stock_name'] or '未知',
                                    'price': float(latest['close']),
                                    'change': float(latest['close'] - latest['open']),
                                    'change_pct': float((latest['close'] - latest['open']) / latest['open'] * 100) if latest['open'] > 0 else 0,
                                    'volume': int(latest['volume']),
                                    'amount': float(latest['close'] * latest['volume']),
                                    'market': 'SH' if '.SH' in record['stock_code'] else 'SZ',
                                })
                        except Exception as e:
                            logger.warning(f"读取数据失败: {e}")
                            continue
                    
                    # 应用过滤
                    if keyword:
                        items = [item for item in items if keyword.lower() in item['code'].lower() or keyword.lower() in (item['name'] or '').lower()]
                    
                    if sector:
                        items = [item for item in items if item.get('sector') == sector]
                    
                    return {
                        "code": 200,
                        "message": "success",
                        "data": {
                            "items": items,
                            "total": result['total'],
                            "page": page,
                            "page_size": page_size
                        }
                    }
                    
            except Exception as e:
                logger.warning(f"本地数据获取失败，使用远程数据: {e}")
        
        # 如果没有本地数据或获取失败，使用远程数据
        logger.info(f"使用远程数据获取股票列表")
        
        # 如果指定了数据源，临时切换数据源
        original_data_source = None
        if data_source and data_source != 'auto':
            original_data_source = market_service.data_fetcher.source
            market_service.data_fetcher.source = data_source
            logger.info(f"临时切换数据源为: {data_source}")

        # 从远程API获取数据
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

        # 字段名映射：中文 -> 英文
        def map_chinese_fields(stock: dict) -> dict:
            """将中文字段名映射为英文字段名"""
            field_map = {
                '代码': 'code',
                '名称': 'name',
                '最新价': 'price',
                '涨跌额': 'change',
                '涨跌幅': 'change_pct',
                '成交量': 'volume',
                '成交额': 'amount',
                '市值': 'market_cap',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '昨收': 'pre_close',
            }
            
            mapped = {}
            for cn_key, en_key in field_map.items():
                if cn_key in stock:
                    mapped[en_key] = stock[cn_key]
            
            return mapped

        # 映射所有股票的字段
        mapped_items = [map_chinese_fields(item) for item in items]

        # 恢复原始数据源
        if original_data_source:
            market_service.data_fetcher.source = original_data_source
            logger.info(f"恢复数据源为: {original_data_source}")

        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": mapped_items,
                "total": len(stocks) if not keyword else len(items),
                "page": page,
                "page_size": page_size
            }
        }

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

        # 字段名映射：中文 -> 英文
        field_map = {
            '代码': 'code',
            '名称': 'name',
            '最新价': 'price',
            '涨跌额': 'change',
            '涨跌幅': 'change_pct',
            '成交量': 'volume',
            '成交额': 'amount',
            '市值': 'market_cap',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '昨收': 'pre_close',
        }
        
        mapped_stock = {}
        for cn_key, en_key in field_map.items():
            if cn_key in stock:
                mapped_stock[en_key] = stock[cn_key]

        return {
            "code": 200,
            "message": "success",
            "data": mapped_stock
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

        # 字段名映射：中文 -> 英文
        def map_chinese_fields(stock: dict) -> dict:
            """将中文字段名映射为英文字段名"""
            field_map = {
                '代码': 'code',
                '名称': 'name',
                '最新价': 'price',
                '涨跌额': 'change',
                '涨跌幅': 'change_pct',
                '成交量': 'volume',
                '成交额': 'amount',
                '市值': 'market_cap',
            }
            
            mapped = {}
            for cn_key, en_key in field_map.items():
                if cn_key in stock:
                    mapped[en_key] = stock[cn_key]
            
            return mapped

        # 映射所有股票的字段
        mapped_stocks = [map_chinese_fields(item) for item in stocks]

        return {
            "code": 200,
            "message": "success",
            "data": mapped_stocks[:limit]
        }

    except Exception as e:
        logger.error(f"搜索股票失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="搜索股票失败"
        )
