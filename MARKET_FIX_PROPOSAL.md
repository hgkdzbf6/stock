# 行情页面修复方案

## 问题1：股票名称显示为"未知"

### 问题根源分析

在 `backend/api/stocks.py` 中，当使用本地已下载数据时：

```python
items.append({
    'code': record['stock_code'],
    'name': record['stock_name'] or '未知',  # ❌ stock_name 可能为 None
    ...
})
```

**根本原因：**
1. 下载股票数据时，没有同时获取并保存股票名称
2. `record['stock_name']` 在数据库中可能为 `None` 或空字符串
3. 导致前端显示"未知"

### 解决方案

#### 方案A：在下载时获取股票名称（推荐）

修改 `backend/services/data_download_service.py` 的 `download_stock_data` 方法：

```python
async def download_stock_data(
    self,
    stock_code: str,
    start_date: datetime,
    end_date: datetime,
    frequency: str = 'daily',
    source: str = 'auto',
    force_download: bool = False
) -> Dict:
    try:
        download_id = f"{stock_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # ✅ 新增：在下载前先获取股票名称
        stock_name = None
        try:
            # 从股票代码服务获取股票信息
            stock_info = self.stock_code_service.get_stock_info(stock_code)
            if stock_info:
                stock_name = stock_info.get('名称') or stock_info.get('name')
                logger.info(f"获取股票名称: {stock_code} -> {stock_name}")
        except Exception as e:
            logger.warning(f"获取股票名称失败: {e}")
        
        # ... 下载数据逻辑 ...
        
        # ✅ 保存时传入股票名称
        record_id = self.storage.save_kline_data(
            df=data,
            stock_code=stock_code,
            frequency=frequency,
            stock_name=stock_name  # 传入获取的股票名称
        )
        
        return {
            'status': 'completed',
            'message': '下载完成',
            'download_id': download_id,
            'stock_code': stock_code,
            'stock_name': stock_name,  # ✅ 返回股票名称
            'data_count': len(data),
            'record_id': record_id,
            'data': data
        }
```

同时修改 `backend/services/duckdb_storage_service.py` 的 `save_kline_data` 方法：

```python
def save_kline_data(
    self,
    df: pd.DataFrame,
    stock_code: str,
    frequency: str,
    stock_name: str = None  # ✅ 新增参数
) -> int:
    """保存K线数据到DuckDB"""
    try:
        # 获取最新的一条数据作为元数据
        latest = df.iloc[-1]
        
        # 构建元数据记录
        record = {
            'stock_code': stock_code,
            'stock_name': stock_name,  # ✅ 使用传入的股票名称
            'start_date': df.index[0].strftime('%Y-%m-%d'),
            'end_date': df.index[-1].strftime('%Y-%m-%d'),
            'frequency': frequency,
            'data_count': len(df),
            'downloaded_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'source': 'duckdb',
            'file_path': f'data/{stock_code}_{frequency}.duckdb',
            'file_size': len(df.to_csv(index=False)),
            'file_size_str': f'{len(df.to_csv(index=False))} bytes'
        }
        
        # 保存元数据到downloads表
        conn = self.get_connection()
        conn.execute('''
            INSERT INTO downloads 
            (stock_code, stock_name, start_date, end_date, frequency, 
             data_count, downloaded_at, updated_at, source, file_path, file_size, file_size_str)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(stock_code, frequency) DO UPDATE SET
                end_date = excluded.end_date,
                data_count = excluded.data_count,
                updated_at = excluded.updated_at,
                file_size = excluded.file_size,
                file_size_str = excluded.file_size_str
        ''', (
            record['stock_code'], record['stock_name'], record['start_date'], 
            record['end_date'], record['frequency'], record['data_count'],
            record['downloaded_at'], record['updated_at'], record['source'],
            record['file_path'], record['file_size'], record['file_size_str']
        ))
        
        # 保存K线数据
        df['stock_code'] = stock_code
        df.to_sql('kline_data', conn, if_exists='append', index=True, index_label='date')
        
        conn.close()
        
        return conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        
    except Exception as e:
        logger.error(f"保存K线数据失败: {e}")
        raise
```

#### 方案B：在显示时实时获取股票名称

修改 `backend/api/stocks.py`：

```python
# 在使用本地数据时，实时获取股票名称
from services.stock_code_service import stock_code_service

for record in result['downloads']:
    # ✅ 实时获取股票名称
    if not record.get('stock_name'):
        try:
            stock_info = stock_code_service.get_stock_info(record['stock_code'])
            if stock_info:
                record['stock_name'] = stock_info.get('名称') or stock_info.get('name')
        except:
            pass
    
    items.append({
        'code': record['stock_code'],
        'name': record.get('stock_name') or record['stock_code'],  # ✅ 使用代码作为后备
        ...
    })
```

**推荐使用方案A**，因为：
- 性能更好：下载时一次获取，不需要每次查询
- 数据完整：股票名称保存在数据库中
- 易于维护：不需要修改现有的查询逻辑

---

## 问题2：板块信息获取方案

### 当前状态

前端Market页面中有板块选择，但：
```tsx
<Select
  placeholder="选择板块"
  allowClear
  style={{ width: 150 }}
  onChange={handleSectorChange}
>
  <Option value="医药">医药</Option>
  <Option value="银行">银行</Option>
  <Option value="白酒">白酒</Option>
  <Option value="房地产">房地产</Option>
</Select>
```

这些选项是硬编码的，并且后端没有提供板块筛选功能。

### 解决方案

#### 1. 后端添加板块信息API

创建 `backend/api/sector.py`：

```python
"""板块API"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from loguru import logger

router = APIRouter(prefix="/sector", tags=["板块"])


@router.get("/list")
async def get_sector_list():
    """
    获取板块列表
    
    Returns:
        板块列表
    """
    try:
        logger.info("获取板块列表")
        
        # TODO: 这里可以从数据库或数据源获取真实的板块列表
        # 临时提供常用板块
        sectors = [
            {"code": "医药", "name": "医药", "description": "医药生物板块"},
            {"code": "银行", "name": "银行", "description": "银行板块"},
            {"code": "白酒", "name": "白酒", "description": "白酒板块"},
            {"code": "房地产", "name": "房地产", "description": "房地产板块"},
            {"code": "科技", "name": "科技", "description": "科技板块"},
            {"code": "消费", "name": "消费", "description": "消费板块"},
            {"code": "金融", "name": "金融", "description": "金融板块"},
            {"code": "新能源", "name": "新能源", "description": "新能源板块"},
            {"code": "军工", "name": "军工", "description": "军工板块"},
        ]
        
        return {
            "code": 200,
            "message": "success",
            "data": sectors
        }
        
    except Exception as e:
        logger.error(f"获取板块列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sector_code}/stocks")
async def get_stocks_by_sector(
    sector_code: str,
    page: int = 1,
    page_size: int = 20
):
    """
    根据板块获取股票列表
    
    Args:
        sector_code: 板块代码
        page: 页码
        page_size: 每页数量
    """
    try:
        logger.info(f"获取板块股票: sector={sector_code}")
        
        # TODO: 从股票代码服务或数据库获取板块下的股票
        # 临时返回空列表
        stocks = []
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": stocks,
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        }
        
    except Exception as e:
        logger.error(f"获取板块股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

在 `backend/api/__init__.py` 中注册：

```python
from api.sector import router as sector_router

api_router.include_router(sector_router, prefix="/api/v1")
```

#### 2. 前端添加板块服务

创建 `frontend/src/services/sector.ts`：

```typescript
/** 板块服务 */
import api from './api';

export interface Sector {
  code: string;
  name: string;
  description?: string;
}

export const sectorService = {
  /** 获取板块列表 */
  async getSectorList(): Promise<Sector[]> {
    const response = await api.get<{ code: number; message: string; data: Sector[] }>('/sector/list');
    return response.data;
  },

  /** 根据板块获取股票列表 */
  async getStocksBySector(
    sectorCode: string,
    page: number = 1,
    pageSize: number = 20
  ) {
    const response = await api.get<{
      code: number;
      message: string;
      data: {
        items: any[];
        total: number;
        page: number;
        page_size: number;
      };
    }>(`/sector/${sectorCode}/stocks`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
};
```

#### 3. 修改Market页面使用动态板块

修改 `frontend/src/pages/Market.tsx`：

```typescript
import { useState, useEffect, useCallback } from 'react';
import { Input, Table, Tag, Button, Select, Spin, message, DatePicker } from 'antd';
import { SearchOutlined, ReloadOutlined, CalendarOutlined } from '@ant-design/icons';
import { sectorService } from '@services/sector';  // ✅ 导入板块服务

const Market = () => {
  // ✅ 添加板块列表状态
  const [sectors, setSectors] = useState<any[]>([]);

  // ✅ 加载板块列表
  useEffect(() => {
    sectorService.getSectorList()
      .then(setSectors)
      .catch(error => {
        console.error('获取板块列表失败:', error);
      });
  }, []);

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center' }}>
        {/* ... 其他控件 ... */}
        
        <Select
          placeholder="选择板块"
          allowClear
          style={{ width: 150 }}
          onChange={handleSectorChange}
        >
          {/* ✅ 使用动态板块列表 */}
          {sectors.map(sector => (
            <Option key={sector.code} value={sector.code}>
              {sector.name}
            </Option>
          ))}
        </Select>
        
        {/* ... 其他控件 ... */}
      </div>
      
      {/* ... 表格 ... */}
    </div>
  );
};
```

---

## 实施步骤

### 步骤1：修复股票名称显示（高优先级）

1. 修改 `backend/services/data_download_service.py`
   - 在 `download_stock_data` 方法中添加获取股票名称的逻辑
   - 在保存数据时传入股票名称

2. 修改 `backend/services/duckdb_storage_service.py`
   - 在 `save_kline_data` 方法中添加 `stock_name` 参数
   - 在保存记录时使用股票名称

3. 测试下载功能
   - 下载一只新股票
   - 验证行情页面是否正确显示名称

### 步骤2：添加板块信息功能（中优先级）

1. 创建 `backend/api/sector.py`
   - 实现板块列表API
   - 实现根据板块获取股票列表API

2. 注册板块路由
   - 在 `backend/api/__init__.py` 中注册

3. 创建 `frontend/src/services/sector.ts`
   - 实现板块服务

4. 修改 `frontend/src/pages/Market.tsx`
   - 使用动态板块列表
   - 实现板块筛选功能

### 步骤3：完善板块数据（低优先级）

1. 建立板块数据库
   - 收集真实板块信息
   - 建立股票与板块的映射关系

2. 实现板块数据更新
   - 定期更新板块信息
   - 从数据源获取最新板块分类

---

## 长期优化建议

### 1. 股票信息缓存

建立股票信息缓存机制：
```python
class StockInfoCache:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1小时过期
    
    async def get_stock_name(self, code: str) -> Optional[str]:
        """获取股票名称（带缓存）"""
        if code in self.cache:
            cached = self.cache[code]
            if time.time() - cached['timestamp'] < self.cache_ttl:
                return cached['name']
        
        # 从数据库或API获取
        stock_info = stock_code_service.get_stock_info(code)
        name = stock_info.get('名称') or stock_info.get('name')
        
        # 缓存结果
        self.cache[code] = {
            'name': name,
            'timestamp': time.time()
        }
        
        return name
```

### 2. 板块分类系统

建立完整的板块分类系统：
- 一级板块：行业（如金融、科技、医药）
- 二级板块：子行业（如银行、保险、证券）
- 三级板块：细分领域（如大型银行、城商行）

### 3. 智能数据更新

实现智能数据更新策略：
- 定期自动更新股票列表
- 检测新增和退市股票
- 自动更新股票名称和板块信息

---

## 总结

### 问题1：股票名称显示"未知"
- **根源**：下载数据时没有保存股票名称
- **方案**：在下载时获取并保存股票名称
- **优先级**：高

### 问题2：板块信息获取
- **根源**：没有板块API，前端使用硬编码选项
- **方案**：
  1. 添加板块列表API
  2. 添加根据板块获取股票API
  3. 前端使用动态板块列表
- **优先级**：中

### 实施建议
1. 先修复股票名称问题（影响用户体验）
2. 再添加板块功能（增强用户体验）
3. 长期优化数据管理和缓存（提升系统性能）