"""
交易API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from core.security import get_current_user
from models.user import User
from trading.base_broker import (
    Order,
    OrderSide,
    OrderType,
    OrderStatus,
    Position,
    Account,
)
from trading.xtp_broker import XTPBroker
from trading.ctp_broker import CTPBroker
from trading.order_manager import OrderManager
from trading.position_manager import PositionManager
from trading.account_manager import AccountManager
from trading.risk_controller import RiskController, RiskLevel


router = APIRouter(prefix="/trading", tags=["交易"])


# 全局交易管理器实例（简化版，实际应该使用依赖注入）
_order_manager: Optional[OrderManager] = None
_position_manager: Optional[PositionManager] = None
_account_manager: Optional[AccountManager] = None
_risk_controller: Optional[RiskController] = None


def init_trading():
    """初始化交易系统"""
    global _order_manager, _position_manager, _account_manager, _risk_controller
    
    # 创建券商接口（使用XTP作为示例）
    broker_config = {
        "broker_id": "1234",
        "account": "test_account",
        "password": "test_password",
        "trading_server": "127.0.0.1",
        "trading_port": 6001,
        "quote_server": "127.0.0.1",
        "quote_port": 6002,
    }
    
    broker = XTPBroker(broker_config)
    
    # 创建管理器
    _order_manager = OrderManager(broker)
    _position_manager = PositionManager(broker)
    _account_manager = AccountManager(broker)
    _risk_controller = RiskController({})


@router.on_event("startup")
async def startup_event():
    """启动事件"""
    init_trading()


async def connect_broker() -> bool:
    """连接券商"""
    try:
        if _order_manager and _order_manager.broker:
            await _order_manager.broker.connect()
            await _order_manager.broker.login("test_user", "test_password")
            return True
        return False
    except Exception as e:
        print(f"连接券商失败: {e}")
        return False


@router.post("/connect")
async def connect_trading(current_user: User = Depends(get_current_user)):
    """连接交易系统"""
    success = await connect_broker()
    
    if success:
        # 同步账户和持仓
        await _account_manager.sync_account()
        await _position_manager.sync_positions()
        
        return {
            "code": 200,
            "message": "连接成功",
            "data": {"connected": True}
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="连接交易系统失败"
        )


@router.post("/orders")
async def create_order(
    stock_code: str,
    side: OrderSide,
    order_type: OrderType,
    quantity: int,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
    remark: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    创建订单
    
    Args:
        stock_code: 股票代码
        side: 买卖方向
        order_type: 订单类型
        quantity: 数量
        price: 价格（限价单）
        stop_price: 止损价（止损单）
        remark: 备注
    """
    if not _order_manager or not _order_manager.broker.is_connected_check():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="交易系统未连接"
        )
    
    # 创建订单
    order = await _order_manager.create_order(
        user_id=current_user.id,
        stock_code=stock_code,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
        remark=remark,
    )
    
    # 风险检查
    account = await _account_manager.get_account()
    positions = await _position_manager.get_positions(current_user.id)
    
    if account:
        risk_result = await _risk_controller.check_order_risk(
            order, account, positions
        )
        
        if not risk_result.passed:
            return {
                "code": 400,
                "message": risk_result.message,
                "data": {
                    "order_id": order.id,
                    "risk_passed": False,
                    "risk_level": risk_result.level.value,
                }
            }
    
    # 提交订单
    success = await _order_manager.submit_order(order)
    
    if success:
        return {
            "code": 200,
            "message": "订单提交成功",
            "data": {
                "order_id": order.id,
                "broker_order_id": order.broker_order_id,
                "status": order.status.value,
                "risk_passed": True,
            }
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="订单提交失败"
        )


@router.get("/orders")
async def get_orders(
    stock_code: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    """
    获取订单列表
    
    Args:
        stock_code: 股票代码
        status: 订单状态
        limit: 返回数量限制
    """
    if not _order_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="订单管理器未初始化"
        )
    
    orders = await _order_manager.get_orders(
        user_id=current_user.id,
        stock_code=stock_code,
        status=status,
        limit=limit,
    )
    
    # 转换为字典
    order_dicts = []
    for order in orders:
        order_dicts.append({
            "id": order.id,
            "stock_code": order.stock_code,
            "side": order.side.value,
            "order_type": order.order_type.value,
            "quantity": order.quantity,
            "price": order.price,
            "stop_price": order.stop_price,
            "filled_quantity": order.filled_quantity,
            "avg_fill_price": order.avg_fill_price,
            "status": order.status.value,
            "commission": order.commission,
            "remark": order.remark,
            "broker_order_id": order.broker_order_id,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
            "filled_at": order.filled_at.isoformat() if order.filled_at else None,
            "cancelled_at": order.cancelled_at.isoformat() if order.cancelled_at else None,
        })
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "orders": order_dicts,
            "total": len(order_dicts),
        }
    }


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
):
    """撤销订单"""
    if not _order_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="订单管理器未初始化"
        )
    
    success = await _order_manager.cancel_order(order_id)
    
    if success:
        return {
            "code": 200,
            "message": "订单撤销成功",
            "data": {"order_id": order_id}
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="订单撤销失败"
        )


@router.get("/orders/statistics")
async def get_order_statistics(
    current_user: User = Depends(get_current_user),
):
    """获取订单统计"""
    if not _order_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="订单管理器未初始化"
        )
    
    stats = await _order_manager.get_order_statistics(current_user.id)
    
    return {
        "code": 200,
        "message": "success",
        "data": stats
    }


@router.get("/positions")
async def get_positions(
    current_user: User = Depends(get_current_user),
):
    """获取持仓列表"""
    if not _position_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="持仓管理器未初始化"
        )
    
    # 同步持仓
    await _position_manager.sync_positions()
    
    positions = await _position_manager.get_positions(current_user.id)
    
    # 转换为字典
    position_dicts = []
    for pos in positions:
        position_dicts.append({
            "id": pos.id,
            "stock_code": pos.stock_code,
            "quantity": pos.quantity,
            "available_quantity": pos.available_quantity,
            "cost_price": pos.cost_price,
            "current_price": pos.current_price,
            "market_value": pos.market_value,
            "pnl_amount": pos.pnl_amount,
            "pnl_ratio": pos.pnl_ratio,
        })
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "positions": position_dicts,
            "total": len(position_dicts),
        }
    }


@router.get("/positions/summary")
async def get_position_summary(
    current_user: User = Depends(get_current_user),
):
    """获取持仓汇总"""
    if not _position_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="持仓管理器未初始化"
        )
    
    summary = await _position_manager.get_position_summary(current_user.id)
    
    return {
        "code": 200,
        "message": "success",
        "data": summary
    }


@router.get("/account")
async def get_account(
    current_user: User = Depends(get_current_user),
):
    """获取账户信息"""
    if not _account_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="账户管理器未初始化"
        )
    
    # 同步账户
    await _account_manager.sync_account()
    
    account = await _account_manager.get_account()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账户信息不存在"
        )
    
    account_dict = {
        "id": account.id,
        "user_id": account.user_id,
        "broker": account.broker,
        "broker_account_id": account.broker_account_id,
        "total_assets": account.total_assets,
        "available_cash": account.available_cash,
        "frozen_cash": account.frozen_cash,
        "market_value": account.market_value,
        "pnl_amount": account.pnl_amount,
        "pnl_ratio": account.pnl_ratio,
    }
    
    return {
        "code": 200,
        "message": "success",
        "data": account_dict
    }


@router.get("/account/summary")
async def get_account_summary(
    current_user: User = Depends(get_current_user),
):
    """获取账户汇总"""
    if not _account_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="账户管理器未初始化"
        )
    
    summary = await _account_manager.get_account_summary()
    
    return {
        "code": 200,
        "message": "success",
        "data": summary
    }


@router.get("/risk/summary")
async def get_risk_summary(
    current_user: User = Depends(get_current_user),
):
    """获取风险汇总"""
    if not _risk_controller:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="风险控制器未初始化"
        )
    
    summary = _risk_controller.get_risk_summary()
    
    return {
        "code": 200,
        "message": "success",
        "data": summary
    }