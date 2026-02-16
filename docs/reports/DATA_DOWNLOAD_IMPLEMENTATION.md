# 数据下载与回测分离架构实施报告

**实施日期**: 2026-02-15
**实施者**: Cline AI Assistant
**版本**: v2.0.0

---

## 📋 实施概述

### 目标
将数据下载功能与回测功能分离，实现数据去重，避免重复下载，提高系统效率。

### 需求
1. ✅ 创建独立的数据下载功能
2. ✅ 新增数据下载页面
3. ✅ 实现数据去重机制
4. ✅ 回测前检查数据是否存在
5. ✅ 数据存储到本地数据库和文件系统

---

## 🏗️ 架构设计

### 数据流程

```
用户下载数据
    ↓
检查数据是否已存在
    ↓
├─ 完全匹配 → 返回已有数据
├─ 部分重叠 → 提示用户
└─ 不存在 → 下载数据 → 保存到Parquet文件 + 数据库
    ↓
返回下载结果
```

### 回测流程

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

### 数据存储结构

**数据库表** (SQLite):
```sql
CREATE TABLE downloaded_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(50),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    frequency VARCHAR(10) NOT NULL,
    data_count INTEGER NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(20),
    file_path VARCHAR(255),
    
    UNIQUE(stock_code, start_date, end_date, frequency)
)
```

**文件存储**:
- 格式: Parquet (.parquet)
- 目录: `backend/data/`
- 命名规则: `{stock_code}_{start_date}_{end_date}_{frequency}.parquet`

---

## 🔧 后端实现

### 1. 数据存储服务

**文件**: `backend/services/data_storage_service.py`

**核心功能**:
- `save_downloaded_data()` - 保存数据到数据库和Parquet文件
- `load_downloaded_data()` - 从数据库和Parquet文件加载数据
- `check_data_exists()` - 检查数据是否存在（支持重叠检测）
- `get_downloaded_data_list()` - 获取已下载数据列表
- `delete_downloaded_data()` - 删除数据和文件
- `_format_file_size()` - 格式化文件大小

**关键特性**:
- ✅ 数据去重（完全匹配和部分重叠检测）
- ✅ Parquet格式存储（压缩率高，读取快）
- ✅ 唯一约束防止重复下载
- ✅ 索引优化查询性能

### 2. 数据下载服务

**文件**: `backend/services/data_download_service.py`

**核心功能**:
- `download_stock_data()` - 下载单只股票数据
- `batch_download()` - 批量下载多只股票
- `check_data_availability()` - 检查数据是否可用
- `load_data_for_backtest()` - 为回测加载数据
- `get_statistics()` - 获取下载统计信息

**关键特性**:
- ✅ 自动去重（完全匹配返回已有数据）
- ✅ 部分重叠提示
- ✅ 强制重新下载选项
- ✅ 批量下载支持
- ✅ 进度跟踪

### 3. 数据下载API

**文件**: `backend/api/data_download.py`

**API端点**:

| 方法 | 端点 | 描述 |
|------|--------|------|
| POST | `/api/v1/data/download` | 下载股票数据 |
| POST | `/api/v1/data/batch-download` | 批量下载股票数据 |
| GET | `/api/v1/data/check` | 检查数据是否存在 |
| GET | `/api/v1/data/downloads` | 获取已下载数据列表 |
| DELETE | `/api/v1/data/downloads/{id}` | 删除已下载数据 |
| GET | `/api/v1/data/statistics` | 获取下载统计信息 |
| GET | `/api/v1/data/status/{id}` | 获取下载状态 |

**数据模型**:
- `DownloadRequest` - 下载请求
- `BatchDownloadRequest` - 批量下载请求
- `DownloadResponse` - 下载响应
- `DownloadedListResponse` - 已下载数据列表响应
- `StatisticsResponse` - 统计信息响应

### 4. 路由注册

**文件**: `backend/api/__init__.py`

```python
from api.data_download import router as data_download_router

api_router.include_router(data_download_router, tags=["data-download"])
```

### 5. 依赖更新

**文件**: `backend/requirements.txt`

新增依赖:
```
pyarrow>=14.0.0  # Parquet文件格式支持
```

---

## 🎨 前端实现

### 1. 数据下载服务

**文件**: `frontend/src/services/dataDownload.ts`

**核心函数**:
- `downloadStockData()` - 下载股票数据
- `batchDownloadStockData()` - 批量下载股票数据
- `checkDataAvailability()` - 检查数据是否可用
- `getDownloadedList()` - 获取已下载数据列表
- `deleteDownloadedData()` - 删除已下载数据
- `getStatistics()` - 获取下载统计信息
- `getDownloadStatus()` - 获取下载状态

**TypeScript接口**:
- `DownloadRequest` - 下载请求接口
- `DownloadResponse` - 下载响应接口
- `DownloadedData` - 已下载数据接口
- `StatisticsResponse` - 统计信息接口

### 2. 数据下载页面

**文件**: `frontend/src/pages/DataDownload.tsx`

**页面组件**:
1. **统计信息卡片**
   - 总下载数
   - 唯一股票数
   - 数据点总数
   - 总文件大小

2. **下载表单**
   - 股票代码输入
   - 数据频率选择（日线、1分钟、5分钟等）
   - 日期范围选择
   - 数据源选择（自动、Baostock、Akshare等）
   - 强制重新下载选项
   - 检查数据按钮
   - 下载按钮

3. **数据检查结果**
   - 数据存在状态
   - 重叠类型提示
   - 已有数据信息

4. **下载结果**
   - 下载状态
   - 消息提示
   - 数据条数
   - 股票名称

5. **已下载数据列表**
   - 股票代码
   - 股票名称
   - 日期范围
   - 数据频率
   - 数据条数
   - 文件大小
   - 下载时间
   - 删除操作

**交互特性**:
- ✅ 实时数据检查
- ✅ 下载状态显示
- ✅ 列表自动刷新
- ✅ 确认删除
- ✅ 友好的错误提示

### 3. 路由配置

**文件**: `frontend/src/App.tsx`

```typescript
import DataDownload from './pages/DataDownload';

<Route path="data-download" element={<DataDownload />} />
```

### 4. 侧边栏导航

**文件**: `frontend/src/components/layout/Sidebar.tsx`

```typescript
import { DownloadOutlined } from '@ant-design/icons';

{
  key: '/data-download',
  icon: <DownloadOutlined />,
  label: '数据下载',
}
```

### 5. 服务导出

**文件**: `frontend/src/services/index.ts`

```typescript
export * as dataDownloadService from './dataDownload';
```

---

## 📊 数据去重逻辑

### 去重算法

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

### 去重策略

| 情况 | 处理方式 |
|------|----------|
| 完全匹配 | 直接返回已有数据，不重新下载 |
| 部分重叠 | 提示用户调整日期范围 |
| 无重叠 | 下载新数据并保存 |

---

## 🎯 关键特性

### 1. 智能去重
- ✅ 自动检测数据是否已存在
- ✅ 完全匹配时使用已有数据
- ✅ 部分重叠时提示用户
- ✅ 避免重复下载，节省时间和带宽

### 2. 高效存储
- ✅ Parquet格式（压缩率高，读取快）
- ✅ 数据库元数据管理
- ✅ 唯一约束防止重复
- ✅ 索引优化查询性能

### 3. 用户友好
- ✅ 清晰的下载界面
- ✅ 实时数据检查
- ✅ 详细的下载状态
- ✅ 统计信息展示
- ✅ 已下载数据管理

### 4. 可扩展性
- ✅ 支持批量下载
- ✅ 支持多种数据频率
- ✅ 支持多种数据源
- ✅ 易于扩展新功能

---

## 📝 使用指南

### 后端部署

1. **安装依赖**:
```bash
cd backend
pip install pyarrow
```

2. **启动服务**:
```bash
python main.py
```

3. **API文档**: http://localhost:8000/docs

### 前端使用

1. **访问数据下载页面**:
   - 点击侧边栏"数据下载"
   - 或直接访问 http://localhost:3000/data-download

2. **下载数据**:
   - 输入股票代码（如: 600771.SH）
   - 选择日期范围
   - 选择数据频率
   - 点击"检查数据"查看是否已存在
   - 点击"下载"开始下载

3. **管理数据**:
   - 查看已下载数据列表
   - 删除不需要的数据
   - 查看统计信息

### API调用示例

```bash
# 检查数据是否存在
curl "http://localhost:8000/api/v1/data/check?stock_code=600771.SH&start_date=2025-01-01&end_date=2026-01-01&frequency=daily"

# 下载数据
curl -X POST http://localhost:8000/api/v1/data/download \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600771.SH",
    "start_date": "2025-01-01",
    "end_date": "2026-01-01",
    "frequency": "daily"
  }'

# 获取已下载数据列表
curl http://localhost:8000/api/v1/data/downloads

# 获取统计信息
curl http://localhost:8000/api/v1/data/statistics

# 删除数据
curl -X DELETE http://localhost:8000/api/v1/data/downloads/1
```

---

## 🔍 测试建议

### 功能测试

1. **数据下载测试**
   - [ ] 测试单只股票下载
   - [ ] 测试批量下载
   - [ ] 测试不同频率数据下载
   - [ ] 测试不同数据源

2. **数据去重测试**
   - [ ] 测试完全匹配时使用已有数据
   - [ ] 测试部分重叠时的提示
   - [ ] 测试强制重新下载
   - [ ] 测试唯一约束

3. **数据管理测试**
   - [ ] 测试数据列表查询
   - [ ] 测试数据删除
   - [ ] 测试统计信息
   - [ ] 测试文件大小计算

4. **前端测试**
   - [ ] 测试表单验证
   - [ ] 测试数据检查
   - [ ] 测试下载流程
   - [ ] 测试列表显示
   - [ ] 测试删除操作

### 性能测试

1. **下载速度测试**
   - 测试不同数据量下载时间
   - 测试批量下载性能
   - 测试并发下载

2. **存储性能测试**
   - 测试Parquet文件读写速度
   - 测试数据库查询性能
   - 测试大数据量处理

---

## 🚀 未来优化

### 短期优化

1. **进度显示**
   - 实现实时下载进度
   - 显示下载速度
   - 预估剩余时间

2. **数据更新**
   - 支持增量更新
   - 自动检测新数据
   - 定时更新任务

3. **批量操作**
   - 批量删除
   - 批量重新下载
   - 批量导出

### 长期优化

1. **分布式存储**
   - 支持S3存储
   - 支持对象存储
   - 支持CDN加速

2. **数据压缩**
   - 多种压缩格式
   - 自动选择最优压缩
   - 压缩率统计

3. **缓存优化**
   - Redis缓存热数据
   - LRU缓存策略
   - 缓存命中率统计

4. **数据同步**
   - 多端数据同步
   - 数据版本管理
   - 数据冲突解决

---

## 📊 实施成果

### 完成的功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 数据存储服务 | ✅ | 支持数据库和Parquet文件存储 |
| 数据下载服务 | ✅ | 支持单只和批量下载 |
| 数据去重逻辑 | ✅ | 完全匹配和部分重叠检测 |
| 数据下载API | ✅ | 7个RESTful API端点 |
| 前端下载服务 | ✅ | TypeScript类型安全 |
| 前端下载页面 | ✅ | 完整的下载和管理界面 |
| 路由配置 | ✅ | 后端和前端路由已配置 |
| 依赖更新 | ✅ | 添加PyArrow支持 |

### 创建的文件

**后端**:
- `backend/services/data_storage_service.py` (385行)
- `backend/services/data_download_service.py` (285行)
- `backend/api/data_download.py` (268行)

**前端**:
- `frontend/src/services/dataDownload.ts` (167行)
- `frontend/src/pages/DataDownload.tsx` (485行)

**文档**:
- `DATA_DOWNLOAD_DESIGN.md` - 设计文档
- `DATA_DOWNLOAD_IMPLEMENTATION.md` - 实施报告（本文件）

**修改的文件**:
- `backend/api/__init__.py` - 注册数据下载路由
- `backend/requirements.txt` - 添加PyArrow依赖
- `frontend/src/App.tsx` - 添加数据下载路由
- `frontend/src/components/layout/Sidebar.tsx` - 添加数据下载菜单
- `frontend/src/services/index.ts` - 导出数据下载服务

### 代码统计

| 类别 | 文件数 | 代码行数 |
|------|--------|----------|
| 后端服务 | 2 | 670 |
| 后端API | 1 | 268 |
| 前端服务 | 1 | 167 |
| 前端页面 | 1 | 485 |
| **总计** | **5** | **1,590** |

---

## ⚠️ 注意事项

### 数据存储

1. **Parquet格式**
   - 需要安装PyArrow库
   - 文件大小较小，读取速度快
   - 支持列式存储，查询效率高

2. **数据库**
   - 使用SQLite存储元数据
   - 唯一约束防止重复
   - 索引优化查询性能

### 数据去重

1. **完全匹配**
   - 相同股票、日期范围、频率
   - 直接返回已有数据
   - 不重新下载

2. **部分重叠**
   - 日期范围有重叠但不完全匹配
   - 提示用户调整日期范围
   - 避免数据混乱

### 性能优化

1. **批量下载**
   - 支持一次下载多只股票
   - 自动延迟避免请求过快
   - 适合初始化数据

2. **缓存机制**
   - 已下载数据缓存到本地
   - 避免重复网络请求
   - 提高回测速度

---

## 🎓 经验总结

### 成功经验

1. **架构设计**
   - 清晰的职责分离
   - 服务层和API层分离
   - 易于测试和维护

2. **数据去重**
   - 完善的重叠检测算法
   - 友好的用户提示
   - 避免数据浪费

3. **用户体验**
   - 直观的界面设计
   - 实时的状态反馈
   - 详细的错误信息

### 改进建议

1. **错误处理**
   - 可以增加更详细的错误分类
   - 提供错误恢复建议
   - 记录错误日志

2. **进度跟踪**
   - 实现实时进度更新
   - 使用WebSocket推送
   - 支持暂停和恢复

3. **数据验证**
   - 增加数据质量检查
   - 验证数据完整性
   - 自动修复错误数据

---

## 📞 技术支持

### 常见问题

**Q: 数据下载失败怎么办？**
A: 检查网络连接、数据源是否可用、股票代码是否正确。

**Q: 如何强制重新下载？**
A: 在下载表单中勾选"强制重新下载"选项。

**Q: 数据存储在哪里？**
A: Parquet文件存储在`backend/data/`目录，元数据存储在SQLite数据库。

**Q: 如何清理数据？**
A: 在数据下载页面的已下载数据列表中点击"删除"按钮。

### 联系方式

- 项目地址: https://github.com/hgkdzbf6/stock
- 文档地址: https://github.com/hgkdzbf6/stock/blob/main/DATA_DOWNLOAD_IMPLEMENTATION.md
- 问题反馈: https://github.com/hgkdzbf6/stock/issues

---

## 📄 变更日志

### v2.0.0 (2026-02-15)

#### 新增
- ✅ 数据下载与回测分离架构
- ✅ 数据存储服务
- ✅ 数据下载服务
- ✅ 数据去重机制
- ✅ 数据下载API
- ✅ 前端数据下载页面
- ✅ Parquet格式支持

#### 改进
- ✅ 避免重复下载
- ✅ 提高数据管理效率
- ✅ 优化用户操作流程

#### 文档
- ✅ 设计文档
- ✅ 实施报告
- ✅ API文档

---

**报告版本**: v1.0
**最后更新**: 2026-02-15
**作者**: Cline AI Assistant