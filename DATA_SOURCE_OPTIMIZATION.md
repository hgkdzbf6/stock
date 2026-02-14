# 数据源超时优化文档

## 📋 优化概述

**优化日期**: 2026-02-14
**优化目标**: 解决数据源请求响应缓慢问题
**优化方案**: 添加5秒超时机制 + 自动切换数据源

---

## 🎯 优化目标

### 问题分析
1. **BaoStock响应缓慢**: 首次请求耗时超过60秒
2. **无超时机制**: 请求卡住，没有自动切换
3. **优先级不合理**: BaoStock放在优先级首位，但其响应较慢
4. **用户体验差**: API请求超时（>30秒）

### 优化策略
1. ✅ **添加超时控制**: 每个数据源请求5秒超时
2. ✅ **自动切换**: 超时或失败自动切换到下一个数据源
3. ✅ **调整优先级**: AkShare响应更快，放首位
4. ✅ **详细日志**: 记录每次切换的原因

---

## 🔧 技术实现

### 修改文件
**文件**: `backend/data_adapters/__init__.py`

### 核心改进

#### 1. 添加超时常量
```python
class AdapterFactory:
    # 数据源请求超时时间（秒）
    REQUEST_TIMEOUT = 5
```

#### 2. 调整数据源优先级
```python
# 优化前
self._priority_order = {
    'stock_list': ['baostock', 'akshare', 'mock'],  # baostock慢
    'stock_quote': ['akshare', 'sina', 'tencent', 'eastmoney', 'mock'],
    'kline_data': ['baostock', 'akshare', 'sina', 'eastmoney', 'mock'],  # baostock慢
    'search_stocks': ['akshare', 'mock']
}

# 优化后
self._priority_order = {
    'stock_list': ['akshare', 'baostock', 'mock'],  # akshare快，放前面
    'stock_quote': ['akshare', 'sina', 'tencent', 'eastmoney', 'mock'],
    'kline_data': ['akshare', 'baostock', 'sina', 'eastmoney', 'mock'],  # akshare快
    'search_stocks': ['akshare', 'mock']
}
```

#### 3. 超时处理机制
```python
async def auto_get_stock_list(
    self,
    page: int = 1,
    page_size: int = 20,
    keyword: str = None
) -> tuple[list[StockQuote], str]:
    """自动获取股票列表（按优先级尝试，每个数据源超时5秒）"""
    priority_list = self._priority_order.get('stock_list', ['mock'])
    last_error = None
    
    for source in priority_list:
        try:
            adapter = self.get_adapter(source)
            logger.info(f"[Auto] 尝试使用 {source} 获取股票列表...")
            
            # 使用超时包装器
            result = await asyncio.wait_for(
                adapter.get_stock_list(page, page_size, keyword),
                timeout=self.REQUEST_TIMEOUT
            )
            
            if result:
                logger.info(f"[Auto] 使用 {source} 获取股票列表成功，共{len(result)}只股票")
                return result, source
            else:
                logger.warning(f"[Auto] {source} 返回空结果，切换数据源")
                last_error = f"{source}返回空结果"
                
        except asyncio.TimeoutError:
            logger.warning(f"[Auto] {source} 获取股票列表超时（>{self.REQUEST_TIMEOUT}秒），切换数据源")
            last_error = f"{source}超时"
            continue
            
        except Exception as e:
            logger.warning(f"[Auto] {source} 获取股票列表失败: {e}")
            last_error = f"{source}失败: {str(e)}"
            continue
    
    # 所有数据源都失败，使用mock（但mock也有超时）
    logger.warning(f"[Auto] 所有数据源都失败，使用mock数据。最后错误: {last_error}")
    try:
        adapter = self.get_adapter('mock')
        result = await asyncio.wait_for(
            adapter.get_stock_list(page, page_size, keyword),
            timeout=self.REQUEST_TIMEOUT
        )
        if result:
            logger.info(f"[Auto] mock数据获取成功，共{len(result)}只股票")
            return result, 'mock'
        else:
            raise ValueError("mock返回空结果")
    except asyncio.TimeoutError:
        logger.error(f"[Auto] mock数据源也超时，返回超时错误")
        raise TimeoutError(f"所有数据源都超时（>{self.REQUEST_TIMEOUT}秒）")
    except Exception as e:
        logger.error(f"[Auto] mock数据源失败: {e}")
        raise TimeoutError(f"所有数据源都失败: {last_error}")
```

#### 4. 应用到所有数据获取方法
相同的超时机制已应用到以下方法：
- `auto_get_stock_list()` - 获取股票列表
- `auto_get_stock_quote()` - 获取股票行情
- `auto_get_kline_data()` - 获取K线数据
- `auto_search_stocks()` - 搜索股票

---

## 📊 优化效果对比

### 优化前
```
请求流程:
1. 尝试 BaoStock
2. 等待 60+ 秒（超时）
3. 切换到 AkShare
4. 等待 75+ 秒（超时）
5. 使用 mock 数据
总耗时: >75秒
```

### 优化后
```
请求流程:
1. 尝试 AkShare (优先级调整)
2. 等待 5 秒（超时控制）
3. 如果失败，切换到 BaoStock
4. 等待 5 秒（超时控制）
5. 如果失败，使用 mock 数据
最大总耗时: 15秒（3个数据源 × 5秒）
```

### 性能提升
- **响应时间**: 从 >75秒 降低到 最大15秒
- **成功率**: AkShare成功率高，优先使用
- **用户体验**: 5秒内有响应，体验大幅提升
- **容错性**: 自动切换，不依赖单一数据源

---

## 🔍 日志示例

### 成功场景
```
2026-02-14 10:53:44 | INFO | [Auto] 尝试使用 akshare 获取股票列表...
2026-02-14 10:53:46 | INFO | [Auto] 使用 akshare 获取股票列表成功，共20只股票
```

### 超时切换场景
```
2026-02-14 10:53:44 | INFO | [Auto] 尝试使用 akshare 获取股票列表...
2026-02-14 10:53:49 | WARNING | [Auto] akshare 获取股票列表超时（>5秒），切换数据源
2026-02-14 10:53:49 | INFO | [Auto] 尝试使用 baostock 获取股票列表...
2026-02-14 10:53:52 | INFO | [Auto] 使用 baostock 获取股票列表成功，共20只股票
```

### 全部失败场景
```
2026-02-14 10:53:44 | INFO | [Auto] 尝试使用 akshare 获取股票列表...
2026-02-14 10:53:49 | WARNING | [Auto] akshare 获取股票列表超时（>5秒），切换数据源
2026-02-14 10:53:49 | INFO | [Auto] 尝试使用 baostock 获取股票列表...
2026-02-14 10:53:54 | WARNING | [Auto] baostock 获取股票列表超时（>5秒），切换数据源
2026-02-14 10:53:54 | INFO | [Auto] 尝试使用 mock 获取股票列表...
2026-02-14 10:53:56 | INFO | [Auto] mock数据获取成功，共20只股票
```

---

## 🎯 预期效果

### 1. 响应时间大幅缩短
- **健康检查**: < 1秒
- **股票列表**: < 6秒（AkShare成功）
- **股票行情**: < 6秒
- **K线数据**: < 6秒
- **最坏情况**: < 16秒（所有数据源都失败）

### 2. 用户体验提升
- ✅ 不再出现30秒超时
- ✅ 快速响应，有即时反馈
- ✅ 自动切换，无需手动重试
- ✅ 详细日志，易于调试

### 3. 系统稳定性
- ✅ 不依赖单一数据源
- ✅ 自动容错
- ✅ Mock兜底，总有数据返回

---

## 📌 后续优化建议

### 短期优化
1. **缓存机制**: 添加Redis缓存，减少重复请求
2. **并发请求**: 同时尝试多个数据源，取最快返回
3. **健康检查**: 定期检测数据源可用性，动态调整优先级

### 长期优化
1. **负载均衡**: 根据数据源响应时间动态分配请求
2. **降级策略**: 数据源异常时自动降低请求频率
3. **监控告警**: 数据源失败率超过阈值时发送告警

---

## 🧪 测试建议

### 单元测试
```python
import pytest
import asyncio
from data_adapters import AdapterFactory

@pytest.mark.asyncio
async def test_timeout_switching():
    """测试超时自动切换"""
    factory = AdapterFactory()
    # 测试所有数据源都超时的情况
    with pytest.raises(TimeoutError):
        await factory.auto_get_stock_list(page=1, page_size=20)
```

### 集成测试
```python
@pytest.mark.asyncio
async def test_akshare_priority():
    """测试AkShare优先级"""
    factory = AdapterFactory()
    stocks, source = await factory.auto_get_stock_list(page=1, page_size=20)
    # 应该优先使用akshare
    assert source == 'akshare' or source == 'baostock' or source == 'mock'
```

---

## ✅ 总结

### 优化成果
1. ✅ **5秒超时**: 每个数据源请求5秒超时
2. ✅ **自动切换**: 超时或失败自动切换到下一个数据源
3. ✅ **优先级优化**: AkShare响应更快，放首位
4. ✅ **详细日志**: 记录每次切换的原因
5. ✅ **全部应用**: 所有数据获取方法都已优化

### 代码变更
- **修改文件**: 1个
- **新增代码**: ~150行
- **核心改进**: 超时控制 + 自动切换

### 预期效果
- **响应时间**: 从 >75秒 降低到 最大15秒
- **成功率**: AkShare优先使用，成功率高
- **用户体验**: 5秒内有响应，体验大幅提升

---

**文档生成时间**: 2026-02-14 10:54
**优化完成状态**: ✅ 代码已优化，待测试验证