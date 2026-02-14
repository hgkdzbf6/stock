/**持仓洞察组件*/
import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import {
  PieChart,
  TrendingUp,
  TrendingDown,
  DollarSign,
  AlertTriangle,
  CheckCircle,
  Target,
} from 'lucide-react';

export interface Position {
  stock_code: string;
  stock_name: string;
  quantity: number;
  cost_price: number;
  current_price: number;
  market_value: number;
  profit_loss: number;
  profit_loss_percent: number;
}

export interface PortfolioInsight {
  id: string;
  riskLevel: 'low' | 'medium' | 'high';
  totalMarketValue: number;
  totalProfitLoss: number;
  totalProfitLossPercent: number;
  bestPosition: Position;
  worstPosition: Position;
  distribution: {
    stock_name: string;
    percentage: number;
  }[];
  suggestions: string[];
  riskFactors: string[];
  confidence: number;
  timestamp: Date;
}

interface PortfolioInsightProps {
  insight: PortfolioInsight;
  onViewDetails?: () => void;
  onOptimize?: () => void;
}

export const PortfolioInsight: React.FC<PortfolioInsightProps> = ({
  insight,
  onViewDetails,
  onOptimize,
}) => {
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRiskText = (level: string) => {
    switch (level) {
      case 'low':
        return '低风险';
      case 'medium':
        return '中风险';
      case 'high':
        return '高风险';
      default:
        return '未知';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'low':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'medium':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-600" />;
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <PieChart className="h-5 w-5 text-blue-500" />
            <CardTitle className="text-lg">持仓洞察</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className={getRiskColor(insight.riskLevel)}>
              {getRiskIcon(insight.riskLevel)}
              <span className="ml-1">{getRiskText(insight.riskLevel)}</span>
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 总览 */}
        <div className="grid grid-cols-3 gap-3 p-3 bg-gray-50 rounded-lg">
          <div>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <DollarSign className="h-3 w-3" />
              总市值
            </div>
            <div className="text-sm font-semibold">
              ¥{insight.totalMarketValue.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              {insight.totalProfitLoss >= 0 ? (
                <TrendingUp className="h-3 w-3 text-green-500" />
              ) : (
                <TrendingDown className="h-3 w-3 text-red-500" />
              )}
              总盈亏
            </div>
            <div
              className={`text-sm font-semibold ${
                insight.totalProfitLoss >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {insight.totalProfitLoss >= 0 ? '+' : ''}
              ¥{insight.totalProfitLoss.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <Target className="h-3 w-3" />
              收益率
            </div>
            <div
              className={`text-sm font-semibold ${
                insight.totalProfitLossPercent >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {insight.totalProfitLossPercent >= 0 ? '+' : ''}
              {insight.totalProfitLossPercent.toFixed(2)}%
            </div>
          </div>
        </div>

        {/* AI置信度 */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">AI分析置信度</span>
            <span className="text-sm font-bold text-blue-600">
              {(insight.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${insight.confidence * 100}%` }}
            />
          </div>
        </div>

        {/* 最佳和最差持仓 */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-800">最佳持仓</span>
            </div>
            <div className="text-xs text-gray-600">
              {insight.bestPosition.stock_name} ({insight.bestPosition.stock_code})
            </div>
            <div className="text-sm font-semibold text-green-600 mt-1">
              +{insight.bestPosition.profit_loss_percent.toFixed(2)}%
            </div>
          </div>
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="h-4 w-4 text-red-600" />
              <span className="text-sm font-medium text-red-800">最差持仓</span>
            </div>
            <div className="text-xs text-gray-600">
              {insight.worstPosition.stock_name} ({insight.worstPosition.stock_code})
            </div>
            <div className="text-sm font-semibold text-red-600 mt-1">
              {insight.worstPosition.profit_loss_percent.toFixed(2)}%
            </div>
          </div>
        </div>

        {/* 持仓分布 */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <PieChart className="h-4 w-4 text-blue-500" />
            <span className="text-sm font-medium">持仓分布</span>
          </div>
          <div className="space-y-2">
            {insight.distribution.map((item, index) => (
              <div key={index}>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-gray-600">{item.stock_name}</span>
                  <span className="font-medium">{item.percentage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className="bg-blue-600 h-1.5 rounded-full"
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI建议 */}
        {insight.suggestions.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Target className="h-4 w-4 text-blue-500" />
              <span className="text-sm font-medium">AI建议</span>
            </div>
            <ul className="space-y-1">
              {insight.suggestions.map((suggestion, index) => (
                <li key={index} className="text-xs text-gray-600 flex items-start gap-2">
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 风险因素 */}
        {insight.riskFactors.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
              <span className="text-sm font-medium">风险因素</span>
            </div>
            <ul className="space-y-1">
              {insight.riskFactors.map((factor, index) => (
                <li key={index} className="text-xs text-gray-600 flex items-start gap-2">
                  <span className="text-yellow-500 mt-0.5">⚠</span>
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 时间戳 */}
        <div className="text-xs text-gray-400 text-right">
          {insight.timestamp.toLocaleString('zh-CN')}
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-2 pt-2">
          <Button variant="outline" size="sm" className="flex-1" onClick={onViewDetails}>
            查看详情
          </Button>
          <Button size="sm" className="flex-1" onClick={onOptimize}>
            AI优化建议
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default PortfolioInsight;