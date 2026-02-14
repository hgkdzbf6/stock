"""优化API"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from core.security import get_current_user_id
from services.optimization_service import OptimizationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/optimization", tags=["optimization"])


# 请求模型
class OptimizationRequest(BaseModel):
    """优化请求"""
    strategy_type: str = Field(..., description="策略类型")
    stock_code: str = Field(..., description="股票代码")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    frequency: str = Field(default="daily", description="频率")
    initial_capital: float = Field(default=100000, description="初始资金")
    optimization_method: str = Field(default="grid_search", description="优化方法")
    param_ranges: Dict[str, Dict[str, Any]] = Field(..., description="参数范围")
    objective: str = Field(default="sharpe_ratio", description="优化目标")
    maximize: bool = Field(default=True, description="是否最大化")
    n_jobs: int = Field(default=1, description="并行任务数")
    
    # 遗传算法参数
    population_size: Optional[int] = Field(default=50, description="种群大小")
    generations: Optional[int] = Field(default=20, description="迭代代数")
    crossover_rate: Optional[float] = Field(default=0.8, description="交叉概率")
    mutation_rate: Optional[float] = Field(default=0.1, description="变异概率")
    elitism_rate: Optional[float] = Field(default=0.1, description="精英保留比例")
    
    # 贝叶斯优化参数
    n_iter: Optional[int] = Field(default=100, description="迭代次数")
    n_init: Optional[int] = Field(default=10, description="初始采样次数")
    acquisition: Optional[str] = Field(default="EI", description="采集函数")


class ParallelOptimizationRequest(BaseModel):
    """并行优化请求"""
    tasks: List[Dict[str, Any]] = Field(..., description="任务列表")


# 响应模型
class OptimizationResponse(BaseModel):
    """优化响应"""
    best_params: Dict[str, Any] = Field(..., description="最优参数")
    best_score: float = Field(..., description="最优得分")
    all_results: List[Dict[str, Any]] = Field(default=[], description="所有结果")
    optimization_time: float = Field(..., description="优化时间（秒）")
    iterations: int = Field(..., description="迭代次数")
    convergence_curve: List[float] = Field(default=[], description="收敛曲线")


# 优化服务实例（全局）
optimization_service: Optional[OptimizationService] = None


def get_optimization_service() -> OptimizationService:
    """获取优化服务"""
    global optimization_service
    if optimization_service is None:
        # TODO: 从依赖注入获取
        from services.backtest_service import BacktestService
        backtest_service = BacktestService()
        optimization_service = OptimizationService(backtest_service)
    return optimization_service


@router.post("/grid-search")
async def grid_search(
    request: OptimizationRequest,
    user_id: int = Depends(get_current_user_id),
    service: OptimizationService = Depends(get_optimization_service)
):
    """
    网格搜索优化
    
    遍历所有参数组合，找到最优解。
    适合参数空间较小的情况。
    保证找到全局最优解。
    """
    try:
        logger.info(f"用户 {user_id} 请求网格搜索优化")
        
        result = await service.run_optimization(
            strategy_type=request.strategy_type,
            stock_code=request.stock_code,
            start_date=request.start_date,
            end_date=request.end_date,
            frequency=request.frequency,
            initial_capital=request.initial_capital,
            optimization_method='grid_search',
            param_ranges=request.param_ranges,
            objective=request.objective,
            maximize=request.maximize,
            n_jobs=request.n_jobs
        )
        
        return OptimizationResponse(
            best_params=result.best_params,
            best_score=result.best_score,
            all_results=result.all_results,
            optimization_time=result.optimization_time,
            iterations=result.iterations,
            convergence_curve=result.convergence_curve
        )
        
    except Exception as e:
        logger.error(f"网格搜索优化失败: {e}")
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")


@router.post("/genetic")
async def genetic_optimization(
    request: OptimizationRequest,
    user_id: int = Depends(get_current_user_id),
    service: OptimizationService = Depends(get_optimization_service)
):
    """
    遗传算法优化
    
    模拟自然选择和遗传过程，通过选择、交叉、变异找到最优解。
    适合参数空间较大的情况。
    支持多目标优化。
    """
    try:
        logger.info(f"用户 {user_id} 请求遗传算法优化")
        
        result = await service.run_optimization(
            strategy_type=request.strategy_type,
            stock_code=request.stock_code,
            start_date=request.start_date,
            end_date=request.end_date,
            frequency=request.frequency,
            initial_capital=request.initial_capital,
            optimization_method='genetic',
            param_ranges=request.param_ranges,
            objective=request.objective,
            maximize=request.maximize,
            n_jobs=request.n_jobs,
            population_size=request.population_size,
            generations=request.generations,
            crossover_rate=request.crossover_rate,
            mutation_rate=request.mutation_rate,
            elitism_rate=request.elitism_rate
        )
        
        return OptimizationResponse(
            best_params=result.best_params,
            best_score=result.best_score,
            all_results=result.all_results,
            optimization_time=result.optimization_time,
            iterations=result.iterations,
            convergence_curve=result.convergence_curve
        )
        
    except Exception as e:
        logger.error(f"遗传算法优化失败: {e}")
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")


@router.post("/bayesian")
async def bayesian_optimization(
    request: OptimizationRequest,
    user_id: int = Depends(get_current_user_id),
    service: OptimizationService = Depends(get_optimization_service)
):
    """
    贝叶斯优化
    
    基于概率模型的优化方法，通过构建代理模型来预测函数值。
    样本效率高，适合评估成本高的情况。
    """
    try:
        logger.info(f"用户 {user_id} 请求贝叶斯优化")
        
        result = await service.run_optimization(
            strategy_type=request.strategy_type,
            stock_code=request.stock_code,
            start_date=request.start_date,
            end_date=request.end_date,
            frequency=request.frequency,
            initial_capital=request.initial_capital,
            optimization_method='bayesian',
            param_ranges=request.param_ranges,
            objective=request.objective,
            maximize=request.maximize,
            n_jobs=request.n_jobs,
            n_iter=request.n_iter,
            n_init=request.n_init,
            acquisition=request.acquisition
        )
        
        return OptimizationResponse(
            best_params=result.best_params,
            best_score=result.best_score,
            all_results=result.all_results,
            optimization_time=result.optimization_time,
            iterations=result.iterations,
            convergence_curve=result.convergence_curve
        )
        
    except Exception as e:
        logger.error(f"贝叶斯优化失败: {e}")
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")


@router.post("/parallel")
async def parallel_optimization(
    request: ParallelOptimizationRequest,
    user_id: int = Depends(get_current_user_id),
    service: OptimizationService = Depends(get_optimization_service)
):
    """
    并行优化
    
    同时运行多个优化任务，提高效率。
    """
    try:
        logger.info(f"用户 {user_id} 请求并行优化，共 {len(request.tasks)} 个任务")
        
        results = await service.run_parallel_optimization(request.tasks)
        
        # 过滤掉失败的任务
        valid_results = [r for r in results if r is not None]
        
        # 转换为响应格式
        response_data = []
        for result in valid_results:
            response_data.append({
                'best_params': result.best_params,
                'best_score': result.best_score,
                'all_results': result.all_results,
                'optimization_time': result.optimization_time,
                'iterations': result.iterations,
                'convergence_curve': result.convergence_curve
            })
        
        return {
            'total': len(request.tasks),
            'successful': len(valid_results),
            'failed': len(results) - len(valid_results),
            'results': response_data
        }
        
    except Exception as e:
        logger.error(f"并行优化失败: {e}")
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")


@router.get("/results/{result_id}")
async def get_optimization_result(
    result_id: int,
    user_id: int = Depends(get_current_user_id),
    service: OptimizationService = Depends(get_optimization_service)
):
    """
    获取优化结果
    """
    try:
        logger.info(f"用户 {user_id} 请求优化结果: {result_id}")
        
        result = service.get_optimization_result(result_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail="优化结果不存在")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取优化结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/history")
async def get_optimization_history(
    strategy_id: Optional[int] = None,
    limit: int = 10,
    user_id: int = Depends(get_current_user_id),
    service: OptimizationService = Depends(get_optimization_service)
):
    """
    获取优化历史
    """
    try:
        logger.info(f"用户 {user_id} 请求优化历史")
        
        if strategy_id:
            results = service.get_optimization_history(strategy_id, limit)
        else:
            results = []
        
        return {
            'total': len(results),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"获取优化历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/save")
async def save_optimization_result(
    request: Dict[str, Any],
    user_id: int = Depends(get_current_user_id),
    service: OptimizationService = Depends(get_optimization_service)
):
    """
    保存优化结果
    """
    try:
        logger.info(f"用户 {user_id} 保存优化结果")
        
        # TODO: 从请求中提取参数
        result_data = service.save_optimization_result(
            result=request.get('result'),
            strategy_id=request.get('strategy_id'),
            method=request.get('method'),
            stock_code=request.get('stock_code'),
            start_date=request.get('start_date'),
            end_date=request.get('end_date'),
            frequency=request.get('frequency')
        )
        
        return {
            'success': True,
            'result_id': result_data['id']
        }
        
    except Exception as e:
        logger.error(f"保存优化结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")