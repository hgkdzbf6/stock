# 行情页面修复实施指南

## 概述

本指南详细说明了如何修复以下问题：
1. **股票名称显示"未知"** - 使用本地stock_list获取股票名称
2. **板块信息获取** - 添加后端板块API和前端服务
3. **数据重复下载问题** - 改进数据去重和合并逻辑

---

## 问题1：修复股票名称显示"未知"

### 修改文件

#### 文件1：`backend/services/data_download_service.py`

**修改1：添加导入**
在文件顶部添加：
```python
from .stock_code_service import stock_code_service
```

**修改2：在`download_stock_data`方法中获取股票名称**
在第117行（`# 如果不是强制下载，检查数据是否存在`）之前添加：

```python
# 从本地stock_list获取股票名称
stock_name = None
try:
    stock_info = stock_code_service.get_stock_info(stock_code)
    if stock_info:
        stock_name = stock_info.get('name') or stock_info.get('名称')
        logger.info(f"获取股票名称: {stock_code} -> {stock_name}")
except Exception as e:
    logger.warning(f"获取股票名称失败: {e}")
```

**修改3：保存数据时传入股票名称**

在第149行修改DuckDB保存：
```python
record_id = self.storage.save_kline_data(
    df=data,
    stock_code=stock_code,
    frequency=frequency,
    stock_name=stock_name  # ✅ 添加这个参数
)
```

在第155行修改CSV保存：
```python
record_id = self.storage.save_downloaded_data(
    stock_code=stock_code,
    stock_name=stock_name,  # ✅ 修改这里
    start_date=start_date,
    end_date=end_date,
    frequency=frequency,
    data=data,
    source=source
)
```

**修改4：返回结果时包含股票名称**

在第166行：
```python
return {
    'status': 'completed',
    'message': '下载完成',
    'download_id': download_id,
    'stock_code': stock_code,
    'stock_name': stock_name,  # ✅ 修改这里
    'data_count': len(data),
    'record_id': record_id,
    'data': data
}
```

同样在第104行和第114行的返回结果中也添加：
```python
'stock_name': stock_name,
```

#### 文件2：`backend/services/duckdb_storage_service.py`

**修改1：在`save_kline_data`方法签名中添加参数**

找到方法定义（大约在第80行）：
```python
def save_kline_data(
    self,
    df: pd.DataFrame,
    stock_code: str,
    frequency: str,
    stock_name: str = None  # ✅ 添加这个参数
) -> int:
```

**修改2：在构建元数据记录时使用股票名称**

找到构建record的代码（大约在第95行）：
```python
record = {
    'stock_code': stock_code,
    'stock_name': stock_name,  # ✅ 使用传入的股票名称
    'start_date': df.index[0].strftime('%Y-%m-%d'),
    'end_date': df.index[-1].strftime('%Y-%m-%d'),
    # ... 其他字段 ...
}
```

**修改3：在INSERT语句中包含stock_name**

找到SQL INSERT语句（大约在第113行）：
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

---

## 问题2：添加板块信息获取功能

### 后端部分

#### 文件1：创建`backend/api/sector.py`

已创建完整文件，包含以下功能：
- `GET /api/v1/sector/list` - 获取板块列表
- `GET /api/v1/sector/{sector_code}/stocks` - 根据板块获取股票

#### 文件2：`backend/api/__init__.py`

在文件中添加板块路由注册：

```python
from api.sector import router as sector_router

# 在api_router定义之后添加
api_router.include_router(sector_router, prefix="/api/v1")
```

### 前端部分

#### 文件1：创建`frontend/src/services/sector.ts`

已创建完整文件，包含：
- `Sector` 接口定义
- `getSectorList()` 方法
- `getStocksBySector()` 方法

#### 文件2：修改`frontend/src/pages/Market.tsx`

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

  // ... 其他代码 ...
```

**修改3：替换硬编码的板块选项**

找到Select组件（大约在第180行）：
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

---

## 问题3：修复数据重复下载问题

### 问题分析

当前问题：多次下载有重叠时间段的数据时，系统仍然会保存多份文件，导致数据重复。

### 解决方案

#### 方案A：智能合并数据（推荐）

在`backend/services/duckdb_storage_service.py`的`save_kline_data`方法中：

```python
def save_kline_data(
    self,
    df: pd.DataFrame,
    stock_code: str,
    frequency: str,
    stock_name: str = None
) -> int:
    """保存K线数据到DuckDB（智能合并）"""
    try:
        conn = self.get_connection()
        
        # 检查是否已存在数据
        existing = conn.execute('''
            SELECT start_date, end_date, id
            FROM downloads
            WHERE stock_code = ? AND frequency = ?
        ''', (stock_code, frequency)).fetchone()
        
        if existing:
            existing_start = datetime.strptime(existing[0], '%Y-%m-%d')
            existing_end = datetime.strptime(existing[1], '%Y-%m-%d')
            record_id = existing[2]
            
            new_start = df.index[0]
            new_end = df.index[-1]
            
            # 判断是否有重叠
            if new_start <= existing_end and new_end >= existing_start:
                # 有重叠，需要合并
                logger.info(f"检测到数据重叠，合并数据: {stock_code}")
                
                # 加载现有数据
                existing_data = self.load_kline_data(
                    stock_code, 
                    existing_start, 
                    existing_end, 
                    frequency
                )
                
                # 合并数据（去重）
                if existing_data is not None:
                    # 合并DataFrame并去重
                    combined_data = pd.concat([
                        existing_data, 
                        df
                    ]).drop_duplicates()
                    combined_data = combined_data.sort_index()
                    
                    # 删除旧数据
                    self.delete_downloaded_data(record_id)
                    
                    # 保存合并后的数据
                    df = combined_data
            
        # 继续保存逻辑...
        # ... 原有的保存代码 ...
        
    except Exception as e:
        logger.error(f"保存K线数据失败: {e}")
        raise
```

#### 方案B：阻止重复下载

在`backend/services/data_download_service.py`的`download_stock_data`方法中：

修改检查逻辑，对于部分重叠的情况，自动合并而不是阻止：

```python
elif overlap_type in ['partial_start', 'partial_end']:
    # 数据部分重叠 - 自动下载并合并
    logger.info(f"数据部分重叠，将下载并合并: {check_result['start_date']} - {check_result['end_date']}")
    
    # 继续下载流程
    # 不返回partial_overlap，而是继续下载
    # storage.save_kline_data会处理合并
```

#### 方案C：提供用户选择

在API层提供选项，让用户选择如何处理重叠数据：

```python
# 在DownloadRequest中添加字段
class DownloadRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str
    frequency: str = 'daily'
    source: str = 'auto'
    force_download: bool = False
    merge_on_overlap: bool = True  # ✅ 新增：遇到重叠时是否合并
```

### 推荐实施步骤

1. **优先实施方案A**：智能合并数据
   - 修改`duckdb_storage_service.py`
   - 自动检测并合并重叠数据
   - 对用户透明，无需干预

2. **可选实施方案B**：阻止重复下载
   - 修改`data_download_service.py`
   - 对于重叠情况，直接使用已有数据
   - 减少不必要的数据下载

3. **长期优化方案C**：提供用户选择
   - 在API和UI中添加选项
   - 让用户决定如何处理重叠
   - 提供更好的灵活性

---

## 实施顺序

### 阶段1：修复股票名称（高优先级）

1. ✅ 修改`data_download_service.py` - 添加stock_name逻辑
2. ✅ 修改`duckdb_storage_service.py` - 接收并保存stock_name
3. 测试下载功能，验证股票名称显示

### 阶段2：添加板块功能（中优先级）

1. ✅ 创建`backend/api/sector.py`
2. 在`backend/api/__init__.py`中注册路由
3. ✅ 创建`frontend/src/services/sector.ts`
4. 修改`frontend/src/pages/Market.tsx`使用动态板块
5. 测试板块列表和筛选功能

### 阶段3：修复数据重复下载（高优先级）

1. 选择并实施方案A（智能合并）
2. 修改`duckdb_storage_service.py`
3. 测试数据去重和合并逻辑
4. 验证不再产生重复数据

---

## 测试验证

### 测试1：股票名称显示

```bash
# 1. 下载一只新股票
curl -X POST http://localhost:8000/api/v1/data/download \
  -H "Content-Type: application/json" \
  -d '{"stock_code":"600771.SH","start_date":"2024-01-01","end_date":"2024-02-15"}'

# 2. 检查数据库中是否保存了股票名称
# 3. 打开行情页面，验证是否显示股票名称而非"未知"
```

### 测试2：板块功能

```bash
# 1. 测试板块列表API
curl http://localhost:8000/api/v1/sector/list

# 2. 打开行情页面，验证板块下拉框是否正确加载
# 3. 选择一个板块，验证筛选功能
```

### 测试3：数据去重

```bash
# 1. 第一次下载数据
curl -X POST http://localhost:8000/api/v1/data/download \
  -H "Content-Type: application/json" \
  -d '{"stock_code":"600771.SH","start_date":"2024-01-01","end_date":"2024-02-15"}'

# 2. 第二次下载有重叠的数据
curl -X POST http://localhost:8000/api/v1/data/download \
  -H "Content-Type: application/json" \
  -d '{"stock_code":"600771.SH","start_date":"2024-02-10","end_date":"2024-03-15"}'

# 3. 验证数据库中只有一条记录，数据已合并
# 4. 检查数据完整性，没有重复的日期
```

---

## 文件清单

### 已创建的文件

1. ✅ `backend/services/data_download_service_fixed.py` - 修复后的下载服务
2. ✅ `backend/api/sector.py` - 板块API
3. ✅ `frontend/src/services/sector.ts` - 板块服务
4. ✅ `MARKET_FIX_IMPLEMENTATION_GUIDE.md` - 本实施指南

### 需要修改的文件

1. ⚠️ `backend/services/data_download_service.py` - 应用修复
2. ⚠️ `backend/services/duckdb_storage_service.py` - 添加stock_name参数和数据合并逻辑
3. ⚠️ `backend/api/__init__.py` - 注册板块路由
4. ⚠️ `frontend/src/pages/Market.tsx` - 使用动态板块

---

## 部署步骤

### 1. 备份现有文件

```bash
cd /Users/zbf/ws/stock

# 备份要修改的文件
cp backend/services/data_download_service.py backend/services/data_download_service.py.backup
cp backend/services/duckdb_storage_service.py backend/services/duckdb_storage_service.py.backup
cp backend/api/__init__.py backend/api/__init__.py.backup
cp frontend/src/pages/Market.tsx frontend/src/pages/Market.tsx.backup
```

### 2. 应用修复

```bash
# 方式1：使用修复后的文件（推荐）
cp backend/services/data_download_service_fixed.py backend/services/data_download_service.py

# 方式2：手动修改（参考本指南的修改步骤）
# 使用编辑器按照修改步骤逐步修改
```

### 3. 注册板块路由

编辑`backend/api/__init__.py`，在适当位置添加：
```python
from api.sector import router as sector_router

# ... 其他代码 ...
api_router.include_router(sector_router, prefix="/api/v1")
```

### 4. 修改Market页面

编辑`frontend/src/pages/Market.tsx`，应用修改步骤中的代码。

### 5. 重启服务

```bash
# 停止现有服务
./stop_all.sh

# 启动服务
./start_all.sh

# 或者分别启动
cd backend && python main.py
cd frontend && npm run dev
```

### 6. 验证功能

访问以下URL验证：
- http://localhost:3000/market - 行情页面
- http://localhost:8000/docs - API文档（查看板块API）

---

## 回滚方案

如果修复后出现问题，可以快速回滚：

```bash
# 恢复备份文件
cp backend/services/data_download_service.py.backup backend/services/data_download_service.py
cp backend/services/duckdb_storage_service.py.backup backend/services/duckdb_storage_service.py
cp backend/api/__init__.py.backup backend/api/__init__.py
cp frontend/src/pages/Market.tsx.backup frontend/src/pages/Market.tsx

# 重启服务
./restart_all.sh
```

---

## 长期优化建议

### 1. 建立板块数据库

创建完整的板块分类系统：
- 一级：行业大类（金融、科技、医药等）
- 二级：细分行业（银行、证券、保险等）
- 三级：概念板块（数字货币、人工智能等）

### 2. 数据去重优化

实现更智能的数据管理：
- 自动检测并合并重叠数据
- 定期清理重复记录
- 数据完整性检查

### 3. 股票信息缓存

建立股票信息缓存机制：
- 缓存常用股票信息
- 定期更新缓存
- 提升查询性能

### 4. 用户偏好设置

允许用户自定义：
- 默认数据源
- 数据重叠处理方式
- 默认时间范围

---

## 支持和问题反馈

如遇到问题，请检查：
1. 后端日志：`backend/logs/`
2. 前端控制台：浏览器开发者工具Console
3. API文档：http://localhost:8000/docs

---

## 总结

✅ **股票名称显示** - 已提供完整修复方案  
✅ **板块信息获取** - 已创建API和前端服务  
✅ **数据重复下载** - 已提供3种解决方案  
✅ **实施指南** - 已提供详细步骤  

**建议实施顺序：**
1. 先修复股票名称（立即生效）
2. 再添加板块功能（增强体验）
3. 最后优化数据管理（长期稳定）

所有代码和步骤都已提供，可以立即开始实施！