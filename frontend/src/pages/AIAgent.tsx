import { useState } from 'react';
import { Sun, Moon } from 'lucide-react';
import Header from './components/AIAgent/Header';
import StockInfo from './components/AIAgent/StockInfo';
import KLineChart from './components/AIAgent/KLineChart';
import AIConsultant from './components/AIAgent/AIConsultant';
import HistoryDecisions from './components/AIAgent/HistoryDecisions';

const AIAgent = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isRunning, setIsRunning] = useState(true);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    // 这里可以添加实际的主题切换逻辑
  };

  const toggleRunning = () => {
    setIsRunning(!isRunning);
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDarkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
      {/* 顶部导航栏 */}
      <Header isDarkMode={isDarkMode} toggleTheme={toggleTheme} />

      {/* 主要内容区域 */}
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* 股票信息栏 */}
        <StockInfo isRunning={isRunning} toggleRunning={toggleRunning} />

        {/* K线图与成交量区域 */}
        <KLineChart />

        {/* 底部功能区 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 左侧：AI战略咨询助手 */}
          <AIConsultant />

          {/* 右侧：历史决策与分析 */}
          <HistoryDecisions />
        </div>
      </div>
    </div>
  );
};

export default AIAgent;