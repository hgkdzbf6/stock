"""行情数据模型"""
from sqlalchemy import Column, Integer, String, Numeric, BigInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Quote(Base):
    """行情数据模型"""
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    close = Column(Numeric(10, 2))
    volume = Column(BigInteger)
    amount = Column(Numeric(20, 2))
    frequency = Column(String(10), index=True)  # 1min, 5min, 15min, 30min, 60min, daily
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    stock = relationship("Stock", backref="quotes")

    __table_args__ = (
        # 索引优化
        {"mysql_engine": "InnoDB"},
    )
