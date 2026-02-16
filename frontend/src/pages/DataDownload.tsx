/**
 * 数据下载页面 - 极简科技风
 */

import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Download, CheckCircle, AlertCircle, Database, Sparkles, TrendingUp, Zap } from 'lucide-react';
import {
  downloadStockData,
  checkDataAvailability,
  getDownloadedList,
  deleteDownloadedData,
  getStatistics,
  type DownloadRequest,
  type DownloadedData,
  type CheckDataResponse,
  type StatisticsResponse
} from '../services/dataDownload';
import StockCodeSearch from '../components/StockCodeSearch';
import { type StockInfo } from '../services/stockCode';

const DataDownload: React.FC = () => {
  const [stockCode, setStockCode] = useState('');
  const [selectedStock, setSelectedStock] = useState<StockInfo | null>(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [frequency, setFrequency] = useState('daily');
  const [source, setSource] = useState('auto');
  const [forceDownload, setForceDownload] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [checkingData, setCheckingData] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [downloadResult, setDownloadResult] = useState<any>(null);
  const [downloadedList, setDownloadedList] = useState<DownloadedData[]>([]);
  const [statistics, setStatistics] = useState<StatisticsResponse | null>(null);
  const [dataCheck, setDataCheck] = useState<CheckDataResponse | null>(null);

  // 初始化日期（默认过去一年）
  useEffect(() => {
    const today = new Date();
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(today.getFullYear() - 1);
    
    setEndDate(today.toISOString().split('T')[0]);
    setStartDate(oneYearAgo.toISOString().split('T')[0]);
    
    loadDownloadedList();
    loadStatistics();
  }, []);

  // 加载已下载数据列表
  const loadDownloadedList = async () => {
    try {
      const result = await getDownloadedList();
      // 安全访问downloads属性
      setDownloadedList(result?.downloads || []);
    } catch (error) {
      console.error('加载数据列表失败:', error);
      setDownloadedList([]);
    }
  };

  // 加载统计信息
  const loadStatistics = async () => {
    try {
      const result = await getStatistics();
      setStatistics(result);
    } catch (error) {
      console.error('加载统计信息失败:', error);
    }
  };

  // 快捷日期选择
  const handleQuickDate = (days: number) => {
    const today = new Date();
    const past = new Date();
    past.setDate(today.getDate() - days);
    
    setEndDate(today.toISOString().split('T')[0]);
    setStartDate(past.toISOString().split('T')[0]);
  };

  // 检查数据是否存在
  const handleCheckData = async () => {
    if (!stockCode || !startDate || !endDate) {
      alert('请填写完整的股票代码和日期范围');
      return;
    }

    setCheckingData(true);
    setDataCheck(null);
    
    // 模拟进度条
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 50));
      setDownloadProgress(i);
    }

    try {
      const result = await checkDataAvailability(stockCode, startDate, endDate, frequency);
      setDataCheck(result);
    } catch (error) {
      console.error('检查数据失败:', error);
      alert('检查数据失败');
    } finally {
      setCheckingData(false);
      setDownloadProgress(0);
    }
  };

  // 下载数据
  const handleDownload = async () => {
    if (!stockCode || !startDate || !endDate) {
      alert('请填写完整的股票代码和日期范围');
      return;
    }

    setDownloading(true);
    setDownloadResult(null);
    setDownloadProgress(0);

    // 模拟进度条
    for (let i = 0; i <= 100; i += 5) {
      await new Promise(resolve => setTimeout(resolve, 100));
      setDownloadProgress(i);
    }

    try {
      const request: DownloadRequest = {
        stock_code: stockCode,
        start_date: startDate,
        end_date: endDate,
        frequency,
        source,
        force_download: forceDownload
      };

      const result = await downloadStockData(request);
      setDownloadResult(result);
      
      await loadDownloadedList();
      await loadStatistics();
      
      if (result.status === 'completed') {
        setTimeout(() => {
          alert(`✓ 下载成功！数据条数: ${result.data_count}`);
          setDownloadResult(null);
        }, 500);
      } else if (result.status === 'exists') {
        alert('✓ 数据已存在，使用已有数据');
      } else if (result.status === 'partial_overlap') {
        alert(`⚠ 数据部分重叠: ${result.message}`);
      } else {
        alert(`✗ 下载失败: ${result.message}`);
      }
    } catch (error: any) {
      console.error('下载数据失败:', error);
      alert(`✗ 下载数据失败: ${error.message || '未知错误'}`);
    } finally {
      setDownloading(false);
      setDownloadProgress(0);
    }
  };

  // 删除已下载数据
  const handleDelete = async (id: number, stockCode: string) => {
    if (!confirm(`确定要删除 ${stockCode} 的数据吗？`)) {
      return;
    }

    try {
      await deleteDownloadedData(id);
      alert('✓ 删除成功');
      await loadDownloadedList();
      await loadStatistics();
    } catch (error) {
      console.error('删除数据失败:', error);
      alert('✗ 删除数据失败');
    }
  };

  // 处理股票选择
  const handleStockSelect = (stock: StockInfo) => {
    setSelectedStock(stock);
    setStockCode(stock.code);
  };

  // 格式化频率显示
  const formatFrequency = (freq: string) => {
    const freqMap: Record<string, string> = {
      'daily': '日线',
      '1d': '日线',
      '1min': '1分钟',
      '5min': '5分钟',
      '15min': '15分钟',
      '30min': '30分钟',
      '60min': '60分钟',
      'weekly': '周线',
      '1w': '周线'
    };
    return freqMap[freq] || freq;
  };

  // 获取频率图标
  const getFrequencyIcon = (freq: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      'daily': <TrendingUp className="w-4 h-4" />,
      '1min': <Clock className="w-4 h-4" />,
      '5min': <Clock className="w-4 h-4" />,
      '15min': <Clock className="w-4 h-4" />,
      '30min': <Clock className="w-4 h-4" />,
      '60min': <Clock className="w-4 h-4" />,
      'weekly': <Sparkles className="w-4 h-4" />,
    };
    return iconMap[freq] || <Database className="w-4 h-4" />;
  };

  // 数据源说明
  const sourceDescriptions: Record<string, string> = {
    'auto': '自动选择最优数据源',
    'baostock': 'Baostock - 免费历史数据',
    'akshare': 'Akshare - 实时行情数据',
    'sina': '新浪财经 - 实时数据',
    'tencent': '腾讯财经 - 实时数据',
    'eastmoney': '东方财富 - 综合数据'
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-blue-50 p-6 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 页面标题 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">数据下载</h1>
            <p className="text-gray-600">下载股票历史数据进行回测和分析</p>
          </div>
          {statistics && (
            <div className="hidden md:flex items-center gap-4 bg-white/80 backdrop-blur-sm rounded-xl px-6 py-3 shadow-sm">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{statistics.total_downloads}</div>
                <div className="text-xs text-gray-500">总下载</div>
              </div>
              <div className="w-px h-8 bg-gray-200"></div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{statistics.unique_stocks}</div>
                <div className="text-xs text-gray-500">股票数</div>
              </div>
              <div className="w-px h-8 bg-gray-200"></div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {(statistics.total_data_points / 10000).toFixed(1)}万
                </div>
                <div className="text-xs text-gray-500">数据点</div>
              </div>
            </div>
          )}
        </div>

        {/* 搜索区 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-4">
            <Database className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">股票代码搜索</h2>
          </div>
          <StockCodeSearch 
            onStockSelect={handleStockSelect}
            placeholder="输入股票代码或名称搜索..."
            className="mb-3"
          />
          {selectedStock && (
            <div className="flex items-center gap-2 text-sm text-gray-600 bg-blue-50 rounded-lg px-4 py-2">
              <CheckCircle className="w-4 h-4 text-blue-600" />
              <span>已选择:</span>
              <span className="font-semibold text-gray-900">{selectedStock.name}</span>
              <span className="text-gray-500">({selectedStock.code})</span>
            </div>
          )}
        </div>

        {/* 下载设置 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-6">
            <Download className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">下载设置</h2>
          </div>

          {/* 快捷日期选择 */}
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm font-medium text-gray-700">快捷选择:</span>
            <button
              onClick={() => handleQuickDate(365)}
              className="px-3 py-1.5 bg-gray-100 hover:bg-blue-50 hover:text-blue-600 rounded-lg text-sm font-medium transition-all"
            >
              近1年
            </button>
            <button
              onClick={() => handleQuickDate(90)}
              className="px-3 py-1.5 bg-gray-100 hover:bg-blue-50 hover:text-blue-600 rounded-lg text-sm font-medium transition-all"
            >
              近3个月
            </button>
            <button
              onClick={() => handleQuickDate(30)}
              className="px-3 py-1.5 bg-gray-100 hover:bg-blue-50 hover:text-blue-600 rounded-lg text-sm font-medium transition-all"
            >
              近1个月
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 数据频率 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                数据频率
              </label>
              <select
                value={frequency}
                onChange={(e) => setFrequency(e.target.value)}
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all appearance-none cursor-pointer hover:border-gray-400"
              >
                <option value="daily">📈 日线数据</option>
                <option value="1min">⏱️ 1分钟数据</option>
                <option value="5min">⏱️ 5分钟数据</option>
                <option value="15min">⏱️ 15分钟数据</option>
                <option value="30min">⏱️ 30分钟数据</option>
                <option value="60min">⏱️ 60分钟数据</option>
                <option value="weekly">📊 周线数据</option>
              </select>
            </div>

            {/* 数据源 */}
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                数据源
              </label>
              <div className="relative">
                <select
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all appearance-none cursor-pointer hover:border-gray-400"
                >
                  <option value="auto">🔮 自动选择</option>
                  <option value="baostock">📊 Baostock</option>
                  <option value="akshare">📈 Akshare</option>
                  <option value="sina">📱 新浪财经</option>
                  <option value="tencent">💬 腾讯财经</option>
                  <option value="eastmoney">🔍 东方财富</option>
                </select>
                <div className="absolute right-10 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
                  <Zap className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-1.5 text-xs text-gray-500 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {sourceDescriptions[source]}
              </div>
            </div>

            {/* 开始日期 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span>开始日期</span>
                </div>
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all hover:border-gray-400"
              />
            </div>

            {/* 结束日期 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span>结束日期</span>
                </div>
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all hover:border-gray-400"
              />
            </div>
          </div>

          {/* 强制重新下载 */}
          <div className="mt-4 flex items-start gap-2">
            <input
              type="checkbox"
              checked={forceDownload}
              onChange={(e) => setForceDownload(e.target.checked)}
              className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1 cursor-pointer"
            />
            <div className="flex-1">
              <label className="text-sm font-medium text-gray-900 cursor-pointer">
                强制重新下载
              </label>
              <p className="text-xs text-gray-500 mt-1">
                ⚠️ 将覆盖已存在的数据，建议仅在数据异常时使用
              </p>
            </div>
          </div>

          {/* 进度条 */}
          {(downloading || checkingData) && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  {downloading ? '下载中...' : '检查数据中...'}
                </span>
                <span className="text-sm font-semibold text-blue-600">{downloadProgress}%</span>
              </div>
              <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-300 ease-out"
                  style={{ width: `${downloadProgress}%` }}
                >
                  <div className="h-full bg-white/20 animate-pulse"></div>
                </div>
              </div>
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex gap-3 mt-6">
            <button
              onClick={handleCheckData}
              disabled={downloading || checkingData}
              className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              {checkingData ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-500 border-t-transparent"></div>
                  <span>检查中...</span>
                </>
              ) : (
                <span>检查数据</span>
              )}
            </button>
            <button
              onClick={handleDownload}
              disabled={downloading || checkingData}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-blue-500/25 flex items-center justify-center gap-2"
            >
              {downloading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  <span>下载中...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>下载</span>
                </>
              )}
            </button>
          </div>

          {/* 检查结果 */}
          {dataCheck && (
            <div className={`mt-4 p-4 rounded-xl border-2 ${
              dataCheck.available 
                ? dataCheck.overlap_type === 'exact'
                  ? 'bg-green-50 border-green-200'
                  : 'bg-yellow-50 border-yellow-200'
                : 'bg-gray-50 border-gray-200'
            }`}>
              <div className="flex items-start gap-3">
                {dataCheck.available ? (
                  dataCheck.overlap_type === 'exact' ? (
                    <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                  )
                ) : (
                  <AlertCircle className="w-5 h-5 text-gray-600 mt-0.5 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">数据检查结果</h3>
                  <p className="text-sm text-gray-700">
                    {dataCheck.available
                      ? dataCheck.overlap_type === 'exact'
                        ? `✓ 数据已存在，包含 ${dataCheck.existing_data?.data_count} 条记录`
                        : `⚠ 数据部分重叠，已存在范围: ${dataCheck.existing_data?.start_date} 至 ${dataCheck.existing_data?.end_date}`
                      : '✗ 数据不存在，需要下载'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* 下载结果 */}
          {downloadResult && (
            <div className={`mt-4 p-4 rounded-xl border-2 ${
              downloadResult.status === 'completed' || downloadResult.status === 'exists'
                ? 'bg-green-50 border-green-200'
                : downloadResult.status === 'partial_overlap'
                  ? 'bg-yellow-50 border-yellow-200'
                  : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-start gap-3">
                {(downloadResult.status === 'completed' || downloadResult.status === 'exists') ? (
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-2">下载结果</h3>
                  <div className="space-y-1 text-sm text-gray-700">
                    <p><strong>状态:</strong> {downloadResult.status}</p>
                    <p><strong>消息:</strong> {downloadResult.message}</p>
                    {downloadResult.data_count !== undefined && (
                      <p><strong>数据条数:</strong> {downloadResult.data_count.toLocaleString()}</p>
                    )}
                    {downloadResult.stock_name && (
                      <p><strong>股票名称:</strong> {downloadResult.stock_name}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 已下载数据列表 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Database className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">已下载数据</h2>
              <span className="px-2.5 py-1 bg-blue-100 text-blue-800 rounded-lg text-sm font-semibold">
                {downloadedList.length}
              </span>
            </div>
          </div>
          
          {downloadedList.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Database className="w-8 h-8 text-gray-400" />
              </div>
              <div className="text-gray-900 font-semibold mb-2">📊 还没有下载过数据</div>
              <p className="text-gray-500 text-sm">快去上方选择股票开始下载吧</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      股票代码
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      股票名称
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      日期范围
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      频率
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      数据条数
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      下载时间
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {downloadedList.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4 text-sm font-semibold text-gray-900">
                        {item.stock_code}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {item.stock_name || '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {item.start_date} 至 {item.end_date}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        <div className="flex items-center gap-1.5 text-gray-700">
                          {getFrequencyIcon(item.frequency)}
                          <span className="font-medium">{formatFrequency(item.frequency)}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {item.data_count.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(item.downloaded_at).toLocaleString()}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm">
                        <button
                          onClick={() => handleDelete(item.id, item.stock_code)}
                          className="text-red-600 hover:text-red-800 font-medium transition-colors flex items-center gap-1"
                        >
                          <AlertCircle className="w-3.5 h-3.5" />
                          删除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataDownload;