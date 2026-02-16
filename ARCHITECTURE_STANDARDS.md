# 量化交易平台 - 架构规范标准

## 概述

本文档定义了量化交易平台的统一架构规范，确保所有组件遵循一致的接口设计、代码风格和文档标准。

## 目录

1. [前端组件规范](#前端组件规范)
2. [后端API规范](#后端api规范)
3. [数据层规范](#数据层规范)
4. [代码风格规范](#代码风格规范)
5. [文档规范](#文档规范)

---

## 前端组件规范

### 1. 组件命名规范

#### 1.1 文件命名
- **组件文件**: PascalCase，如 `EnhancedKLineChart.tsx`
- **工具文件**: camelCase，如 `chartUtils.ts`
- **类型文件**: PascalCase，如 `ChartTypes.ts`
- **常量文件**: PascalCase，如 `ChartConstants.ts`

#### 1.2 组件命名
- **UI组件**: PascalCase，如 `EnhancedKLineChart`
- **Hook**: camelCase + 'use' 前缀，如 `useChart`
- **类型/接口**: PascalCase + 'Props' 后缀，如 `EnhancedKLineChartProps`

### 2. 组件接口规范

所有组件必须遵循以下接口模板：

```typescript
/**
 * 组件功能描述
 * 
 * @description 详细描述组件的功能、用途和使用场景
 * @component EnhancedKLineChart
 * @example
 * ```tsx
 * <EnhancedKLineChart
 *   data={kLineData}
 *   title="K线图"
 *   onStockSelect={handleStockSelect}
 * />
 * ```
 */
import React, { FC, useEffect, useRef, useState, useCallback } from 'react';
import * as echarts from 'echarts';

// ==================== 类型定义 ====================

/**
 * 数据项类型
 */
interface DataItem {
  /** 数据标识 */
  id: string;
  /** 数据值 */
  value: number;
  /** 时间戳 */
  timestamp: string;
}

/**
 * 组件Props接口
 */
interface ComponentNameProps {
  /** 数据源，必填 */
  data: DataItem[];
  
  /** 组件标题，默认为"图表" */
  title?: string;
  
  /** 组件高度，默认为"600px" */
  height?: string;
  
  /** 是否启用全屏功能，默认为true */
  enableFullscreen?: boolean;
  
  /** 主题模式，默认为"light" */
  theme?: 'light' | 'dark';
  
  /** 数据加载状态 */
  loading?: boolean;
  
  /** 错误信息 */
  error?: string | null;
  
  /** 数据刷新回调 */
  onRefresh?: () => void;
  
  /** 数据选择回调 */
  onSelect?: (item: DataItem) => void;
}

// ==================== 常量定义 ====================

/** 默认配置 */
const DEFAULT_CONFIG = {
  HEIGHT: '600px',
  TITLE: '图表',
  THEME: 'light' as const,
  ENABLE_FULLSCREEN: true
};

/** 颜色常量 */
const COLORS = {
  PRIMARY: '#1890ff',
  SUCCESS: '#52c41a',
  WARNING: '#faad14',
  ERROR: '#f5222d',
  INFO: '#1890ff'
};

// ==================== 工具函数 ====================

/**
 * 计算移动平均线
 * 
 * @param dayCount - 周期天数
 * @param data - 数据数组
 * @returns MA数组
 */
const calculateMA = (dayCount: number, data: DataItem[]): number[] => {
  const result: number[] = [];
  for (let i = 0; i < data.length; i++) {
    if (i < dayCount - 1) {
      result.push(NaN);
    } else {
      let sum = 0;
      for (let j = 0; j < dayCount; j++) {
        sum += data[i - j].value;
      }
      result.push(+(sum / dayCount).toFixed(2));
    }
  }
  return result;
};

// ==================== 主组件 ====================

/**
 * 组件名称
 * 
 * 这是一个功能完整的React组件，遵循以下原则：
 * 1. 使用TypeScript类型检查
 * 2. 使用React Hooks管理状态
 * 3. 提供完整的Props接口文档
 * 4. 包含错误处理和加载状态
 * 5. 支持主题切换
 * 6. 响应式设计
 */
const ComponentName: FC<ComponentNameProps> = ({
  data,
  title = DEFAULT_CONFIG.TITLE,
  height = DEFAULT_CONFIG.HEIGHT,
  enableFullscreen = DEFAULT_CONFIG.ENABLE_FULLSCREEN,
  theme = DEFAULT_CONFIG.THEME,
  loading = false,
  error = null,
  onRefresh,
  onSelect
}) => {
  // ==================== Ref定义 ====================
  
  /** 图表容器Ref */
  const chartRef = useRef<HTMLDivElement>(null);
  /** 图表实例Ref */
  const chartInstance = useRef<echarts.ECharts | null>(null);

  // ==================== State定义 ====================
  
  /** 是否全屏状态 */
  const [isFullscreen, setIsFullscreen] = useState(false);
  /** 当前选中的指标 */
  const [activeIndicator, setActiveIndicator] = useState<string>('default');

  // ==================== 副作用 ====================
  
  /**
   * 初始化图表实例
   */
  useEffect(() => {
    if (!chartRef.current) return;

    // 初始化图表
    chartInstance.current = echarts.init(chartRef.current, theme);

    // 监听窗口大小变化
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener('resize', handleResize);

    // 清理函数
    return () => {
      window.removeEventListener('resize', handleResize);
      chartInstance.current?.dispose();
    };
  }, [theme]);

  /**
   * 更新图表数据
   */
  useEffect(() => {
    if (!chartInstance.current || data.length === 0) return;

    // 更新图表配置
    const option: echarts.EChartsOption = {
      // ... ECharts配置
    };

    chartInstance.current.setOption(option, true);
  }, [data, title, height, activeIndicator, theme]);

  // ==================== 事件处理 ====================
  
  /**
   * 处理数据刷新
   */
  const handleRefresh = useCallback(() => {
    onRefresh?.();
    chartInstance.current?.setOption(chartInstance.current.getOption(), true);
  }, [onRefresh]);

  /**
   * 处理全屏切换
   */
  const handleFullscreen = useCallback(() => {
    if (!isFullscreen) {
      chartRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, [isFullscreen]);

  // ==================== 渲染 ====================
  
  /**
   * 渲染加载状态
   */
  if (loading) {
    return <div className="loading">加载中...</div>;
  }

  /**
   * 渲染错误状态
   */
  if (error) {
    return (
      <div className="error">
        <p>加载失败: {error}</p>
        <button onClick={handleRefresh}>重试</button>
      </div>
    );
  }

  /**
   * 渲染主界面
   */
  return (
    <div className="component-container">
      {/* 控制栏 */}
      <div className="control-bar">
        {/* 控制按钮 */}
      </div>

      {/* 图表容器 */}
      <div 
        ref={chartRef} 
        style={{ width: '100%', height }}
      />
    </div>
  );
};

// ==================== 导出 ====================

export default ComponentName;
export type { ComponentNameProps, DataItem };
```

### 3. 图表组件基类

所有图表组件应继承或遵循以下基类规范：

```typescript
/**
 * 图表组件基础Props
 */
interface BaseChartProps {
  /** 数据源 */
  data: any[];
  
  /** 标题 */
  title?: string;
  
  /** 高度 */
  height?: string;
  
  /** 主题 */
  theme?: 'light' | 'dark';
  
  /** 是否显示工具栏 */
  showToolbar?: boolean;
  
  /** 是否支持缩放 */
  enableZoom?: boolean;
  
  /** 是否支持全屏 */
  enableFullscreen?: boolean;
  
  /** 自定义配置 */
  options?: Record<string, any>;
}

/**
 * 图表组件基础接口
 */
interface IChartComponent {
  /** 初始化图表 */
  init: () => void;
  
  /** 更新数据 */
  update: (data: any[]) => void;
  
  /** 销毁图表 */
  destroy: () => void;
  
  /** 调整大小 */
  resize: () => void;
  
  /** 获取配置 */
  getOption: () => echarts.EChartsOption;
}
```

### 4. 组件文档模板

每个组件文件头部必须包含以下文档：

```typescript
/**
 * [组件名称]
 * 
 * @module frontend/src/components/[目录]/[组件名称]
 * @description [组件功能描述]
 * @author [作者]
 * @version [版本号]
 * @since [创建日期]
 * 
 * @example
 * ```tsx
 * <ComponentName
 *   data={data}
 *   title="示例"
 *   onAction={handleAction}
 * />
 * ```
 * 
 * @features
 * - 功能1
 * - 功能2
 * - 功能3
 * 
 * @dependencies
 * - react
 * - echarts
 * - antd
 * 
 * @see {@link 相关文档链接}
 * @see {@link 相关组件链接}
 */
```

---

## 后端API规范

### 1. API路由规范

#### 1.1 路由命名
- **RESTful风格**: `/api/v1/{resource}/{id}`
- **资源名**: 小写复数，如 `/api/v1/stocks/{code}`
- **版本控制**: 通过URL路径，如 `/api/v1/`, `/api/v2/`

#### 1.2 HTTP方法规范
- `GET`: 获取资源
- `POST`: 创建资源
- `PUT`: 更新整个资源
- `PATCH`: 部分更新资源
- `DELETE`: 删除资源

#### 1.3 API端点模板

```python
"""
[API模块名称]

@module backend/api/[模块名称]
@description [API功能描述]
@author [作者]
@version [版本号]
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List
from pydantic import BaseModel, Field
import logging

# ==================== 日志配置 ====================

logger = logging.getLogger(__name__)

# ==================== 路由定义 ====================

router = APIRouter(prefix="/api/v1/resource", tags=["资源管理"])

# ==================== 数据模型 ====================

class ResourceModel(BaseModel):
    """资源数据模型"""
    
    id: str = Field(..., description="资源ID")
    name: str = Field(..., description="资源名称")
    value: float = Field(..., description="资源值")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123",
                "name": "示例资源",
                "value": 100.0
            }
        }

class ResourceResponse(BaseModel):
    """统一响应格式"""
    
    code: int = Field(200, description="响应码")
    message: str = Field("success", description="响应消息")
    data: Optional[ResourceModel] = Field(None, description="响应数据")

# ==================== API端点 ====================

@router.get(
    "/{resource_id}",
    response_model=ResourceResponse,
    summary="获取资源详情",
    description="根据资源ID获取详细信息"
)
async def get_resource(
    resource_id: str = Path(..., description="资源ID"),
    include_details: bool = Query(False, description="是否包含详细信息")
):
    """
    获取资源详情
    
    Args:
        resource_id: 资源ID
        include_details: 是否包含详细信息
        
    Returns:
        ResourceResponse: 资源详情
        
    Raises:
        HTTPException: 资源不存在时返回404
        
    Example:
        >>> GET /api/v1/resource/123?include_details=true
        {
            "code": 200,
            "message": "success",
            "data": {
                "id": "123",
                "name": "示例资源",
                "value": 100.0
            }
        }
    """
    try:
        logger.info(f"获取资源详情: {resource_id}")
        
        # 业务逻辑
        resource = await fetch_resource(resource_id)
        
        if not resource:
            raise HTTPException(status_code=404, detail="资源不存在")
        
        return ResourceResponse(
            code=200,
            message="success",
            data=resource
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取资源详情失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")
```

### 2. 统一响应格式

```python
class BaseResponse(BaseModel):
    """基础响应模型"""
    
    code: int = Field(..., description="响应码", example=200)
    message: str = Field(..., description="响应消息", example="success")
    data: Optional[Any] = Field(None, description="响应数据")

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    
    code: int = Field(200, description="响应码")
    message: str = Field("success", description="响应消息")
    data: dict = Field(..., description="分页数据")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
```

### 3. 服务层规范

```python
"""
服务层基类

所有服务类应继承此基类，确保统一的接口和错误处理
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any
import logging

logger = logging.getLogger(__name__)

class BaseService(ABC):
    """服务基类"""
    
    def __init__(self):
        self.logger = logger
    
    @abstractmethod
    async def get(self, id: str) -> Optional[dict]:
        """获取单个资源"""
        pass
    
    @abstractmethod
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict = None
    ) -> tuple[List[dict], int]:
        """
        获取资源列表
        
        Returns:
            (items, total): 数据列表和总数
        """
        pass
    
    @abstractmethod
    async def create(self, data: dict) -> dict:
        """创建资源"""
        pass
    
    @abstractmethod
    async def update(self, id: str, data: dict) -> dict:
        """更新资源"""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """删除资源"""
        pass
```

---

## 数据层规范

### 1. 数据适配器接口

```python
"""
数据适配器基类

所有数据适配器必须实现此接口
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseAdapter(ABC):
    """数据适配器基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logger
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化适配器"""
        pass
    
    @abstractmethod
    async def get_kline_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        frequency: str = '1d'
    ) -> List[Dict[str, Any]]:
        """
        获取K线数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            frequency: 频率 (1min, 5min, 15min, 30min, 60min, 1d)
            
        Returns:
            K线数据列表，每条数据包含:
            - date: 日期
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量
            - amount: 成交额 (可选)
        """
        pass
    
    @abstractmethod
    async def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """获取股票列表"""
        pass
    
    @abstractmethod
    async def get_stock_quote(self, stock_code: str) -> Dict[str, Any]:
        """获取股票实时行情"""
        pass
    
    @abstractmethod
    async def search_stocks(
        self,
        keyword: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索股票"""
        pass
    
    def normalize_code(self, code: str) -> str:
        """
        标准化股票代码
        
        统一转换为：6位数字 + .SZ 或 .SH
        
        Args:
            code: 原始股票代码
            
        Returns:
            标准化的股票代码
        """
        code = code.strip().upper()
        
        # 移除常见前缀
        if code.startswith(('SH', 'SZ', 'SZ')):
            code = code[2:]
        
        # 提取6位数字
        import re
        match = re.search(r'(\d{6})', code)
        if not match:
            return code
        
        digits = match.group(1)
        
        # 确定市场
        if code.endswith('.SZ') or code.endswith('.SH'):
            return code
        elif digits.startswith('6'):
            return f"{digits}.SH"
        else:
            return f"{digits}.SZ"
```

### 2. 数据模型规范

```python
"""
数据模型定义

使用Pydantic进行数据验证和序列化
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class KLineData(BaseModel):
    """K线数据模型"""
    
    date: str = Field(..., description="日期 (YYYY-MM-DD)")
    open: float = Field(..., gt=0, description="开盘价")
    high: float = Field(..., gt=0, description="最高价")
    low: float = Field(..., gt=0, description="最低价")
    close: float = Field(..., gt=0, description="收盘价")
    volume: int = Field(..., ge=0, description="成交量")
    amount: Optional[float] = Field(None, ge=0, description="成交额")
    
    @validator('high')
    def validate_high(cls, v, values):
        """验证最高价必须大于等于开盘价和收盘价"""
        if 'low' in values and v < values['low']:
            raise ValueError('最高价不能低于最低价')
        return v

class StockQuote(BaseModel):
    """股票实时行情模型"""
    
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    price: float = Field(..., description="当前价格")
    change: float = Field(..., description="涨跌额")
    change_pct: float = Field(..., description="涨跌幅(%)")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    volume: int = Field(..., description="成交量")
    amount: float = Field(..., description="成交额")
    timestamp: str = Field(..., description="时间戳")
```

---

## 代码风格规范

### 1. TypeScript/JavaScript规范

```typescript
// ✅ 推荐
const calculateAverage = (numbers: number[]): number => {
  if (numbers.length === 0) return 0;
  const sum = numbers.reduce((acc, num) => acc + num, 0);
  return sum / numbers.length;
};

// ❌ 不推荐
function calc(n){
  if(n==0)return 0;
  var s=0;
  for(var i=0;i<n.length;i++)s+=n[i];
  return s/n.length;
}
```

### 2. Python规范

```python
# ✅ 推荐
async def calculate_average(numbers: List[float]) -> float:
    """计算平均值"""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

# ❌ 不推荐
def calc(n):
    if not n: return 0
    return sum(n)/len(n)
```

### 3. 命名规范

| 语言 | 类型 | 规范 | 示例 |
|------|------|------|------|
| TypeScript | 变量/函数 | camelCase | `calculateMA` |
| TypeScript | 类/接口 | PascalCase | `BaseAdapter` |
| TypeScript | 常量 | UPPER_SNAKE_CASE | `DEFAULT_CONFIG` |
| Python | 变量/函数 | snake_case | `calculate_ma` |
| Python | 类 | PascalCase | `BaseAdapter` |
| Python | 常量 | UPPER_SNAKE_CASE | `DEFAULT_CONFIG` |

---

## 文档规范

### 1. 组件文档模板

每个组件必须包含：

1. **文件头注释**: 模块信息、作者、版本
2. **类型文档**: 所有类型和接口的JSDoc注释
3. **函数文档**: 所有函数的参数、返回值、示例
4. **使用示例**: 代码示例和最佳实践

### 2. API文档模板

每个API端点必须包含：

1. **端点描述**: 功能说明
2. **请求参数**: 参数类型、是否必填、示例值
3. **响应格式**: 成功和失败的响应示例
4. **错误码**: 可能的错误码和含义
5. **使用示例**: curl命令和响应

### 3. README模板

每个模块/组件目录应包含README.md：

```markdown
# [模块名称]

## 功能描述

[模块功能描述]

## 目录结构

```
[目录树]
```

## 安装和使用

### 安装

```bash
npm install [包名]
```

### 基本使用

```typescript
import Component from './Component';

<Component
  prop1="value1"
  prop2="value2"
/>
```

## API文档

### Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| prop1 | string | 是 | - | 属性1描述 |
| prop2 | number | 否 | 0 | 属性2描述 |

### Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| onChange | (value: any) => void | 值变化时触发 |

## 示例

### 示例1: 基本用法

```tsx
// 代码示例
```

### 示例2: 高级用法

```tsx
// 代码示例
```

## 常见问题

### Q1: 问题1?

A1: 答案1

## 更新日志

### v1.0.0 (2024-XX-XX)
- 初始版本

## 作者

[作者名]

## 许可证

[许可证信息]
```

---

## 总结

遵循以上规范可以确保：

1. ✅ **一致性**: 所有组件遵循相同的接口设计
2. ✅ **可维护性**: 清晰的代码结构和文档
3. ✅ **可扩展性**: 易于添加新功能和组件
4. ✅ **可读性**: 清晰的命名和注释
5. ✅ **可测试性**: 统一的接口便于单元测试

## 参考资料

- [React官方文档](https://react.dev/)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [TypeScript官方文档](https://www.typescriptlang.org/)
- [Python PEP 8](https://peps.python.org/pep-0008/)