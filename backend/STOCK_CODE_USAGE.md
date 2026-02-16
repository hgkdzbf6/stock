# 股票代码映射服务使用指南

## 📚 功能概述

股票代码映射服务提供了以下核心功能：

1. **下载股票列表** - 从数据源下载完整的股票列表到本地
2. **多种搜索方式** - 支持代码、名称、前缀、模糊搜索
3. **市场识别** - 自动识别股票所属市场（沪市主板、科创板、深市主板、创业板、北交所）
4. **本地存储** - 数据保存在本地CSV文件，快速查询
5. **统计分析** - 提供股票列表统计信息

## 🚀 快速开始

### 1. 下载股票列表

#### 方式一：使用API（推荐）

```bash
# 下载股票列表（默认5000条/页，自动获取所有页）
curl -X POST "http://localhost:8000/api/stock-code/download"

# 自定义页码和每页数量
curl -X POST "http://localhost:8000/api/stock-code/download?page=1&page_size=100"
```

#### 方式二：使用Python代码

```python
from services.stock_code_service import stock_code_service
from services.data_fetcher import DataFetcher
import asyncio

async def download_stock_list():
    """下载股票列表"""
    # 初始化数据获取器
    data_fetcher = DataFetcher(source='ashare')
    
    # 分批下载所有股票
    all_stocks = []
    for page in range(1, 10):  # 下载前10页
        stocks = await data_fetcher.get_stock_list(
            page=page,
            page_size=500
        )
        if not stocks:
            break
        all_stocks.extend(stocks)
        print(f"已获取 {len(all_stocks)} 只股票")
    
    # 保存到本地
    success = stock_code_service.save_stock_list(all_stocks)
    if success:
        print(f"✅ 成功保存 {len(all_stocks)} 只股票")

# 运行
asyncio.run(download_stock_list())
```

### 2. 搜索股票

#### 方式一：使用API

```bash
# 模糊搜索（同时搜索代码和名称）
curl "http://localhost:8000/api/stock-code/search?keyword=贵州&search_type=fuzzy&limit=10"

# 根据代码搜索
curl "http://localhost:8000/api/stock-code/search?keyword=600519&search_type=code&limit=10"

# 根据名称搜索
curl "http://localhost:8000/api/stock-code/search?keyword=茅台&search_type=name&limit=10"

# 根据前缀搜索
curl "http://localhost:8000/api/stock-code/search?keyword=贵州&search_type=prefix&limit=10"

# 专用API - 根据名称搜索
curl "http://localhost:8000/api/stock-code/name/茅台?limit=10"

# 专用API - 根据代码搜索
curl "http://localhost:8000/api/stock-code/code/600519?limit=10"

# 专用API - 根据前缀搜索
curl "http://localhost:8000/api/stock-code/prefix?prefix=贵州&search_field=name&limit=10"
```

#### 方式二：使用Python代码

```python
from services.stock_code_service import stock_code_service

# 1. 根据股票代码精确搜索
results = stock_code_service.search_by_code('600519', limit=5)
print(f"找到 {len(results)} 只股票")
for stock in results:
    print(f"  {stock['code']} {stock['name']} ({stock['market']})")

# 2. 根据股票名称模糊搜索
results = stock_code_service.search_by_name('茅台', limit=5)
print(f"找到 {len(results)} 只股票")
for stock in results:
    print(f"  {stock['code']} {stock['name']} ({stock['market']})")

# 3. 根据前缀搜索（推荐用于自动补全）
results = stock_code_service.search_by_prefix('贵州', search_field='name', limit=10)
print(f"找到 {len(results)} 只股票")
for stock in results:
    print(f"  {stock['code']} {stock['name']}")

# 4. 模糊搜索（同时搜索代码和名称）
results = stock_code_service.fuzzy_search('银行', limit=10)
print(f"找到 {len(results)} 只股票")
for stock in results:
    print(f"  {stock['code']} {stock['name']} ({stock['market']})")
```

### 3. 获取股票详细信息

```bash
# 使用API
curl "http://localhost:8000/api/stock-code/info/600519.SH"
```

```python
# 使用Python代码
stock_info = stock_code_service.get_stock_info('600519.SH')
if stock_info:
    print(f"股票代码: {stock_info['code']}")
    print(f"股票名称: {stock_info['name']}")
    print(f"所属市场: {stock_info['market']}")
    print(f"最新价格: {stock_info['price']}")
    print(f"涨跌幅: {stock_info['change_pct']}%")
```

### 4. 根据市场获取股票

```bash
# 使用API - 获取沪市主板股票
curl "http://localhost:8000/api/stock-code/market/沪市主板?limit=100"

# 获取科创板股票
curl "http://localhost:8000/api/stock-code/market/科创板?limit=100"

# 获取创业板股票
curl "http://localhost:8000/api/stock-code/market/创业板?limit=100"
```

```python
# 使用Python代码
results = stock_code_service.get_stocks_by_market('沪市主板', limit=100)
print(f"沪市主板共 {len(results)} 只股票")

results = stock_code_service.get_stocks_by_market('科创板', limit=100)
print(f"科创板共 {len(results)} 只股票")
```

### 5. 获取统计信息

```bash
# 使用API
curl "http://localhost:8000/api/stock-code/statistics"
```

```python
# 使用Python代码
stats = stock_code_service.get_statistics()
print(f"总股票数: {stats['total']}")
print("\n各市场分布:")
for market, count in stats['by_market'].items():
    print(f"  {market}: {count}只")
```

### 6. 刷新股票列表

```bash
# 使用API
curl -X POST "http://localhost:8000/api/stock-code/refresh"
```

```python
# 使用Python代码
success = stock_code_service.refresh()
if success:
    print("✅ 股票列表已刷新")
```

## 📊 市场识别规则

服务会根据股票代码自动识别所属市场：

| 市场名称 | 代码规则 | 示例 |
|---------|---------|------|
| 沪市主板 | 600xxx, 601xxx, 603xxx, 605xxx | 600519.SH |
| 科创板 | 688xxx | 688111.SH |
| 深市主板 | 000xxx, 001xxx, 003xxx | 000001.SZ |
| 创业板 | 300xxx | 300001.SZ |
| 北交所 | 83xxxx, 87xxxx, 43xxxx | 832566.BJ |

## 💡 使用场景示例

### 场景1：前端自动补全

```python
# 用户输入前几个字符
prefix = "贵州"

# 获取匹配的股票
results = stock_code_service.search_by_prefix(
    prefix, 
    search_field='name', 
    limit=10
)

# 返回给前端用于自动补全
return {
    'suggestions': [
        {'code': '600519.SH', 'name': '贵州茅台'},
        {'code': '600519.SH', 'name': '贵州轮胎'},
        # ...
    ]
}
```

### 场景2：根据名称查找代码

```python
# 用户只知道股票名称
stock_name = "贵州茅台"

# 查找对应的股票代码
results = stock_code_service.search_by_name(stock_name, limit=1)

if results:
    stock_code = results[0]['code']
    stock_market = results[0]['market']
    print(f"股票代码: {stock_code}")
    print(f"所属市场: {stock_market}")
```

### 场景3：股票筛选

```python
# 获取所有科创板股票
star_market_stocks = stock_code_service.get_stocks_by_market(
    '科创板', 
    limit=500
)

# 进一步筛选
filtered_stocks = [
    stock for stock in star_market_stocks
    if stock['price'] < 50  # 价格低于50元
]

print(f"科创板中价格低于50元的股票: {len(filtered_stocks)}只")
```

### 场景4：批量查询

```python
# 批量获取股票信息
stock_codes = ['600519.SH', '000001.SZ', '688111.SH']

for code in stock_codes:
    stock_info = stock_code_service.get_stock_info(code)
    if stock_info:
        print(f"{stock_info['name']}: {stock_info['price']}元")
```

## 🧪 测试

运行单元测试：

```bash
# 运行所有测试
cd backend
python test_stock_code_service.py

# 运行特定测试
python -m unittest test_stock_code_service.TestStockCodeService.test_search_by_name

# 下载真实股票列表测试（需要网络）
python -m unittest test_stock_code_service.TestStockCodeService.test_download_real_stock_list
```

## 📁 数据存储

股票列表保存在：`data/stock_list.csv`

文件格式：
```csv
代码,名称,最新价,涨跌额,涨跌幅,成交量,成交额,市值,开盘,最高,最低,昨收,market,update_time
600519.SH,贵州茅台,1500.00,10.00,0.67,1000000,1500000000,2000000000000,1490.00,1510.00,1485.00,1490.00,沪市主板,2024-02-15 17:00:00
...
```

## 🔧 API端点列表

| 端点 | 方法 | 描述 |
|-------|------|------|
| `/api/stock-code/download` | POST | 下载股票列表到本地 |
| `/api/stock-code/search` | GET | 搜索股票 |
| `/api/stock-code/info/{code}` | GET | 获取股票详细信息 |
| `/api/stock-code/market/{market}` | GET | 根据市场获取股票 |
| `/api/stock-code/statistics` | GET | 获取统计信息 |
| `/api/stock-code/refresh` | POST | 刷新股票列表 |
| `/api/stock-code/prefix` | GET | 根据前缀搜索 |
| `/api/stock-code/name/{name}` | GET | 根据名称搜索 |
| `/api/stock-code/code/{code}` | GET | 根据代码搜索 |

## 📝 参数说明

### 搜索参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| search_type | string | 否 | 搜索类型：`fuzzy`(默认), `code`, `name`, `prefix` |
| limit | integer | 否 | 返回数量限制，默认10 |

### 市场参数

| 市场名称 | 说明 |
|---------|------|
| 沪市主板 | 上海证券交易所主板 |
| 科创板 | 上海证券交易所科创板 |
| 深市主板 | 深圳证券交易所主板 |
| 创业板 | 深圳证券交易所创业板 |
| 北交所 | 北京证券交易所 |

## ⚠️ 注意事项

1. **首次使用前请先下载股票列表**
2. **数据保存在本地，首次下载后查询速度很快**
3. **股票列表需要定期更新以保持最新**
4. **搜索不区分大小写**
5. **前缀搜索比模糊搜索更快，适合自动补全场景**

## 🔄 更新股票列表

建议定期更新股票列表（如每周一次）：

```bash
# 方式一：API
curl -X POST "http://localhost:8000/api/stock-code/download"

# 方式二：Python
from services.stock_code_service import stock_code_service
from services.data_fetcher import DataFetcher
import asyncio

async def update():
    data_fetcher = DataFetcher(source='ashare')
    stocks = await data_fetcher.get_stock_list(page=1, page_size=5000)
    stock_code_service.save_stock_list(stocks)

asyncio.run(update())
```

## 📚 完整示例

查看完整示例代码：`backend/test_stock_code_service.py`

## 🆘 故障排除

### 问题：搜索不到股票

**原因**：股票列表未下载或已过期

**解决**：
```bash
# 重新下载股票列表
curl -X POST "http://localhost:8000/api/stock-code/download"
```

### 问题：市场识别错误

**原因**：股票代码格式不正确

**解决**：确保股票代码格式正确，如 `600519.SH` 或 `000001.SZ`

### 问题：数据文件损坏

**解决**：
```python
# 删除数据文件，重新下载
from pathlib import Path
Path('data/stock_list.csv').unlink()

# 然后重新下载
stock_code_service.refresh()