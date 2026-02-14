/**
 * 数据下载页面
 */

import React, { useState, useEffect } from 'react';
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

const DataDownload: React.FC = () => {
  const [stockCode, setStockCode] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [frequency, setFrequency] = useState('daily');
  const [source, setSource] = useState('auto');
  const [forceDownload, setForceDownload] = useState(false);
  const [downloading, setDownloading] = useState(false);
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
      setDownloadedList(result.downloads);
    } catch (error) {
      console.error('加载数据列表失败:', error);
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

  // 检查数据是否存在
  const handleCheckData = async () => {
    if (!stockCode || !startDate || !endDate) {
      alert('请填写完整的股票代码和日期范围');
      return;
    }

    try {
      const result = await checkDataAvailability(stockCode, startDate, endDate, frequency);
      setDataCheck(result);
    } catch (error) {
      console.error('检查数据失败:', error);
      alert('检查数据失败');
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
      
      // 重新加载数据列表和统计信息
      await loadDownloadedList();
      await loadStatistics();
      
      if (result.status === 'completed') {
        alert(`下载成功！数据条数: ${result.data_count}`);
      } else if (result.status === 'exists') {
        alert('数据已存在，使用已有数据');
      } else if (result.status === 'partial_overlap') {
        alert(`数据部分重叠: ${result.message}`);
      } else {
        alert(`下载失败: ${result.message}`);
      }
    } catch (error: any) {
      console.error('下载数据失败:', error);
      alert(`下载数据失败: ${error.message || '未知错误'}`);
    } finally {
      setDownloading(false);
    }
  };

  // 删除已下载数据
  const handleDelete = async (id: number, stockCode: string) => {
    if (!confirm(`确定要删除 ${stockCode} 的数据吗？`)) {
      return;
    }

    try {
      await deleteDownloadedData(id);
      alert('删除成功');
      await loadDownloadedList();
      await loadStatistics();
    } catch (error) {
      console.error('删除数据失败:', error);
      alert('删除数据失败');
    }
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

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">数据下载</h1>

      {/* 统计信息 */}
      {statistics && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h2 className="text-xl font-semibold mb-3">统计信息</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-gray-600">总下载数</div>
              <div className="text-2xl font-bold text-blue-600">{statistics.total_downloads}</div>
            </div>
            <div>
              <div className="text-gray-600">唯一股票</div>
              <div className="text-2xl font-bold text-blue-600">{statistics.unique_stocks}</div>
            </div>
            <div>
              <div className="text-gray-600">数据点总数</div>
              <div className="text-2xl font-bold text-blue-600">{statistics.total_data_points.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-gray-600">总大小</div>
              <div className="text-2xl font-bold text-blue-600">{statistics.total_file_size_str}</div>
            </div>
          </div>
        </div>
      )}

      {/* 下载表单 */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">下载设置</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              股票代码
            </label>
            <input
              type="text"
              value={stockCode}
              onChange={(e) => setStockCode(e.target.value.toUpperCase())}
              placeholder="例如: 600771.SH"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              数据频率
            </label>
            <select
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="daily">日线</option>
              <option value="1min">1分钟</option>
              <option value="5min">5分钟</option>
              <option value="15min">15分钟</option>
              <option value="30min">30分钟</option>
              <option value="60min">60分钟</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              开始日期
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              结束日期
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              数据源
            </label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="auto">自动</option>
              <option value="baostock">Baostock</option>
              <option value="akshare">Akshare</option>
              <option value="sina">新浪</option>
              <option value="tencent">腾讯</option>
              <option value="eastmoney">东方财富</option>
            </select>
          </div>

          <div className="flex items-center pt-6">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={forceDownload}
                onChange={(e) => setForceDownload(e.target.checked)}
                className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="text-sm text-gray-700">强制重新下载</span>
            </label>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleCheckData}
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            disabled={downloading}
          >
            检查数据
          </button>
          <button
            onClick={handleDownload}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={downloading}
          >
            {downloading ? '下载中...' : '下载'}
          </button>
        </div>

        {/* 数据检查结果 */}
        {dataCheck && (
          <div className={`mt-4 p-4 rounded-md ${
            dataCheck.available 
              ? dataCheck.overlap_type === 'exact'
                ? 'bg-green-50 border border-green-200'
                : 'bg-yellow-50 border border-yellow-200'
              : 'bg-gray-50 border border-gray-200'
          }`}>
            <h3 className="font-semibold mb-2">数据检查结果</h3>
            <p className="text-sm">
              {dataCheck.available
                ? dataCheck.overlap_type === 'exact'
                  ? `✓ 数据已存在，包含 ${dataCheck.existing_data?.data_count} 条记录`
                  : `⚠ 数据部分重叠，已存在范围: ${dataCheck.existing_data?.start_date} 至 ${dataCheck.existing_data?.end_date}`
                : '✗ 数据不存在，需要下载'}
            </p>
          </div>
        )}

        {/* 下载结果 */}
        {downloadResult && (
          <div className={`mt-4 p-4 rounded-md ${
            downloadResult.status === 'completed' || downloadResult.status === 'exists'
              ? 'bg-green-50 border border-green-200'
              : downloadResult.status === 'partial_overlap'
                ? 'bg-yellow-50 border border-yellow-200'
                : 'bg-red-50 border border-red-200'
          }`}>
            <h3 className="font-semibold mb-2">下载结果</h3>
            <div className="text-sm">
              <p><strong>状态:</strong> {downloadResult.status}</p>
              <p><strong>消息:</strong> {downloadResult.message}</p>
              {downloadResult.data_count !== undefined && (
                <p><strong>数据条数:</strong> {downloadResult.data_count}</p>
              )}
              {downloadResult.stock_name && (
                <p><strong>股票名称:</strong> {downloadResult.stock_name}</p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 已下载数据列表 */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">已下载数据</h2>
        
        {downloadedList.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            暂无已下载数据
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    股票代码
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    股票名称
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    日期范围
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    频率
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    数据条数
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    文件大小
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    下载时间
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {downloadedList.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.stock_code}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.stock_name || '-'}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.start_date} 至 {item.end_date}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatFrequency(item.frequency)}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.data_count.toLocaleString()}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.file_size_str}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(item.downloaded_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button
                        onClick={() => handleDelete(item.id, item.stock_code)}
                        className="text-red-600 hover:text-red-900"
                      >
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
  );
};

export default DataDownload;