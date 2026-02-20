# 板块数据获取工具使用指南

## 概述

本工具用于从公开渠道（AkShare、Tushare）获取A股市场的板块数据，并保存到CSV文件中。这些板块数据用于K线图功能，提供真实的市场板块信息。

## 板块数据来源

### 1. AkShare 数据源
- **行业板块**：获取东方财富网的所有行业板块分类
- **概念板块**：获取东方财富网的所有概念板块分类
- **数据量**：约960+个板块
- **无需API密钥**：免费使用

### 2. Tushare 数据源（可选）
- **行业分类**：申万行业分类（SW2021）
- **需要API密钥**：需要在 `.env` 文件中配置 `TUSHARE_TOKEN`
- **数据权限**：部分接口需要高级权限

## 文件结构

```
backend/
├── scripts/
│   └── fetch_sectors.py          # 板块数据获取脚本
├── data/
│   ├── sectors.csv               # 板块数据CSV文件
│   └── sectors.xlsx             # 板块数据Excel文件（便于查看）
└── api/
    └── sector.py                # 板块API（从CSV读取数据）
```

## 使用方法

### 1. 获取板块数据

运行脚本获取最新的板块数据：

```bash
cd backend
python scripts/fetch_sectors.py
```

### 2. 输出文件

脚本会生成两个文件：

- `backend/data/sectors.csv` - CSV格式，供后端API读取
- `backend/data/sectors.xlsx` - Excel格式，便于人工查看

### 3. 数据格式

CSV文件包含以下字段：

```csv
code,name,type,market,description
其他数字媒体,其他数字媒体,industry,A股,行业板块
海洋捕捞,海洋捕捞,industry,A股,行业板块
航海装备Ⅲ,航海装备Ⅲ,industry,A股,行业板块
```

字段说明：
- `code`: 板块代码（与名称相同）
- `name`: 板块名称
- `type`: 板块类型（industry=行业, concept=概念）
- `market`: 市场类型（A股、申万等）
- `description`: 板块描述

## 定期更新

### 手动更新

建议每月或每季度更新一次板块数据：

```bash
cd backend
python scripts/fetch_sectors.py
```

### 自动更新（可选）

可以设置cron定时任务自动更新：

```bash
# 编辑crontab
crontab -e

# 添加每月1号凌晨2点执行
0 2 1 * * cd /path/to/stock/backend && python scripts/fetch_sectors.py
```

## 板块K线功能

### 后端API

#### 1. 获取板块列表

```bash
GET /api/v1/sector/list
```

返回示例：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "code": "医药",
      "name": "医药",
      "type": "industry",
      "market": "A股",
      "description": "行业板块"
    }
  ]
}
```

#### 2. 获取板块K线数据

```bash
GET /api/v1/sector/{sector_code}/kline?freq=daily&start_date=2025-11-21&end_date=2026-02-19
```

参数说明：
- `sector_code`: 板块代码（如：医药、银行、白酒等）
- `freq`: 频率（daily, 1min, 5min, 15min, 30min, 60min）
- `start_date`: 开始日期（YYYY-MM-DD）
- `end_date`: 结束日期（YYYY-MM-DD）

返回示例：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "date": "2025-11-21",
      "open": 3896.665,
      "high": 3912.006,
      "low": 3834.749,
      "close": 3834.891,
      "volume": 63164625100
    }
  ]
}
```

### 板块指数映射

对于常见板块，系统会使用对应的指数代码：

| 板块名称 | 指数代码 | 指数名称 |
|---------|---------|---------|
| 银行 | SH399986 | 中证银行指数 |
| 医药 | SH000932 | 医药生物指数 |
| 白酒 | SZ399997 | 中证白酒指数 |
| 新能源 | SZ399976 | 中证新能源指数 |
| 军工 | SZ399967 | 中证军工指数 |
| 汽车 | SZ399006 | 汽车指数 |

对于没有特定指数的板块，系统会自动使用上证指数（SH000001）作为替代。

## 前端使用

### 板块K线图组件

前端组件 `SectorKLineChart` 会：

1. 从 `/api/v1/sector/list` 获取所有板块列表
2. 用户选择板块后，调用 `/api/v1/sector/{code}/kline` 获取K线数据
3. 使用 `EnhancedKLineChart` 组件展示K线图
4. 显示板块统计信息（股票总数、上涨/下跌数量、平均涨跌幅）

### 访问页面

打开浏览器访问：
```
http://localhost:3000/kline
```

切换到"板块K线"标签页即可查看板块K线图。

## 常见问题

### 1. 板块数据为空

**问题**：运行脚本后没有获取到数据

**解决方案**：
- 检查网络连接
- 确认AkShare库已正确安装：`pip install akshare`
- 查看日志文件了解详细错误

### 2. 前端不显示板块列表

**问题**：前端板块下拉列表为空

**解决方案**：
- 确认 `backend/data/sectors.csv` 文件存在
- 检查后端API是否正常返回数据
- 查看浏览器控制台是否有错误

### 3. 板块K线数据加载失败

**问题**：选择板块后无法加载K线数据

**解决方案**：
- 确认日期格式正确（YYYY-MM-DD）
- 检查后端日志查看具体错误
- 某些板块可能暂时没有对应指数，系统会使用上证指数替代

### 4. 如何添加新板块

**方法1**：重新运行获取脚本
```bash
cd backend
python scripts/fetch_sectors.py
```

**方法2**：手动编辑CSV文件
编辑 `backend/data/sectors.csv`，添加新板块：
```csv
code,name,type,market,description
新板块,新板块,industry,A股,新板块描述
```

## 性能优化

### 1. 缓存机制

板块列表数据会在内存中缓存，避免频繁读取CSV文件。

### 2. 数据去重

脚本会自动去除重复的板块（基于板块名称）。

### 3. 建议更新频率

- 行业板块：每季度更新一次
- 概念板块：每月更新一次（概念板块变化较频繁）

## 相关文件

- 脚本文件：`backend/scripts/fetch_sectors.py`
- 后端API：`backend/api/sector.py`
- 前端组件：`frontend/src/components/charts/SectorKLineChart.tsx`
- 前端服务：`frontend/src/services/sector.ts`
- 数据文件：`backend/data/sectors.csv`

## 技术支持

如有问题，请查看：
1. 后端日志：`tail -f backend/logs/app_*.log`
2. 前端日志：`tail -f logs/frontend.log`
3. API文档：`http://localhost:8000/docs`