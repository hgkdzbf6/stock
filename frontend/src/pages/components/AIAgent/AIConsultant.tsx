import { useState } from 'react';
import { Sparkles, Send, Copy, Check } from 'lucide-react';

const AIConsultant = () => {
  const [prompt, setPrompt] = useState('等待生成...');
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  const exampleQuestions = [
    '当前趋势如何，是否应该止盈？',
    '分析当前的量价背离情况',
    '评估当前持仓的风险收益比',
    '下一步操作建议是什么？'
  ];

  const handleGeneratePrompt = async () => {
    setIsGenerating(true);
    setPrompt('正在分析市场数据并生成提示词...');

    // 模拟AI生成过程
    setTimeout(() => {
      const generatedPrompt = `作为一名专业的量化交易分析师，请基于以下持仓和市场数据提供专业的投资建议：

【当前持仓状态】
- 股票代码：600519
- 持仓数量：20,900股
- 持仓成本：¥1.45
- 当前价格：¥1.42
- 持仓市值：¥29,761.60
- 可用资金：¥30,000.00

【市场技术指标】
- MA5：1.41 | MA10：1.40 | MA20：1.38 | MA60：1.35
- BOLL上轨：1.50 | BOLL中轨：1.42 | BOLL下轨：1.34
- RSI：42.5（接近超卖区域）
- 成交量：近期放量，显示资金活跃度提升

【市场趋势分析】
- 短期趋势：震荡下行，但接近支撑位
- 中期趋势：处于上升通道回调阶段
- 市场情绪：谨慎偏乐观

【请回答以下问题】
1. 当前技术形态是否企稳？是否存在反弹机会？
2. 考虑到量能变化，主力资金意图如何？
3. 当前持仓是否需要调整？止盈止损位应该设置在什么位置？
4. 如果考虑加仓，什么时机合适？
5. 未来3-5个交易日的趋势预判是什么？

请基于量化分析方法，结合技术面、资金面和市场情绪，给出具体的操作建议和风险提示。`;

      setPrompt(generatedPrompt);
      setIsGenerating(false);
    }, 2000);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExampleClick = (example: string) => {
    setPrompt(example);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 h-full">
      <div className="flex flex-col h-full">
        {/* 标题和描述 */}
        <div className="mb-4">
          <div className="flex items-center space-x-2 mb-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
              AI 战略咨询助手
            </h3>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            本工具将自动提取当前资产的持仓状态、盈亏数据以及最新的市场行情，为您生成一份能够体现专业化量化投资的策略词云，将所生成的模型词词云复制并发送给 DeepSeek 或 ChatGPT，以获得最精准的决策建议。
          </p>
        </div>

        {/* 输入区 */}
        <div className="flex-1 flex flex-col">
          <div className="mb-3">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              跟分析师聊天
            </h4>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              示例："{exampleQuestions[0]}" 或 "{exampleQuestions[1]}"
            </p>
          </div>

          {/* 示例问题 */}
          <div className="mb-3 flex flex-wrap gap-2">
            {exampleQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(question)}
                className="text-xs px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded hover:bg-purple-200 dark:hover:bg-purple-800 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>

          {/* 文本输入框 */}
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="输入您的问题或等待AI生成提示词..."
            className="flex-1 w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white resize-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            rows={6}
          />

          {/* 操作按钮 */}
          <div className="flex space-x-3 mt-4">
            <button
              onClick={handleGeneratePrompt}
              disabled={isGenerating}
              className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
                isGenerating
                  ? 'bg-purple-400 cursor-not-allowed'
                  : 'bg-purple-600 hover:bg-purple-700'
              } text-white`}
            >
              <Sparkles className="w-4 h-4" />
              <span>{isGenerating ? '生成中...' : '生成新的提示词'}</span>
            </button>

            <button
              onClick={handleCopy}
              className="flex items-center justify-center space-x-2 px-4 py-2 rounded-lg font-medium bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 transition-all"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>已复制</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>复制</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIConsultant;