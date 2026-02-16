# 图表组件文档

## 概述

本目录包含所有图表相关的React组件，遵循统一的架构规范和接口标准。

## 目录结构

```
charts/
├── BaseChart.tsx              # 图表基类（所有图表的基础）
├── EnhancedKLineChart.tsx     # 增强K线图组件
├── MarketKLineChart.tsx       # 市场K线图组件
├── SectorKLineChart.tsx       # 行业K线图组件
└── README.md                  # 本文档
```

---

## 核心组件

### 1. BaseChart (图表基类)

**文件**: `BaseChart.tsx`

**描述**: 所有图表组件的基类，提供通用的图表功能和UI。

**主要功能**:
- ✅ 自动初始化ECharts实例
- ✅ 响应式图表大小调整
- ✅ 主题切换支持（light/dark）
- ✅ 加载状态和错误处理
- ✅ 统一的控制栏（缩放、重置、刷新、全屏）
- ✅ 自定义图表配置

**Props接口**:
```typescript
interface BaseChartProps {
  /** 数据源 */
  data: ChartDataItem[];
  
  /** 图表标题 */
  title?: string;
  
  /** 图表副标题 */
  subtitle?: string;
  
  /** 图表高度，默认为"600px" */
  height?: string;
  
  /** 图表主题，默认为"light" */
  theme?: 'light' | 'dark';
  
  /** 是否显示工具栏，默认为true */
  showToolbar?: boolean;
  
  /** 工具栏配置 */
  toolbarConfig?: ChartToolbarConfig;
  
  /** 数据加载状态 */
  loading?: boolean;
  
  /** 错误信息 */
  error?: string | null;
  
  /** 数据刷新回调 */
  onRefresh?: () => void;
  
  /** 数据更新回调 */
  onUpdate?: (data: ChartDataItem[]) => void;
  
  /** 自定义图表配置 */
  getChartOption?: (data: ChartDataItem[]) => echarts.EChartsOption;
  
  /** 图表容器样式 */
  containerStyle?: React.CSSProperties;
  
  /** 是否启用全屏功能，默认为true */
  enableFullscreen?: boolean;
}
```

**使用示例**:

```tsx
import BaseChart from '@/components/charts/BaseChart';

function MyChart({ data }) {
  const getChartOption = (data) => ({
    title: { text: '我的图表' },
    xAxis: { 
      type: 'category',
      data: data.map(item => item.date)
    },
    yAxis: { type: 'value' },
    series: [{
      type: 'line',
      data: data.map(item => item.value)
    }]
  });

  return (
    <BaseChart
      data={data}
      title="我的图表"
      height="400px"
      getChartOption={getChartOption}
      onRefresh={() => console.log('刷新')}
    />
  );
}
```

**常量**:
- `DEFAULT_CHART_CONFIG`: 默认配置
- `CHART_COLORS`: 颜色常量

---

### 2. EnhancedKLineChart (增强K线图)

**文件**: `EnhancedKLineChart.tsx`

**描述**: 功能完整的K线图组件，支持多种技术指标和交互功能。

**主要功能**:
- ✅ 标准蜡烛图显示（红绿柱子）
- ✅ MA均线指标（MA5, MA10, MA20, MA30）
- ✅ MACD指标（DIF, DEA, MACD柱）
- ✅ 成交量显示
- ✅ 缩放、拖动、全屏
- ✅ 详细的Tooltip提示
- ✅ 响应式设计

**Props接口**:
```typescript
interface EnhancedKLineChartProps {
  /** K线数据 */
  data: KLineDataItem[];
  
  /** 图表标题 */
  title?: string;
  
  /** 图表副标题 */
  subtitle?: string;
  
  /** 图表高度 */
  height?: string;
  
  /** 是否显示成交量 */
  showVolume?: boolean;
  
  /** 指标数据 */
  indicators?: IndicatorData;
  
  /** 图表主题 */
  theme?: 'light' | 'dark';
  
  /** 股票选择回调 */
  onStockSelect?: (stockCode: string) => void;
  
  /** 是否启用全屏 */
  enableFullscreen?: boolean;
}
```

**数据格式**:
```typescript
interface KLineDataItem {
  date: string;      // 日期 (YYYY-MM-DD)
  open: number;      // 开盘价
  high: number;      // 最高价
  low: number;       // 最低价
  close: number;     // 收盘价
  volume: number;    // 成交量
  amount?: number;   // 成交额（可选）
}
```

**使用示例**:

```tsx
import EnhancedKLineChart from '@/components/charts/EnhancedKLineChart';
import type { KLineDataItem } from '@/types/chart.types';

function StockChart({ stockCode }) {
  const [data, setData] = useState<KLineDataItem[]>([]);
  
  useEffect(() => {
    // 加载数据
    fetch(`/api/v1/market/kline/${stockCode}`)
      .then(res => res.json())
      .then(result => setData(result.data));
  }, [stockCode]);
  
  return (
    <EnhancedKLineChart
      data={data}
      title={`${stockCode} K线图`}
      showVolume={true}
      theme="light"
      onStockSelect={(code) => console.log('选择股票:', code)}
    />
  );
}
```

**蜡烛图显示说明**:
- **阳线（上涨）**: 红色 `#ef5350`
- **阴线（下跌）**: 绿色 `#26a69a`
- **实体**: 开盘价到收盘价
- **影线**: 最高价和最低价

---

### 3. MarketKLineChart (市场K线图)

**文件**: `MarketKLineChart.tsx`

**描述**: 用于显示市场整体行情的K线图组件。

**特点**:
- 继承自EnhancedKLineChart
- 针对市场数据优化
- 支持多只股票对比

**使用示例**:

```tsx
import MarketKLineChart from '@/components/charts/MarketKLineChart';

function MarketOverview() {
  const [marketData, setMarketData] = useState([]);
  
  return (
    <MarketKLineChart
      data={marketData}
      title="市场行情"
      height="500px"
    />
  );
}
```

---

### 4. SectorKLineChart (行业K线图)

**文件**: `SectorKLineChart.tsx`

**描述**: 用于显示行业板块行情的K线图组件。

**特点**:
- 继承自EnhancedKLineChart
- 针对行业数据优化
- 支持行业筛选

**使用示例**:

```tsx
import SectorKLineChart from '@/components/charts/SectorKLineChart';

function SectorOverview() {
  const [sectorData, setSectorData] = useState([]);
  
  return (
    <SectorKLineChart
      data={sectorData}
      title="行业行情"
      height="500px"
      onSectorSelect={(sectorCode) => console.log('选择行业:', sectorCode)}
    />
  );
}
```

---

## 类型定义

所有类型定义统一在 `@/types/chart.types.ts` 中：

### 核心类型

```typescript
// K线数据项
export interface KLineDataItem {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount?: number;
}

// 指标数据
export interface IndicatorData {
  ma5?: number[];
  ma10?: number[];
  ma20?: number[];
  ma30?: number[];
  macd?: {
    dif: number[];
    dea: number[];
    macd: number[];
  };
  kdj?: {
    k: number[];
    d: number[];
    j: number[];
  };
}

// 股票信息
export interface StockInfo {
  code: string;
  name: string;
  price?: number;
  change?: number;
  change_pct?: number;
  // ...
}
```

---

## 开发新图表组件

### 步骤1: 创建组件文件

```bash
touch frontend/src/components/charts/MyNewChart.tsx
```

### 步骤2: 定义组件接口

```tsx
import type { BaseChartProps } from '@/components/charts/BaseChart';
import type { ChartDataItem } from '@/types/chart.types';

interface MyNewChartProps extends BaseChartProps {
  /** 自定义属性 */
  customProp?: string;
}
```

### 步骤3: 实现组件

```tsx
import React, { FC } from 'react';
import BaseChart from '@/components/charts/BaseChart';
import * as echarts from 'echarts';

const MyNewChart: FC<MyNewChartProps> = ({ 
  data, 
  title = '我的图表',
  getChartOption,
  ...props 
}) => {
  /**
   * 生成图表配置
   */
  const generateOption = (data: ChartDataItem[]): echarts.EChartsOption => {
    return {
      title: { text: title },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: data.map(item => item.date)
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        type: 'line',
        data: data.map(item => item.value)
      }]
    };
  };

  return (
    <BaseChart
      {...props}
      data={data}
      title={title}
      getChartOption={getChartOption || generateOption}
    />
  );
};

export default MyNewChart;
```

### 步骤4: 添加类型定义

```tsx
// 在 types/chart.types.ts 中添加
export interface MyChartDataItem extends ChartDataItem {
  /** 自定义字段 */
  customField?: string;
}
```

### 步骤5: 编写文档

```tsx
/**
 * 我的图表组件
 * 
 * @module frontend/src/components/charts/MyNewChart
 * @description 组件功能描述
 * @author 作者名
 * @version 1.0.0
 * 
 * @example
 * ```tsx
 * <MyNewChart
 *   data={data}
 *   title="我的图表"
 * />
 * ```
 * 
 * @features
 * - 功能1
 * - 功能2
 * 
 * @dependencies
 * - react
 * - echarts
 * - antd
 * 
 * @see {@link ARCHITECTURE_STANDARDS.md}
 */
```

---

## 最佳实践

### 1. 使用TypeScript类型

```tsx
// ✅ 推荐
const MyComponent: FC<MyProps> = ({ data }) => {
  // ...
};

// ❌ 不推荐
const MyComponent = ({ data }) => {
  // ...
};
```

### 2. 使用BaseChart作为基础

```tsx
// ✅ 推荐 - 继承BaseChart
import BaseChart from '@/components/charts/BaseChart';

const MyChart: FC<MyProps> = (props) => {
  return <BaseChart {...props} />;
};

// ❌ 不推荐 - 重新实现所有功能
const MyChart = () => {
  // 重复实现图表初始化、响应式等功能
};
```

### 3. 使用统一的类型定义

```tsx
// ✅ 推荐 - 使用共享类型
import type { KLineDataItem } from '@/types/chart.types';

const data: KLineDataItem[] = [...];

// ❌ 不推荐 - 重复定义类型
interface MyKLineData {
  date: string;
  open: number;
  // ...
}
```

### 4. 添加完整的文档

```tsx
/**
 * 组件描述
 * 
 * @module 模块路径
 * @description 详细描述
 * @author 作者
 * @version 版本号
 * 
 * @example
 * ```tsx
 * 使用示例
 * ```
 */
```

---

## 常见问题

### Q1: 如何自定义图表颜色？

使用 `getChartOption` 覆盖默认配置：

```tsx
const getChartOption = (data) => ({
  series: [{
    type: 'line',
    data: data.map(item => item.value),
    itemStyle: {
      color: '#1890ff'
    }
  }]
});
```

### Q2: 如何处理加载状态？

使用 `loading` 和 `error` 属性：

```tsx
<MyChart
  data={data}
  loading={isLoading}
  error={error}
  onRefresh={handleRefresh}
/>
```

### Q3: 如何切换主题？

使用 `theme` 属性：

```tsx
<MyChart
  data={data}
  theme="dark"  // 或 "light"
/>
```

### Q4: 如何禁用某些工具栏按钮？

使用 `toolbarConfig`：

```tsx
<MyChart
  data={data}
  toolbarConfig={{
    showZoom: false,
    showFullscreen: false
  }}
/>
```

### Q5: 如何响应数据变化？

使用 `onUpdate` 回调：

```tsx
<MyChart
  data={data}
  onUpdate={(newData) => console.log('数据更新:', newData)}
/>
```

---

## 相关文档

- [架构规范标准](../../../../ARCHITECTURE_STANDARDS.md)
- [框架总览](../../../../FRAMEWORK_OVERVIEW.md)
- [K线图组件架构](../../../../KLINE_CHART_COMPONENTS_ARCHITECTURE.md)
- [类型定义](../../types/chart.types.ts)

---

## 更新日志

### v1.0.0 (2024-02-16)
- ✅ 创建BaseChart基类
- ✅ 实现EnhancedKLineChart组件
- ✅ 实现MarketKLineChart组件
- ✅ 实现SectorKLineChart组件
- ✅ 统一类型定义
- ✅ 完善文档

---

## 贡献指南

### 开发新组件

1. 继承 `BaseChart` 或 `EnhancedKLineChart`
2. 遵循命名规范（PascalCase）
3. 添加完整的TypeScript类型
4. 编写详细的文档和示例
5. 添加单元测试

### 代码审查

1. 检查是否符合架构规范
2. 确保类型定义完整
3. 验证文档完整性
4. 测试所有功能

---

## 联系方式

如有问题，请联系开发团队或提交Issue。

---

## 许可证

遵循项目整体许可证。