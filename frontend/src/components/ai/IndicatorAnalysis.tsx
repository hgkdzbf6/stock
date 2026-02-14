/**技术指标分析组件*/
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
  ArrowUpRight,
  ArrowDownRight,
  Info,
  BarChart3,
} from 'lucide-react';

export interface IndicatorData {
  name: string;
  value: string;
  trend: 'up' | 'down' | 'neutral';
  signal: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell';
  description: string;
}

export interface IndicatorAnalysis {
  id: string;
  trendStrength: 'strong' | 'medium' | 'weak';
  overallSignal: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell';
  keyLevels: {
    support: number;
    resistance: number;
  };
  indicators: IndicatorData[];
  riskAlerts: string[];
  timestamp: Date;
}

interface IndicatorAnalysisProps {
  analysis: IndicatorAnalysis;
  onViewDetails?: () => void;
}

export const IndicatorAnalysis: React.FC<IndicatorAnalysisProps> = ({
  analysis,
  onViewDetails,
}) => {
  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'strong_buy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'buy':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'hold':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'sell':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'strong_sell':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSignalText = (signal: string) => {
    switch (signal) {
      case 'strong_buy':
        return '强烈买入';
      case 'buy':
        return '买入';
      case 'hold':
        return '持有';
      case 'sell':
        return '卖出';
      case 'strong_sell':
        return '强烈卖出';
      default:
        return '观望';
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'strong_buy':
      case 'buy':
        return <ArrowUpRight className="h-4 w-4 text-green-600" />;
      case 'sell':
      case 'strong_sell':
        return <ArrowDownRight className="h-4 w-4 text-red-600" />;
      case 'hold':
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'strong':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'weak':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getTrendText = (trend: string) => {
    switch (trend) {
      case 'strong':
        return '强势';
      case 'medium':
        return '中等';
      case 'weak':
        return '弱势';
      default:
        return '未知';
    }
  };

  const getIndicatorTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-3 w-3 text-green-500" />;
      case 'down':
        return <TrendingDown className="h-3 w-3 text-red-500" />;
      case 'neutral':
      default:
        return <Minus className="h-3 w-3 text-gray-500" />;
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-500" />
            <CardTitle className="text-lg">技术指标分析</CardTitle>
          </div>
          <Badge variant="outline" className={getSignalColor(analysis.overallSignal)}>
            {getSignalIcon(analysis.overallSignal)}
            <span className="ml-1">{getSignalText(analysis.overallSignal)}</span>
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 趋势强度 */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">趋势强度</span>
            <span className={`text-sm font-bold ${getTrendColor(analysis.trendStrength)}`}>
              {getTrendText(analysis.trendStrength)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                analysis.trendStrength === 'strong'
                  ? 'bg-green-600'
                  : analysis.trendStrength === 'medium'
                  ? 'bg-yellow-600'
                  : 'bg-red-600'
              }`}
              style={{
                width:
                  analysis.trendStrength === 'strong'
                    ? '80%'
                    : analysis.trendStrength === 'medium'
                    ? '50%'
                    : '20%',
              }}
            />
          </div>
        </div>

        {/* 关键点位 */}
        <div className="grid grid-cols-2 gap-3 p-3 bg-gray-50 rounded-lg">
          <div>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <ArrowDownRight className="h-3 w-3 text-green-500" />
              支撑位
            </div>
            <div className="text-sm font-semibold text-green-600">
              ¥{analysis.keyLevels.support.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <ArrowUpRight className="h-3 w-3 text-red-500" />
              压力位
            </div>
            <div className="text-sm font-semibold text-red-600">
              ¥{analysis.keyLevels.resistance.toFixed(2)}
            </div>
          </div>
        </div>

        {/* 技术指标列表 */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Info className="h-4 w-4 text-blue-500" />
            <span className="text-sm font-medium">指标详情</span>
          </div>
          <div className="space-y-2">
            {analysis.indicators.map((indicator, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    {getIndicatorTrendIcon(indicator.trend)}
                    <span className="text-sm font-medium">{indicator.name}</span>
                    <Badge variant="outline" className={`text-xs ${getSignalColor(indicator.signal)}`}>
                      {getSignalText(indicator.signal)}
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-600 mt-1">{indicator.description}</div>
                </div>
                <div className="text-sm font-semibold ml-2">{indicator.value}</div>
              </div>
            ))}
          </div>
        </div>

        {/* 风险提示 */}
        {analysis.riskAlerts.length > 0 && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Info className="h-4 w-4 text-red-600" />
              <span className="text-sm font-medium text-red-800">风险提示</span>
            </div>
            <ul className="space-y-1">
              {analysis.riskAlerts.map((alert, index) => (
                <li key={index} className="text-xs text-red-700 flex items-start gap-2">
                  <span className="mt-0.5">•</span>
                  <span>{alert}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 时间戳 */}
        <div className="text-xs text-gray-400 text-right">
          {analysis.timestamp.toLocaleString('zh-CN')}
        </div>

        {/* 操作按钮 */}
        <Button className="w-full" onClick={onViewDetails}>
          查看完整分析
        </Button>
      </CardContent>
    </Card>
  );
};

export default IndicatorAnalysis;