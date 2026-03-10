"""策略API"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from itertools import product
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core.database import get_db
from models.strategy import Strategy, BacktestResult
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
    },
    'TURTLE': {
        'name': '海龟交易策略',
        'description': '基于唐奇安通道的趋势突破策略（经典海龟交易法则）',
        'params': {
            'period': {'type': 'int', 'default': 20, 'min': 10, 'max': 60, 'description': '突破周期（日）'}
        }
    },
    'KDJ': {
        'name': 'KDJ策略',
        'description': '基于随机指标（KDJ）的超买超卖策略，适合短线交易',
        'params': {
            'fastk_period': {'type': 'int', 'default': 9, 'min': 5, 'max': 20, 'description': '快速K线周期'},
            'slowk_period': {'type': 'int', 'default': 3, 'min': 1, 'max': 10, 'description': '慢速K线周期'},
            'slowd_period': {'type': 'int', 'default': 3, 'min': 1, 'max': 10, 'description': 'D线周期'},
            'kdj_buy': {'type': 'int', 'default': 20, 'min': 5, 'max': 40, 'description': '买入阈值'},
            'kdj_sell': {'type': 'int', 'default': 80, 'min': 60, 'max': 95, 'description': '卖出阈值'}
        }
    },
    'ATR': {
        'name': 'ATR策略',
        'description': '基于平均真实波幅（ATR）的波动率策略，用于止损和趋势跟踪',
        'params': {
            'atr_period': {'type': 'int', 'default': 14, 'min': 5, 'max': 30, 'description': 'ATR周期'},
            'atr_multiplier': {'type': 'float', 'default': 2.0, 'min': 1.0, 'max': 5.0, 'description': 'ATR倍数'}
        }
    },
    'DUAL_THRUST': {
        'name': 'Dual-Thrust策略',
        'description': '基于区间突破的日内交易策略，根据前N日高低价确定突破区间',
        'params': {
            'n_days': {'type': 'int', 'default': 5, 'min': 3, 'max': 10, 'description': '回看天数'},
            'k1': {'type': 'float', 'default': 0.7, 'min': 0.5, 'max': 1.0, 'description': '上轨系数'},
            'k2': {'type': 'float', 'default': 0.7, 'min': 0.5, 'max': 1.0, 'description': '下轨系数'}
        }
    },
    'HANS123': {
        'name': 'Hans123策略',
        'description': '基于开盘后30分钟区间的突破策略，经典的日内交易系统',
        'params': {
            'morning_bars': {'type': 'int', 'default': 6, 'min': 3, 'max': 12, 'description': '早盘K线数量（6=30分钟）'},
            'breakout_percent': {'type': 'float', 'default': 0.1, 'min': 0.05, 'max': 0.3, 'description': '突破百分比'}
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


class OptimizeRequest(BaseModel):
    """参数优化请求"""
    stock_code: str
    start_date: date
    end_date: date
    frequency: str = "daily"
    strategy_type: Optional[str] = None
    param_ranges: Dict[str, Any]
    objective: str = "sharpe_ratio"
    maximize: bool = True


@router.get("")
async def get_strategies(db: AsyncSession = Depends(get_db)):
    """获取策略列表"""
    try:
        logger.info("获取策略列表")

        result = await db.execute(select(Strategy).order_by(Strategy.created_at.desc()))
        strategy_rows = result.scalars().all()

        strategies = []
        for row in strategy_rows:
            latest_backtest_result = await db.execute(
                select(BacktestResult)
                .where(BacktestResult.strategy_id == row.id)
                .order_by(BacktestResult.created_at.desc())
                .limit(1)
            )
            latest_backtest = latest_backtest_result.scalar_one_or_none()

            performance = None
            if latest_backtest:
                performance = {
                    "total_return": float(latest_backtest.total_return or 0),
                    "sharpe_ratio": float(latest_backtest.sharpe_ratio or 0),
                }

            strategies.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "type": row.type,
                    "description": row.description,
                    "params": row.params or {},
                    "status": row.status,
                    "performance": performance,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
            )

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
async def create_strategy(strategy_data: StrategyCreate, db: AsyncSession = Depends(get_db)):
    """创建策略"""
    try:
        logger.info(f"创建策略: {strategy_data.name}")

        if strategy_data.type not in STRATEGY_TEMPLATES:
            raise HTTPException(status_code=400, detail=f"不支持的策略类型: {strategy_data.type}")

        strategy = Strategy(
            name=strategy_data.name,
            type=strategy_data.type,
            description=strategy_data.description,
            params=strategy_data.params,
            status="active",
        )
        db.add(strategy)
        await db.commit()
        await db.refresh(strategy)

        return {
            "code": 200,
            "message": "策略创建成功",
            "data": {
                "id": strategy.id,
                "name": strategy.name,
                "type": strategy.type,
                "status": strategy.status,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"创建策略失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="创建策略失败"
        )


@router.get("/{strategy_id}")
async def get_strategy(strategy_id: int, db: AsyncSession = Depends(get_db)):
    """获取策略详情"""
    try:
        logger.info(f"获取策略详情: {strategy_id}")

        result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
        strategy = result.scalar_one_or_none()
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")

        latest_backtest_result = await db.execute(
            select(BacktestResult)
            .where(BacktestResult.strategy_id == strategy.id)
            .order_by(BacktestResult.created_at.desc())
            .limit(1)
        )
        latest_backtest = latest_backtest_result.scalar_one_or_none()

        return {
            "code": 200,
            "message": "success",
            "data": {
                "id": strategy_id,
                "name": strategy.name,
                "type": strategy.type,
                "description": strategy.description,
                "params": strategy.params or {},
                "status": strategy.status,
                "created_at": strategy.created_at.isoformat() if strategy.created_at else None,
                "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
                "latest_backtest": (
                    {
                        "total_return": float(latest_backtest.total_return or 0),
                        "annual_return": float(latest_backtest.annual_return or 0),
                        "max_drawdown": float(latest_backtest.max_drawdown or 0),
                        "sharpe_ratio": float(latest_backtest.sharpe_ratio or 0),
                        "win_rate": float(latest_backtest.win_rate or 0),
                        "trade_count": latest_backtest.trade_count,
                        "created_at": latest_backtest.created_at.isoformat() if latest_backtest.created_at else None,
                    }
                    if latest_backtest
                    else None
                ),
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略详情失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取策略详情失败"
        )


@router.put("/{strategy_id}")
async def update_strategy(
    strategy_id: int,
    strategy_data: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新策略"""
    try:
        logger.info(f"更新策略: {strategy_id}")

        result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
        strategy = result.scalar_one_or_none()
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")

        if strategy_data.name is not None:
            strategy.name = strategy_data.name
        if strategy_data.description is not None:
            strategy.description = strategy_data.description
        if strategy_data.params is not None:
            strategy.params = strategy_data.params
        if strategy_data.status is not None:
            strategy.status = strategy_data.status

        await db.commit()
        await db.refresh(strategy)

        return {
            "code": 200,
            "message": "策略更新成功",
            "data": {
                "id": strategy.id,
                "name": strategy.name,
                "type": strategy.type,
                "description": strategy.description,
                "params": strategy.params or {},
                "status": strategy.status,
                "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"更新策略失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="更新策略失败"
        )


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: int, db: AsyncSession = Depends(get_db)):
    """删除策略"""
    try:
        logger.info(f"删除策略: {strategy_id}")

        result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
        strategy = result.scalar_one_or_none()
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")

        await db.delete(strategy)
        await db.commit()

        return {
            "code": 200,
            "message": "策略删除成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"删除策略失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="删除策略失败"
        )


@router.post("/{strategy_id}/backtest")
async def run_backtest(
    strategy_id: int,
    request: BacktestRequest,
    db: AsyncSession = Depends(get_db),
):
    """运行回测"""
    try:
        logger.info(f"运行回测: strategy_id={strategy_id}, stock={request.stock_code}")

        strategy_result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
        strategy = strategy_result.scalar_one_or_none()

        if strategy:
            strategy_type = strategy.type
            base_params = strategy.params or {}
        else:
            strategy_type = request.strategy_type
            base_params = {}

        if strategy_type not in STRATEGY_TEMPLATES:
            raise HTTPException(status_code=400, detail=f"不支持的策略类型: {strategy_type}")

        # 获取策略模板
        strategy_template = STRATEGY_TEMPLATES[strategy_type]
        
        # 构建策略参数
        strategy_params = {
            'type': strategy_type,
            'name': strategy_template['name'],
            'description': strategy_template['description']
        }
        
        # 添加默认参数
        for param_name, param_config in strategy_template['params'].items():
            strategy_params[param_name] = param_config['default']

        # 数据库参数覆盖默认参数
        strategy_params.update(base_params)
        
        # 如果有自定义参数，覆盖默认值
        if request.custom_params:
            strategy_params.update(request.custom_params)
        
        # 转换频率参数：将前端格式转换为数据获取器期望的格式
        freq_mapping = {
            'daily': '1d',
            '60min': '60min',
            '30min': '30min',
            '15min': '15min',
            '5min': '5min'
        }
        freq = freq_mapping.get(request.frequency, request.frequency)
        logger.info(f"频率参数转换: {request.frequency} -> {freq}")
        
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
            freq=freq,
            strategy_params=strategy_params,
            data_source='auto'
        )

        # 保存回测结果（仅在策略存在时）
        if strategy:
            metrics = result.get("metrics", {})
            backtest_row = BacktestResult(
                strategy_id=strategy.id,
                stock_code=result.get("stock_code"),
                start_date=request.start_date,
                end_date=request.end_date,
                frequency=result.get("frequency"),
                initial_capital=result.get("initial_capital"),
                final_capital=result.get("final_capital"),
                total_return=metrics.get("total_return", 0),
                annual_return=metrics.get("annual_return", 0),
                max_drawdown=metrics.get("max_drawdown", 0),
                sharpe_ratio=metrics.get("sharpe_ratio", 0),
                win_rate=metrics.get("win_rate", 0),
                profit_loss_ratio=metrics.get("profit_loss_ratio", 0),
                volatility=metrics.get("volatility", 0),
                calmar_ratio=metrics.get("calmar_ratio", 0),
                trade_count=metrics.get("trade_count", 0),
                params=strategy_params,
                equity_curve=result.get("equity_curve", []),
            )
            db.add(backtest_row)
            await db.commit()
        
        return {
            "code": 200,
            "message": "回测完成",
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"运行回测失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"运行回测失败: {str(e)}"
        )


@router.post("/{strategy_id}/optimize")
async def optimize_strategy(
    strategy_id: int,
    request: OptimizeRequest,
    method: str = Query("grid_search", pattern="^(grid_search|genetic|bayesian)$"),
    db: AsyncSession = Depends(get_db),
):
    """参数优化"""
    try:
        logger.info(f"参数优化: strategy_id={strategy_id}, method={method}")

        strategy_result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
        strategy = strategy_result.scalar_one_or_none()
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")

        strategy_type = request.strategy_type or strategy.type
        if strategy_type not in STRATEGY_TEMPLATES:
            raise HTTPException(status_code=400, detail=f"不支持的策略类型: {strategy_type}")

        if not request.param_ranges:
            raise HTTPException(status_code=400, detail="param_ranges 不能为空")

        # 解析参数空间（支持 list 或 {min,max,step}）
        grid_values: Dict[str, List[Any]] = {}
        for key, value in request.param_ranges.items():
            if isinstance(value, list):
                if len(value) == 0:
                    raise HTTPException(status_code=400, detail=f"参数 {key} 候选值为空")
                grid_values[key] = value
            elif isinstance(value, dict) and {"min", "max"}.issubset(value.keys()):
                start = value["min"]
                end = value["max"]
                step = value.get("step", 1)
                if step == 0:
                    raise HTTPException(status_code=400, detail=f"参数 {key} 的 step 不能为0")
                vals = []
                current = start
                max_loops = 2000
                loops = 0
                while current <= end and loops < max_loops:
                    vals.append(current)
                    current = current + step
                    loops += 1
                if len(vals) == 0:
                    raise HTTPException(status_code=400, detail=f"参数 {key} 无可用取值")
                grid_values[key] = vals
            else:
                raise HTTPException(status_code=400, detail=f"参数 {key} 格式不支持")

        keys = list(grid_values.keys())
        combinations = [dict(zip(keys, values)) for values in product(*[grid_values[k] for k in keys])]

        # 防止组合爆炸导致接口阻塞
        max_combinations = 300
        if len(combinations) > max_combinations:
            combinations = combinations[:max_combinations]

        objective = request.objective
        maximize = request.maximize if objective != "max_drawdown" else False

        best_score = float("-inf") if maximize else float("inf")
        best_params = None
        best_result = None
        all_results = []

        for param_combo in combinations:
            base_params = strategy.params or {}
            run_params = {
                "type": strategy_type,
                **base_params,
                **param_combo,
            }

            freq_mapping = {
                "daily": "1d",
                "60min": "60min",
                "30min": "30min",
                "15min": "15min",
                "5min": "5min",
            }
            freq = freq_mapping.get(request.frequency, request.frequency)

            engine = BacktestEngine(
                initial_capital=100000,
                commission=0.0003,
                slippage=0.001,
            )

            backtest_result = await engine.run_backtest(
                stock_code=request.stock_code,
                start_date=datetime.combine(request.start_date, datetime.min.time()),
                end_date=datetime.combine(request.end_date, datetime.max.time()),
                freq=freq,
                strategy_params=run_params,
                data_source="auto",
            )

            metrics = backtest_result.get("metrics", {})
            score = metrics.get(objective, None)
            if score is None:
                # 目标不存在时默认用夏普
                score = metrics.get("sharpe_ratio", 0)

            score_value = float(score)
            all_results.append(
                {
                    "params": param_combo,
                    "score": score_value,
                    "metrics": metrics,
                }
            )

            if maximize:
                if score_value > best_score:
                    best_score = score_value
                    best_params = param_combo
                    best_result = metrics
            else:
                if score_value < best_score:
                    best_score = score_value
                    best_params = param_combo
                    best_result = metrics

        # 将最优参数保存到策略配置中
        if best_params is not None:
            strategy.params = {**(strategy.params or {}), **best_params}
            await db.commit()

        return {
            "code": 200,
            "message": "优化完成",
            "data": {
                "strategy_id": strategy_id,
                "method": method,
                "objective": objective,
                "maximize": maximize,
                "evaluated": len(combinations),
                "best_params": best_params,
                "best_score": best_score,
                "best_metrics": best_result,
                "all_results": all_results,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"参数优化失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="参数优化失败"
        )
