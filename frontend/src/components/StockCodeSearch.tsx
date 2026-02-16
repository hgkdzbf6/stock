/**
 * 股票代码搜索组件 - 极简科技风
 */
import React, { useState, useEffect, useRef } from 'react';
import { Search, X, TrendingUp, TrendingDown, Calendar, Sparkles, AlertCircle, Check, Edit2, Save, X as XIcon } from 'lucide-react';
import { searchStocks, type StockInfo } from '../services/stockCode';

interface StockCodeSearchProps {
  placeholder?: string;
  onStockSelect?: (stock: StockInfo) => void;
  className?: string;
}

const StockCodeSearch: React.FC<StockCodeSearchProps> = ({ 
  placeholder = '输入股票代码或名称...', 
  onStockSelect,
  className = ''
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<StockInfo[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedStock, setSelectedStock] = useState<StockInfo | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<StockInfo>>({});
  const [recentStocks, setRecentStocks] = useState<StockInfo[]>([]);
  const [stockQuote, setStockQuote] = useState<any>(null);
  const searchRef = useRef<HTMLDivElement>(null);

  // 搜索股票
  const handleSearch = async (searchQuery: string) => {
    setQuery(searchQuery);
    
    if (!searchQuery.trim()) {
      setResults([]);
      setShowResults(false);
      return;
    }

    setLoading(true);
    try {
      const data = await searchStocks(searchQuery);
      setResults(data.results || []);
      setShowResults(true);
    } catch (error) {
      console.error('搜索股票失败:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // 选择股票
  const handleSelect = (stock: StockInfo) => {
    setSelectedStock(stock);
    setQuery(`${stock.code} - ${stock.name}`);
    setShowResults(false);
    setResults([]);
    
    // 添加到最近搜索
    addToRecent(stock);
    
    // 触发回调
    if (onStockSelect) {
      onStockSelect(stock);
    }
  };

  // 添加到最近搜索
  const addToRecent = (stock: StockInfo) => {
    setRecentStocks(prev => {
      const filtered = prev.filter(s => s.code !== stock.code);
      return [stock, ...filtered].slice(0, 5);
    });
  };

  // 清空搜索
  const handleClear = () => {
    setQuery('');
    setResults([]);
    setShowResults(false);
    setSelectedStock(null);
  };

  // 编辑模式
  const handleEdit = () => {
    setIsEditing(true);
    setEditForm({
      code: selectedStock?.code,
      name: selectedStock?.name,
      market: selectedStock?.market
    });
  };

  // 保存编辑
  const handleSave = () => {
    if (selectedStock) {
      setSelectedStock({
        ...selectedStock,
        code: editForm.code || selectedStock.code,
        name: editForm.name || selectedStock.name,
        market: editForm.market || selectedStock.market
      });
      setIsEditing(false);
    }
  };

  // 取消编辑
  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditForm({});
  };

  // 点击外部关闭下拉框
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 加载最近搜索
  useEffect(() => {
    const saved = localStorage.getItem('recentStocks');
    if (saved) {
      try {
        setRecentStocks(JSON.parse(saved));
      } catch (error) {
        console.error('加载最近搜索失败:', error);
      }
    }
  }, []);

  // 保存最近搜索
  useEffect(() => {
    if (recentStocks.length > 0) {
      localStorage.setItem('recentStocks', JSON.stringify(recentStocks));
    }
  }, [recentStocks]);

  return (
    <div className={`relative ${className}`} ref={searchRef}>
      {/* 搜索框 */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          onFocus={() => {
            if (query.trim()) setShowResults(true);
            else if (recentStocks.length > 0) setShowResults(true);
          }}
          placeholder={placeholder}
          className="w-full pl-12 pr-12 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all hover:border-gray-300 text-gray-900 placeholder-gray-400"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* 搜索结果下拉框 */}
      {showResults && (
        <div className="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-lg max-h-96 overflow-y-auto">
          {loading ? (
            <div className="py-8 text-center text-gray-500">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-blue-600"></div>
              <p className="mt-2 text-sm">搜索中...</p>
            </div>
          ) : results.length === 0 && !query ? (
            <div className="py-8 px-4 text-center text-gray-500">
              <Search className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm">输入股票代码或名称进行搜索</p>
            </div>
          ) : results.length === 0 ? (
            <div className="py-8 px-4 text-center text-gray-500">
              <AlertCircle className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm">未找到匹配的股票</p>
            </div>
          ) : (
            <div className="py-2">
              {results.map((stock) => (
                <button
                  key={stock.code}
                  onClick={() => handleSelect(stock)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-900 text-sm">
                          {stock.code}
                        </span>
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                          {stock.market || 'SH'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 truncate mt-1">
                        {stock.name}
                      </div>
                    </div>
                    <Check className="h-4 w-4 text-blue-600 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 选中的股票信息卡片 */}
      {selectedStock && !showResults && (
        <div className="mt-4 bg-gradient-to-br from-white via-blue-50/50 to-indigo-50/50 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          {/* 装饰性元素 */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 rounded-full blur-2xl -translate-y-16 translate-x-16"></div>
          
          <div className="relative p-6">
            {/* 头部：股票信息 */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="text-2xl font-bold text-gray-900">
                    {selectedStock.name}
                  </h3>
                  {!isEditing && (
                    <button
                      onClick={handleEdit}
                      className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                      title="编辑"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <span className="font-semibold text-gray-900">{selectedStock.code}</span>
                  <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs font-medium">
                    {selectedStock.market || 'SH'}
                  </span>
                </div>
              </div>
              
              {isEditing ? (
                <div className="flex gap-2">
                  <button
                    onClick={handleSave}
                    className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
                  >
                    <Save className="w-3.5 h-3.5" />
                    保存
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
                  >
                    <XIcon className="w-3.5 h-3.5" />
                    取消
                  </button>
                </div>
              ) : (
                <div className="text-right">
                  <div className="text-sm text-gray-500 mb-1">最新价</div>
                  <div className="text-2xl font-bold text-gray-900">--.--</div>
                </div>
              )}
            </div>

            {/* 编辑表单 */}
            {isEditing && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4 p-4 bg-white/60 rounded-xl border border-gray-200">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">股票代码</label>
                  <input
                    type="text"
                    value={editForm.code || ''}
                    onChange={(e) => setEditForm({...editForm, code: e.target.value})}
                    className="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">股票名称</label>
                  <input
                    type="text"
                    value={editForm.name || ''}
                    onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                    className="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">市场</label>
                  <select
                    value={editForm.market || 'SH'}
                    onChange={(e) => setEditForm({...editForm, market: e.target.value})}
                    className="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="SH">上海</option>
                    <option value="SZ">深圳</option>
                    <option value="BJ">北京</option>
                  </select>
                </div>
              </div>
            )}

            {/* 核心指标卡片 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 border border-gray-100">
                <div className="text-xs text-gray-500 mb-1">最新价</div>
                <div className="text-xl font-bold text-gray-900">--.--</div>
              </div>
              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 border border-gray-100">
                <div className="text-xs text-gray-500 mb-1">涨跌幅</div>
                <div className="text-xl font-bold text-gray-500">--%</div>
              </div>
              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 border border-gray-100">
                <div className="text-xs text-gray-500 mb-1">成交量</div>
                <div className="text-xl font-bold text-gray-900">--</div>
              </div>
              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4 border border-gray-100">
                <div className="text-xs text-gray-500 mb-1">成交额</div>
                <div className="text-xl font-bold text-gray-900">--</div>
              </div>
            </div>

            {/* 详细数据小卡片 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3">
              <div className="bg-white/40 rounded-lg p-3 border border-gray-100">
                <div className="text-xs text-gray-500 mb-0.5">开盘</div>
                <div className="text-sm font-semibold text-gray-700">--.--</div>
              </div>
              <div className="bg-white/40 rounded-lg p-3 border border-gray-100">
                <div className="text-xs text-gray-500 mb-0.5">最高</div>
                <div className="text-sm font-semibold text-gray-700">--.--</div>
              </div>
              <div className="bg-white/40 rounded-lg p-3 border border-gray-100">
                <div className="text-xs text-gray-500 mb-0.5">最低</div>
                <div className="text-sm font-semibold text-gray-700">--.--</div>
              </div>
              <div className="bg-white/40 rounded-lg p-3 border border-gray-100">
                <div className="text-xs text-gray-500 mb-0.5">昨收</div>
                <div className="text-sm font-semibold text-gray-700">--.--</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 最近搜索提示 */}
      {!query && recentStocks.length > 0 && !selectedStock && showResults && (
        <div className="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-semibold text-gray-700">最近搜索</span>
            </div>
          </div>
          {recentStocks.map((stock) => (
            <button
              key={stock.code}
              onClick={() => handleSelect(stock)}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900 text-sm">
                      {stock.code}
                    </span>
                    <span className="text-sm text-gray-600 truncate">
                      {stock.name}
                    </span>
                  </div>
                </div>
                <Calendar className="h-4 w-4 text-gray-400 flex-shrink-0" />
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default StockCodeSearch;