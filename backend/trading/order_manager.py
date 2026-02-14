"""
订单管理器
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import asyncio

from .base_broker import (
    BaseBroker,
    Order,
    Trade,
    OrderSide,
    OrderType,
    OrderStatus,
)


class OrderManager:
    """订单管理器"""
    
    def __init__(self, broker: BaseBroker, db_session=None):
        """
        初始化订单管理器
        
        Args:
            broker: 券商接口
            db_session: 数据库会话（可选）
        """
        self.broker = broker
        self.db_session = db_session
        self._orders: Dict[str, Order] = {}  # 系统订单ID -> 订单
        self._broker_orders: Dict[str, str] = {}  # 券商订单ID -> 系统订单ID
        
    async def create_order(
        self,
        user_id: int,
        stock_code: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: int,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        remark: Optional[str] = None,
        strategy_id: Optional[int] = None,
    ) -> Order:
        """
        创建订单
        
        Args:
            user_id: 用户ID
            stock_code: 股票代码
            side: 买卖方向
            order_type: 订单类型
            quantity: 数量
            price: 价格（限价单）
            stop_price: 止损价（止损单）
            remark: 备注
            strategy_id: 策略ID
            
        Returns:
            订单对象
        """
        order_id = f"ORD_{uuid.uuid4().hex[:12]}"
        
        order = Order(
            id=order_id,
            user_id=user_id,
            stock_code=stock_code,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            remark=remark,
            created_at=datetime.now(),
        )
        
        self._orders[order_id] = order
        return order
    
    async def submit_order(self, order: Order) -> bool:
        """
        提交订单到券商
        
        Args:
            order: 订单对象
            
        Returns:
            是否成功
        """
        try:
            if not self.broker.is_connected_check():
                raise Exception("券商未连接")
            
            # 提交到券商
            broker_order_id = await self.broker.submit_order(order)
            
            # 更新订单状态
            order.broker_order_id = broker_order_id
            order.status = OrderStatus.SUBMITTED
            order.submitted_at = datetime.now()
            
            # 建立映射
            self._broker_orders[broker_order_id] = order.id
            
            # 保存到数据库（如果有）
            if self.db_session:
                await self._save_order_to_db(order)
            
            return True
            
        except Exception as e:
            print(f"提交订单失败: {e}")
            order.status = OrderStatus.REJECTED
            return False
    
    async def cancel_order(self, order_id: str) -> bool:
        """
        撤销订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            是否成功
        """
        try:
            order = self._orders.get(order_id)
            if not order:
                raise Exception(f"订单不存在: {order_id}")
            
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                raise Exception(f"订单状态不允许撤销: {order.status}")
            
            if not order.broker_order_id:
                raise Exception("订单尚未提交到券商")
            
            # 撤销订单
            success = await self.broker.cancel_order(order_id, order.broker_order_id)
            
            if success:
                order.status = OrderStatus.CANCELLED
                order.cancelled_at = datetime.now()
                
                # 更新数据库
                if self.db_session:
                    await self._update_order_in_db(order)
            
            return success
            
        except Exception as e:
            print(f"撤销订单失败: {e}")
            return False
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """
        获取订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            订单对象
        """
        return self._orders.get(order_id)
    
    async def get_orders(
        self,
        user_id: Optional[int] = None,
        stock_code: Optional[str] = None,
        status: Optional[OrderStatus] = None,
        limit: int = 100,
    ) -> List[Order]:
        """
        获取订单列表
        
        Args:
            user_id: 用户ID
            stock_code: 股票代码
            status: 订单状态
            limit: 返回数量限制
            
        Returns:
            订单列表
        """
        orders = list(self._orders.values())
        
        # 过滤
        if user_id:
            orders = [o for o in orders if o.user_id == user_id]
        if stock_code:
            orders = [o for o in orders if o.stock_code == stock_code]
        if status:
            orders = [o for o in orders if o.status == status]
        
        # 排序（按创建时间倒序）
        orders.sort(key=lambda o: o.created_at or datetime.min, reverse=True)
        
        return orders[:limit]
    
    async def sync_order_status(self, broker_order_id: str) -> bool:
        """
        同步订单状态
        
        Args:
            broker_order_id: 券商订单ID
            
        Returns:
            是否成功
        """
        try:
            order_id = self._broker_orders.get(broker_order_id)
            if not order_id:
                return False
            
            # 从券商查询订单状态
            broker_order = await self.broker.query_order(broker_order_id)
            if not broker_order:
                return False
            
            # 更新本地订单
            local_order = self._orders.get(order_id)
            if local_order:
                local_order.status = broker_order.status
                local_order.filled_quantity = broker_order.filled_quantity
                local_order.avg_fill_price = broker_order.avg_fill_price
                local_order.filled_at = broker_order.filled_at
                local_order.commission = broker_order.commission
                
                # 更新数据库
                if self.db_session:
                    await self._update_order_in_db(local_order)
            
            return True
            
        except Exception as e:
            print(f"同步订单状态失败: {e}")
            return False
    
    async def sync_all_orders(self) -> int:
        """
        同步所有未完成订单的状态
        
        Returns:
            同步成功的数量
        """
        success_count = 0
        
        # 获取所有未完成的订单
        pending_orders = [
            o for o in self._orders.values()
            if o.status in [OrderStatus.SUBMITTED, OrderStatus.PARTIAL_FILLED]
        ]
        
        # 批量同步
        for order in pending_orders:
            if order.broker_order_id:
                success = await self.sync_order_status(order.broker_order_id)
                if success:
                    success_count += 1
        
        return success_count
    
    async def get_trades(
        self,
        order_id: Optional[str] = None,
        stock_code: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Trade]:
        """
        获取成交记录
        
        Args:
            order_id: 订单ID
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            成交记录列表
        """
        return await self.broker.query_trades(stock_code, start_date, end_date)
    
    async def get_order_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        获取订单统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息
        """
        orders = await self.get_orders(user_id=user_id)
        
        total = len(orders)
        pending = len([o for o in orders if o.status == OrderStatus.PENDING])
        submitted = len([o for o in orders if o.status == OrderStatus.SUBMITTED])
        partial_filled = len([o for o in orders if o.status == OrderStatus.PARTIAL_FILLED])
        filled = len([o for o in orders if o.status == OrderStatus.FILLED])
        cancelled = len([o for o in orders if o.status == OrderStatus.CANCELLED])
        rejected = len([o for o in orders if o.status == OrderStatus.REJECTED])
        
        return {
            "total": total,
            "pending": pending,
            "submitted": submitted,
            "partial_filled": partial_filled,
            "filled": filled,
            "cancelled": cancelled,
            "rejected": rejected,
            "filled_rate": filled / total if total > 0 else 0,
        }
    
    async def _save_order_to_db(self, order: Order) -> bool:
        """
        保存订单到数据库
        
        Args:
            order: 订单对象
            
        Returns:
            是否成功
        """
        # TODO: 实现数据库保存逻辑
        # 这里应该是SQLAlchemy操作
        return True
    
    async def _update_order_in_db(self, order: Order) -> bool:
        """
        更新数据库中的订单
        
        Args:
            order: 订单对象
            
        Returns:
            是否成功
        """
        # TODO: 实现数据库更新逻辑
        # 这里应该是SQLAlchemy操作
        return True
    
    async def cleanup_old_orders(self, days: int = 30) -> int:
        """
        清理旧订单
        
        Args:
            days: 保留天数
            
        Returns:
            清理的订单数量
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        old_orders = [
            order_id for order_id, order in self._orders.items()
            if order.created_at and order.created_at < cutoff_date
            and order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]
        ]
        
        # 删除旧订单
        for order_id in old_orders:
            order = self._orders.pop(order_id, None)
            if order and order.broker_order_id:
                self._broker_orders.pop(order.broker_order_id, None)
        
        return len(old_orders)