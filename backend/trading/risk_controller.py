"""
风险控制器
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from .base_broker import Order, OrderSide, OrderType, Position, Account


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCheckResult:
    """风险检查结果"""
    
    def __init__(self, passed: bool, message: str, level: RiskLevel = RiskLevel.LOW):
        self.passed = passed
        self.message = message
        self.level = level


class RiskController:
    """风险控制器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化风险控制器
        
        Args:
            config: 风控配置
                - max_single_position_ratio: 单一持仓最大比例
                - max_total_position_ratio: 总持仓最大比例
                - max_daily_trades: 日内最大交易次数
                - max_daily_loss: 日内最大亏损
                - max_daily_trade_amount: 日内最大交易金额
                - stop_loss_ratio: 止损比例
                - take_profit_ratio: 止盈比例
                - min_volume: 最小成交量要求
                - max_spread: 最大买卖价差
        """
        self.config = config
        
        # 默认配置
        self.defaults = {
            "max_single_position_ratio": 0.3,      # 单一持仓最大30%
            "max_total_position_ratio": 0.8,       # 总持仓最大80%
            "max_daily_trades": 100,               # 日内最多100笔
            "max_daily_loss": -50000,               # 日内最大亏损5万
            "max_daily_trade_amount": 1000000,       # 日内最大交易金额100万
            "stop_loss_ratio": 0.1,                # 止损10%
            "take_profit_ratio": 0.2,               # 止盈20%
            "min_volume": 100000,                    # 最小成交量
            "max_spread": 0.02,                    # 最大买卖价差2%
        }
        
        # 应用配置
        for key, value in config.items():
            if value is not None:
                self.defaults[key] = value
        
        # 今日统计
        self.daily_stats = {
            "trades": 0,
            "loss": 0.0,
            "trade_amount": 0.0,
            "date": datetime.now().date(),
        }
    
    async def check_order_risk(
        self,
        order: Order,
        account: Account,
        positions: List[Position],
        market_data: Optional[Dict[str, Any]] = None,
    ) -> RiskCheckResult:
        """
        检查订单风险
        
        Args:
            order: 订单对象
            account: 账户信息
            positions: 持仓列表
            market_data: 市场数据
            
        Returns:
            风险检查结果
        """
        # 1. 检查持仓限制
        result = await self._check_position_limit(order, account, positions)
        if not result.passed:
            return result
        
        # 2. 检查日内限制
        result = await self._check_daily_limit(order, account)
        if not result.passed:
            return result
        
        # 3. 检查止损止盈
        result = await self._check_stop_loss_take_profit(order, positions)
        if not result.passed:
            return result
        
        # 4. 检查流动性
        result = await self._check_liquidity(order, market_data)
        if not result.passed:
            return result
        
        # 所有检查通过
        return RiskCheckResult(
            passed=True,
            message="风险检查通过",
            level=RiskLevel.LOW
        )
    
    async def _check_position_limit(
        self,
        order: Order,
        account: Account,
        positions: List[Position],
    ) -> RiskCheckResult:
        """检查持仓限制"""
        
        order_value = order.quantity * (order.price or 0)
        
        # 检查单一持仓限制
        for pos in positions:
            if pos.stock_code == order.stock_code:
                # 现有持仓市值
                existing_value = pos.quantity * (pos.cost_price or 0)
                total_value = existing_value + order_value
                
                ratio = total_value / account.total_assets
                max_ratio = self.defaults["max_single_position_ratio"]
                
                if ratio > max_ratio:
                    return RiskCheckResult(
                        passed=False,
                        message=f"单一持仓超限: {ratio:.2%} > {max_ratio:.0%}",
                        level=RiskLevel.HIGH
                    )
        
        # 检查总持仓限制
        total_position_value = sum(
            pos.quantity * (pos.cost_price or 0) for pos in positions
        )
        new_total = total_position_value + order_value
        total_ratio = new_total / account.total_assets
        max_total_ratio = self.defaults["max_total_position_ratio"]
        
        if total_ratio > max_total_ratio:
            return RiskCheckResult(
                passed=False,
                message=f"总持仓超限: {total_ratio:.2%} > {max_total_ratio:.0%}",
                level=RiskLevel.HIGH
            )
        
        return RiskCheckResult(passed=True, message="持仓限制检查通过")
    
    async def _check_daily_limit(
        self,
        order: Order,
        account: Account,
    ) -> RiskCheckResult:
        """检查日内限制"""
        
        # 更新日期
        today = datetime.now().date()
        if self.daily_stats["date"] != today:
            self.daily_stats = {
                "trades": 0,
                "loss": 0.0,
                "trade_amount": 0.0,
                "date": today,
            }
        
        # 检查交易次数
        if self.daily_stats["trades"] >= self.defaults["max_daily_trades"]:
            return RiskCheckResult(
                passed=False,
                message=f"日内交易次数超限: {self.daily_stats['trades']} > {self.defaults['max_daily_trades']}",
                level=RiskLevel.HIGH
            )
        
        # 检查交易金额
        order_amount = order.quantity * (order.price or 0)
        if self.daily_stats["trade_amount"] + order_amount > self.defaults["max_daily_trade_amount"]:
            return RiskCheckResult(
                passed=False,
                message=f"日内交易金额超限",
                level=RiskLevel.MEDIUM
            )
        
        return RiskCheckResult(passed=True, message="日内限制检查通过")
    
    async def _check_stop_loss_take_profit(
        self,
        order: Order,
        positions: List[Position],
    ) -> RiskCheckResult:
        """检查止损止盈"""
        
        for pos in positions:
            if pos.stock_code == order.stock_code and order.side == OrderSide.SELL:
                # 卖出时检查是否触发止损止盈
                if pos.cost_price and pos.current_price:
                    pnl_ratio = (pos.current_price - pos.cost_price) / pos.cost_price
                    
                    # 止损检查
                    stop_loss_ratio = self.defaults["stop_loss_ratio"]
                    if pnl_ratio <= -stop_loss_ratio:
                        return RiskCheckResult(
                            passed=True,
                            message=f"触发止损: {pnl_ratio:.2%}",
                            level=RiskLevel.HIGH
                        )
                    
                    # 止盈检查
                    take_profit_ratio = self.defaults["take_profit_ratio"]
                    if pnl_ratio >= take_profit_ratio:
                        return RiskCheckResult(
                            passed=True,
                            message=f"触发止盈: {pnl_ratio:.2%}",
                            level=RiskLevel.MEDIUM
                        )
        
        return RiskCheckResult(passed=True, message="止损止盈检查通过")
    
    async def _check_liquidity(
        self,
        order: Order,
        market_data: Optional[Dict[str, Any]],
    ) -> RiskCheckResult:
        """检查流动性"""
        
        if not market_data:
            # 如果没有市场数据，跳过流动性检查
            return RiskCheckResult(passed=True, message="流动性检查跳过（无市场数据）")
        
        # 检查成交量
        volume = market_data.get("volume", 0)
        if volume < self.defaults["min_volume"]:
            return RiskCheckResult(
                passed=False,
                message=f"成交量不足: {volume} < {self.defaults['min_volume']}",
                level=RiskLevel.HIGH
            )
        
        # 检查买卖价差
        bids = market_data.get("bids", [])
        asks = market_data.get("asks", [])
        
        if bids and asks:
            best_bid = bids[0].get("price", 0) if bids else 0
            best_ask = asks[0].get("price", 0) if asks else 0
            
            if best_bid > 0 and best_ask > 0:
                spread = (best_ask - best_bid) / best_bid
                max_spread = self.defaults["max_spread"]
                
                if spread > max_spread:
                    return RiskCheckResult(
                        passed=False,
                        message=f"买卖价差过大: {spread:.2%} > {max_spread:.0%}",
                        level=RiskLevel.MEDIUM
                    )
        
        return RiskCheckResult(passed=True, message="流动性检查通过")
    
    def update_daily_stats(
        self,
        trade_amount: float,
        pnl: Optional[float] = None,
    ):
        """
        更新日内统计
        
        Args:
            trade_amount: 交易金额
            pnl: 盈亏
        """
        today = datetime.now().date()
        if self.daily_stats["date"] != today:
            self.daily_stats = {
                "trades": 0,
                "loss": 0.0,
                "trade_amount": 0.0,
                "date": today,
            }
        
        self.daily_stats["trades"] += 1
        self.daily_stats["trade_amount"] += trade_amount
        
        if pnl is not None and pnl < 0:
            self.daily_stats["loss"] += pnl
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """
        获取风险汇总
        
        Returns:
            风险汇总信息
        """
        today = datetime.now().date()
        
        return {
            "config": self.defaults,
            "daily_stats": self.daily_stats if self.daily_stats["date"] == today else None,
            "risk_level": self._calculate_risk_level(),
        }
    
    def _calculate_risk_level(self) -> RiskLevel:
        """计算当前风险等级"""
        
        # 根据日内亏损判断
        if self.daily_stats["date"] == datetime.now().date():
            loss_ratio = abs(self.daily_stats["loss"]) / self.defaults["max_daily_loss"] if self.defaults["max_daily_loss"] != 0 else 0
            
            if loss_ratio >= 1.0:
                return RiskLevel.CRITICAL
            elif loss_ratio >= 0.8:
                return RiskLevel.HIGH
            elif loss_ratio >= 0.5:
                return RiskLevel.MEDIUM
        
        return RiskLevel.LOW