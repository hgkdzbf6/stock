"""策略和回测模型"""
from sqlalchemy import Column, Integer, String, Numeric, BigInteger, DateTime, ForeignKey, JSON, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Strategy(Base):
    """策略模型"""
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, index=True)  # MA, RSI, MACD, etc.
    description = Column(String(500))
    params = Column(JSON)
    status = Column(String(20), default="active", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", backref="strategies")
    backtest_results = relationship("BacktestResult", back_populates="strategy", cascade="all, delete-orphan")


class BacktestResult(Base):
    """回测结果模型"""
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), index=True)
    stock_code = Column(String(20), index=True)
    start_date = Column(Date)
    end_date = Column(Date)
    frequency = Column(String(10))
    initial_capital = Column(Numeric(20, 2))
    final_capital = Column(Numeric(20, 2))
    total_return = Column(Numeric(10, 4))
    annual_return = Column(Numeric(10, 4))
    max_drawdown = Column(Numeric(10, 4))
    sharpe_ratio = Column(Numeric(10, 4))
    win_rate = Column(Numeric(10, 4))
    profit_loss_ratio = Column(Numeric(10, 4))
    volatility = Column(Numeric(10, 4))
    calmar_ratio = Column(Numeric(10, 4))
    trade_count = Column(Integer)
    params = Column(JSON)
    equity_curve = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    strategy = relationship("Strategy", back_populates="backtest_results")
