"""策略API"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from loguru import logger
from services.backtest_service import BacktestEngine

router = APIRouter()

# 预设策略模板
STRATEGY_TEMPLATES = {
    'MA': {
        'name': '双均线策略',
        'description': '基于短期和长期移动平均线交叉',
        'params': {
            'short_window': {'type': 'int', 'default': 5, 'min': 1, 'max': 60, 'description': '短期均线周期'},
            'long_window': {'type': 'int', 'default': 20, 'min': 1, 'max': 200, 'description': '长期均线周期'},
            'stop_loss': {'type': 'float', 'default': 0.1, 'min': 0, 'max': 1, 'description': '止损比例'}
        }
    },
    'RSI': {
        'name': 'RSI策略',
        'description': '基于相对强弱指标的超买超卖',
        'params': {
            'rsi_window': {'type': 'int', 'default': 14, 'min': 5, 'max': 30, 'description': 'RSI周期'},
            'oversold': {'type': 'int', 'default': 30, 'min': 10, 'max': 40, 'description': '超卖阈值'},
            'overbought': {'type': 'int', 'default': 70, 'min': 60, 'max': 90, 'description': '超买阈值'}
        }
    },
    'BOLL': {
        'name': '布林带策略',
        'description': '基于布林带的突破交易',
        'params': {
            'boll_window': {'type': 'int', 'default': 20, 'min': 5, 'max': 50, 'description': '布林带周期'},
            'num_std': {'type': 'float', 'default': 2, 'min': 1, 'max': 3, 'description': '标准差倍数'}
        }
    },
    'MACD': {
        'name': 'MACD策略',
        'description': '基于MACD指标的趋势跟踪',
        'params': {
            'fast': {'type': 'int', 'default': 12, 'min': 5, 'max': 20, 'description': '快线周期'},
            'slow': {'type': 'int', 'default': 26, 'min': 10, 'max': 50, 'description': '慢线周期'},
            'signal': {'type': 'int', 'default': 9, 'min': 5, 'max': 20, 'description': '信号线周期'}
        }
    }
}


class StrategyCreate(BaseModel):
    """创建策略请求"""
    name: str
    type: str
    description: Optional[str] = None
    params: Dict[str, Any]


class StrategyUpdate(BaseModel):
    """更新策略请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class BacktestRequest(BaseModel):
    """回测请求"""
    stock_code: str
    start_date: date
    end_date: date
    frequency: str = "daily"
    initial_capital: float = 100000.0
    strategy_type: str = "MA"
    custom_params: Optional[Dict[str, Any]] = None


@router.get("")
async def get_strategies():
    """获取策略列表"""
    try:
        logger.info("获取策略列表")

        # TODO: 从数据库获取策略列表
        # 临时返回模拟数据
        strategies = [
            {
                "id": 1,
                "name": "双均线策略",
                "type": "MA",
                "description": "基于5日和20日均线交叉",
                "params": {
                    "short_window": 5,
                    "long_window": 20,
                    "stop_loss": 0.1
                },
                "status": "active",
                "performance": {
                    "total_return": 0.15,
                    "sharpe_ratio": 1.2
                },
                "created_at": "2026-02-01T00:00:00"
            },
            {
                "id": 2,
                "name": "RSI策略",
                "type": "RSI",
                "description": "基于RSI指标的超买超卖",
                "params": {
                    "rsi_window": 14,
                    "oversold": 30,
                    "overbought": 70
                },
                "status": "active",
                "performance": {
                    "total_return": 0.12,
                    "sharpe_ratio": 1.0
                },
                "created_at": "2026-02-02T00:00:00"
            }
        ]

        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": strategies,
                "total": len(strategies)
            }
        }

    except Exception as e:
        logger.error(f"获取策略列表失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取策略列表失败"
        )


@router.post("")
async def create_strategy(strategy_data: StrategyCreate):
    """创建策略"""
    try:
        logger.info(f"创建策略: {strategy_data.name}")

        # TODO: 保存策略到数据库

        return {
            "code": 200,
            "message": "策略创建成功",
            "data": {
                "id": 3,
                "name": strategy_data.name,
                "type": strategy_data.type,
                "status": "active"
            }
        }

    except Exception as e:
        logger.error(f"创建策略失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="创建策略失败"
        )


@router.get("/{strategy_id}")
async def get_strategy(strategy_id: int):
    """获取策略详情"""
    try:
        logger.info(f"获取策略详情: {strategy_id}")

        # TODO: 从数据库获取策略详情

        return {
            "code": 200,
            "message": "success",
            "data": {
                "id": strategy_id,
                "name": "双均线策略",
                "type": "MA",
                "description": "基于5日和20日均线交叉",
                "params": {
                    "short_window": 5,
                    "long_window": 20,
                    "stop_loss": 0.1
                },
                "status": "active"
            }
        }

    except Exception as e:
        logger.error(f"获取策略详情失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取策略详情失败"
        )


@router.put("/{strategy_id}")
async def update_strategy(strategy_id: int, strategy_data: StrategyUpdate):
    """更新策略"""
    try:
        logger.info(f"更新策略: {strategy_id}")

        # TODO: 更新数据库中的策略

        return {
            "code": 200,
            "message": "策略更新成功"
        }

    except Exception as e:
        logger.error(f"更新策略失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="更新策略失败"
        )


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: int):
    """删除策略"""
    try:
        logger.info(f"删除策略: {strategy_id}")

        # TODO: 从数据库删除策略

        return {
            "code": 200,
            "message": "策略删除成功"
        }

    except Exception as e:
        logger.error(f"删除策略失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="删除策略失败"
        )


@router.post("/{strategy_id}/backtest")
async def run_backtest(strategy_id: int, request: BacktestRequest):
    """运行回测"""
    try:
        logger.info(f"运行回测: strategy_id={strategy_id}, stock={request.stock_code}")

        # 获取策略模板
        strategy_template = STRATEGY_TEMPLATES.get(request.strategy_type, STRATEGY_TEMPLATES['MA'])
        
        # 构建策略参数
        strategy_params = {
            'type': request.strategy_type,
            'name': strategy_template['name'],
            'description': strategy_template['description']
        }
        
        # 添加默认参数
        for param_name, param_config in strategy_template['params'].items():
            strategy_params[param_name] = param_config['default']
        
        # 如果有自定义参数，覆盖默认值
        if request.custom_params:
            strategy_params.update(request.custom_params)
        
        # 创建回测引擎
        engine = BacktestEngine(
            initial_capital=request.initial_capital,
            commission=0.0003,  # 万三手续费
            slippage=0.001  # 千一滑点
        )
        
        # 运行回测
        result = await engine.run_backtest(
            stock_code=request.stock_code,
            start_date=datetime.combine(request.start_date, datetime.min.time()),
            end_date=datetime.combine(request.end_date, datetime.max.time()),
            freq=request.frequency,
            strategy_params=strategy_params,
            data_source='auto'
        )
        
        return {
            "code": 200,
            "message": "回测完成",
            "data": result
        }

    except Exception as e:
        logger.error(f"运行回测失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"运行回测失败: {str(e)}"
        )


@router.post("/{strategy_id}/optimize")
async def optimize_strategy(
    strategy_id: int,
    method: str = Query("grid_search", pattern="^(grid_search|genetic|bayesian)$"),
    stock_code: str = Query(...),
    param_ranges: Dict[str, Any] = None
):
    """参数优化"""
    try:
        logger.info(f"参数优化: strategy_id={strategy_id}, method={method}")

        # TODO: 实现参数优化逻辑
        # 1. 获取策略
        # 2. 设置参数范围
        # 3. 运行优化算法
        # 4. 返回最优参数

        task_id = f"OPT{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return {
            "code": 200,
            "message": "优化任务已提交",
            "data": {
                "task_id": task_id,
                "status": "running"
            }
        }

    except Exception as e:
        logger.error(f"参数优化失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="参数优化失败"
        )
