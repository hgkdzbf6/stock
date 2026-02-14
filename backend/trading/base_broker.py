"""
券商接口基类
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class OrderSide(str, Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """订单类型"""
    MARKET = "market"  # 市价单
    LIMIT = "limit"    # 限价单
    STOP = "stop"      # 止损单
    STOP_LIMIT = "stop_limit"  # 止损限价单


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "pending"          # 待提交
    SUBMITTED = "submitted"      # 已提交
    PARTIAL_FILLED = "partial_filled"  # 部分成交
    FILLED = "filled"            # 全部成交
    CANCELLED = "cancelled"      # 已撤销
    REJECTED = "rejected"        # 已拒绝
    EXPIRED = "expired"          # 已过期


@dataclass
class Order:
    """订单数据类"""
    id: str
    user_id: int
    stock_code: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    filled_quantity: int = 0
    avg_fill_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    commission: float = 0.0
    remark: Optional[str] = None
    broker_order_id: Optional[str] = None
    created_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None


@dataclass
class Trade:
    """成交记录数据类"""
    id: str
    order_id: str
    stock_code: str
    side: OrderSide
    price: float
    quantity: int
    amount: float
    commission: float
    timestamp: datetime
    broker_trade_id: Optional[str] = None


@dataclass
class Position:
    """持仓数据类"""
    id: int
    user_id: int
    stock_code: str
    quantity: int
    available_quantity: int
    cost_price: float
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    pnl_amount: Optional[float] = None
    pnl_ratio: Optional[float] = None


@dataclass
class Account:
    """账户数据类"""
    id: int
    user_id: int
    broker: str
    broker_account_id: str
    total_assets: float
    available_cash: float
    frozen_cash: float
    market_value: float
    pnl_amount: float
    pnl_ratio: float


class BaseBroker(ABC):
    """券商接口基类"""
    
    def __init__(self, broker_config: Dict[str, Any]):
        """
        初始化券商接口
        
        Args:
            broker_config: 券商配置
        """
        self.broker_config = broker_config
        self.is_connected = False
        self.session_id: Optional[str] = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """
        连接券商服务器
        
        Returns:
            连接是否成功
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        断开连接
        
        Returns:
            断开是否成功
        """
        pass
    
    @abstractmethod
    async def login(self, user_id: str, password: str) -> bool:
        """
        登录
        
        Args:
            user_id: 用户ID
            password: 密码
            
        Returns:
            登录是否成功
        """
        pass
    
    @abstractmethod
    async def logout(self) -> bool:
        """
        登出
        
        Returns:
            登出是否成功
        """
        pass
    
    @abstractmethod
    async def submit_order(self, order: Order) -> str:
        """
        提交订单
        
        Args:
            order: 订单对象
            
        Returns:
            券商订单ID
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str, broker_order_id: str) -> bool:
        """
        撤销订单
        
        Args:
            order_id: 系统订单ID
            broker_order_id: 券商订单ID
            
        Returns:
            撤销是否成功
        """
        pass
    
    @abstractmethod
    async def query_order(self, broker_order_id: str) -> Optional[Order]:
        """
        查询订单状态
        
        Args:
            broker_order_id: 券商订单ID
            
        Returns:
            订单对象
        """
        pass
    
    @abstractmethod
    async def query_orders(
        self,
        stock_code: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Order]:
        """
        查询订单列表
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            订单列表
        """
        pass
    
    @abstractmethod
    async def query_trades(
        self,
        stock_code: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Trade]:
        """
        查询成交记录
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            成交记录列表
        """
        pass
    
    @abstractmethod
    async def query_positions(self) -> List[Position]:
        """
        查询持仓
        
        Returns:
            持仓列表
        """
        pass
    
    @abstractmethod
    async def query_account(self) -> Account:
        """
        查询账户信息
        
        Returns:
            账户信息
        """
        pass
    
    @abstractmethod
    async def query_market_depth(self, stock_code: str) -> Dict[str, Any]:
        """
        查询市场深度
        
        Args:
            stock_code: 股票代码
            
        Returns:
            市场深度数据
        """
        pass
    
    @abstractmethod
    async def subscribe_market_data(self, stock_codes: List[str]) -> bool:
        """
        订阅行情数据
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            订阅是否成功
        """
        pass
    
    @abstractmethod
    async def unsubscribe_market_data(self, stock_codes: List[str]) -> bool:
        """
        取消订阅行情数据
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            取消订阅是否成功
        """
        pass
    
    def is_connected_check(self) -> bool:
        """
        检查是否已连接
        
        Returns:
            是否已连接
        """
        return self.is_connected
    
    async def reconnect(self) -> bool:
        """
        重连
        
        Returns:
            重连是否成功
        """
        await self.disconnect()
        await self.connect()
        return self.is_connected