import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { 
  OptimizationRequest, 
  OptimizationMethod, 
  OptimizationObjective,
  ParamRange,
  optimizationService 
} from '@/services/optimization';

interface OptimizationConfigProps {
  onOptimize: (request: OptimizationRequest) => Promise<void>;
  loading?: boolean;
}

export function OptimizationConfig({ onOptimize, loading }: OptimizationConfigProps) {
  const [strategyType, setStrategyType] = useState('双均线策略');
  const [stockCode, setStockCode] = useState('600771');
  const [startDate, setStartDate] = useState('2025-01-01');
  const [endDate, setEndDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  });
  const [initialCapital, setInitialCapital] = useState(100000);
  const [optimizationMethod, setOptimizationMethod] = useState<OptimizationMethod>('grid_search');
  const [objective, setObjective] = useState<OptimizationObjective>('sharpe_ratio');
  const [maximize, setMaximize] = useState(true);
  const [nJobs, setNJobs] = useState(1);
  const [paramRanges, setParamRanges] = useState<Record<string, ParamRange>>({
    ma_short: {
      type: 'int',
      min: 5,
      max: 20,
      step: 1
    },
    ma_long: {
      type: 'int',
      min: 20,
      max: 60,
      step: 1
    },
    stop_loss: {
      type: 'float',
      min: 0.05,
      max: 0.20
    }
  });

  // 遗传算法参数
  const [populationSize, setPopulationSize] = useState(50);
  const [generations, setGenerations] = useState(20);
  const [crossoverRate, setCrossoverRate] = useState(0.8);
  const [mutationRate, setMutationRate] = useState(0.1);
  const [elitismRate, setElitismRate] = useState(0.1);

  // 贝叶斯优化参数
  const [nIter, setNIter] = useState(100);
  const [nInit, setNInit] = useState(10);
  const [acquisition, setAcquisition] = useState<'EI' | 'PI' | 'UCB'>('EI');

  const handleParamChange = (paramName: string, field: keyof ParamRange, value: any) => {
    setParamRanges(prev => ({
      ...prev,
      [paramName]: {
        ...prev[paramName],
        [field]: value
      }
    }));
  };

  const handleSubmit = async () => {
    const request: OptimizationRequest = {
      strategy_type: strategyType,
      stock_code: stockCode,
      start_date: startDate,
      end_date: endDate,
      initial_capital: initialCapital,
      optimization_method: optimizationMethod,
      param_ranges: paramRanges,
      objective: objective,
      maximize: maximize,
      n_jobs: nJobs
    };

    // 添加优化方法特定参数
    if (optimizationMethod === 'genetic') {
      request.population_size = populationSize;
      request.generations = generations;
      request.crossover_rate = crossoverRate;
      request.mutation_rate = mutationRate;
      request.elitism_rate = elitismRate;
    } else if (optimizationMethod === 'bayesian') {
      request.n_iter = nIter;
      request.n_init = nInit;
      request.acquisition = acquisition;
    }

    await onOptimize(request);
  };

  const optimizationMethods: { value: OptimizationMethod; label: string; description: string }[] = [
    { value: 'grid_search', label: '网格搜索', description: '遍历所有参数组合，保证全局最优' },
    { value: 'genetic', label: '遗传算法', description: '适合大规模参数空间，进化优化' },
    { value: 'bayesian', label: '贝叶斯优化', description: '样本效率高，适合评估成本高' }
  ];

  const objectives: { value: OptimizationObjective; label: string }[] = [
    { value: 'total_return', label: '总收益率' },
    { value: 'sharpe_ratio', label: '夏普比率' },
    { value: 'max_drawdown', label: '最大回撤' },
    { value: 'calmar_ratio', label: '卡尔玛比率' },
    { value: 'win_rate', label: '胜率' },
    { value: 'profit_loss_ratio', label: '盈亏比' }
  ];

  return (
    <div className="space-y-6">
      {/* 基本信息 */}
      <Card>
        <CardHeader>
          <CardTitle>优化配置</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">策略类型</label>
              <select
                className="w-full p-2 border rounded-md"
                value={strategyType}
                onChange={(e) => setStrategyType(e.target.value)}
              >
                <option value="双均线策略">双均线策略</option>
                <option value="布林带策略">布林带策略</option>
                <option value="MACD策略">MACD策略</option>
                <option value="RSI策略">RSI策略</option>
                <option value="KDJ策略">KDJ策略</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">股票代码</label>
              <Input
                value={stockCode}
                onChange={(e) => setStockCode(e.target.value)}
                placeholder="600771"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">开始日期</label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">结束日期</label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">初始资金</label>
              <Input
                type="number"
                value={initialCapital}
                onChange={(e) => setInitialCapital(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">并行任务数</label>
              <Input
                type="number"
                value={nJobs}
                onChange={(e) => setNJobs(Number(e.target.value))}
                min={1}
                max={10}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 优化方法选择 */}
      <Card>
        <CardHeader>
          <CardTitle>优化方法</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {optimizationMethods.map((method) => (
              <div
                key={method.value}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  optimizationMethod === method.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setOptimizationMethod(method.value)}
              >
                <div className="font-medium mb-1">{method.label}</div>
                <div className="text-sm text-gray-600">{method.description}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 优化目标 */}
      <Card>
        <CardHeader>
          <CardTitle>优化目标</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {objectives.map((obj) => (
              <Badge
                key={obj.value}
                variant={objective === obj.value ? 'default' : 'outline'}
                className="cursor-pointer justify-center py-2 px-4"
                onClick={() => setObjective(obj.value)}
              >
                {obj.label}
              </Badge>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={maximize}
              onChange={(e) => setMaximize(e.target.checked)}
              className="w-4 h-4"
            />
            <label className="text-sm">最大化（否则最小化）</label>
          </div>
        </CardContent>
      </Card>

      {/* 参数范围 */}
      <Card>
        <CardHeader>
          <CardTitle>参数范围</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(paramRanges).map(([paramName, paramRange]) => (
            <div key={paramName} className="border rounded-lg p-4">
              <h4 className="font-medium mb-3">{paramName}</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div>
                  <label className="block text-sm mb-1">类型</label>
                  <select
                    className="w-full p-2 border rounded-md"
                    value={paramRange.type}
                    onChange={(e) => handleParamChange(paramName, 'type', e.target.value)}
                  >
                    <option value="int">整数</option>
                    <option value="float">浮点数</option>
                    <option value="choice">选择</option>
                  </select>
                </div>
                {paramRange.type !== 'choice' && (
                  <>
                    <div>
                      <label className="block text-sm mb-1">最小值</label>
                      <Input
                        type="number"
                        value={paramRange.min || ''}
                        onChange={(e) => handleParamChange(paramName, 'min', Number(e.target.value))}
                      />
                    </div>
                    <div>
                      <label className="block text-sm mb-1">最大值</label>
                      <Input
                        type="number"
                        value={paramRange.max || ''}
                        onChange={(e) => handleParamChange(paramName, 'max', Number(e.target.value))}
                      />
                    </div>
                    {paramRange.type === 'int' && (
                      <div>
                        <label className="block text-sm mb-1">步长</label>
                        <Input
                          type="number"
                          value={paramRange.step || ''}
                          onChange={(e) => handleParamChange(paramName, 'step', Number(e.target.value))}
                        />
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* 遗传算法参数 */}
      {optimizationMethod === 'genetic' && (
        <Card>
          <CardHeader>
            <CardTitle>遗传算法参数</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">种群大小</label>
                <Input
                  type="number"
                  value={populationSize}
                  onChange={(e) => setPopulationSize(Number(e.target.value))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">迭代代数</label>
                <Input
                  type="number"
                  value={generations}
                  onChange={(e) => setGenerations(Number(e.target.value))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">交叉概率</label>
                <Input
                  type="number"
                  step={0.1}
                  min={0}
                  max={1}
                  value={crossoverRate}
                  onChange={(e) => setCrossoverRate(Number(e.target.value))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">变异概率</label>
                <Input
                  type="number"
                  step={0.1}
                  min={0}
                  max={1}
                  value={mutationRate}
                  onChange={(e) => setMutationRate(Number(e.target.value))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">精英保留比例</label>
                <Input
                  type="number"
                  step={0.1}
                  min={0}
                  max={1}
                  value={elitismRate}
                  onChange={(e) => setElitismRate(Number(e.target.value))}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 贝叶斯优化参数 */}
      {optimizationMethod === 'bayesian' && (
        <Card>
          <CardHeader>
            <CardTitle>贝叶斯优化参数</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">迭代次数</label>
                <Input
                  type="number"
                  value={nIter}
                  onChange={(e) => setNIter(Number(e.target.value))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">初始采样次数</label>
                <Input
                  type="number"
                  value={nInit}
                  onChange={(e) => setNInit(Number(e.target.value))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">采集函数</label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={acquisition}
                  onChange={(e) => setAcquisition(e.target.value as 'EI' | 'PI' | 'UCB')}
                >
                  <option value="EI">EI (期望改进)</option>
                  <option value="PI">PI (改进概率)</option>
                  <option value="UCB">UCB (上置信界)</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 提交按钮 */}
      <div className="flex justify-end">
        <Button
          onClick={handleSubmit}
          disabled={loading}
          size="lg"
          className="px-8"
        >
          {loading ? '优化中...' : '开始优化'}
        </Button>
      </div>
    </div>
  );
}