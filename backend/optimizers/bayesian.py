"""贝叶斯优化器"""
import time
import random
from typing import Dict, Any, List, Callable, Tuple
import logging

from .base_optimizer import BaseOptimizer, OptimizationResult

logger = logging.getLogger(__name__)


class BayesianOptimizer(BaseOptimizer):
    """贝叶斯优化器
    
    基于概率模型的优化方法，通过构建代理模型来预测函数值。
    样本效率高，适合评估成本高的情况。
    """
    
    def __init__(
        self,
        objective: str = 'sharpe_ratio',
        maximize: bool = True,
        n_jobs: int = 1,
        n_iter: int = 100,
        n_init: int = 10,
        acquisition: str = 'EI'
    ):
        """
        初始化贝叶斯优化器
        
        Args:
            objective: 优化目标
            maximize: 是否最大化
            n_jobs: 并行任务数
            n_iter: 迭代次数
            n_init: 初始采样次数
            acquisition: 采集函数 (EI, PI, UCB)
        """
        super().__init__(objective, maximize, n_jobs)
        self.n_iter = n_iter
        self.n_init = n_init
        self.acquisition = acquisition
    
    async def optimize(
        self,
        objective_func: Callable,
        param_ranges: Dict[str, Dict[str, Any]],
        verbose: bool = True,
        **kwargs
    ) -> OptimizationResult:
        """
        执行贝叶斯优化
        
        Args:
            objective_func: 目标函数
            param_ranges: 参数范围字典
            verbose: 是否打印进度
            **kwargs: 其他参数
            
        Returns:
            OptimizationResult: 优化结果
        """
        start_time = time.time()
        
        # 验证参数范围
        if not self._validate_param_ranges(param_ranges):
            raise ValueError("参数范围无效")
        
        if verbose:
            logger.info(f"贝叶斯优化开始，迭代次数: {self.n_iter}, 初始采样: {self.n_init}")
        
        # 初始随机采样
        X_init = self._sample_params(param_ranges, self.n_init)
        y_init = await self._evaluate_params(objective_func, X_init)
        
        # 记录初始结果
        X = [x.copy() for x in X_init]
        y = y_init.copy()
        all_results = []
        
        for i, (params, score) in enumerate(zip(X_init, y_init)):
            result = {'params': params, 'score': score}
            all_results.append(result)
            self._update_best(params, score)
        
        # 贝叶斯优化迭代
        for iteration in range(self.n_iter):
            if verbose and iteration % 10 == 0:
                logger.info(f"第 {iteration} 次迭代，最优得分: {self.best_score:.4f}")
            
            # 构建代理模型（简化版：使用最近邻）
            next_params = self._suggest_next_params(X, y, param_ranges)
            
            # 评估新参数
            score = await objective_func(next_params)
            
            # 记录结果
            X.append(next_params)
            y.append(score)
            all_results.append({'params': next_params, 'score': score})
            self._update_best(next_params, score)
        
        optimization_time = time.time() - start_time
        
        if verbose:
            logger.info(f"贝叶斯优化完成，用时 {optimization_time:.2f} 秒")
            logger.info(f"最优参数: {self.best_params}")
            logger.info(f"最优得分: {self.best_score:.4f}")
        
        return self._create_result(all_results, optimization_time)
    
    def _suggest_next_params(
        self,
        X: List[Dict[str, Any]],
        y: List[float],
        param_ranges: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        建议下一个采样点
        
        Args:
            X: 历史参数列表
            y: 历史得分列表
            param_ranges: 参数范围
            
        Returns:
            Dict[str, Any]: 建议的参数
        """
        # 简化版：结合探索和利用
        n_samples = 100
        candidates = self._sample_params(param_ranges, n_samples)
        
        # 评估候选点
        best_candidate = None
        best_acquisition = float('-inf') if self.maximize else float('inf')
        
        for candidate in candidates:
            # 计算采集函数值
            acquisition_value = self._acquisition_function(
                candidate, X, y, param_ranges
            )
            
            if self.maximize:
                if acquisition_value > best_acquisition:
                    best_acquisition = acquisition_value
                    best_candidate = candidate
            else:
                if acquisition_value < best_acquisition:
                    best_acquisition = acquisition_value
                    best_candidate = candidate
        
        return best_candidate
    
    def _acquisition_function(
        self,
        candidate: Dict[str, Any],
        X: List[Dict[str, Any]],
        y: List[float],
        param_ranges: Dict[str, Dict[str, Any]]
    ) -> float:
        """
        采集函数
        
        Args:
            candidate: 候选参数
            X: 历史参数
            y: 历史得分
            param_ranges: 参数范围
            
        Returns:
            float: 采集函数值
        """
        # 找到最近的邻居
        distances = []
        for x in X:
            distance = self._param_distance(candidate, x, param_ranges)
            distances.append(distance)
        
        k = min(5, len(distances))  # k近邻
        nearest_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:k]
        
        # 计算均值和标准差
        nearest_scores = [y[i] for i in nearest_indices]
        mu = sum(nearest_scores) / len(nearest_scores)
        sigma = (sum((s - mu) ** 2 for s in nearest_scores) / len(nearest_scores)) ** 0.5 if len(nearest_scores) > 1 else 0
        
        # 采集函数
        if self.acquisition == 'EI':
            # Expected Improvement
            if self.maximize:
                xi = mu - self.best_score
                if sigma == 0:
                    return xi
                from math import erf, sqrt, exp
                z = xi / sigma
                return xi * (0.5 + 0.5 * erf(z / sqrt(2))) + sigma * exp(-0.5 * z * z) / sqrt(2 * 3.14159)
            else:
                xi = self.best_score - mu
                if sigma == 0:
                    return xi
                from math import erf, sqrt, exp
                z = xi / sigma
                return xi * (0.5 + 0.5 * erf(z / sqrt(2))) + sigma * exp(-0.5 * z * z) / sqrt(2 * 3.14159)
        
        elif self.acquisition == 'PI':
            # Probability of Improvement
            if self.maximize:
                if sigma == 0:
                    return 1.0 if mu > self.best_score else 0.0
                from math import erf, sqrt
                z = (mu - self.best_score) / sigma
                return 0.5 + 0.5 * erf(z / sqrt(2))
            else:
                if sigma == 0:
                    return 1.0 if mu < self.best_score else 0.0
                from math import erf, sqrt
                z = (self.best_score - mu) / sigma
                return 0.5 + 0.5 * erf(z / sqrt(2))
        
        elif self.acquisition == 'UCB':
            # Upper Confidence Bound
            kappa = 2.576  # 99%置信区间
            if self.maximize:
                return mu + kappa * sigma
            else:
                return mu - kappa * sigma
        
        else:
            # 默认使用EI
            if self.maximize:
                return mu - self.best_score + sigma
            else:
                return self.best_score - mu + sigma
    
    def _param_distance(
        self,
        params1: Dict[str, Any],
        params2: Dict[str, Any],
        param_ranges: Dict[str, Dict[str, Any]]
    ) -> float:
        """
        计算参数之间的距离（归一化欧氏距离）
        
        Args:
            params1: 参数1
            params2: 参数2
            param_ranges: 参数范围
            
        Returns:
            float: 距离
        """
        distance = 0.0
        
        for param_name in param_ranges.keys():
            val1 = params1[param_name]
            val2 = params2[param_name]
            param_config = param_ranges[param_name]
            
            # 归一化到[0, 1]
            if param_config['type'] == 'int':
                norm_val1 = (val1 - param_config['min']) / (param_config['max'] - param_config['min'])
                norm_val2 = (val2 - param_config['min']) / (param_config['max'] - param_config['min'])
                distance += (norm_val1 - norm_val2) ** 2
                
            elif param_config['type'] == 'float':
                norm_val1 = (val1 - param_config['min']) / (param_config['max'] - param_config['min'])
                norm_val2 = (val2 - param_config['min']) / (param_config['max'] - param_config['min'])
                distance += (norm_val1 - norm_val2) ** 2
                
            elif param_config['type'] == 'choice':
                # 对于离散选择，距离为0（相同）或1（不同）
                distance += 0.0 if val1 == val2 else 1.0
        
        return distance ** 0.5