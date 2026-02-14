"""遗传算法优化器"""
import time
import random
from typing import Dict, Any, List, Callable, Tuple
import logging

from .base_optimizer import BaseOptimizer, OptimizationResult

logger = logging.getLogger(__name__)


class GeneticOptimizer(BaseOptimizer):
    """遗传算法优化器
    
    模拟自然选择和遗传过程，通过选择、交叉、变异找到最优解。
    适合参数空间较大的情况。
    支持多目标优化。
    """
    
    def __init__(
        self,
        objective: str = 'sharpe_ratio',
        maximize: bool = True,
        n_jobs: int = 1,
        population_size: int = 50,
        generations: int = 20,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.1,
        elitism_rate: float = 0.1
    ):
        """
        初始化遗传算法优化器
        
        Args:
            objective: 优化目标
            maximize: 是否最大化
            n_jobs: 并行任务数
            population_size: 种群大小
            generations: 迭代代数
            crossover_rate: 交叉概率
            mutation_rate: 变异概率
            elitism_rate: 精英保留比例
        """
        super().__init__(objective, maximize, n_jobs)
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_rate = elitism_rate
    
    async def optimize(
        self,
        objective_func: Callable,
        param_ranges: Dict[str, Dict[str, Any]],
        verbose: bool = True,
        **kwargs
    ) -> OptimizationResult:
        """
        执行遗传算法优化
        
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
            logger.info(f"遗传算法开始，种群大小: {self.population_size}, 迭代代数: {self.generations}")
        
        # 初始化种群
        population = self._initialize_population(param_ranges)
        
        # 评估初始种群
        population = await self._evaluate_population(objective_func, population)
        
        all_results = []
        
        # 进化迭代
        for generation in range(self.generations):
            if verbose and generation % 5 == 0:
                logger.info(f"第 {generation} 代，最优得分: {self.best_score:.4f}")
            
            # 选择
            selected = self._select(population)
            
            # 交叉
            offspring = self._crossover(selected, param_ranges)
            
            # 变异
            mutated = self._mutate(offspring, param_ranges)
            
            # 评估新种群
            mutated = await self._evaluate_population(objective_func, mutated)
            
            # 精英保留
            population = self._elitism(population, mutated)
            
            # 记录结果
            current_best = max(population, key=lambda x: x['score'])
            all_results.append({
                'generation': generation,
                'best_params': current_best['params'],
                'best_score': current_best['score'],
                'avg_score': sum(p['score'] for p in population) / len(population)
            })
        
        optimization_time = time.time() - start_time
        
        if verbose:
            logger.info(f"遗传算法完成，用时 {optimization_time:.2f} 秒")
            logger.info(f"最优参数: {self.best_params}")
            logger.info(f"最优得分: {self.best_score:.4f}")
        
        return self._create_result(all_results, optimization_time)
    
    def _initialize_population(
        self,
        param_ranges: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """初始化种群"""
        return self._sample_params(param_ranges, self.population_size)
    
    async def _evaluate_population(
        self,
        objective_func: Callable,
        population: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """评估种群"""
        scores = await self._evaluate_params(objective_func, population)
        
        for i, score in enumerate(scores):
            population[i]['score'] = score
            self._update_best(population[i], score)
        
        return population
    
    def _select(
        self,
        population: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """选择操作（轮盘赌选择）"""
        # 按得分排序
        sorted_population = sorted(population, key=lambda x: x['score'], reverse=self.maximize)
        
        # 计算适应度
        if self.maximize:
            min_score = min(p['score'] for p in population)
            fitness = [p['score'] - min_score + 1 for p in sorted_population]
        else:
            max_score = max(p['score'] for p in population)
            fitness = [max_score - p['score'] + 1 for p in sorted_population]
        
        total_fitness = sum(fitness)
        probabilities = [f / total_fitness for f in fitness]
        
        # 轮盘赌选择
        selected = []
        for _ in range(self.population_size):
            r = random.random()
            cumulative = 0
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if r <= cumulative:
                    selected.append(sorted_population[i].copy())
                    break
        
        return selected
    
    def _crossover(
        self,
        population: List[Dict[str, Any]],
        param_ranges: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """交叉操作"""
        offspring = []
        
        for i in range(0, len(population), 2):
            parent1 = population[i]
            parent2 = population[i + 1] if i + 1 < len(population) else population[0]
            
            if random.random() < self.crossover_rate:
                # 单点交叉
                child1, child2 = self._single_point_crossover(
                    parent1, parent2, param_ranges
                )
                offspring.extend([child1, child2])
            else:
                offspring.extend([parent1.copy(), parent2.copy()])
        
        return offspring[:self.population_size]
    
    def _single_point_crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
        param_ranges: Dict[str, Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """单点交叉"""
        params = list(param_ranges.keys())
        crossover_point = random.randint(1, len(params) - 1)
        
        child1 = {}
        child2 = {}
        
        for i, param in enumerate(params):
            if i < crossover_point:
                child1[param] = parent1['params'][param]
                child2[param] = parent2['params'][param]
            else:
                child1[param] = parent2['params'][param]
                child2[param] = parent1['params'][param]
        
        return {'params': child1}, {'params': child2}
    
    def _mutate(
        self,
        population: List[Dict[str, Any]],
        param_ranges: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """变异操作"""
        for individual in population:
            for param_name, param_config in param_ranges.items():
                if random.random() < self.mutation_rate:
                    # 变异该参数
                    param_type = param_config.get('type')
                    
                    if param_type == 'int':
                        start = param_config['min']
                        stop = param_config['max']
                        step = param_config['step']
                        num_steps = (stop - start) // step
                        individual['params'][param_name] = start + random.randint(0, num_steps) * step
                        
                    elif param_type == 'float':
                        start = param_config['min']
                        stop = param_config['max']
                        individual['params'][param_name] = random.uniform(start, stop)
                        
                    elif param_type == 'choice':
                        individual['params'][param_name] = random.choice(param_config['choices'])
        
        return population
    
    def _elitism(
        self,
        old_population: List[Dict[str, Any]],
        new_population: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """精英保留"""
        # 保留最优个体
        elite_size = int(self.population_size * self.elitism_rate)
        
        sorted_old = sorted(old_population, key=lambda x: x['score'], reverse=self.maximize)
        sorted_new = sorted(new_population, key=lambda x: x['score'], reverse=self.maximize)
        
        # 从旧种群中选择精英
        elite = sorted_old[:elite_size]
        
        # 从新种群中选择剩余个体
        remaining = sorted_new[:self.population_size - elite_size]
        
        return elite + remaining