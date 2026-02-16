import { Power, PowerOff } from 'lucide-react';

interface StockInfoProps {
  isRunning: boolean;
  toggleRunning: () => void;
}

const StockInfo = ({ isRunning, toggleRunning }: StockInfoProps) => {
  const stockData = {
    price: 1.42,
    changePct: -0.56,
    availableFunds: 30000,
    holdingQuantity: 20900,
    holdingValue: 29761.6,
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
        {/* 核心数据区 */}
        <div className="flex-1 w-full">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {/* 股价 */}
            <div className="space-y-1">
              <p className="text-sm text-gray-600 dark:text-gray-400">股价</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ¥{stockData.price.toFixed(2)}
              </p>
            </div>

            {/* 涨跌幅 */}
            <div className="space-y-1">
              <p className="text-sm text-gray-600 dark:text-gray-400">涨跌幅</p>
              <p className={`text-2xl font-bold ${stockData.changePct >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                {stockData.changePct >= 0 ? '+' : ''}{stockData.changePct.toFixed(2)}%
              </p>
            </div>

            {/* 可用资金 */}
            <div className="space-y-1">
              <p className="text-sm text-gray-600 dark:text-gray-400">可用资金</p>
              <p className="text-2xl font-bold text-blue-600">
                ¥{stockData.availableFunds.toLocaleString()}
              </p>
            </div>

            {/* 持有数量 */}
            <div className="space-y-1">
              <p className="text-sm text-gray-600 dark:text-gray-400">持有数量</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stockData.holdingQuantity.toLocaleString()}
              </p>
            </div>

            {/* 持仓市值 */}
            <div className="space-y-1">
              <p className="text-sm text-gray-600 dark:text-gray-400">持仓市值</p>
              <p className="text-2xl font-bold text-purple-600">
                ¥{stockData.holdingValue.toLocaleString(undefined, { minimumFractionDigits: 1 })}
              </p>
            </div>
          </div>
        </div>

        {/* 操作区 */}
        <div className="flex items-center space-x-4 bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <button
            onClick={toggleRunning}
            className={`flex items-center space-x-3 px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
              isRunning
                ? 'bg-green-500 hover:bg-green-600 text-white'
                : 'bg-gray-400 hover:bg-gray-500 text-white'
            }`}
          >
            {isRunning ? (
              <>
                <Power className="w-5 h-5" />
                <span>运行中</span>
              </>
            ) : (
              <>
                <PowerOff className="w-5 h-5" />
                <span>已停止</span>
              </>
            )}
          </button>
          <p className="text-sm text-gray-600 dark:text-gray-400 max-w-xs">
            {isRunning ? '系统正在运行，实时监控市场数据并执行策略' : '系统已停止，暂停所有自动化交易操作'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default StockInfo;