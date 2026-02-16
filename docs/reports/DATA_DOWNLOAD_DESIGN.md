# 数据下载与回测分离设计文档

**设计日期**: 2026-02-15
**设计者**: Cline AI Assistant

---

## 📋 需求分析

### 当前问题
1. 回测功能和下载数据功能耦合在一起
2. 每次回测都会重新下载数据，效率低下
3. 无法控制数据下载时机
4. 缺少数据去重机制

### 新需求
1. **数据下载与回测分离**
   - 创建独立的数据下载功能
   - 回测只使用已下载的数据
   - 回测前检查数据是否存在

2. **新增数据下载页面**
   - 支持选择股票代码
   - 支持选择日期范围
   - 支持选择数据频率
   - 显示下载进度

3. **数据去重机制**
   - 检查数据是否已存在
   - 只下载缺失的数据
   - 支持增量更新

---

## 🏗️ 架构设计

### 1. 数据流程

```
用户请求下载
    ↓
检查数据是否已存在
    ↓
├─ 已存在 → 返回已有数据
└─ 不存在 → 从数据源下载 → 保存到数据库
    ↓
返回下载结果
```

### 2. 回测流程

```
用户请求回测
    ↓
检查数据是否已下载
    ↓
├─ 未下载 → 提示先下载数据
└─ 已下载 → 执行回测
    ↓
返回回测结果
```

### 3. 数据存储结构

```sql
-- 已下载数据表
CREATE TABLE downloaded_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    frequency VARCHAR(10) NOT NULL,
    data_count INTEGER NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(20),
    file_path VARCHAR(255),
    
    -- 唯一约束：同一股票、日期范围、频率只允许一条记录
    UNIQUE(stock_code, start_date, end_date, frequency)
);
```

### 4. 数据去重逻辑

**检查规则**：
1. 检查数据库中是否存在相同的数据
   - 股票代码相同
   - 日期范围相同或包含
   - 频率相同

2. 去重策略：
   - 完全匹配：直接返回已有数据
   - 部分重叠：提示用户选择
   - 无重叠：下载新数据

**判断逻辑**：
```python
def check_data_overlap(existing_data, new_start, new_end):
    """
    检查数据重叠
    
    返回:
    - 'none': 无重叠，可以下载
    - 'exact': 完全匹配，使用已有数据
    - 'partial': 部分重叠，提示用户
    """
    if existing_data.start_date <= new_start and existing_data.end_date >= new_end:
        return 'exact'
    elif existing_data.end_date < new_start or existing_data.start_date > new_end:
        return 'none'
    else:
        return 'partial'
```

---

## 🔧 技术实现

### 后端实现

#### 1. 数据下载服务

**文件**: `backend/services/data_download_service.py`

**核心功能**：
- `download_data()` - 下载数据
- `check_data_exists()` - 检查数据是否存在
- `get_downloaded_data_list()` - 获取已下载数据列表
- `delete_downloaded_data()` - 删除已下载数据

#### 2. 数据存储服务

**文件**: `backend/services/data_storage_service.py`

**核心功能**：
- `save_to_database()` - 保存到数据库
- `load_from_database()` - 从数据库加载
- `delete_from_database()` - 从数据库删除

#### 3. 修改回测服务

**文件**: `backend/services/backtest_service.py`

**修改内容**：
- 移除数据获取逻辑
- 添加数据依赖检查
- 使用已下载的数据执行回测

#### 4. 数据下载API

**文件**: `backend/api/data_download.py`

**API端点**：
- `POST /api/v1/data/download` - 下载股票数据
- `GET /api/v1/data/downloads` - 获取已下载数据列表
- `DELETE /api/v1/data/downloads/{id}` - 删除已下载数据
- `GET /api/v1/data/check` - 检查数据是否存在

### 前端实现

#### 1. 数据下载页面

**文件**: `frontend/src/pages/DataDownload.tsx`

**核心功能**：
- 股票选择器
- 日期范围选择器
- 频率选择器
- 下载按钮
- 进度显示
- 已下载数据列表

#### 2. 修改回测页面

**文件**: `frontend/src/pages/Strategies.tsx`

**修改内容**：
- 添加数据依赖检查
- 显示数据状态
- 引导用户下载数据
- 禁用未下载数据的回测

---

## 📊 数据流程图

```
用户操作流程：
1. 访问数据下载页面
2. 选择股票、日期范围、频率
3. 点击下载按钮
4. 系统检查数据是否存在
   ├─ 已存在 → 提示使用已有数据
   └─ 不存在 → 下载数据并保存
5. 下载完成，显示在列表中

回测操作流程：
1. 访问策略页面
2. 选择策略和参数
3. 点击回测按钮
4. 系统检查数据是否已下载
   ├─ 未下载 → 提示先下载数据，跳转到下载页面
   └─ 已下载 → 执行回测，显示结果
```

---

## 🎯 实施计划

### Phase 1: 后端基础（优先级：高）

1. 创建数据下载服务
   - [ ] 实现 `data_download_service.py`
   - [ ] 实现数据去重逻辑
   - [ ] 实现进度跟踪

2. 创建数据存储服务
   - [ ] 实现 `data_storage_service.py`
   - [ ] 创建数据库表
   - [ ] 实现数据读写

3. 修改回测服务
   - [ ] 移除数据获取逻辑
   - [ ] 添加数据依赖检查
   - [ ] 使用存储的数据

### Phase 2: 后端API（优先级：高）

1. 创建数据下载API
   - [ ] 实现 `api/data_download.py`
   - [ ] 添加下载端点
   - [ ] 添加查询端点
   - [ ] 添加删除端点

2. 注册路由
   - [ ] 更新 `api/__init__.py`
   - [ ] 测试API端点

### Phase 3: 前端页面（优先级：中）

1. 创建数据下载页面
   - [ ] 实现 `DataDownload.tsx`
   - [ ] 添加表单组件
   - [ ] 添加列表组件
   - [ ] 添加进度显示

2. 修改回测页面
   - [ ] 更新 `Strategies.tsx`
   - [ ] 添加数据检查
   - [ ] 添加提示信息

### Phase 4: 测试与文档（优先级：中）

1. 测试
   - [ ] 测试数据下载
   - [ ] 测试数据去重
   - [ ] 测试回测依赖

2. 文档
   - [ ] 更新API文档
   - [ ] 更新使用指南
   - [ ] 更新README

---

## 💡 关键技术点

### 1. 数据去重算法

```python
async def check_and_download(
    self,
    stock_code: str,
    start_date: datetime,
    end_date: datetime,
    frequency: str
) -> Dict:
    """
    检查并下载数据
    
    Returns:
        {
            'status': 'exists' | 'downloading' | 'completed',
            'message': str,
            'data': DataFrame | None
        }
    """
    # 检查是否存在
    existing = await self.storage.get_downloaded_data(
        stock_code, start_date, end_date, frequency
    )
    
    if existing:
        overlap = self._check_overlap(existing, start_date, end_date)
        if overlap == 'exact':
            # 完全匹配，直接返回
            data = await self.storage.load_data(existing.file_path)
            return {
                'status': 'exists',
                'message': '数据已存在，使用已有数据',
                'data': data
            }
        elif overlap == 'partial':
            # 部分重叠，提示用户
            return {
                'status': 'partial_overlap',
                'message': '数据部分重叠，请调整日期范围'
            }
    
    # 不存在，开始下载
    return await self._download_data(stock_code, start_date, end_date, frequency)
```

### 2. 数据存储格式

**选项1: SQLite数据库**
- 优点：轻量级，易于管理
- 缺点：不适合大量数据
- 适用：开发和小规模使用

**选项2: Parquet文件**
- 优点：压缩率高，读取快
- 缺点：需要额外存储
- 适用：中规模使用

**选项3: PostgreSQL**
- 优点：可扩展，支持并发
- 缺点：配置复杂
- 适用：生产环境

**建议**：初期使用Parquet文件，后期可迁移到PostgreSQL

### 3. 进度跟踪

```python
class DownloadProgress:
    """下载进度跟踪"""
    
    def __init__(self, download_id: str):
        self.download_id = download_id
        self.total = 0
        self.downloaded = 0
        self.status = 'pending'
        self.error = None
        self.start_time = datetime.now()
        
    def update(self, downloaded: int, total: int):
        """更新进度"""
        self.downloaded = downloaded
        self.total = total
        self.status = 'downloading'
        
    def complete(self):
        """完成下载"""
        self.status = 'completed'
        self.downloaded = self.total
        
    def failed(self, error: str):
        """下载失败"""
        self.status = 'failed'
        self.error = error
```

---

## 📝 API设计

### 数据下载API

#### POST /api/v1/data/download

**请求**：
```json
{
  "stock_code": "600771.SH",
  "start_date": "2025-01-01",
  "end_date": "2026-01-01",
  "frequency": "daily"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "下载成功",
  "data": {
    "download_id": "download_123456",
    "stock_code": "600771.SH",
    "data_count": 252,
    "status": "completed"
  }
}
```

#### GET /api/v1/data/check

**请求参数**：
- `stock_code`: 股票代码
- `start_date`: 开始日期
- `end_date`: 结束日期
- `frequency`: 频率

**响应**：
```json
{
  "code": 200,
  "message": "检查完成",
  "data": {
    "exists": true,
    "overlap_type": "exact",
    "downloaded_at": "2026-02-15T00:00:00Z",
    "data_count": 252
  }
}
```

#### GET /api/v1/data/downloads

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "downloads": [
      {
        "id": 1,
        "stock_code": "600771.SH",
        "stock_name": "东威精密",
        "start_date": "2025-01-01",
        "end_date": "2026-01-01",
        "frequency": "daily",
        "data_count": 252,
        "downloaded_at": "2026-02-15T00:00:00Z",
        "file_size": "256KB"
      }
    ],
    "total": 1
  }
}
```

---

## 🎨 前端页面设计

### 数据下载页面布局

```
┌─────────────────────────────────────────────────┐
│  数据下载                                │
├─────────────────────────────────────────────────┤
│                                         │
│  股票代码: [_______] [搜索]            │
│                                         │
│  日期范围:                               │
│    开始: [2025-01-01]                  │
│    结束: [2026-01-01]                  │
│                                         │
│  数据频率: [日线 ▼]                      │
│  数据源: [自动 ▼]                        │
│                                         │
│  [下载] [批量下载]                       │
│                                         │
├─────────────────────────────────────────────────┤
│  已下载数据                              │
├─────────────────────────────────────────────────┤
│  股票代码  |  日期范围     |  频率   │
│  600771.SH | 2025-01-01  | 日线       │
│            ~ 2026-01-01               │
│                                         │
│  000001.SZ | 2025-01-01  | 日线       │
│            ~ 2026-01-01               │
│                                         │
└─────────────────────────────────────────────────┘
```

---

## 🔄 向后兼容

### 数据获取器兼容

保留 `DataFetcher` 类，用于：
1. 实时行情获取
2. 股票列表获取
3. 股票搜索功能

### 回测服务兼容

添加新接口，保留旧接口：
```python
class BacktestEngine:
    async def run_backtest_with_data(
        self,
        data: pd.DataFrame,
        strategy_params: Dict
    ) -> Dict:
        """
        使用已有数据运行回测（新接口）
        """
        # 直接使用传入的数据
        pass
    
    async def run_backtest(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        # ... 其他参数
    ) -> Dict:
        """
        自动获取数据并运行回测（旧接口，保持兼容）
        """
        # 自动下载数据（如果需要）
        # 运行回测
        pass
```

---

## 📊 预期效果

### 用户体验提升

1. **明确的操作流程**
   - 先下载数据 → 再进行回测
   - 清晰的状态提示
   - 减少等待时间

2. **数据管理能力**
   - 查看已下载数据
   - 删除不需要的数据
   - 管理磁盘空间

3. **避免重复下载**
   - 自动检测数据是否存在
   - 智能去重
   - 节省时间和带宽

### 性能提升

1. **减少网络请求**
   - 相同数据只下载一次
   - 支持增量更新

2. **提高回测速度**
   - 使用本地数据
   - 无需等待下载
   - 可以快速迭代测试

---

**文档版本**: v1.0
**最后更新**: 2026-02-15