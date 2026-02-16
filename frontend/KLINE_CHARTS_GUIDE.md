# K线图组件使用指南

## 概述

本系统提供了功能强大的K线图组件，支持市场大盘K线图和板块K线图的展示，具有丰富的交互功能和视觉效果。

## 功能特性

### 1. 增强版K线图 (EnhancedKLineChart)

核心K线图组件，提供以下功能：

#### 交互功能
- **缩放控制**: 支持鼠标滚轮缩放和拖动
- **重置视图**: 一键恢复默认视图
- **刷新图表**: 重新渲染图表
- **全屏显示**: 支持全屏模式查看

#### 技术指标
- **均线指标 (MA)**: 支持5日、10日、20日、30日均线
- **MACD指标**: 显示DIF、DEA和MACD柱状图
- **成交量**: 显示成交量柱状图

#### 视觉效果
- 红涨绿跌配色方案
- 详细的悬停提示信息
- 流畅的动画效果
- 响应式设计

### 2. 市场K线图 (MarketKLineChart)

专门用于展示大盘指数K线图：

#### 支持的指数
- 上证指数 (SH000001)
- 深证成指 (SZ399001)
- 创业板指 (SZ399006)
- 沪深300 (SH000300)
- 上证50 (SH000016)
- 中证500 (SZ399905)

#### 市场统计
- 开盘价、最高价、最低价、收盘价
- 涨跌额和涨跌幅
- 成交量和成交额

### 3. 板块K线图 (SectorKLineChart)

用于展示各个板块的K线图：

#### 板块统计
- 股票总数
- 上涨股票数
- 下跌股票数
- 平均涨跌幅

## 组件API

### EnhancedKLineChart

```typescript
interface EnhancedKLineChartProps {
  data: KLineData[];           // K线数据
  title?: string;                // 图表标题
  subtitle?: string;             // 图表副标题
  height?: string;               // 图表高度，默认'600px'
  showVolume?: boolean;          // 是否显示成交量，默认true
  indicators?: IndicatorData;      // 预计算的指标数据
  theme?: 'light' | 'dark';     // 主题，默认'light'
  onStockSelect?: (code: string) => void;  // 股票选择回调
  enableFullscreen?: boolean;     // 是否启用全屏，默认true
}

interface KLineData {
  date: string;      // 日期
  open: number;      // 开盘价
  high: number;      // 最高价
  low: number;       // 最低价
  close: number;     // 收盘价
  volume: number;    // 成交量
  amount?: number;   // 成交额
}
```

### MarketKLineChart

```typescript
interface MarketKLineChartProps {
  height?: string;               // 图表高度，默认'600px'
  theme?: 'light' | 'dark';     // 主题，默认'light'
}
```

### SectorKLineChart

```typescript
interface SectorKLineChartProps {
  height?: string;               // 图表高度，默认'600px'
  theme?: 'light' | 'dark';     // 主题，默认'light'
}
```

## 使用示例

### 1. 使用增强版K线图

```tsx
import EnhancedKLineChart from '@components/charts/EnhancedKLineChart';

const kLineData = [
  {
    date: '2024-01-01',
    open: 100.0,
    high: 105.0,
    low: 98.0,
    close: 103.0,
    volume: 1000000
  },
  // ... 更多数据
];

function MyComponent() {
  return (
    <EnhancedKLineChart
      data={kLineData}
      title="股票K线图"
      subtitle="代码: 600000"
      height="700px"
      showVolume={true}
      theme="light"
    />
  );
}
```

### 2. 使用市场K线图

```tsx
import MarketKLineChart from '@components/charts/MarketKLineChart';

function MyComponent() {
  return (
    <MarketKLineChart
      height="700px"
      theme="light"
    />
  );
}
```

### 3. 使用板块K线图

```tsx
import SectorKLineChart from '@components/charts/SectorKLineChart';

function MyComponent() {
  return (
    <SectorKLineChart
      height="700px"
      theme="light"
    />
  );
}
```

### 4. 使用K线图仪表板

```tsx
import KLineDashboard from '@pages/KLineDashboard';

function MyComponent() {
  return <KLineDashboard />;
}
```

## 数据格式

### K线数据格式

```typescript
{
  "date": "2024-01-01",     // YYYY-MM-DD格式
  "open": 100.0,            // 开盘价
  "high": 105.0,            // 最高价
  "low": 98.0,              // 最低价
  "close": 103.0,           // 收盘价
  "volume": 1000000,        // 成交量（股）
  "amount": 103000000        // 成交额（元，可选）
}
```

### 板块数据格式

```typescript
interface Sector {
  code: string;              // 板块代码
  name: string;              // 板块名称
  description: string;        // 板块描述
}
```

## API接口

### 市场指数K线数据

**接口**: `GET /api/v1/market/kline`

**参数**:
```typescript
{
  code: string;              // 指数代码，如'SH000001'
  freq: string;              // 频率，'daily', 'weekly', 'monthly'
  start_date: string;        // 开始日期，YYYY-MM-DD
  end_date: string;          // 结束日期，YYYY-MM-DD
}
```

### 板块列表

**接口**: `GET /api/v1/sectors`

### 股票列表（按板块筛选）

**接口**: `GET /api/v1/stocks`

**参数**:
```typescript
{
  sector?: string;           // 板块代码
  page: number;             // 页码
  page_size: number;         // 每页数量
  data_source?: string;      // 数据源
}
```

## 颜色方案

### 涨跌颜色
- **上涨**: 红色 (#ef5350)
- **下跌**: 绿色 (#26a69a)

### 均线颜色
- **MA5**: 橙色 (#f39c12)
- **MA10**: 红色 (#e74c3c)
- **MA20**: 紫色 (#9b59b6)
- **MA30**: 蓝色 (#3498db)

### MACD颜色
- **DIF**: 白色 (#ffffff)
- **DEA**: 黄色 (#ffd700)
- **MACD柱状图**: 红涨绿跌

## 交互操作

### 鼠标操作
- **滚轮**: 缩放K线图
- **拖动**: 平移K线图
- **悬停**: 显示详细数据提示

### 按钮操作
- **放大图标 (+)**: 放大显示
- **缩小图标 (-)**: 缩小显示
- **撤销图标**: 重置视图
- **刷新图标**: 刷新图表
- **全屏图标**: 全屏显示

### 下拉选择
- **指标选择**: 切换MA/MACD指标
- **指数选择**: 选择不同市场指数
- **板块选择**: 选择不同板块

## 性能优化

### 数据加载
- 组件首次加载时会请求最近90天的数据
- 切换指标或指数时会重新加载数据
- 使用模拟数据作为后备方案

### 渲染优化
- 使用echarts的setOption进行增量更新
- 避免不必要的重新渲染
- 组件卸载时正确清理资源

## 注意事项

1. **数据格式**: 确保K线数据格式正确，特别是日期格式为YYYY-MM-DD
2. **数据量**: 建议单个图表显示不超过500个数据点
3. **性能**: 大数据量时建议使用分页或数据聚合
4. **响应式**: 图表会自动适应容器大小，但建议设置合适的高度
5. **错误处理**: 组件内置错误处理，会显示友好的错误提示

## 故障排除

### 图表不显示
- 检查数据是否正确加载
- 查看浏览器控制台是否有错误
- 确认容器高度已设置

### 数据加载失败
- 检查API接口是否正常
- 确认网络连接正常
- 查看后端日志

### 图表样式异常
- 确认echarts依赖已安装
- 检查主题配置是否正确
- 清除浏览器缓存

## 未来扩展

计划添加的功能：
1. 更多技术指标（KDJ、RSI、BOLL等）
2. 自定义指标计算
3. 图表导出功能（PNG、PDF）
4. 数据导出功能（Excel、CSV）
5. 多图对比功能
6. 实时数据推送
7. 自定义时间范围选择
8. 图表模板保存

## 技术栈

- **React 18**: 前端框架
- **TypeScript**: 类型安全
- **ECharts 5**: 图表库
- **Ant Design 5**: UI组件库
- **Axios**: HTTP客户端

## 支持

如有问题或建议，请联系开发团队。