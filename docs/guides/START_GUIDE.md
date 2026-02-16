# 一键启动脚本使用指南

## 📋 概述

本项目提供了三个便捷的启动脚本，用于快速启动、停止和重启量化交易平台的所有服务。

## 🚀 快速开始

### 1. 启动所有服务

```bash
./start_all.sh
```

这个脚本会自动完成以下操作：
- ✅ 检查环境依赖（Python、Node.js）
- ✅ 检查端口占用情况
- ✅ 创建Python虚拟环境（如果不存在）
- ✅ 安装Python依赖
- ✅ 启动后端服务（端口8000）
- ✅ 安装前端依赖（如果需要）
- ✅ 启动前端服务（端口3000）
- ✅ 等待服务启动并验证

### 2. 停止所有服务

```bash
./stop_all.sh
```

这个脚本会：
- ✅ 停止后端服务
- ✅ 停止前端服务
- ✅ 清理PID文件
- ✅ 检查并清理残留进程

### 3. 重启所有服务

```bash
./restart_all.sh
```

这个脚本会：
- ✅ 停止所有服务
- ✅ 等待服务完全停止
- ✅ 重新启动所有服务

## 📊 启动后的访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端应用 | http://localhost:3000 | Web界面 |
| 后端API | http://localhost:8000 | REST API |
| API文档 | http://localhost:8000/docs | Swagger UI |
| 健康检查 | http://localhost:8000/health | 服务状态 |

## 📝 日志文件

脚本会在 `logs/` 目录下创建日志文件：

- `logs/backend.log` - 后端服务日志
- `logs/frontend.log` - 前端服务日志

查看日志：
```bash
# 查看后端日志
tail -f logs/backend.log

# 查看前端日志
tail -f logs/frontend.log

# 同时查看所有日志
tail -f logs/*.log
```

## 🔍 故障排查

### 问题1：端口被占用

**错误信息**：
```
⚠️  端口 8000 已被占用
```

**解决方案**：
1. 查看占用端口的进程：
```bash
lsof -i :8000
lsof -i :3000
```

2. 手动停止占用进程：
```bash
kill -9 <PID>
```

或者先运行停止脚本：
```bash
./stop_all.sh
```

### 问题2：后端启动失败

**错误信息**：
```
❌ 后端服务启动超时
```

**解决方案**：
1. 查看后端日志：
```bash
tail -n 50 logs/backend.log
```

2. 检查Python依赖是否安装：
```bash
cd backend
source venv/bin/activate
pip list
```

3. 手动测试启动：
```bash
cd backend
source venv/bin/activate
python main.py
```

### 问题3：前端启动失败

**错误信息**：
```
⚠️  前端服务启动超时
```

**解决方案**：
1. 查看前端日志：
```bash
tail -n 50 logs/frontend.log
```

2. 手动测试启动：
```bash
cd frontend
npm run dev
```

### 问题4：导入错误

**错误信息**：
```
ImportError: cannot import name 'xxx'
```

**解决方案**：
1. 清理Python缓存：
```bash
cd backend
find . -type d -name __pycache__ -exec rm -rf {} +
```

2. 重新安装依赖：
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## 🔧 高级使用

### 只启动后端

```bash
cd backend
source venv/bin/activate
python main.py
```

### 只启动前端

```bash
cd frontend
npm run dev
```

### 使用Docker启动

```bash
# 使用docker-compose
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📋 环境要求

### 后端
- Python 3.11+
- pip

### 前端
- Node.js 18+
- npm

### 可选
- Docker（用于容器化部署）
- PostgreSQL（生产环境数据库）
- Redis（生产环境缓存）

## ⚙️ 配置文件

### 后端配置

文件：`backend/.env`

```env
# 数据库配置
DATABASE_URL=sqlite:///./stock.db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI服务配置
GLM_API_KEY=your-glm-api-key-here
GLM_API_BASE=https://open.bigmodel.cn/api/paas/v4/

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 前端配置

文件：`frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

## 🎯 常用操作

### 查看服务状态

```bash
# 查看后端进程
ps aux | grep "python.*main.py"

# 查看前端进程
ps aux | grep "vite.*--port"

# 查看端口占用
lsof -i :8000 -i :3000
```

### 测试API

```bash
# 健康检查
curl http://localhost:8000/health

# 获取股票列表
curl http://localhost:8000/api/v1/stocks

# 测试认证
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 清理环境

```bash
# 停止所有服务
./stop_all.sh

# 清理Python虚拟环境
rm -rf backend/venv

# 清理前端依赖
rm -rf frontend/node_modules

# 清理日志
rm -rf logs/*.log
```

## 📚 相关文档

- [项目进度分析报告](PROJECT_PROGRESS_ANALYSIS.md) - 详细的进度分析
- [Phase 1完成报告](PHASE1_STATUS.md) - 基础架构完成情况
- [Phase 2完成报告](PHASE2_COMPLETION.md) - AI系统完成情况
- [Phase 3完成报告](PHASE3_BACKEND_COMPLETION.md) - 优化系统完成情况
- [Phase 4完成报告](PHASE4_COMPLETION_REPORT.md) - 交易系统完成情况

## 💡 提示

1. **首次启动**：首次启动时会自动安装依赖，可能需要几分钟时间
2. **日志监控**：建议在一个终端窗口中运行 `tail -f logs/backend.log` 监控后端日志
3. **端口冲突**：如果端口8000或3000被占用，脚本会提示是否继续
4. **PID文件**：脚本使用PID文件管理进程，不要手动删除
5. **环境变量**：首次运行前，请检查并配置 `backend/.env` 文件

## 🆘 获取帮助

如果遇到问题：

1. 查看日志文件：`logs/backend.log` 和 `logs/frontend.log`
2. 查看相关文档：项目根目录下的各种报告文件
3. 检查环境要求：确保Python和Node.js版本正确
4. 清理缓存：删除 `__pycache__` 和 `node_modules` 重新安装

## 📞 联系方式

- 项目地址：https://github.com/hgkdzbf6/stock
- 问题反馈：GitHub Issues

---

**最后更新**: 2026-02-14
**脚本版本**: v1.0