# K线图组件架构说明

## 概述

系统已统一使用单个K线图表核心组件，所有K线图都使用蜡烛图（candlestick）显示。

## 组件架构

### 1. 核心组件

#### `EnhancedKLineChart.tsx` - 增强版K线图表组件
- **位置**: `frontend/src/components/charts/EnhancedKLineChart.tsx`
- **功能**: 提供完整的K线图显示功能
- **特性**:
  - ✅ 蜡烛图（Candlestick）显示
  - ✅ 支持MA指标（5日、10日、20日、30日均线）
  - ✅ 支持MACD指标
  - ✅ 支持成交量显示
  - ✅ 支持缩放和拖动
  - ✅ 支持全屏显示
  - ✅ 支持主题切换（light/dark）
  - ✅ 交互式工具提示

**关键配置**:
```typescript
{
  type: 'candlestick',
  name: '日K',
  data: kLineData,
  itemStyle: {
    color: '#ef5350',      // 阳线（上涨）颜色
    color0: '#26a69a',     // 阴线（下跌）颜色
    borderColor: '#ef5350',
    borderColor0: '#26a69a'
  }
}
```

### 2. 业务组件

#### `MarketKLineChart.tsx` - 市场K线图组件
- **位置**: `frontend/src/components/charts/MarketKLineChart.tsx`
- **功能**: 显示大盘指数K线图
- **内部使用**: `EnhancedKLineChart`
- **特性**:
  - 支持多个指数切换（上证指数、深证成指、创业板指等）
  - 显示市场统计信息（开盘、最高、最低、收盘、涨跌幅等）
  - 显示成交量和成交额

#### `SectorKLineChart.tsx` - 板块K线图组件
- **位置**: `frontend/src/components/charts/SectorKLineChart.tsx`
- **功能**: 显示板块指数K线图
- **内部使用**: `EnhancedKLineChart`
- **特性**:
  - 支持板块选择
  - 显示板块统计信息（股票总数、上涨/下跌数量、平均涨跌等）
  - 自动生成板块指数K线数据

### 3. 页面组件

#### `StockDetail.tsx` - 股票详情页
- **位置**: `frontend/src/pages/StockDetail.tsx`
- **功能**: 显示单个股票的详细信息
- **使用**: `EnhancedKLineChart`
- **特性**:
  - 显示股票基本信息
  - 显示实时行情
  - 显示K线图（最近90天）

#### `KLineDashboard.tsx` - K线图仪表板
- **位置**: `frontend/src/pages/KLineDashboard.tsx`
- **功能**: 整合市场K线和板块K线
- **使用**: 
  - `MarketKLineChart` (市场K线标签)
  - `SectorKLineChart` (板块K线标签)
- **特性**: Tab切换界面，方便查看不同类型的K线图

## 组件关系图

```
EnhancedKLineChart (核心K线图组件)
    ↓
    ├──→ MarketKLineChart (市场K线业务组件)
    │       ↓
    │   KLineDashboard (市场K线Tab)
    │
    ├──→ SectorKLineChart (板块K线业务组件)
    │       ↓
    │   KLineDashboard (板块K线Tab)
    │
    └──→ StockDetail (股票详情页)
```

## 蜡烛图显示说明

所有K线图都使用标准的蜡烛图格式：

### 蜡烛图元素

1. **实体（Body）**
   - 阳线（上涨）：红色 (`#ef5350`)
   - 阴线（下跌）：绿色 (`#26a69a`)

2. **影线（Shadow）**
   - 上影线：最高价到实体顶部的线
   - 下影线：实体底部到最低价的线

3. **数据格式**
   ```
   [日期, 开盘价, 收盘价, 最低价, 最高价]
   ```

### 优势

- ✅ **一目了然**: 每个时间周期的价格变化清晰可见
- ✅ **趋势识别**: 通过颜色快速判断涨跌
- ✅ **信息完整**: 同时显示开盘、收盘、最高、最低价格
- ✅ **专业标准**: 符合金融行业标准的K线图显示方式

## 技术实现

### 使用 ECharts

所有K线图组件都基于 ECharts 库实现：

```typescript
import * as echarts from 'echarts';

const chartInstance = echarts.init(chartRef.current, theme);
chartInstance.current.setOption(option);
```

### 数据转换

后端返回的K线数据格式：
```json
{
  "timestamp": "2026-02-16T00:00:00",
  "open": 17.92,
  "high": 17.97,
  "low": 17.70,
  "close": 17.73,
  "volume": 4457270
}
```

前端转换为ECharts格式：
```typescript
const kLineData = data.map(item => [
  item.date,        // 日期
  item.open,        // 开盘价
  item.close,       // 收盘价
  item.low,         // 最低价
  item.high         // 最高价
]);
```

## 删除的组件

### `KLineChart.tsx` (已删除)

- **原因**: 功能较基础，已被 `EnhancedKLineChart` 完全替代
- **删除时间**: 2026-02-16
- **影响**: 无，该组件未被任何地方引用

## 最佳实践

### 1. 使用核心组件

对于新的K线图需求，直接使用 `EnhancedKLineChart`：

```typescript
import EnhancedKLineChart from '@components/charts/EnhancedKLineChart';

<EnhancedKLineChart
  data={kLineData}
  title="股票K线图"
  height="600px"
  showVolume={true}
  theme="light"
/>
```

### 2. 创建业务组件

对于需要特定业务逻辑的场景，创建业务组件并内部使用 `EnhancedKLineChart`：

```typescript
export default function CustomKLineChart() {
  // 业务逻辑处理
  const data = processData();
  
  return (
    <EnhancedKLineChart
      data={data}
      title="自定义K线图"
      {...props}
    />
  );
}
```

### 3. 保持一致性

所有K线图应保持一致的视觉风格和交互体验：
- 使用相同的蜡烛图配色
- 使用相同的数据格式
- 保持相似的布局结构

## 总结

✅ **所有K线图已统一使用蜡烛图显示**
✅ **使用单个核心组件 `EnhancedKLineChart` 进行管理**
✅ **通过业务组件封装特定功能**
✅ **保持了组件的复用性和可维护性**
✅ **删除了冗余的 `KLineChart.tsx` 组件**

这种架构设计确保了：
1. 代码复用性高
2. 维护成本低
3. 功能扩展容易
4. 视觉效果统一