"""股票模型"""
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from core.database import Base


class Stock(Base):
    """股票模型"""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    market = Column(String(10), nullable=False)  # SH, SZ
    sector = Column(String(50), index=True)
    industry = Column(String(100))
    list_date = Column(Date)
    status = Column(String(20), default="active", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
