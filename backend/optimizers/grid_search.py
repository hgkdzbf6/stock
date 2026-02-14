"""网格搜索优化器"""
import time
from typing import Dict, Any, List, Callable
import logging

from .base_optimizer import BaseOptimizer, OptimizationResult

logger = logging.getLogger(__name__)


class GridSearchOptimizer(BaseOptimizer):
    """网格搜索优化器
    
    遍历所有参数组合，找到最优解。
    适合参数空间较小的情况。
    保证找到全局最优解。
    """
    
    async def optimize(
        self,
        objective_func: Callable,
        param_ranges: Dict[str, Dict[str, Any]],
        verbose: bool = True,
        batch_size: int = 10,
        **kwargs
    ) -> OptimizationResult:
        """
        执行网格搜索优化
        
        Args:
            objective_func: 目标函数
            param_ranges: 参数范围字典
            verbose: 是否打印进度
            batch_size: 批处理大小（并行执行时有效）
            **kwargs: 其他参数
            
        Returns:
            OptimizationResult: 优化结果
        """
        start_time = time.time()
        
        # 验证参数范围
        if not self._validate_param_ranges(param_ranges):
            raise ValueError("参数范围无效")
        
        # 生成所有参数组合
        all_combinations = self._generate_param_combinations(param_ranges)
        total_combinations = len(all_combinations)
        
        if verbose:
            logger.info(f"网格搜索开始，共 {total_combinations} 个参数组合")
        
        # 分批执行
        all_results = []
        batch_num = 0
        
        for i in range(0, total_combinations, batch_size):
            batch = all_combinations[i:i + batch_size]
            batch_num += 1
            
            if verbose:
                logger.info(f"处理批次 {batch_num}/{(total_combinations + batch_size - 1) // batch_size}")
            
            # 评估当前批次
            scores = await self._evaluate_params(objective_func, batch)
            
            # 记录结果
            for params, score in zip(batch, scores):
                result = {
                    'params': params.copy(),
                    'score': score
                }
                all_results.append(result)
                
                # 更新最优解
                self._update_best(params, score)
            
            if verbose:
                logger.info(f"当前最优: {self.best_params}, 得分: {self.best_score:.4f}")
        
        optimization_time = time.time() - start_time
        
        if verbose:
            logger.info(f"网格搜索完成，用时 {optimization_time:.2f} 秒")
            logger.info(f"最优参数: {self.best_params}")
            logger.info(f"最优得分: {self.best_score:.4f}")
        
        return self._create_result(all_results, optimization_time)