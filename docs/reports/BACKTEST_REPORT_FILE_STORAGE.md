# 回测报告文件存储功能实现报告

## 概述
实现了回测报告的文件存储功能，解决了导航到其他页面后返回时数据丢失的问题。

## 实现时间
2026-02-17

## 功能特性

### 1. 后端实现

#### 新增文件：`backend/api/backtest_reports.py`
- **保存报告**: 将回测数据保存为JSON文件到 `backend/data/backtest_reports/` 目录
- **列出报告**: 获取所有已保存的回测报告列表
- **加载报告**: 从文件加载指定的回测报告
- **删除报告**: 删除指定的回测报告文件

#### 文件命名规则
```
{股票代码}_{策略名称}_{时间戳}.json
```
例如: `000001.SZ_双均线策略_20260217_001234.json`

#### API端点
- `POST /api/v1/backtest-reports/save` - 保存回测报告
- `GET /api/v1/backtest-reports/list` - 获取报告列表
- `GET /api/v1/backtest-reports/load/{filename}` - 加载指定报告
- `DELETE /api/v1/backtest-reports/{filename}` - 删除指定报告

### 2. 前端实现

#### 新增文件：`frontend/src/api/backtestReports.ts`
- 提供与后端API交互的TypeScript接口和函数
- 类型安全的API调用

#### 修改文件：`frontend/src/pages/BacktestReport.tsx`
- **文件选择器**: 在页面顶部添加下拉选择框，可以选择已保存的回测报告
- **保存按钮**: 点击保存按钮将当前回测数据保存到文件
- **加载功能**: 从选择框选择报告后自动加载并显示
- **删除功能**: 可以删除不需要的回测报告
- **加载状态**: 显示加载中的提示
- **空状态优化**: 当没有新数据但有已保存报告时，显示报告列表供用户选择

### 3. 数据持久化

#### 文件存储结构
```json
{
  "metadata": {
    "create_time": "2026-02-17 00:30:00",
    "strategy_name": "双均线策略",
    "stock_code": "000001.SZ",
    "start_date": "2025-01-01",
    "end_date": "2026-02-16",
    "filename": "000001.SZ_双均线策略_20260217_001234.json"
  },
  "data": {
    // 完整的回测数据
  }
}
```

#### 存储位置
```
backend/data/backtest_reports/
```

回测报告以JSON文件格式存储在上述目录中，每个文件包含完整的回测数据和元数据信息。

## 使用流程

### 保存回测报告
1. 在策略管理页面运行回测
2. 查看回测报告
3. 点击右上角的"保存报告"按钮
4. 系统自动保存报告并刷新列表

### 加载回测报告
1. 进入回测报告页面
2. 在顶部选择器中选择要查看的报告
3. 系统自动加载并显示数据

### 管理回测报告
- 从下拉框快速选择报告
- 在空状态页面查看所有报告
- 点击删除按钮删除不需要的报告

## 技术细节

### 状态管理
```typescript
const [backtestDataFromState, setBacktestDataFromState] = useState<any>(location.state?.backtestData);
const [strategyNameFromState, setStrategyNameFromState] = useState<string>(location.state?.strategyName);
const [reports, setReports] = useState<BacktestReportMetadata[]>([]);
const [selectedReport, setSelectedReport] = useState<string>('');
```

### 页面逻辑
1. 初始化时自动加载报告列表
2. 支持从路由传递的新数据
3. 支持从文件加载的历史数据
4. 数据变化时自动更新UI

### 安全性
- 文件名验证，防止路径遍历攻击
- 仅允许 `.json` 文件扩展名
- 删除操作需要用户确认

## 优势

1. **数据持久化**: 回测报告永久保存，不会因导航而丢失
2. **历史记录**: 可以查看和对比不同时期的回测结果
3. **快速切换**: 通过选择器快速切换不同报告
4. **易于管理**: 可以删除不需要的报告
5. **类型安全**: 完整的TypeScript类型支持
6. **用户友好**: 直观的UI和清晰的操作流程

## 后续优化建议

1. 添加报告搜索和过滤功能
2. 支持报告导出为Excel或PDF格式
3. 添加报告对比功能，对比不同策略的表现
4. 支持报告标签和分类
5. 添加报告收藏功能
6. 实现报告分享功能

## 文件清单

### 新增文件
- `backend/api/backtest_reports.py` - 后端API
- `frontend/src/api/backtestReports.ts` - 前端API封装
- `backend/data/backtest_reports/` - 报告存储目录

### 修改文件
- `backend/api/__init__.py` - 注册新API路由
- `frontend/src/pages/BacktestReport.tsx` - 添加文件管理功能

## 测试建议

1. 保存多个不同策略的回测报告
2. 测试报告加载功能
3. 测试报告删除功能
4. 测试页面导航后返回时数据是否保留
5. 测试并发保存和加载
6. 测试异常情况处理

## 总结

本次实现完整解决了回测数据持久化的问题，提供了完善的报告管理功能。用户现在可以轻松保存、加载和管理回测报告，大大提升了系统的可用性和用户体验。