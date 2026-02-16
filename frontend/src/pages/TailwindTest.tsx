/**
 * Tailwind CSS 测试页面 - 验证基础样式
 */
import React from 'react';

const TailwindTest: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-blue-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* 标题 */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Tailwind CSS 测试</h1>
          <p className="text-gray-600">验证Tailwind CSS是否正常工作</p>
        </div>

        {/* 1. 基础卡片 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. 基础卡片</h2>
          <p className="text-gray-600">
            如果您能看到白色背景、圆角和阴影，说明Tailwind基础样式正常。
          </p>
        </div>

        {/* 2. 渐变卡片 */}
        <div className="bg-gradient-to-br from-white via-blue-50/50 to-indigo-50/50 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-sm p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. 渐变卡片（毛玻璃）</h2>
          <p className="text-gray-600">
            如果您能看到渐变背景（白色 → 蓝色 → 靛蓝色）和毛玻璃效果，说明渐变和backdrop-filter正常。
          </p>
        </div>

        {/* 3. 按钮测试 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. 按钮测试</h2>
          <div className="flex gap-4 flex-wrap">
            <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-blue-800 shadow-lg shadow-blue-500/25 transition-all">
              渐变按钮
            </button>
            <button className="px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-all">
              灰色按钮
            </button>
            <button className="px-6 py-3 bg-blue-50 text-blue-600 font-semibold rounded-xl hover:bg-blue-100 transition-all">
              浅蓝按钮
            </button>
          </div>
        </div>

        {/* 4. 颜色测试 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. 颜色测试</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-red-500 text-white rounded-xl p-4 text-center">
              红色 bg-red-500
            </div>
            <div className="bg-green-500 text-white rounded-xl p-4 text-center">
              绿色 bg-green-500
            </div>
            <div className="bg-blue-500 text-white rounded-xl p-4 text-center">
              蓝色 bg-blue-500
            </div>
          </div>
        </div>

        {/* 5. 圆角测试 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. 圆角测试</h2>
          <div className="flex gap-4 items-end">
            <div className="w-16 h-16 bg-blue-500 rounded-none text-white flex items-center justify-center">
              none
            </div>
            <div className="w-16 h-16 bg-blue-500 rounded-sm text-white flex items-center justify-center">
              sm
            </div>
            <div className="w-16 h-16 bg-blue-500 rounded-md text-white flex items-center justify-center">
              md
            </div>
            <div className="w-16 h-16 bg-blue-500 rounded-lg text-white flex items-center justify-center">
              lg
            </div>
            <div className="w-16 h-16 bg-blue-500 rounded-xl text-white flex items-center justify-center">
              xl
            </div>
            <div className="w-16 h-16 bg-blue-500 rounded-2xl text-white flex items-center justify-center">
              2xl
            </div>
            <div className="w-16 h-16 bg-blue-500 rounded-full text-white flex items-center justify-center">
              full
            </div>
          </div>
        </div>

        {/* 6. 阴影测试 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. 阴影测试</h2>
          <div className="flex gap-4 flex-wrap">
            <div className="w-24 h-24 bg-gray-100 rounded-xl shadow-sm flex items-center justify-center text-gray-600">
              shadow-sm
            </div>
            <div className="w-24 h-24 bg-gray-100 rounded-xl shadow-md flex items-center justify-center text-gray-600">
              shadow-md
            </div>
            <div className="w-24 h-24 bg-gray-100 rounded-xl shadow-lg flex items-center justify-center text-gray-600">
              shadow-lg
            </div>
            <div className="w-24 h-24 bg-gray-100 rounded-xl shadow-xl flex items-center justify-center text-gray-600">
              shadow-xl
            </div>
          </div>
        </div>

        {/* 7. 文字测试 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. 文字测试</h2>
          <div className="space-y-2">
            <p className="text-gray-900 font-bold">text-gray-900 font-bold</p>
            <p className="text-gray-700 font-semibold">text-gray-700 font-semibold</p>
            <p className="text-gray-600 font-medium">text-gray-600 font-medium</p>
            <p className="text-gray-500">text-gray-500</p>
            <p className="text-gray-400 text-sm">text-gray-400 text-sm</p>
          </div>
        </div>

        {/* 8. 输入框测试 */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. 输入框测试</h2>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="基础输入框"
              className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <input
              type="text"
              placeholder="有阴影的输入框"
              className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent hover:border-gray-400"
            />
          </div>
        </div>

        {/* 9. 状态说明 */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-yellow-900 mb-2">如何检查</h3>
          <ol className="list-decimal list-inside space-y-2 text-yellow-800">
            <li>检查页面背景是否是浅灰渐变色</li>
            <li>检查卡片是否是白色背景、圆角、阴影</li>
            <li>检查按钮是否有渐变色和悬停效果</li>
            <li>检查"2. 渐变卡片"是否有毛玻璃效果</li>
            <li>检查所有颜色、圆角、阴影是否正确显示</li>
          </ol>
          <p className="mt-4 text-yellow-700">
            <strong>如果看到这些效果，说明Tailwind CSS正常工作！</strong>
          </p>
        </div>
      </div>
    </div>
  );
};

export default TailwindTest;