# API加载失败问题诊断

## 问题描述
股票详情页面出现"加载行情失败"和"加载K线数据失败"的错误信息。

## 已检查的配置

### 1. 前端API配置 ✅
**文件**: `frontend/src/services/api.ts`
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
```
- 默认URL: `http://localhost:8000/api/v1`
- 正确

### 2. 后端路由注册 ✅
**文件**: `backend/api/__init__.py`
```python
api_router.include_router(market_router, prefix="/market", tags=["market"])
```
- 路由前缀: `/api/v1/market`
- 正确

### 3. 后端主配置 ✅
**文件**: `backend/main.py`
```python
app.include_router(api_router, prefix="/api/v1")
```
- 完整路径: `/api/v1/market`
- 正确

### 4. 数据源配置 ✅
**文件**: `backend/core/config.py`
```python
DATA_SOURCE: str = "akshare"  # 默认使用akshare
```
- 默认数据源: akshare
- 正确

## 可能的问题原因

### 原因1: 后端服务未运行 ⚠️
**症状**: 所有API请求都失败

**检查方法**:
```bash
# 检查后端是否在运行
curl http://localhost:8000/health

# 或检查端口是否被占用
lsof -i :8000
```

**解决方案**:
```bash
# 启动后端服务
cd backend
python main.py

# 或使用启动脚本
./start_backend.sh
```

### 原因2: CORS问题 ⚠️
**症状**: 浏览器控制台显示CORS错误

**检查方法**:
1. 打开浏览器开发者工具 (F12)
2. 切换到Console标签
3. 查看是否有CORS错误

**解决方案**:
后端已配置CORS:
```python
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
# CORS_ORIGINS = "http://localhost:3000,http://localhost:3001"
```

如果仍有问题，检查`.env`文件中的`CORS_ORIGINS`配置。

### 原因3: 数据源API问题 ⚠️
**症状**: 后端返回错误，数据源无法获取数据

**检查方法**:
1. 查看后端日志: `logs/app_YYYY-MM-DD.log`
2. 查看浏览器Network标签中的响应

**可能的原因**:
- akshare API网络问题
- akshare API限流
- 股票代码格式不正确

**解决方案**:
1. 查看后端日志中的具体错误信息
2. 尝试其他数据源（如tushare）
3. 检查股票代码格式是否正确

### 原因4: 响应格式不匹配 ⚠️
**症状**: API返回成功但前端解析失败

**检查方法**:
1. 打开浏览器开发者工具
2. 切换到Network标签
3. 查看API响应内容

**后端返回格式**:
```python
@router.get("/kline/{code}")
async def get_kline(...):
    return {
        "code": 200,
        "message": "success",
        "data": kline_data
    }
```

**前端期望格式**:
```typescript
const response = await marketService.getKlineData({...});
// response应该包含 { code, message, data }
```

**问题**: 前端apiClient直接返回`response.data`，所以response就是{code, message, data}

**解决方案**: 当前代码已经正确处理了这种格式。

### 原因5: 请求参数错误 ⚠️
**症状**: 400 Bad Request错误

**检查方法**:
查看Network标签中的请求URL和参数

**前端请求**:
```typescript
await marketService.getKlineData({
  code: code,  // 如 "688191.SH"
  freq: 'daily',
  start_date: '2024-01-01',
  end_date: '2024-02-01'
})
```

**后端期望**:
```python
code: str  # 股票代码
freq: str = "daily"
start_date: str  # YYYY-MM-DD
end_date: str  # YYYY-MM-DD
```

**可能的问题**:
- 日期格式不正确
- 股票代码格式不正确

## 诊断步骤

### 步骤1: 检查后端服务状态
```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 预期响应:
# {"status":"ok","app_name":"Stock Platform","version":"2.0.0"}
```

### 步骤2: 检查API文档
```bash
# 访问API文档
open http://localhost:8000/docs
```

在浏览器中：
1. 找到 `/api/v1/market/kline/{code}` 端点
2. 点击 "Try it out"
3. 输入参数测试
4. 查看响应

### 步骤3: 查看浏览器控制台
1. 打开 http://localhost:3000/stock/688191.SH
2. 打开开发者工具 (F12)
3. 切换到Console标签
4. 查看错误信息
5. 切换到Network标签
6. 查看失败的请求详情

### 步骤4: 查看后端日志
```bash
# 查看今天的日志
tail -f logs/app_$(date +%Y-%m-%d).log

# 或查看最近100行
tail -n 100 logs/app_$(date +%Y-%m-%d).log
```

### 步骤5: 测试API端点
```bash
# 测试获取行情
curl http://localhost:8000/api/v1/market/quote/688191.SH

# 测试获取K线数据
curl "http://localhost:8000/api/v1/market/kline/688191.SH?start_date=2024-01-01&end_date=2024-02-01&freq=daily"
```

## 常见解决方案

### 方案1: 启动后端服务
```bash
# 方式1: 直接启动
cd backend
python main.py

# 方式2: 使用启动脚本
./start_backend.sh

# 方式3: 使用Docker
docker-compose up backend
```

### 方案2: 检查端口占用
```bash
# macOS/Linux
lsof -i :8000

# 如果被占用，杀死进程
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### 方案3: 配置数据源
编辑 `backend/.env`:
```bash
# 使用akshare（免费）
DATA_SOURCE=akshare

# 或使用tushare（需要token）
DATA_SOURCE=tushare
TUSHARE_TOKEN=你的tushare_token
```

### 方案4: 调整CORS配置
编辑 `backend/.env`:
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 方案5: 查看详细错误
前端已添加console.log：
```typescript
console.log('成功加载K线数据:', formattedData.length, '条记录');
console.log('加载K线数据失败:', error);
```

在浏览器控制台查看这些日志。

## 推荐的调试顺序

1. **首先**: 确认后端服务正在运行
   ```bash
   curl http://localhost:8000/health
   ```

2. **其次**: 检查浏览器控制台错误
   - F12 → Console标签
   - 查看具体的错误信息

3. **然后**: 检查Network标签
   - F12 → Network标签
   - 查看失败的请求状态码和响应

4. **最后**: 查看后端日志
   ```bash
   tail -f logs/app_$(date +%Y-%m-%d).log
   ```

## 联系支持

如果以上步骤都无法解决问题，请提供以下信息：
1. 后端健康检查结果: `curl http://localhost:8000/health`
2. 浏览器控制台错误截图
3. Network标签中的请求详情截图
4. 后端日志中的相关错误信息