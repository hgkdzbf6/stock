# 量化交易平台 - 框架总览

## 概述

本文档提供了量化交易平台的整体框架架构总览，包括前后端的核心组件、接口规范、以及如何使用统一的标准开发新功能。

## 目录

1. [架构概览](#架构概览)
2. [前端框架](#前端框架)
3. [后端框架](#后端框架)
4. [数据层框架](#数据层框架)
5. [开发指南](#开发指南)
6. [最佳实践](#最佳实践)

---

## 架构概览

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  UI组件层    │  │  业务组件层  │  │  页面层      │  │
│  │  (基础组件)  │  │  (业务逻辑)  │  │  (路由页面)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         ↓                 ↓                 ↓               │
│  ┌──────────────────────────────────────────────────┐    │
│  │              图表组件基类 (BaseChart)            │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                      API层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  路由层      │  │  验证层      │  │  响应层      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         ↓                 ↓                 ↓               │
│  ┌──────────────────────────────────────────────────┐    │
│  │              API端点 (FastAPI)                   │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                      服务层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 业务服务层   │  │ 数据服务层   │  │ 缓存服务层   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         ↓                 ↓                 ↓               │
│  ┌──────────────────────────────────────────────────┐    │
│  │            服务基类 (BaseService)                │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 数据适配器   │  │ 数据模型     │  │ 数据存储     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         ↓                 ↓                 ↓               │
│  ┌──────────────────────────────────────────────────┐    │
│  │        适配器基类 (BaseAdapter)                  │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 核心设计原则

1. **统一接口**: 所有组件遵循统一的接口规范
2. **分层架构**: 清晰的分层，职责明确
3. **可扩展性**: 易于添加新功能和组件
4. **可维护性**: 清晰的代码结构和文档
5. **类型安全**: 使用TypeScript和Pydantic进行类型检查

---

## 前端框架

### 目录结构

```
frontend/src/
├── components/
│   ├── charts/           # 图表组件
│   │   ├── BaseChart.tsx         # 图表基类
│   │   ├── EnhancedKLineChart.tsx # 增强K线图
│   │   ├── MarketKLineChart.tsx   # 市场K线图
│   │   └── SectorKLineChart.tsx   # 行业K线图
│   ├── ui/               # UI基础组件
│   └── business/         # 业务组件
├── types/
│   └── chart.types.ts     # 类型定义
├── hooks/                # React Hooks
├── utils/                # 工具函数
├── services/             # API服务
└── pages/                # 页面组件
```

### 核心组件

#### 1. BaseChart (图表基类)

**位置**: `frontend/src/components/charts/BaseChart.tsx`

**功能**:
- 自动初始化ECharts实例
- 响应式图表大小调整
- 主题切换支持
- 加载状态和错误处理
- 统一的控制栏

**使用示例**:
```tsx
import BaseChart from '@/components/charts/BaseChart';

function MyChart({ data }) {
  const getChartOption = (data) => ({
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
    />
  );
}
```

#### 2. EnhancedKLineChart (增强K线图)

**位置**: `frontend/src/components/charts/EnhancedKLineChart.tsx`

**功能**:
- 标准蜡烛图显示
- MA均线指标
- MACD指标
- 成交量显示
- 缩放、拖动、全屏

**使用示例**:
```tsx
import EnhancedKLineChart from '@/components/charts/EnhancedKLineChart';
import type { KLineDataItem } from '@/types/chart.types';

function StockChart({ stockCode }) {
  const [data, setData] = useState<KLineDataItem[]>([]);
  
  return (
    <EnhancedKLineChart
      data={data}
      title={`${stockCode} K线图`}
      showVolume={true}
      onStockSelect={(code) => console.log(code)}
    />
  );
}
```

### 类型系统

**位置**: `frontend/src/types/chart.types.ts`

**核心类型**:
- `KLineDataItem`: K线数据项
- `IndicatorData`: 指标数据
- `StockInfo`: 股票信息
- `BaseApiResponse`: 基础API响应
- `PaginatedApiResponse`: 分页API响应

**使用示例**:
```tsx
import type { KLineDataItem, BaseApiResponse } from '@/types/chart.types';

const fetchData = async (): Promise<BaseApiResponse<KLineDataItem[]>> => {
  const response = await fetch('/api/v1/market/kline/600519.SH');
  return response.json();
};
```

### 开发新图表组件

**步骤**:

1. **继承BaseChart**:
```tsx
import BaseChart, { BaseChartProps } from '@/components/charts/BaseChart';

interface MyChartProps extends BaseChartProps {
  customProp?: string;
}

const MyChart: FC<MyChartProps> = ({ data, getChartOption, ...props }) => {
  return (
    <BaseChart
      {...props}
      data={data}
      getChartOption={generateOption}
    />
  );
};
```

2. **实现getChartOption**:
```tsx
const generateOption = (data: ChartDataItem[]): echarts.EChartsOption => {
  return {
    xAxis: { data: data.map(item => item.date) },
    yAxis: {},
    series: [{
      type: 'my-chart-type',
      data: data.map(item => item.value)
    }]
  };
};
```

3. **添加类型定义**:
```tsx
// 在 types/chart.types.ts 中添加
export interface MyChartDataItem {
  date: string;
  value: number;
}
```

---

## 后端框架

### 目录结构

```
backend/
├── api/                  # API路由
│   ├── stocks.py         # 股票API
│   ├── market.py         # 市场API
│   └── ...
├── services/             # 服务层
│   ├── market_service.py   # 市场服务
│   └── ...
├── core/                 # 核心模块
│   ├── base_service.py    # 服务基类
│   ├── config.py         # 配置
│   └── database.py      # 数据库
├── data_adapters/        # 数据适配器
│   ├── base.py           # 适配器基类
│   ├── baostock_adapter.py
│   └── ...
├── models/               # 数据模型
│   ├── stock.py
│   └── ...
└── main.py              # 应用入口
```

### 核心组件

#### 1. BaseService (服务基类)

**位置**: `backend/core/base_service.py`

**功能**:
- 统一的CRUD接口
- 标准化错误处理
- 统一日志记录
- 数据验证

**使用示例**:
```python
from core.base_service import BaseService, NotFoundError

class StockService(BaseService[Stock]):
    async def get(self, id: str) -> Optional[Stock]:
        return await self.db.query(Stock).filter(Stock.code == id).first()
    
    async def create(self, data: dict) -> Stock:
        stock = Stock(**data)
        self.db.add(stock)
        await self.db.commit()
        return stock
    
    # ... 实现其他抽象方法
```

#### 2. API路由

**标准格式**:
```python
from fastapi import APIRouter, HTTPException
from core.base_service import BaseResponse

router = APIRouter(prefix="/api/v1/stocks", tags=["股票管理"])

@router.get("/{stock_code}")
async def get_stock(stock_code: str):
    """
    获取股票详情
    
    Args:
        stock_code: 股票代码
        
    Returns:
        BaseResponse: 股票详情
    """
    try:
        stock = await stock_service.get(stock_code)
        if not stock:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        return BaseResponse.success(data=stock)
    except Exception as e:
        return BaseResponse.error(message=str(e), code=500)
```

### 开发新服务

**步骤**:

1. **继承BaseService**:
```python
from core.base_service import BaseService

class MyService(BaseService[MyModel]):
    async def initialize(self) -> bool:
        # 初始化逻辑
        return True
    
    async def get(self, id: str) -> Optional[MyModel]:
        # 实现获取逻辑
        pass
    
    async def list(self, page, page_size, filters=None):
        # 实现列表查询
        pass
    
    # ... 实现其他抽象方法
```

2. **创建API端点**:
```python
from services.my_service import MyService

my_service = MyService()

@router.get("/items/{item_id}")
async def get_item(item_id: str):
    response = await my_service.get_or_error(item_id)
    return response.to_dict()
```

3. **添加数据模型**:
```python
from pydantic import BaseModel

class MyModel(BaseModel):
    id: str
    name: str
    value: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123",
                "name": "示例",
                "value": 100.0
            }
        }
```

---

## 数据层框架

### 数据适配器

**位置**: `backend/data_adapters/base.py`

**核心接口**:
```python
class BaseAdapter(ABC):
    async def initialize(self) -> bool:
        """初始化适配器"""
        pass
    
    async def get_kline_data(self, stock_code, start_date, end_date, frequency='1d'):
        """获取K线数据"""
        pass
    
    async def get_stock_list(self, page=1, page_size=100):
        """获取股票列表"""
        pass
    
    async def get_stock_quote(self, stock_code):
        """获取实时行情"""
        pass
    
    async def search_stocks(self, keyword, limit=10):
        """搜索股票"""
        pass
    
    def normalize_code(self, code: str) -> str:
        """标准化股票代码"""
        pass
```

### 使用适配器

```python
from data_adapters.baostock_adapter import BaostockAdapter

adapter = BaostockAdapter(config={})
await adapter.initialize()

# 获取K线数据
kline_data = await adapter.get_kline_data(
    stock_code="600519.SH",
    start_date="2024-01-01",
    end_date="2024-12-31",
    frequency="1d"
)

# 标准化股票代码
normalized = adapter.normalize_code("sh600519")  # 返回 "600519.SH"
```

---

## 开发指南

### 前端开发流程

#### 1. 创建新组件

```bash
# 在 components 目录下创建组件文件
touch frontend/src/components/my-chart/MyChart.tsx
```

#### 2. 定义组件接口

```tsx
import type { BaseChartProps } from '@/components/charts/BaseChart';

interface MyChartProps extends BaseChartProps {
  customProp: string;
}
```

#### 3. 实现组件逻辑

```tsx
import { FC } from 'react';
import BaseChart from '@/components/charts/BaseChart';

const MyChart: FC<MyChartProps> = ({ data, ...props }) => {
  const getChartOption = (data) => ({
    // ECharts配置
  });
  
  return <BaseChart {...props} data={data} getChartOption={getChartOption} />;
};

export default MyChart;
```

#### 4. 添加类型定义

```tsx
// 在 types/chart.types.ts 中添加
export interface MyChartDataItem {
  id: string;
  value: number;
  timestamp: string;
}
```

#### 5. 编写文档

```tsx
/**
 * 我的图表组件
 * 
 * @module frontend/src/components/my-chart/MyChart
 * @description 组件功能描述
 * @author 作者名
 * @version 1.0.0
 * 
 * @example
 * ```tsx
 * <MyChart
 *   data={data}
 *   title="我的图表"
 * />
 * ```
 */
```

### 后端开发流程

#### 1. 创建服务

```bash
# 在 services 目录下创建服务文件
touch backend/services/my_service.py
```

#### 2. 继承服务基类

```python
from core.base_service import BaseService

class MyService(BaseService[MyModel]):
    async def initialize(self) -> bool:
        self.logger.info("初始化服务")
        return True
    
    async def get(self, id: str) -> Optional[MyModel]:
        return await self.db.get(id)
    
    # ... 实现其他方法
```

#### 3. 创建API端点

```python
from fastapi import APIRouter
from services.my_service import MyService

router = APIRouter(prefix="/api/v1/my-resource", tags=["我的资源"])

my_service = MyService()

@router.get("/{resource_id}")
async def get_resource(resource_id: str):
    response = await my_service.get_or_error(resource_id)
    return response.to_dict()
```

#### 4. 添加数据模型

```python
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    id: str = Field(..., description="资源ID")
    name: str = Field(..., description="资源名称")
    value: float = Field(..., gt=0, description="资源值")
```

---

## 最佳实践

### 前端最佳实践

#### 1. 使用TypeScript类型

```tsx
// ✅ 推荐
interface Props {
  data: KLineDataItem[];
  onRefresh?: () => void;
}

const MyComponent: FC<Props> = ({ data, onRefresh }) => {
  // ...
};

// ❌ 不推荐
const MyComponent = ({ data, onRefresh }) => {
  // ...
};
```

#### 2. 使用自定义Hooks

```tsx
// 创建自定义Hook
const useChartData = (stockCode: string) => {
  const [data, setData] = useState<KLineDataItem[]>([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/v1/market/kline/${stockCode}`);
        const result = await response.json();
        setData(result.data);
      } catch (error) {
        console.error('加载数据失败:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [stockCode]);
  
  return { data, loading };
};

// 使用Hook
function StockChart({ stockCode }) {
  const { data, loading } = useChartData(stockCode);
  
  if (loading) return <div>加载中...</div>;
  
  return <EnhancedKLineChart data={data} />;
}
```

#### 3. 错误处理

```tsx
const MyComponent = () => {
  const [error, setError] = useState<string | null>(null);
  
  const handleAction = async () => {
    try {
      setError(null);
      await someAsyncAction();
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
    }
  };
  
  return (
    <div>
      {error && <Alert type="error" message={error} />}
      <Button onClick={handleAction}>执行操作</Button>
    </div>
  );
};
```

### 后端最佳实践

#### 1. 使用服务基类

```python
# ✅ 推荐
from core.base_service import BaseService

class StockService(BaseService[Stock]):
    async def get(self, id: str) -> Optional[Stock]:
        return await self.db.get(id)

# ❌ 不推荐
class StockService:
    def get_stock(self, id: str):
        return self.db.get(id)
```

#### 2. 统一错误处理

```python
# ✅ 推荐
try:
    item = await service.create(data)
    return BaseResponse.success(data=item, message="创建成功")
except ValidationError as e:
    return BaseResponse.error(message=e.message, code=e.code)
except Exception as e:
    logger.error(f"创建失败: {e}")
    return BaseResponse.error(message="服务器错误", code=500)

# ❌ 不推荐
try:
    item = await service.create(data)
    return {"success": True, "data": item}
except Exception as e:
    return {"success": False, "error": str(e)}
```

#### 3. 使用日志

```python
import logging

logger = logging.getLogger(__name__)

class MyService(BaseService[MyModel]):
    async def get(self, id: str) -> Optional[MyModel]:
        logger.info(f"获取资源: {id}")
        try:
            item = await self.db.get(id)
            logger.debug(f"找到资源: {item}")
            return item
        except Exception as e:
            logger.error(f"获取资源失败: {e}", exc_info=True)
            return None
```

---

## 文档索引

- [架构规范标准](./ARCHITECTURE_STANDARDS.md) - 详细的架构规范和标准
- [K线图组件架构](./KLINE_CHART_COMPONENTS_ARCHITECTURE.md) - K线图组件详细说明
- [股票代码格式修复](./STOCK_CODE_FORMAT_FIX.md) - 股票代码处理说明

---

## 总结

本框架提供了：

1. ✅ **统一的标准**: 所有组件遵循相同的接口规范
2. ✅ **清晰的架构**: 分层设计，职责明确
3. ✅ **类型安全**: TypeScript和Pydantic类型检查
4. ✅ **易于扩展**: 基类设计，易于添加新功能
5. ✅ **完整文档**: 详细的使用说明和示例

遵循本框架开发可以确保代码的一致性、可维护性和可扩展性。

## 支持

如有问题，请参考：
- [架构规范标准](./ARCHITECTURE_STANDARDS.md)
- [项目README](./README.md)
- [API文档](http://localhost:8000/docs)