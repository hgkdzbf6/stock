"""优化服务"""
import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timedelta

from optimizers import (
    BaseOptimizer,
    GridSearchOptimizer,
    GeneticOptimizer,
    BayesianOptimizer,
    OptimizationResult
)
from services.backtest_service import BacktestEngine as BacktestService

logger = logging.getLogger(__name__)


class OptimizationService:
    """优化服务
    
    提供统一的优化接口，管理优化任务
    """
    
    def __init__(self, backtest_service: BacktestService):
        """
        初始化优化服务
        
        Args:
            backtest_service: 回测服务
        """
        self.backtest_service = backtest_service
        self.optimization_tasks = {}  # 存储优化任务
    
    async def run_optimization(
        self,
        strategy_type: str,
        stock_code: str,
        start_date: str,
        end_date: str,
        frequency: str = 'daily',
        initial_capital: float = 100000,
        optimization_method: str = 'grid_search',
        param_ranges: Dict[str, Dict[str, Any]] = None,
        objective: str = 'sharpe_ratio',
        maximize: bool = True,
        n_jobs: int = 1,
        **kwargs
    ) -> OptimizationResult:
        """
        运行优化
        
        Args:
            strategy_type: 策略类型
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 频率
            initial_capital: 初始资金
            optimization_method: 优化方法 (grid_search, genetic, bayesian)
            param_ranges: 参数范围
            objective: 优化目标
            maximize: 是否最大化
            n_jobs: 并行任务数
            **kwargs: 其他参数
            
        Returns:
            OptimizationResult: 优化结果
        """
        logger.info(f"开始优化: {strategy_type}, {stock_code}, 方法: {optimization_method}")
        
        # 创建优化器
        optimizer = self._create_optimizer(
            method=optimization_method,
            objective=objective,
            maximize=maximize,
            n_jobs=n_jobs,
            **kwargs
        )
        
        # 创建目标函数
        objective_func = self._create_objective_func(
            strategy_type=strategy_type,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            initial_capital=initial_capital,
            objective=objective
        )
        
        # 运行优化
        result = await optimizer.optimize(
            objective_func=objective_func,
            param_ranges=param_ranges,
            verbose=True,
            **kwargs
        )
        
        logger.info(f"优化完成: 最优得分 {result.best_score:.4f}")
        
        return result
    
    def _create_optimizer(
        self,
        method: str,
        objective: str,
        maximize: bool,
        n_jobs: int,
        **kwargs
    ) -> BaseOptimizer:
        """
        创建优化器
        
        Args:
            method: 优化方法
            objective: 优化目标
            maximize: 是否最大化
            n_jobs: 并行任务数
            **kwargs: 其他参数
            
        Returns:
            BaseOptimizer: 优化器实例
        """
        if method == 'grid_search':
            return GridSearchOptimizer(
                objective=objective,
                maximize=maximize,
                n_jobs=n_jobs
            )
        elif method == 'genetic':
            return GeneticOptimizer(
                objective=objective,
                maximize=maximize,
                n_jobs=n_jobs,
                population_size=kwargs.get('population_size', 50),
                generations=kwargs.get('generations', 20),
                crossover_rate=kwargs.get('crossover_rate', 0.8),
                mutation_rate=kwargs.get('mutation_rate', 0.1),
                elitism_rate=kwargs.get('elitism_rate', 0.1)
            )
        elif method == 'bayesian':
            return BayesianOptimizer(
                objective=objective,
                maximize=maximize,
                n_jobs=n_jobs,
                n_iter=kwargs.get('n_iter', 100),
                n_init=kwargs.get('n_init', 10),
                acquisition=kwargs.get('acquisition', 'EI')
            )
        else:
            raise ValueError(f"不支持的优化方法: {method}")
    
    def _create_objective_func(
        self,
        strategy_type: str,
        stock_code: str,
        start_date: str,
        end_date: str,
        frequency: str,
        initial_capital: float,
        objective: str
    ) -> Callable:
        """
        创建目标函数
        
        Args:
            strategy_type: 策略类型
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 频率
            initial_capital: 初始资金
            objective: 优化目标
            
        Returns:
            Callable: 目标函数
        """
        async def objective_func(params: Dict[str, Any]) -> float:
            """目标函数"""
            try:
                # 运行回测
                result = await self.backtest_service.run_backtest(
                    strategy_type=strategy_type,
                    stock_code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    frequency=frequency,
                    initial_capital=initial_capital,
                    params=params
                )
                
                # 提取目标值
                if objective == 'total_return':
                    return result.get('total_return', float('-inf'))
                elif objective == 'sharpe_ratio':
                    return result.get('sharpe_ratio', float('-inf'))
                elif objective == 'max_drawdown':
                    # 对于回撤，越小越好
                    return result.get('max_drawdown', float('inf'))
                elif objective == 'calmar_ratio':
                    return result.get('calmar_ratio', float('-inf'))
                elif objective == 'win_rate':
                    return result.get('win_rate', float('-inf'))
                elif objective == 'profit_loss_ratio':
                    return result.get('profit_loss_ratio', float('-inf'))
                else:
                    logger.warning(f"未知的目标: {objective}, 使用total_return")
                    return result.get('total_return', float('-inf'))
                    
            except Exception as e:
                logger.error(f"回测失败: {params}, 错误: {e}")
                # 返回最差值
                return float('-inf') if objective != 'max_drawdown' else float('inf')
        
        return objective_func
    
    async def run_parallel_optimization(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[OptimizationResult]:
        """
        并行运行多个优化任务
        
        Args:
            tasks: 任务列表
            
        Returns:
            List[OptimizationResult]: 优化结果列表
        """
        import asyncio
        
        logger.info(f"开始并行优化，共 {len(tasks)} 个任务")
        
        # 创建任务
        async_tasks = []
        for task in tasks:
            async_tasks.append(self.run_optimization(**task))
        
        # 并行执行
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"任务 {i} 失败: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        logger.info(f"并行优化完成，成功 {sum(1 for r in processed_results if r is not None)}/{len(tasks)}")
        
        return processed_results
    
    def save_optimization_result(
        self,
        result: OptimizationResult,
        strategy_id: int,
        method: str,
        stock_code: str,
        start_date: str,
        end_date: str,
        frequency: str
    ) -> Dict[str, Any]:
        """
        保存优化结果到数据库
        
        Args:
            result: 优化结果
            strategy_id: 策略ID
            method: 优化方法
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 频率
            
        Returns:
            Dict[str, Any]: 保存的结果
        """
        # TODO: 实现数据库保存
        logger.info(f"保存优化结果: 策略ID={strategy_id}, 方法={method}")
        
        return {
            'id': 1,
            'strategy_id': strategy_id,
            'method': method,
            'stock_code': stock_code,
            'start_date': start_date,
            'end_date': end_date,
            'frequency': frequency,
            'best_params': result.best_params,
            'best_score': result.best_score,
            'all_results': result.all_results,
            'optimization_time': result.optimization_time,
            'iterations': result.iterations,
            'created_at': datetime.now()
        }
    
    def get_optimization_result(
        self,
        result_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取优化结果
        
        Args:
            result_id: 结果ID
            
        Returns:
            Optional[Dict[str, Any]]: 优化结果
        """
        # TODO: 实现数据库查询
        logger.info(f"获取优化结果: ID={result_id}")
        return None
    
    def get_optimization_history(
        self,
        strategy_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取优化历史
        
        Args:
            strategy_id: 策略ID
            limit: 限制数量
            
        Returns:
            List[Dict[str, Any]]: 优化历史列表
        """
        # TODO: 实现数据库查询
        logger.info(f"获取优化历史: 策略ID={strategy_id}, 限制={limit}")
        return []