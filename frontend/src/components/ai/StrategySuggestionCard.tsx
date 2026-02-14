/**策略建议卡片*/
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
  TrendingUp,
  TrendingDown,
  Minus,
  Lightbulb,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react';

export interface StrategySuggestion {
  id: string;
  title: string;
  type: 'buy' | 'sell' | 'hold';
  confidence: number;
  price?: number;
  targetPrice?: number;
  stopLoss?: number;
  reason: string;
  keyPoints: string[];
  riskLevel: 'low' | 'medium' | 'high';
  timestamp: Date;
}

interface StrategySuggestionCardProps {
  suggestion: StrategySuggestion;
  onViewDetails?: () => void;
  onApply?: () => void;
}

export const StrategySuggestionCard: React.FC<StrategySuggestionCardProps> = ({
  suggestion,
  onViewDetails,
  onApply,
}) => {
  const getSignalIcon = (type: string) => {
    switch (type) {
      case 'buy':
        return <TrendingUp className="h-5 w-5 text-green-500" />;
      case 'sell':
        return <TrendingDown className="h-5 w-5 text-red-500" />;
      case 'hold':
        return <Minus className="h-5 w-5 text-gray-500" />;
      default:
        return <Minus className="h-5 w-5 text-gray-500" />;
    }
  };

  const getSignalColor = (type: string) => {
    switch (type) {
      case 'buy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'sell':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'hold':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSignalText = (type: string) => {
    switch (type) {
      case 'buy':
        return '买入';
      case 'sell':
        return '卖出';
      case 'hold':
        return '持有';
      default:
        return '观望';
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'high':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
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
        return <CheckCircle className="h-3 w-3" />;
      case 'medium':
        return <AlertTriangle className="h-3 w-3" />;
      case 'high':
        return <AlertTriangle className="h-3 w-3" />;
      default:
        return <Minus className="h-3 w-3" />;
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {getSignalIcon(suggestion.type)}
            <CardTitle className="text-lg">{suggestion.title}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className={getSignalColor(suggestion.type)}>
              {getSignalText(suggestion.type)}
            </Badge>
            <Badge variant="outline" className={`flex items-center gap-1 ${getRiskColor(suggestion.riskLevel)}`}>
              {getRiskIcon(suggestion.riskLevel)}
              {getRiskText(suggestion.riskLevel)}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 置信度和原因 */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">AI置信度</span>
            <span className="text-sm font-bold text-blue-600">
              {(suggestion.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${suggestion.confidence * 100}%` }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-2">{suggestion.reason}</p>
        </div>

        {/* 价格信息 */}
        {(suggestion.price || suggestion.targetPrice || suggestion.stopLoss) && (
          <div className="grid grid-cols-3 gap-2 p-3 bg-gray-50 rounded-lg">
            {suggestion.price && (
              <div>
                <div className="text-xs text-gray-500">当前价格</div>
                <div className="text-sm font-semibold">¥{suggestion.price.toFixed(2)}</div>
              </div>
            )}
            {suggestion.targetPrice && (
              <div>
                <div className="text-xs text-gray-500">目标价格</div>
                <div className="text-sm font-semibold text-green-600">
                  ¥{suggestion.targetPrice.toFixed(2)}
                </div>
              </div>
            )}
            {suggestion.stopLoss && (
              <div>
                <div className="text-xs text-gray-500">止损价格</div>
                <div className="text-sm font-semibold text-red-600">
                  ¥{suggestion.stopLoss.toFixed(2)}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 关键要点 */}
        {suggestion.keyPoints.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Lightbulb className="h-4 w-4 text-yellow-500" />
              <span className="text-sm font-medium">关键要点</span>
            </div>
            <ul className="space-y-1">
              {suggestion.keyPoints.map((point, index) => (
                <li key={index} className="text-xs text-gray-600 flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 时间戳 */}
        <div className="text-xs text-gray-400 text-right">
          {suggestion.timestamp.toLocaleString('zh-CN')}
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-2 pt-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={onViewDetails}
          >
            查看详情
          </Button>
          {suggestion.type === 'buy' || suggestion.type === 'sell' ? (
            <Button
              size="sm"
              className="flex-1"
              onClick={onApply}
            >
              执行建议
            </Button>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
};

export default StrategySuggestionCard;