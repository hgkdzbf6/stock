"""优化器基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """优化结果"""
    best_params: Dict[str, Any]  # 最优参数
    best_score: float  # 最优得分
    all_results: List[Dict[str, Any]] = field(default_factory=list)  # 所有结果
    optimization_time: float = 0.0  # 优化时间（秒）
    iterations: int = 0  # 迭代次数
    convergence_curve: List[float] = field(default_factory=list)  # 收敛曲线
    timestamp: datetime = field(default_factory=datetime.now)  # 时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'all_results': self.all_results,
            'optimization_time': self.optimization_time,
            'iterations': self.iterations,
            'convergence_curve': self.convergence_curve,
            'timestamp': self.timestamp.isoformat()
        }


class BaseOptimizer(ABC):
    """优化器基类"""
    
    def __init__(
        self,
        objective: str = 'sharpe_ratio',
        maximize: bool = True,
        n_jobs: int = 1
    ):
        """
        初始化优化器
        
        Args:
            objective: 优化目标（sharpe_ratio, total_return, max_drawdown等）
            maximize: 是否最大化（True）或最小化（False）
            n_jobs: 并行任务数
        """
        self.objective = objective
        self.maximize = maximize
        self.n_jobs = n_jobs
        self.best_score = float('-inf') if maximize else float('inf')
        self.best_params = {}
        self.convergence_curve = []
        
    @abstractmethod
    async def optimize(
        self,
        objective_func: Callable,
        param_ranges: Dict[str, Dict[str, Any]],
        **kwargs
    ) -> OptimizationResult:
        """
        执行优化
        
        Args:
            objective_func: 目标函数，接受参数字典，返回得分
            param_ranges: 参数范围字典
                {
                    'param_name': {
                        'type': 'int' | 'float' | 'choice',
                        'min': 0,  # 对于int/float
                        'max': 100,  # 对于int/float
                        'step': 1,  # 对于int/float
                        'choices': [1, 2, 3]  # 对于choice
                    }
                }
            **kwargs: 其他参数
            
        Returns:
            OptimizationResult: 优化结果
        """
        pass
    
    def _is_better(self, score: float) -> bool:
        """
        判断得分是否更好
        
        Args:
            score: 新得分
            
        Returns:
            bool: 是否更好
        """
        if self.maximize:
            return score > self.best_score
        else:
            return score < self.best_score
    
    def _update_best(self, params: Dict[str, Any], score: float):
        """
        更新最优解
        
        Args:
            params: 参数字典
            score: 得分
        """
        if self._is_better(score):
            self.best_score = score
            self.best_params = params.copy()
        
        self.convergence_curve.append(score)
    
    async def _evaluate_params(
        self,
        objective_func: Callable,
        params_list: List[Dict[str, Any]]
    ) -> List[float]:
        """
        评估参数列表
        
        Args:
            objective_func: 目标函数
            params_list: 参数列表
            
        Returns:
            List[float]: 得分列表
        """
        scores = []
        
        if self.n_jobs == 1:
            # 串行执行
            for params in params_list:
                try:
                    score = await objective_func(params)
                    scores.append(score)
                except Exception as e:
                    logger.error(f"评估参数失败: {params}, 错误: {e}")
                    scores.append(float('-inf') if self.maximize else float('inf'))
        else:
            # 并行执行
            tasks = [objective_func(params) for params in params_list]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"评估参数失败: {result}")
                    scores.append(float('-inf') if self.maximize else float('inf'))
                else:
                    scores.append(result)
        
        return scores
    
    def _validate_param_ranges(self, param_ranges: Dict[str, Dict[str, Any]]) -> bool:
        """
        验证参数范围
        
        Args:
            param_ranges: 参数范围字典
            
        Returns:
            bool: 是否有效
        """
        for param_name, param_config in param_ranges.items():
            param_type = param_config.get('type')
            
            if param_type == 'int':
                required_keys = ['min', 'max', 'step']
                if not all(key in param_config for key in required_keys):
                    logger.error(f"参数 {param_name} 缺少必需的键: {required_keys}")
                    return False
                    
                if param_config['min'] >= param_config['max']:
                    logger.error(f"参数 {param_name} 的min必须小于max")
                    return False
                    
            elif param_type == 'float':
                required_keys = ['min', 'max']
                if not all(key in param_config for key in required_keys):
                    logger.error(f"参数 {param_name} 缺少必需的键: {required_keys}")
                    return False
                    
                if param_config['min'] >= param_config['max']:
                    logger.error(f"参数 {param_name} 的min必须小于max")
                    return False
                    
            elif param_type == 'choice':
                if 'choices' not in param_config:
                    logger.error(f"参数 {param_name} 缺少choices")
                    return False
                    
                if not isinstance(param_config['choices'], list) or len(param_config['choices']) == 0:
                    logger.error(f"参数 {param_name} 的choices必须是非空列表")
                    return False
                    
            else:
                logger.error(f"参数 {param_name} 的类型 {param_type} 不支持")
                return False
        
        return True
    
    def _generate_param_combinations(
        self,
        param_ranges: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        生成参数组合（用于网格搜索等需要枚举的情况）
        
        Args:
            param_ranges: 参数范围字典
            
        Returns:
            List[Dict[str, Any]]: 参数组合列表
        """
        import itertools
        
        param_values = {}
        for param_name, param_config in param_ranges.items():
            param_type = param_config.get('type')
            
            if param_type == 'int':
                start = param_config['min']
                stop = param_config['max']
                step = param_config['step']
                param_values[param_name] = list(range(start, stop + 1, step))
                
            elif param_type == 'float':
                # 对于float，使用固定数量的采样点
                start = param_config['min']
                stop = param_config['max']
                num_points = 10  # 默认采样点数
                step = (stop - start) / (num_points - 1)
                param_values[param_name] = [
                    round(start + i * step, 4)
                    for i in range(num_points)
                ]
                
            elif param_type == 'choice':
                param_values[param_name] = param_config['choices']
        
        # 生成所有组合
        param_names = list(param_values.keys())
        values_list = list(param_values.values())
        
        combinations = []
        for combination in itertools.product(*values_list):
            param_dict = dict(zip(param_names, combination))
            combinations.append(param_dict)
        
        return combinations
    
    def _sample_params(
        self,
        param_ranges: Dict[str, Dict[str, Any]],
        n_samples: int = 1
    ) -> List[Dict[str, Any]]:
        """
        随机采样参数
        
        Args:
            param_ranges: 参数范围字典
            n_samples: 采样数量
            
        Returns:
            List[Dict[str, Any]]: 参数字典列表
        """
        import random
        
        samples = []
        for _ in range(n_samples):
            params = {}
            for param_name, param_config in param_ranges.items():
                param_type = param_config.get('type')
                
                if param_type == 'int':
                    start = param_config['min']
                    stop = param_config['max']
                    step = param_config['step']
                    num_steps = (stop - start) // step
                    params[param_name] = start + random.randint(0, num_steps) * step
                    
                elif param_type == 'float':
                    start = param_config['min']
                    stop = param_config['max']
                    params[param_name] = random.uniform(start, stop)
                    
                elif param_type == 'choice':
                    params[param_name] = random.choice(param_config['choices'])
            
            samples.append(params)
        
        return samples
    
    def _create_result(
        self,
        all_results: List[Dict[str, Any]],
        optimization_time: float
    ) -> OptimizationResult:
        """
        创建优化结果对象
        
        Args:
            all_results: 所有结果列表
            optimization_time: 优化时间
            
        Returns:
            OptimizationResult: 优化结果
        """
        return OptimizationResult(
            best_params=self.best_params,
            best_score=self.best_score,
            all_results=all_results,
            optimization_time=optimization_time,
            iterations=len(all_results),
            convergence_curve=self.convergence_curve
        )