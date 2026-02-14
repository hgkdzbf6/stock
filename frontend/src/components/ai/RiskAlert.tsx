/**风险提示组件*/
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
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  XCircle,
  Info,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export interface RiskAlert {
  id: string;
  level: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  riskFactors: string[];
  suggestions: string[];
  metrics: {
    label: string;
    value: string;
    status: 'good' | 'warning' | 'danger';
  }[];
  timestamp: Date;
}

interface RiskAlertProps {
  alert: RiskAlert;
  onDismiss?: () => void;
  onAction?: () => void;
  compact?: boolean;
}

export const RiskAlert: React.FC<RiskAlertProps> = ({
  alert,
  onDismiss,
  onAction,
  compact = false,
}) => {
  const [expanded, setExpanded] = React.useState(false);

  const getLevelColor = (level: string) => {
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

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'low':
        return <ShieldCheck className="h-5 w-5 text-green-600" />;
      case 'medium':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'high':
        return <ShieldAlert className="h-5 w-5 text-red-600" />;
      default:
        return <Info className="h-5 w-5 text-gray-600" />;
    }
  };

  const getLevelText = (level: string) => {
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

  const getMetricStatusColor = (status: string) => {
    switch (status) {
      case 'good':
        return 'text-green-600';
      case 'warning':
        return 'text-yellow-600';
      case 'danger':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getMetricStatusIcon = (status: string) => {
    switch (status) {
      case 'good':
        return <ShieldCheck className="h-3 w-3" />;
      case 'warning':
        return <AlertTriangle className="h-3 w-3" />;
      case 'danger':
        return <XCircle className="h-3 w-3" />;
      default:
        return <Info className="h-3 w-3" />;
    }
  };

  if (compact) {
    return (
      <Card className="border-l-4">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              {getLevelIcon(alert.level)}
              <CardTitle className="text-base">{alert.title}</CardTitle>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className={getLevelColor(alert.level)}>
                {getLevelText(alert.level)}
              </Badge>
              <Button variant="ghost" size="icon" onClick={onDismiss}>
                <XCircle className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <p className="text-sm text-gray-600">{alert.description}</p>
          <div className="mt-2 flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setExpanded(!expanded)}>
              {expanded ? (
                <>
                  <ChevronUp className="h-3 w-3 mr-1" />
                  收起
                </>
              ) : (
                <>
                  <ChevronDown className="h-3 w-3 mr-1" />
                  展开
                </>
              )}
            </Button>
            {onAction && (
              <Button variant="primary" size="sm" onClick={onAction}>
                查看详情
              </Button>
            )}
          </div>
          {expanded && (
            <div className="mt-4 space-y-3">
              <div>
                <div className="text-xs font-medium mb-2">风险因素</div>
                <ul className="space-y-1">
                  {alert.riskFactors.map((factor, index) => (
                    <li key={index} className="text-xs text-gray-600 flex items-start gap-2">
                      <AlertTriangle className="h-3 w-3 text-yellow-500 mt-0.5 flex-shrink-0" />
                      <span>{factor}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <div className="text-xs font-medium mb-2">建议措施</div>
                <ul className="space-y-1">
                  {alert.suggestions.map((suggestion, index) => (
                    <li key={index} className="text-xs text-gray-600 flex items-start gap-2">
                      <span className="text-blue-500 mt-0.5">•</span>
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {getLevelIcon(alert.level)}
            <CardTitle className="text-lg">{alert.title}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className={getLevelColor(alert.level)}>
              {getLevelText(alert.level)}
            </Badge>
            {onDismiss && (
              <Button variant="ghost" size="icon" onClick={onDismiss}>
                <XCircle className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 描述 */}
        <p className="text-sm text-gray-600">{alert.description}</p>

        {/* 风险指标 */}
        {alert.metrics.length > 0 && (
          <div className="grid grid-cols-2 gap-3 p-3 bg-gray-50 rounded-lg">
            {alert.metrics.map((metric, index) => (
              <div key={index}>
                <div className="text-xs text-gray-500">{metric.label}</div>
                <div className={`text-sm font-semibold flex items-center gap-1 ${getMetricStatusColor(metric.status)}`}>
                  {getMetricStatusIcon(metric.status)}
                  {metric.value}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 风险因素 */}
        {alert.riskFactors.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
              <span className="text-sm font-medium">风险因素</span>
            </div>
            <ul className="space-y-1">
              {alert.riskFactors.map((factor, index) => (
                <li key={index} className="text-xs text-gray-600 flex items-start gap-2">
                  <span className="text-yellow-500 mt-1">•</span>
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 建议措施 */}
        {alert.suggestions.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <ShieldCheck className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium">建议措施</span>
            </div>
            <ul className="space-y-1">
              {alert.suggestions.map((suggestion, index) => (
                <li key={index} className="text-xs text-gray-600 flex items-start gap-2">
                  <span className="text-green-500 mt-1">✓</span>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 时间戳 */}
        <div className="text-xs text-gray-400 text-right">
          {alert.timestamp.toLocaleString('zh-CN')}
        </div>

        {/* 操作按钮 */}
        {onAction && (
          <Button className="w-full" onClick={onAction}>
            查看详情并处理
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

export default RiskAlert;