"""
持仓管理器
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base_broker import Position, BaseBroker


class PositionManager:
    """持仓管理器"""
    
    def __init__(self, broker: BaseBroker, db_session=None):
        """
        初始化持仓管理器
        
        Args:
            broker: 券商接口
            db_session: 数据库会话
        """
        self.broker = broker
        self.db_session = db_session
        self._positions: Dict[str, Position] = {}  # 股票代码 -> 持仓
        
    async def sync_positions(self) -> bool:
        """
        从券商同步持仓
        
        Returns:
            是否成功
        """
        try:
            if not self.broker.is_connected_check():
                raise Exception("券商未连接")
            
            # 从券商查询持仓
            broker_positions = await self.broker.query_positions()
            
            # 更新本地持仓
            for pos in broker_positions:
                self._positions[pos.stock_code] = pos
                
                # 保存到数据库
                if self.db_session:
                    await self._save_position_to_db(pos)
            
            return True
            
        except Exception as e:
            print(f"同步持仓失败: {e}")
            return False
    
    async def get_position(self, stock_code: str) -> Optional[Position]:
        """
        获取指定股票的持仓
        
        Args:
            stock_code: 股票代码
            
        Returns:
            持仓对象
        """
        return self._positions.get(stock_code)
    
    async def get_positions(self, user_id: int) -> List[Position]:
        """
        获取所有持仓
        
        Args:
            user_id: 用户ID
            
        Returns:
            持仓列表
        """
        return [pos for pos in self._positions.values() if pos.user_id == user_id]
    
    async def get_position_summary(self, user_id: int) -> Dict[str, Any]:
        """
        获取持仓汇总
        
        Args:
            user_id: 用户ID
            
        Returns:
            汇总信息
        """
        positions = await self.get_positions(user_id)
        
        total_market_value = sum(pos.market_value or 0 for pos in positions)
        total_pnl = sum(pos.pnl_amount or 0 for pos in positions)
        total_quantity = sum(pos.quantity for pos in positions)
        
        # 盈利持仓
        profit_positions = [pos for pos in positions if (pos.pnl_amount or 0) > 0]
        # 亏损持仓
        loss_positions = [pos for pos in positions if (pos.pnl_amount or 0) < 0]
        
        return {
            "total_positions": len(positions),
            "total_market_value": total_market_value,
            "total_pnl": total_pnl,
            "total_pnl_ratio": total_pnl / total_market_value if total_market_value > 0 else 0,
            "total_quantity": total_quantity,
            "profit_count": len(profit_positions),
            "loss_count": len(loss_positions),
            "profit_positions": profit_positions,
            "loss_positions": loss_positions,
        }
    
    async def _save_position_to_db(self, position: Position) -> bool:
        """
        保存持仓到数据库
        
        Args:
            position: 持仓对象
            
        Returns:
            是否成功
        """
        # TODO: 实现数据库保存逻辑
        return True
    
    async def _update_position_in_db(self, position: Position) -> bool:
        """
        更新数据库中的持仓
        
        Args:
            position: 持仓对象
            
        Returns:
            是否成功
        """
        # TODO: 实现数据库更新逻辑
        return True