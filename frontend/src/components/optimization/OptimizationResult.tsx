import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { OptimizationResult as OptimizationResultType } from '@/services/optimization';

interface OptimizationResultProps {
  result: OptimizationResultType;
  onBack?: () => void;
  onApply?: (params: Record<string, any>) => void;
}

export function OptimizationResult({ result, onBack, onApply }: OptimizationResultProps) {
  const formatNumber = (num: number, decimals: number = 2) => {
    return num.toFixed(decimals);
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds.toFixed(2)}秒`;
    } else if (seconds < 3600) {
      return `${(seconds / 60).toFixed(2)}分钟`;
    } else {
      return `${(seconds / 3600).toFixed(2)}小时`;
    }
  };

  return (
    <div className="space-y-6">
      {/* 返回按钮 */}
      {onBack && (
        <div className="flex justify-start">
          <Button variant="outline" onClick={onBack}>
            返回
          </Button>
        </div>
      )}

      {/* 最优结果摘要 */}
      <Card className="border-2 border-green-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span>优化完成</span>
            <Badge variant="success">最优</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">最优得分</div>
              <div className="text-2xl font-bold text-green-700">
                {formatNumber(result.best_score)}
              </div>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">迭代次数</div>
              <div className="text-2xl font-bold text-blue-700">
                {result.iterations}
              </div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">优化时间</div>
              <div className="text-2xl font-bold text-purple-700">
                {formatTime(result.optimization_time)}
              </div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">评估组合数</div>
              <div className="text-2xl font-bold text-orange-700">
                {result.all_results.length}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 最优参数 */}
      <Card>
        <CardHeader>
          <CardTitle>最优参数</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(result.best_params).map(([key, value]) => (
              <div key={key} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">{key}</span>
                <Badge variant="default" className="ml-4">
                  {typeof value === 'number' ? formatNumber(value) : String(value)}
                </Badge>
              </div>
            ))}
          </div>
          
          {onApply && (
            <div className="mt-4 flex justify-end">
              <Button
                onClick={() => onApply(result.best_params)}
                variant="primary"
              >
                应用参数
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 收敛曲线 */}
      <Card>
        <CardHeader>
          <CardTitle>收敛曲线</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
            {result.convergence_curve.length > 0 ? (
              <div className="text-center">
                <p className="text-gray-600 mb-2">收敛数据已生成</p>
                <p className="text-sm text-gray-500">
                  最小值: {formatNumber(Math.min(...result.convergence_curve))}
                </p>
                <p className="text-sm text-gray-500">
                  最大值: {formatNumber(Math.max(...result.convergence_curve))}
                </p>
              </div>
            ) : (
              <p className="text-gray-500">暂无收敛数据</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 所有结果 */}
      <Card>
        <CardHeader>
          <CardTitle>所有评估结果</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">#</th>
                  <th className="text-left p-2">得分</th>
                  <th className="text-left p-2">参数</th>
                </tr>
              </thead>
              <tbody>
                {result.all_results.map((item, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="p-2">{index + 1}</td>
                    <td className="p-2 font-medium">
                      {formatNumber(item.score)}
                    </td>
                    <td className="p-2 text-xs text-gray-600">
                      {Object.entries(item.params).map(([k, v]) => (
                        <span key={k} className="mr-2">
                          {k}: {typeof v === 'number' ? formatNumber(v) : String(v)}
                        </span>
                      ))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {result.all_results.length > 100 && (
            <p className="text-sm text-gray-500 mt-2">
              仅显示前 100 条结果，共 {result.all_results.length} 条
            </p>
          )}
        </CardContent>
      </Card>

      {/* 统计信息 */}
      <Card>
        <CardHeader>
          <CardTitle>统计信息</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h4 className="font-medium mb-2">得分分布</h4>
              <div className="space-y-1 text-sm">
                <div>最大值: {formatNumber(Math.max(...result.all_results.map(r => r.score)))}</div>
                <div>最小值: {formatNumber(Math.min(...result.all_results.map(r => r.score)))}</div>
                <div>
                  平均值: {formatNumber(
                    result.all_results.reduce((sum, r) => sum + r.score, 0) / result.all_results.length
                  )}
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">性能指标</h4>
              <div className="space-y-1 text-sm">
                <div>平均每次迭代: {formatTime(result.optimization_time / result.iterations)}</div>
                <div>评估速度: {formatNumber(result.all_results.length / result.optimization_time)} 次/秒</div>
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">优化效率</h4>
              <div className="space-y-1 text-sm">
                <div>收敛速度: {result.convergence_curve.length > 0 ? '快速' : '未知'}</div>
                <div>稳定性: {result.convergence_curve.length > 10 ? '良好' : '待评估'}</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}