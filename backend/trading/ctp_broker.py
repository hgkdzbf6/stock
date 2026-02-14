"""
CTP券商接口适配器（模拟实现）
主要用于期货交易
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import uuid

from .base_broker import (
    BaseBroker,
    Order,
    Trade,
    Position,
    Account,
    OrderSide,
    OrderType,
    OrderStatus,
)


class CTPBroker(BaseBroker):
    """CTP券商接口适配器（模拟实现）"""
    
    def __init__(self, broker_config: Dict[str, Any]):
        """
        初始化CTP接口
        
        Args:
            broker_config: 券商配置
                - broker_id: 券商ID
                - account: 账号
                - password: 密码
                - trading_server: 交易服务器地址
                - trading_port: 交易服务器端口
                - quote_server: 行情服务器地址
                - quote_port: 行情服务器端口
        """
        super().__init__(broker_config)
        self.broker_id = broker_config.get("broker_id")
        self.account = broker_config.get("account")
        self.password = broker_config.get("password")
        self.trading_server = broker_config.get("trading_server")
        self.trading_port = broker_config.get("trading_port")
        self.quote_server = broker_config.get("quote_server")
        self.quote_port = broker_config.get("quote_port")
        
        # 模拟数据存储
        self._orders: Dict[str, Order] = {}
        self._trades: Dict[str, Trade] = {}
        self._positions: Dict[str, Position] = {}
        self._account: Optional[Account] = None
        
    async def connect(self) -> bool:
        """连接CTP服务器（模拟）"""
        try:
            await asyncio.sleep(0.5)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"CTP连接失败: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开CTP连接（模拟）"""
        try:
            if self.is_connected:
                await asyncio.sleep(0.2)
                self.is_connected = False
            return True
        except Exception as e:
            print(f"CTP断开连接失败: {e}")
            return False
    
    async def login(self, user_id: str, password: str) -> bool:
        """登录CTP（模拟）"""
        try:
            if not self.is_connected:
                return False
            
            await asyncio.sleep(0.3)
            self.session_id = str(uuid.uuid4())
            
            # 初始化模拟账户数据（期货账户）
            self._account = Account(
                id=1,
                user_id=int(user_id),
                broker="CTP",
                broker_account_id=self.account,
                total_assets=500000.0,
                available_cash=300000.0,
                frozen_cash=20000.0,
                market_value=200000.0,
                pnl_amount=5000.0,
                pnl_ratio=0.01,
            )
            
            return True
        except Exception as e:
            print(f"CTP登录失败: {e}")
            return False
    
    async def logout(self) -> bool:
        """登出CTP（模拟）"""
        try:
            await asyncio.sleep(0.2)
            self.session_id = None
            return True
        except Exception as e:
            print(f"CTP登出失败: {e}")
            return False
    
    async def submit_order(self, order: Order) -> str:
        """提交订单（模拟）"""
        try:
            if not self.is_connected:
                raise Exception("CTP未连接")
            
            await asyncio.sleep(0.1)
            broker_order_id = f"CTP_{uuid.uuid4().hex[:12]}"
            
            order.broker_order_id = broker_order_id
            order.status = OrderStatus.SUBMITTED
            order.submitted_at = datetime.now()
            
            # 模拟订单成交
            if order.order_type == OrderType.MARKET:
                order.status = OrderStatus.FILLED
                order.filled_quantity = order.quantity
                order.avg_fill_price = order.price or 3000.0
                order.filled_at = datetime.now()
                
                trade = Trade(
                    id=f"TRADE_{uuid.uuid4().hex[:12]}",
                    order_id=order.id,
                    stock_code=order.stock_code,
                    side=order.side,
                    price=order.avg_fill_price,
                    quantity=order.filled_quantity,
                    amount=order.avg_fill_price * order.filled_quantity,
                    commission=order.avg_fill_price * order.filled_quantity * 0.0001,
                    timestamp=datetime.now(),
                    broker_trade_id=f"CTPT_{uuid.uuid4().hex[:12]}",
                )
                self._trades[trade.id] = trade
            
            self._orders[order.id] = order
            return broker_order_id
        except Exception as e:
            print(f"CTP提交订单失败: {e}")
            raise
    
    async def cancel_order(self, order_id: str, broker_order_id: str) -> bool:
        """撤销订单（模拟）"""
        try:
            await asyncio.sleep(0.1)
            order = self._orders.get(order_id)
            if order:
                order.status = OrderStatus.CANCELLED
                order.cancelled_at = datetime.now()
            return True
        except Exception as e:
            print(f"CTP撤销订单失败: {e}")
            return False
    
    async def query_order(self, broker_order_id: str) -> Optional[Order]:
        """查询订单状态（模拟）"""
        try:
            await asyncio.sleep(0.05)
            for order in self._orders.values():
                if order.broker_order_id == broker_order_id:
                    return order
            return None
        except Exception as e:
            print(f"CTP查询订单失败: {e}")
            return None
    
    async def query_orders(
        self,
        stock_code: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Order]:
        """查询订单列表（模拟）"""
        try:
            await asyncio.sleep(0.1)
            orders = list(self._orders.values())
            
            if stock_code:
                orders = [o for o in orders if o.stock_code == stock_code]
            if start_date:
                orders = [o for o in orders if o.created_at and o.created_at >= start_date]
            if end_date:
                orders = [o for o in orders if o.created_at and o.created_at <= end_date]
            
            return orders
        except Exception as e:
            print(f"CTP查询订单列表失败: {e}")
            return []
    
    async def query_trades(
        self,
        stock_code: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Trade]:
        """查询成交记录（模拟）"""
        try:
            await asyncio.sleep(0.1)
            trades = list(self._trades.values())
            
            if stock_code:
                trades = [t for t in trades if t.stock_code == stock_code]
            if start_date:
                trades = [t for t in trades if t.timestamp >= start_date]
            if end_date:
                trades = [t for t in trades if t.timestamp <= end_date]
            
            return trades
        except Exception as e:
            print(f"CTP查询成交记录失败: {e}")
            return []
    
    async def query_positions(self) -> List[Position]:
        """查询持仓（模拟）"""
        try:
            await asyncio.sleep(0.1)
            return list(self._positions.values())
        except Exception as e:
            print(f"CTP查询持仓失败: {e}")
            return []
    
    async def query_account(self) -> Account:
        """查询账户信息（模拟）"""
        try:
            await asyncio.sleep(0.1)
            if not self._account:
                raise Exception("账户未初始化")
            return self._account
        except Exception as e:
            print(f"CTP查询账户信息失败: {e}")
            raise
    
    async def query_market_depth(self, stock_code: str) -> Dict[str, Any]:
        """查询市场深度（模拟）"""
        try:
            await asyncio.sleep(0.05)
            return {
                "stock_code": stock_code,
                "bids": [
                    {"price": 2995.0, "quantity": 10},
                    {"price": 2994.0, "quantity": 20},
                ],
                "asks": [
                    {"price": 3005.0, "quantity": 10},
                    {"price": 3006.0, "quantity": 20},
                ],
                "timestamp": datetime.now(),
            }
        except Exception as e:
            print(f"CTP查询市场深度失败: {e}")
            return {}
    
    async def subscribe_market_data(self, stock_codes: List[str]) -> bool:
        """订阅行情数据（模拟）"""
        try:
            await asyncio.sleep(0.2)
            return True
        except Exception as e:
            print(f"CTP订阅行情失败: {e}")
            return False
    
    async def unsubscribe_market_data(self, stock_codes: List[str]) -> bool:
        """取消订阅行情数据（模拟）"""
        try:
            await asyncio.sleep(0.2)
            return True
        except Exception as e:
            print(f"CTP取消订阅行情失败: {e}")
            return False