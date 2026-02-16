/**
 * 测试股票搜索组件页面
 */
import React from 'react';
import StockCodeSearch from '../components/StockCodeSearch';

const TestSearch: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          股票搜索组件测试页面
        </h1>
        
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">
            StockCodeSearch 组件
          </h2>
          
          <StockCodeSearch 
            placeholder="输入股票代码或名称搜索..."
            onStockSelect={(stock) => {
              console.log('选中股票:', stock);
              alert(`选中股票: ${stock.name} (${stock.code})`);
            }}
          />
        </div>
        
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">
            测试说明
          </h3>
          <ul className="space-y-2 text-blue-800">
            <li>• 在上方搜索框输入股票代码（如：600519）或名称（如：贵州茅台）</li>
            <li>• 点击下拉列表中的股票查看详细信息</li>
            <li>• 点击编辑按钮（铅笔图标）可修改股票信息</li>
            <li>• 如果看到渐变背景、圆角卡片、阴影效果，说明样式已生效</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TestSearch;