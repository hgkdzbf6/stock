import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// 优化器类型
export type OptimizationMethod = 'grid_search' | 'genetic' | 'bayesian';

export type OptimizationObjective = 
  | 'total_return'
  | 'sharpe_ratio'
  | 'max_drawdown'
  | 'calmar_ratio'
  | 'win_rate'
  | 'profit_loss_ratio';

// 参数类型
export interface ParamRange {
  type: 'int' | 'float' | 'choice';
  min?: number;
  max?: number;
  step?: number;
  choices?: any[];
}

// 优化请求
export interface OptimizationRequest {
  strategy_type: string;
  stock_code: string;
  start_date: string;
  end_date: string;
  frequency?: string;
  initial_capital?: number;
  optimization_method: OptimizationMethod;
  param_ranges: Record<string, ParamRange>;
  objective: OptimizationObjective;
  maximize?: boolean;
  n_jobs?: number;
  
  // 遗传算法参数
  population_size?: number;
  generations?: number;
  crossover_rate?: number;
  mutation_rate?: number;
  elitism_rate?: number;
  
  // 贝叶斯优化参数
  n_iter?: number;
  n_init?: number;
  acquisition?: 'EI' | 'PI' | 'UCB';
}

// 优化结果
export interface OptimizationResult {
  best_params: Record<string, any>;
  best_score: number;
  all_results: Array<{
    params: Record<string, any>;
    score: number;
  }>;
  optimization_time: number;
  iterations: number;
  convergence_curve: number[];
}

// 并行优化任务
export interface OptimizationTask extends OptimizationRequest {
  id?: string;
}

// 并行优化响应
export interface ParallelOptimizationResponse {
  total: number;
  successful: number;
  failed: number;
  results: OptimizationResult[];
}

class OptimizationService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_URL;
  }

  // 获取认证token
  private getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  // 网格搜索优化
  async gridSearch(request: OptimizationRequest): Promise<OptimizationResult> {
    const response = await axios.post(
      `${this.baseUrl}/api/v1/optimization/grid-search`,
      request,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // 遗传算法优化
  async geneticOptimization(request: OptimizationRequest): Promise<OptimizationResult> {
    const response = await axios.post(
      `${this.baseUrl}/api/v1/optimization/genetic`,
      request,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // 贝叶斯优化
  async bayesianOptimization(request: OptimizationRequest): Promise<OptimizationResult> {
    const response = await axios.post(
      `${this.baseUrl}/api/v1/optimization/bayesian`,
      request,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // 并行优化
  async parallelOptimization(tasks: OptimizationTask[]): Promise<ParallelOptimizationResponse> {
    const response = await axios.post(
      `${this.baseUrl}/api/v1/optimization/parallel`,
      { tasks },
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // 获取优化结果
  async getOptimizationResult(resultId: number): Promise<any> {
    const response = await axios.get(
      `${this.baseUrl}/api/v1/optimization/results/${resultId}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // 获取优化历史
  async getOptimizationHistory(strategyId?: number, limit: number = 10): Promise<any> {
    const params: any = { limit };
    if (strategyId) {
      params.strategy_id = strategyId;
    }
    
    const response = await axios.get(
      `${this.baseUrl}/api/v1/optimization/history`,
      { 
        headers: this.getAuthHeaders(),
        params
      }
    );
    return response.data;
  }

  // 保存优化结果
  async saveOptimizationResult(data: any): Promise<{ success: boolean; result_id: number }> {
    const response = await axios.post(
      `${this.baseUrl}/api/v1/optimization/save`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // 通用优化方法
  async optimize(request: OptimizationRequest): Promise<OptimizationResult> {
    switch (request.optimization_method) {
      case 'grid_search':
        return this.gridSearch(request);
      case 'genetic':
        return this.geneticOptimization(request);
      case 'bayesian':
        return this.bayesianOptimization(request);
      default:
        throw new Error(`Unsupported optimization method: ${request.optimization_method}`);
    }
  }
}

export const optimizationService = new OptimizationService();