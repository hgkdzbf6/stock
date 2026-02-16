# 行情页面数据源更新指南

## 问题说明

**当前问题：** 行情页面显示的是原始CSV数据（stock_list.csv），而不是用户下载的数据。

**期望行为：** 行情页面应该显示用户已下载的股票数据。

---

## 解决方案

### 分析

后端 `backend/api/stocks.py` 已经支持两种数据源：
1. **本地数据** (`use_local=true`) - 从DuckDB读取已下载的数据
2. **远程数据** (`use_local=false`) - 从远程API获取实时数据

前端需要明确传递 `use_local=true` 参数来使用已下载数据。

### 实施步骤

#### 步骤1：修改前端stock服务 ✅

**文件：** `frontend/src/services/stock.ts`

已修改完成，添加了 `use_local` 参数并设置默认值为 `true`：

```typescript
async getStockList(params: {
  page?: number;
  page_size?: number;
  sector?: string;
  keyword?: string;
  data_source?: string;
  use_local?: boolean;  // 是否使用本地已下载数据（默认true）
} = {}) {
  // 默认使用本地数据
  if (params.use_local === undefined) {
    params.use_local = true;
  }
  return apiClient.get<PaginatedResponse<any>>('/stocks', { params });
}
```

#### 步骤2：修改Market页面使用动态板块 ⚠️

**文件：** `frontend/src/pages/Market.tsx`

需要修改以下内容：

**修改1：添加导入**
```typescript
import { sectorService } from '@services/sector';
```

**修改2：添加板块列表状态**
```typescript
const Market = () => {
  // ... 其他状态 ...
  const [sectors, setSectors] = useState<any[]>([]);

  // 加载板块列表
  useEffect(() => {
    sectorService.getSectorList()
      .then(setSectors)
      .catch(error => {
        console.error('获取板块列表失败:', error);
      });
  }, []);
```

**修改3：替换硬编码的板块选项**

找到Select组件（大约在第147-156行）：
```tsx
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
```

**修改4：添加数据源切换选项（可选）**

在数据源Select中添加"本地数据"选项（大约在第158-170行）：
```tsx
<Select
  placeholder="数据源"
  value={dataSource}
  onChange={handleDataSourceChange}
  style={{ width: 150 }}
>
  <Option value="local">本地数据</Option>
  <Option value="auto">远程数据</Option>
</Select>
```

然后修改 `handleDataSourceChange` 函数：
```typescript
const handleDataSourceChange = (source: string) => {
  if (source === 'local') {
    // 使用本地数据
    setDataSource('auto');
    // 在fetchStocks中会默认传递use_local=true
  } else {
    // 使用远程数据
    setDataSource(source);
  }
  setPagination({ ...pagination, current: 1 });
};
```

#### 步骤3：确保后端支持stock_name ⚠️

**文件：** `backend/services/data_download_service.py`

需要应用 `data_download_service_fixed.py` 中的修改：

```bash
cp backend/services/data_download_service_fixed.py backend/services/data_download_service.py
```

或者手动修改（参考 `MARKET_FIX_IMPLEMENTATION_GUIDE.md` 中的详细步骤）。

#### 步骤4：修改DuckDB存储服务 ⚠️

**文件：** `backend/services/duckdb_storage_service.py`

在 `save_kline_data` 方法中添加 `stock_name` 参数：

```python
def save_kline_data(
    self,
    df: pd.DataFrame,
    stock_code: str,
    frequency: str,
    stock_name: str = None  # ✅ 添加这个参数
) -> int:
```

在构建元数据记录时使用股票名称：
```python
record = {
    'stock_code': stock_code,
    'stock_name': stock_name,  # ✅ 使用传入的股票名称
    'start_date': df.index[0].strftime('%Y-%m-%d'),
    'end_date': df.index[-1].strftime('%Y-%m-%d'),
    # ... 其他字段 ...
}
```

在INSERT语句中包含stock_name并更新：
```python
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
        file_size_str = excluded.file_size_str,
        stock_name = excluded.stock_name  # ✅ 更新stock_name
''', (
    record['stock_code'], record['stock_name'], record['start_date'], 
    # ... 其他参数 ...
))
```

#### 步骤5：注册板块路由 ⚠️

**文件：** `backend/api/__init__.py`

在文件中添加板块路由注册：

```python
from api.sector import router as sector_router

# ... 其他代码 ...

# 在api_router定义之后添加
api_router.include_router(sector_router, prefix="/api/v1")
```

---

## 数据流程说明

### 正常流程（使用已下载数据）

```
1. 用户打开行情页面
   ↓
2. Market组件调用 stockService.getStockList()
   ↓
3. stockService 默认传递 use_local=true
   ↓
4. 后端 stocks API 接收到 use_local=true
   ↓
5. 使用 DuckDBStorageService.get_downloaded_data_list()
   ↓
6. 从DuckDB读取已下载的数据记录
   ↓
7. 对每条记录加载K线数据
   ↓
8. 使用最新数据作为价格信息
   ↓
9. 返回给前端显示
```

### 备用流程（使用远程数据）

```
1. 用户选择"远程数据"
   ↓
2. stockService.getStockList({ use_local: false })
   ↓
3. 后端 stocks API 接收到 use_local=false
   ↓
4. 调用 market_service.data_fetcher.get_stock_list()
   ↓
5. 从远程API获取实时数据
   ↓
6. 返回给前端显示
```

---

## 测试验证

### 测试1：验证使用本地数据

```bash
# 1. 确保已下载一些数据
# 访问 http://localhost:3000/data-download 下载数据

# 2. 打开行情页面
# 访问 http://localhost:3000/market

# 3. 检查网络请求
# 打开浏览器开发者工具 -> Network
# 查看 /api/v1/stocks 请求
# 确认参数中包含 use_local=true

# 4. 验证显示的数据
# 确认显示的是已下载的股票
# 确认股票名称正确显示（非"未知"）
```

### 测试2：验证板块功能

```bash
# 1. 测试板块API
curl http://localhost:8000/api/v1/sector/list

# 2. 打开行情页面
# 验证板块下拉框是否正确加载
# 验证板块选项是否为动态加载

# 3. 选择板块（可选）
# 验证筛选功能（需要后端实现板块筛选逻辑）
```

### 测试3：验证数据源切换

```bash
# 1. 切换到"本地数据"
# 验证显示已下载的数据

# 2. 切换到"远程数据"
# 验证显示远程API的数据
# 注意：远程数据可能包含所有股票，不限于已下载的
```

---

## 常见问题

### Q1: 为什么行情页面显示的数据和下载的不一致？

**A:** 可能的原因：
1. 没有传递 `use_local=true` 参数
2. 后端 `use_local` 参数默认值不是 `true`
3. DuckDB中没有数据

**解决方法：**
- 确认前端 stockService 默认设置 `use_local=true`
- 确认后端 stocks API 中 `use_local` 默认值为 `True`
- 检查 DuckDB 数据库中是否有数据

### Q2: 股票名称显示"未知"怎么办？

**A:** 需要应用股票名称修复：
1. 使用 `data_download_service_fixed.py` 替换原文件
2. 修改 `duckdb_storage_service.py` 添加 `stock_name` 参数
3. 重新下载数据

### Q3: 板块功能不生效？

**A:** 检查：
1. 后端是否注册了板块路由（`backend/api/__init__.py`）
2. 前端是否正确导入并使用 `sectorService`
3. API文档中是否有板块相关的接口（`http://localhost:8000/docs`）

### Q4: 如何切换使用远程数据？

**A:** 在Market页面中添加数据源切换选项，或者临时修改：
```typescript
stockService.getStockList({ use_local: false })
```

---

## 文件清单

### 已修改的文件

1. ✅ `frontend/src/services/stock.ts` - 添加use_local参数

### 已创建的文件

1. ✅ `backend/api/sector.py` - 板块API
2. ✅ `frontend/src/services/sector.ts` - 板块服务
3. ✅ `MARKET_DATA_SOURCE_UPDATE.md` - 本更新指南

### 需要修改的文件

1. ⚠️ `frontend/src/pages/Market.tsx` - 使用动态板块
2. ⚠️ `backend/services/data_download_service.py` - 应用修复
3. ⚠️ `backend/services/duckdb_storage_service.py` - 添加stock_name参数
4. ⚠️ `backend/api/__init__.py` - 注册板块路由

---

## 部署步骤

### 1. 备份文件

```bash
cd /Users/zbf/ws/stock

cp frontend/src/pages/Market.tsx frontend/src/pages/Market.tsx.backup
cp backend/services/data_download_service.py backend/services/data_download_service.py.backup
cp backend/services/duckdb_storage_service.py backend/services/duckdb_storage_service.py.backup
cp backend/api/__init__.py backend/api/__init__.py.backup
```

### 2. 应用修复

```bash
# 应用下载服务修复
cp backend/services/data_download_service_fixed.py backend/services/data_download_service.py

# 或者手动修改其他文件（参考上面的步骤）
```

### 3. 注册板块路由

编辑 `backend/api/__init__.py`，添加：
```python
from api.sector import router as sector_router

# 在api_router定义之后添加
api_router.include_router(sector_router, prefix="/api/v1")
```

### 4. 修改Market页面

编辑 `frontend/src/pages/Market.tsx`，应用修改步骤中的代码。

### 5. 重启服务

```bash
./stop_all.sh
./start_all.sh
```

### 6. 验证

访问以下URL：
- http://localhost:3000/market - 行情页面
- http://localhost:8000/docs - API文档

---

## 回滚方案

如果出现问题，快速回滚：

```bash
# 恢复备份
cp frontend/src/pages/Market.tsx.backup frontend/src/pages/Market.tsx
cp backend/services/data_download_service.py.backup backend/services/data_download_service.py
cp backend/services/duckdb_storage_service.py.backup backend/services/duckdb_storage_service.py
cp backend/api/__init__.py.backup backend/api/__init__.py

# 恢复stock服务（如果需要）
git checkout frontend/src/services/stock.ts

# 重启服务
./restart_all.sh
```

---

## 总结

### 核心改进

1. ✅ **前端默认使用本地数据** - `use_local=true` 默认值
2. ✅ **后端支持两种数据源** - 本地数据 vs 远程数据
3. ✅ **添加板块API** - 动态板块列表
4. ✅ **股票名称修复** - 使用stock_list获取名称

### 用户体验提升

- ✅ 行情页面显示已下载的数据
- ✅ 股票名称正确显示
- ✅ 支持板块筛选
- ✅ 可切换数据源

### 技术改进

- ✅ 数据源灵活切换
- ✅ 本地数据优先
- ✅ 减少不必要的网络请求
- ✅ 更好的数据管理

---

## 相关文档

- `MARKET_FIX_IMPLEMENTATION_GUIDE.md` - 完整实施指南
- `MARKET_FIX_PROPOSAL.md` - 原始修复方案
- `PORT_OCCUPATION_FIX_REPORT.md` - 端口占用修复
- `DATA_DOWNLOAD_ERROR_FIX_REPORT.md` - 数据下载修复

---

**最后更新：** 2026-02-16
**版本：** v1.0