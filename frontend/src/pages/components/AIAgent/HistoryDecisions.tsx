import { Clock, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';

interface Decision {
  id: string;
  title: string;
  decision: string;
  analysis: string;
  timestamp: string;
  type: 'buy' | 'sell' | 'hold';
}

const HistoryDecisions = () => {
  const decisions: Decision[] = [
    {
      id: '1',
      title: '继续持有',
      decision: 'HOLD',
      analysis: `【市场分析报告】

【技术面解读】
当前股价在1.42元附近震荡，技术指标显示：
1. MACD指标在零轴附近金叉，但动能较弱
2. KDJ指标进入超卖区域，J值为8.5，存在反弹可能
3. 成交量近期有所放大，显示资金关注度提升
4. 股价在BOLL下轨（1.34元）附近获得支撑

【基本面评估】
1. 公司基本面稳健，财务状况良好
2. 行业景气度维持高位，政策支持力度大
3. 估值水平合理，PE处于历史中位以下

【风险评估】
1. 市场整体波动性增加，需关注系统性风险
2. 短期技术面偏弱，但下行空间有限
3. 资金流向显示主力资金小幅流出

【操作建议】
基于以上分析，建议继续持有，理由如下：
1. 当前价格接近技术支撑位，下跌风险可控
2. 中期趋势未改变，基本面支撑强劲
3. 建议设置止损位在1.35元，止盈位在1.55元
4. 如股价跌破1.35元，考虑减仓避险

【风险提示】
投资有风险，以上分析仅供参考，不构成投资建议。请根据自身风险承受能力做出决策。`,
      timestamp: '2026-02-16 14:30:00',
      type: 'hold'
    },
    {
      id: '2',
      title: '加仓机会',
      decision: 'BUY',
      analysis: `【市场分析报告】

【技术面解读】
技术指标出现积极信号：
1. 股价在1.35-1.38区间构筑底部形态
2. RSI指标从30以下回升，显示空头力量减弱
3. 成交量温和放大，买盘逐渐增强
4. 短期均线（5日、10日）开始向上发散

【操作建议】
建议在1.40元以下分批加仓：
1. 第一笔：1.40元加仓20%
2. 第二笔：1.38元加仓30%
3. 第三笔：1.35元加仓50%

【风险控制】
严格设置止损位在1.30元，单笔亏损不超过5%`,
      timestamp: '2026-02-15 10:15:00',
      type: 'buy'
    },
    {
      id: '3',
      title: '减仓规避风险',
      decision: 'SELL',
      analysis: `【市场分析报告】

【风险提示】
市场出现以下风险信号：
1. 成交量异常放大但股价滞涨
2. 技术指标MACD出现顶背离
3. 外围市场波动加剧

【操作建议】
建议减仓30%-50%，降低风险敞口
保留核心仓位，等待趋势明朗后再做决策`,
      timestamp: '2026-02-14 15:45:00',
      type: 'sell'
    }
  ];

  const getDecisionIcon = (type: string) => {
    switch (type) {
      case 'buy':
        return <TrendingUp className="w-5 h-5 text-green-600" />;
      case 'sell':
        return <TrendingDown className="w-5 h-5 text-red-600" />;
      case 'hold':
        return <AlertCircle className="w-5 h-5 text-blue-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  const getDecisionBadge = (type: string) => {
    switch (type) {
      case 'buy':
        return <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">买入</span>;
      case 'sell':
        return <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium">卖出</span>;
      case 'hold':
        return <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">持有</span>;
      default:
        return <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">未知</span>;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 h-full">
      <div className="flex flex-col h-full">
        {/* 标题 */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-blue-600" />
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
              历史决策与分析
            </h3>
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            共 {decisions.length} 条记录
          </span>
        </div>

        {/* 决策列表 */}
        <div className="flex-1 overflow-y-auto space-y-4">
          {decisions.map((decision) => (
            <div
              key={decision.id}
              className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              {/* 决策头部 */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {getDecisionIcon(decision.type)}
                  <h4 className="font-semibold text-gray-900 dark:text-white">
                    {decision.title}
                  </h4>
                  {getDecisionBadge(decision.type)}
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {decision.timestamp}
                </span>
              </div>

              {/* 详细分析 */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded p-3 max-h-48 overflow-y-auto">
                <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-sans leading-relaxed">
                  {decision.analysis}
                </pre>
              </div>
            </div>
          ))}
        </div>

        {/* 底部提示 */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            历史决策仅供参考，不构成投资建议
          </p>
        </div>
      </div>
    </div>
  );
};

export default HistoryDecisions;