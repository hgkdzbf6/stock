# 超时问题诊断报告

## 问题描述

访问 `http://localhost:3000/stock/600111.SH` 时出现超时错误：

```
股票信息: timeout of 60000ms exceeded
K线数据: timeout of 60000ms exceeded
```

## 问题根源分析

### 后端服务状态 ✅
```bash
$ curl http://localhost:8000/health
{"status":"ok","app_name":"Stock Platform","version":"2.0.0"}
```
**结论**: 后端服务正常运行

### 后端日志分析 ❌

查看后端日志 (`backend/logs/app_2026-02-16.log`)：

```
2026-02-16 11:08:03.564 | ERROR | data_adapters.baostock_adapter:get_kline_data:188 
- [BaoStock] 获取K线数据失败: BaoStock查询失败: 网络接收错误。

2026-02-16 11:08:03.565 | ERROR | services.market_service:get_realtime_quote:92 
- 获取实时行情失败: BaoStock查询失败: 网络接收错误。

2026-02-16 11:08:18.468 | ERROR | data_adapters.baostock_adapter:get_stock_list:101 
- [BaoStock] 获取股票列表失败: BaoStock查询失败: 网络接收错误。
```

### 根本原因

**数据源API（BaoStock）网络不可用**

- ❌ BaoStock API连接失败
- ❌ 所有依赖BaoStock的请求都超时
- ❌ 包括：实时行情、K线数据、股票列表

## 详细分析

### 错误模式

1. **前端请求**: `GET /api/v1/stocks/600111.SH`
2. **后端调用**: 尝试从BaoStock获取数据
3. **网络错误**: `BaoStock查询失败: 网络接收错误。`
4. **超时**: 60秒后前端超时

### 为什么超时60秒？

后端配置：
- **前端超时**: 60秒
- **数据源超时**: 可能更短或无限等待

数据源API响应慢或无响应时，前端等待60秒后超时。

### 重试机制

从日志可以看到，系统有重试机制，但每次都失败：

```
11:08:03 - 第一次请求失败
11:08:03 - 第二次请求失败
11:08:03 - 第三次请求失败
11:08:04 - 第四次请求失败
11:08:09 - 第五次请求失败
...
```

## 解决方案

### 方案1: 切换数据源（推荐）

BaoStock API网络不稳定，切换到其他数据源：

#### 1.1 切换到Akshare（推荐）

编辑 `backend/.env`:

```bash
# 修改数据源配置
DATA_SOURCE=akshare
```

重启后端服务：

```bash
./stop_all.sh
./start_all.sh
```

#### 1.2 检查当前数据源

查看后端配置：

```bash
cat backend/.env | grep DATA_SOURCE
```

#### 1.3 测试数据源

测试不同数据源的可用性：

```bash
# 测试Akshare
python -c "import akshare as ak; print(ak.stock_zh_a_hist('600111'))"

# 测试Tushare（需要token）
python -c "import tushare as ts; print(ts.get_k_data('600111'))"
```

### 方案2: 使用本地缓存数据

如果之前下载过数据，可以使用本地缓存：

1. 访问数据下载页面：`http://localhost:3000/data-download`
2. 检查已下载数据列表
3. 使用已下载的数据

### 方案3: 等待BaoStock恢复

如果是临时网络问题，可以等待BaoStock API恢复：

- 检查网络连接
- 等待一段时间后重试
- 查看BaoStock官方公告

### 方案4: 使用多个数据源

配置多个数据源，自动切换：

```python
# 在 backend/core/config.py 中配置
DATA_SOURCES = ["akshare", "tushare", "baostock"]
# 按顺序尝试，失败则切换到下一个
```

## 临时解决方案

### 立即测试

1. **切换到Akshare**:

```bash
cd backend
echo "DATA_SOURCE=akshare" >> .env
```

2. **重启后端**:

```bash
cd /Users/zbf/ws/stock
./restart_all.sh
```

3. **测试API**:

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/api/v1/stocks/600111.SH"
```

### 检查数据源状态

创建测试脚本检查数据源：

```bash
# 创建测试脚本
cat > test_datasource.py << 'EOF'
import akshare as ak
import tushare as ts

# 测试Akshare
try:
    data = ak.stock_zh_a_hist('600111.SH', period="daily", start_date="20240201", end_date="20240216")
    print(f"✓ Akshare正常: 获取到 {len(data)} 条数据")
except Exception as e:
    print(f"✗ Akshare失败: {e}")

# 测试BaoStock
try:
    import baostock as bs
    lg = bs.login()
    if lg.error_code != '0':
        print(f"✗ BaoStock登录失败: {lg.error_msg}")
    else:
        rs = bs.query_history_k_data_plus("sh.600111", "date,code,open,high,low,close")
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        print(f"✓ BaoStock正常: 获取到 {len(data_list)} 条数据")
        bs.logout()
except Exception as e:
    print(f"✗ BaoStock失败: {e}")
EOF

# 运行测试
cd backend
python test_datasource.py
```

## 长期解决方案

### 1. 实现数据源健康检查

定期检查数据源可用性，自动切换：

```python
# backend/services/data_source_health.py
class DataSourceHealthChecker:
    async def check_data_source(self, source: str) -> bool:
        """检查数据源是否可用"""
        try:
            if source == "akshare":
                data = ak.stock_zh_a_hist('000001', period="daily")
                return len(data) > 0
            elif source == "baostock":
                # 测试连接
                pass
        except:
            return False
        return False
```

### 2. 实现数据源自动切换

```python
class DataFetcher:
    def __init__(self):
        self.sources = ["akshare", "tushare", "baostock"]
        self.current_source_index = 0
    
    def get_data(self, *args, **kwargs):
        """尝试多个数据源，直到成功"""
        for i in range(len(self.sources)):
            source = self.sources[(self.current_source_index + i) % len(self.sources)]
            try:
                result = self._fetch_from_source(source, *args, **kwargs)
                if result:
                    # 切换到成功的数据源
                    self.current_source_index = (self.current_source_index + i) % len(self.sources)
                    return result
            except Exception as e:
                logger.warning(f"{source} 失败: {e}")
                continue
        raise Exception("所有数据源都失败")
```

### 3. 优化超时和重试

```python
# 添加数据源级别的超时
DATA_SOURCE_TIMEOUTS = {
    "akshare": 30,  # 30秒
    "baostock": 10,  # 10秒
    "tushare": 30,   # 30秒
}

# 限制重试次数
MAX_RETRIES = 2
RETRY_DELAY = 1  # 秒
```

### 4. 添加数据源状态监控

```python
# 在前端显示数据源状态
{
  "akshare": "✓ 正常",
  "baostock": "✗ 网络错误",
  "tushare": "✓ 正常"
}
```

## 推荐操作步骤

### 立即执行

1. **切换数据源**:
   ```bash
   cd backend
   echo "DATA_SOURCE=akshare" >> .env
   cd ..
   ./restart_all.sh
   ```

2. **测试页面**:
   ```
   访问: http://localhost:3000/stock/600111.SH
   ```

3. **查看日志**:
   ```bash
   tail -f backend/logs/app_$(date +%Y-%m-%d).log
   ```

### 如果仍然失败

1. **检查网络连接**:
   ```bash
   ping api.baoStock.com
   ping api.akshare.xyz
   ```

2. **测试数据源**:
   ```bash
   cd backend
   python test_datasource.py
   ```

3. **查看详细错误**:
   ```bash
   grep -A 10 "ERROR" backend/logs/app_$(date +%Y-%m-%d).log | tail -50
   ```

## 预防措施

### 1. 配置多个数据源

在 `.env` 中配置备用数据源：

```bash
DATA_SOURCE=akshare
BACKUP_DATA_SOURCE=tushare,baostock
```

### 2. 定期检查数据源

创建定时任务检查数据源健康：

```bash
# 添加到crontab
*/10 * * * * cd /Users/zbf/ws/stock && python check_datasource_health.py
```

### 3. 使用本地缓存

优先使用已下载的本地数据：

```python
use_local=True  # 默认使用本地数据
```

## 总结

### 问题原因
- ❌ 数据源API（BaoStock）网络不可用
- ❌ 所有依赖BaoStock的请求都失败
- ❌ 导致前端60秒超时

### 解决方案
- ✅ 切换到Akshare数据源（推荐）
- ✅ 使用本地缓存数据
- ✅ 等待BaoStock恢复
- ✅ 实现多数据源自动切换

### 下一步
1. 立即切换到Akshare
2. 重启后端服务
3. 测试页面是否正常
4. 实现数据源健康检查
5. 配置多个备用数据源

**关键**: 这不是代码问题，是数据源API的网络问题。切换数据源即可解决！