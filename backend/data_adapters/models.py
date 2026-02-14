"""统一数据模型"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StockQuote(BaseModel):
    """股票行情数据"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    price: float = Field(0.0, description="最新价")
    change: float = Field(0.0, description="涨跌额")
    change_pct: float = Field(0.0, description="涨跌幅(%)")
    open: Optional[float] = Field(None, description="开盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    pre_close: Optional[float] = Field(None, description="昨收价")
    volume: int = Field(0, description="成交量(手)")
    amount: float = Field(0.0, description="成交额(元)")
    market_cap: float = Field(0.0, description="市值(亿元)")
    turnover_rate: Optional[float] = Field(None, description="换手率(%)")
    pe: Optional[float] = Field(None, description="市盈率")
    pb: Optional[float] = Field(None, description="市净率")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "000001",
                "name": "平安银行",
                "price": 12.5,
                "change": 0.15,
                "change_pct": 1.25,
                "open": 12.35,
                "high": 12.6,
                "low": 12.3,
                "pre_close": 12.35,
                "volume": 1000000,
                "amount": 12450000.0,
                "market_cap": 2425.0
            }
        }


class KlineData(BaseModel):
    """K线数据"""
    date: datetime = Field(..., description="日期/时间")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: int = Field(..., description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-01T09:30:00",
                "open": 12.35,
                "high": 12.6,
                "low": 12.3,
                "close": 12.5,
                "volume": 1000000,
                "amount": 12450000.0
            }
        }


class StockListResponse(BaseModel):
    """股票列表响应"""
    items: List[StockQuote] = Field(..., description="股票列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class StockInfo(BaseModel):
    """股票基本信息"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    market: str = Field(..., description="市场(SH/SZ)")
    sector: Optional[str] = Field(None, description="板块")
    industry: Optional[str] = Field(None, description="行业")
    list_date: Optional[str] = Field(None, description="上市日期")
    status: Optional[str] = Field(None, description="状态")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "000001",
                "name": "平安银行",
                "market": "SZ",
                "sector": "金融",
                "industry": "银行",
                "list_date": "1991-04-03",
                "status": "正常交易"
            }
        }