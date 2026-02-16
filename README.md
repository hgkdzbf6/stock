# 量化交易平台 (Stock Platform)

基于AI驱动的量化交易平台，支持实时行情、策略回测、参数优化和实盘交易。

## 项目结构

```
stock/
├── backend/           # 后端服务 (FastAPI + Python)
├── frontend/          # 前端应用 (React + TypeScript)
├── legacy/            # 原有代码（已迁移）
├── docs/              # 项目文档
│   ├── reports/       # 开发报告
│   └── guides/        # 指南文档
└── README.md         # 项目说明
```

## 文档索引

### 快速开始
- [快速开始指南](docs/guides/START_GUIDE.md) - 项目启动和配置指南
- [系统设计文档](docs/guides/design.md) - 系统架构和设计思路
- [开发计划](docs/guides/PLAN.md) - 详细的开发计划和里程碑

### 架构文档
- [架构标准](docs/ARCHITECTURE_STANDARDS.md) - 项目架构规范和设计原则
- [框架概述](docs/FRAMEWORK_OVERVIEW.md) - 技术框架和核心概念
- [K线图组件架构](docs/KLINE_CHART_COMPONENTS_ARCHITECTURE.md) - 图表组件设计

### 开发报告
- [项目状态总结](docs/reports/PROJECT_STATUS_SUMMARY.md) - 整体项目进度
- [数据源优化](docs/reports/DATA_SOURCE_OPTIMIZATION.md) - 数据源优化方案
- [缓存实现](docs/reports/CACHE_IMPLEMENTATION.md) - 缓存系统实现
- [数据下载设计](docs/reports/DATA_DOWNLOAD_DESIGN.md) - 数据下载服务设计

### 问题修复
- [问题诊断](docs/reports/API_LOADING_ISSUES_DIAGNOSIS.md) - API加载问题诊断
- [超时问题](docs/reports/TIMEOUT_ISSUE_DIAGNOSIS.md) - 超时问题分析
- [启动问题](docs/reports/STARTUP_DIAGNOSIS.md) - 启动问题排查

更多文档请查看 [docs/](docs/) 目录

## 技术栈

### 后端
- FastAPI - Web框架
- PostgreSQL - 数据库
- Redis - 缓存
- Celery - 异步任务队列
- SQLAlchemy - ORM

### 前端
- React 18 - UI框架
- TypeScript - 类型安全
- Ant Design - UI组件库
- ECharts - 图表库
- Zustand - 状态管理
- React Query - 服务端状态管理

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的配置

# 运行数据库迁移
python -c "from core.database import init_db; import asyncio; asyncio.run(init_db())"

# 启动服务
python main.py
```

后端API将运行在 http://localhost:8000

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" > .env
echo "VITE_WS_URL=ws://localhost:8000/ws" >> .env

# 启动开发服务器
npm run dev
```

前端应用将运行在 http://localhost:3000

## Docker部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 访问地址

- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- Grafana: http://localhost:3001 (用户名: admin)

## 当前开发进度

### Phase 1: Web基础平台 + 实时行情 ✅
- [x] 后端基础架构
- [x] 前端基础架构
- [x] 股票列表API
- [x] 行情数据API
- [x] 策略管理API
- [x] 基础UI页面
- [ ] K线图组件
- [ ] 技术指标图表
- [ ] WebSocket实时推送

### Phase 2: AI智能咨询系统 (待实施)
- [ ] GLM 4.7 API集成
- [ ] 提示词模板
- [ ] AI聊天界面
- [ ] 智能分析功能

### Phase 3: 策略优化与管理 (待实施)
- [ ] 策略参数配置
- [ ] 网格搜索优化
- [ ] 遗传算法优化
- [ ] 贝叶斯优化
- [ ] 回测引擎

### Phase 4: 实盘交易系统 (待实施)
- [ ] 券商API对接
- [ ] 订单管理系统
- [ ] 持仓管理
- [ ] 风险控制
- [ ] 监控告警

## 开发规范

### 后端
- 遵循PEP 8规范
- 使用异步编程
- 完整的类型提示
- 详细的API文档
- 使用loguru记录日志

### 前端
- 使用TypeScript
- 遵循React Hooks最佳实践
- 组件化开发
- 统一的代码风格
- 完善的错误处理

## 测试

### 后端测试
```bash
cd backend
pytest
```

### 前端测试
```bash
cd frontend
npm test
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证

## 联系方式

- 项目主页: https://github.com/yourorg/stock-platform
- 问题反馈: https://github.com/yourorg/stock-platform/issues
- 文档: PLAN.md

## 致谢

感谢所有贡献者的支持！
