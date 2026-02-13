# 量化交易平台扩展计划文档

**版本**: v1.0
**创建日期**: 2026-02-13
**项目代号**: Stock Platform 2.0

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术架构](#2-技术架构)
3. [实施阶段](#3-实施阶段)
4. [技术栈详情](#4-技术栈详情)
5. [数据库设计](#5-数据库设计)
6. [API接口设计](#6-api接口设计)
7. [部署方案](#7-部署方案)
8. [开发规范](#8-开发规范)
9. [风险评估](#9-风险评估)
10. [验收标准](#10-验收标准)

---

## 1. 项目概述

### 1.1 项目背景

当前项目是一个基于Python的量化交易策略回测系统，支持分钟级数据和多种技术指标策略。为了满足实际交易需求，需要将其扩展为一个完整的AI驱动量化交易平台，集成实时行情、智能分析、策略优化和实盘交易功能。

### 1.2 项目目标

构建一个企业级的量化交易平台，实现以下核心功能：

1. **AI智能交易助手**
   - 实时行情可视化（K线、技术指标、成交量）
   - 持仓与盈亏实时监控
   - AI驱动的策略咨询（基于GLM 4.7）
   - 历史决策分析（基于技术指标）

2. **股票池与板块管理**
   - 多维度股票池分类
   - 实时行情与持仓详情
   - 自定义股票池管理

3. **策略回测与绩效分析**
   - 自定义周期回测
   - 核心绩效指标统计
   - 可视化分析（净值曲线、盈亏分布、回撤）
   - 参数优化（网格搜索、遗传算法）

4. **实盘交易系统**
   - 对接券商API（XTP/CTP）
   - 订单管理与执行
   - 风险控制系统
   - 实时监控与告警

### 1.3 项目范围

**包含**:
- Web平台（前端 + 后端）
- 实时行情系统
- AI智能咨询
- 策略管理与优化
- 实盘交易接口
- 监控告警系统

**不包含**:
- 高频交易系统
- 机器学习策略自动生成
- 国际市场交易
- 复杂衍生品交易

### 1.4 成功标准

- ✅ 系统稳定性：99.5%在线率
- ✅ 实时延迟：行情推送延迟 < 500ms
- ✅ 回测准确性：与实盘误差 < 2%
- ✅ 用户体验：页面加载时间 < 2s
- ✅ 交易成功率：订单执行成功率 > 99%

---

## 2. 技术架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                        客户端层                           │
│  React + TypeScript + Ant Design + ECharts             │
└─────────────────────────────────────────────────────────┘
                              │
                    HTTP/WebSocket
                              │
┌─────────────────────────────────────────────────────────┐
│                      API网关层                            │
│           FastAPI (认证、限流、路由)                      │
└─────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
│   业务逻辑层    │   │   AI服务层      │   │   交易执行层    │
│ - 策略管理      │   │ - GLM 4.7集成  │   │ - XTP/CTP接口  │
│ - 回测引擎      │   │ - 提示词生成    │   │ - 订单管理      │
│ - 参数优化      │   │ - 智能分析      │   │ - 持仓管理      │
│ - 风险控制      │   │                 │   │ - 风险检查      │
└────────────────┘   └─────────────────┘   └─────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
│   数据访问层   │   │   缓存层       │   │   消息队列      │
│ - SQLAlchemy   │   │ - Redis        │   │ - Celery        │
│ - PostgreSQL   │   │ - 行情缓存     │   │ - 异步任务      │
└────────────────┘   └─────────────────┘   └─────────────────┘
```

### 2.2 技术选型理由

#### 前端技术栈
| 技术 | 选择理由 |
|------|---------|
| React 18 | 组件化开发，生态丰富，适合复杂应用 |
| TypeScript | 类型安全，提高代码质量和可维护性 |
| Ant Design | 企业级UI组件库，设计一致性好 |
| ECharts | 强大的图表库，支持复杂的K线图和指标图 |
| Zustand | 轻量级状态管理，简单易用 |
| React Query | 服务端状态管理，缓存和请求优化 |
| Vite | 快速的构建工具，开发体验好 |

#### 后端技术栈
| 技术 | 选择理由 |
|------|---------|
| FastAPI | 高性能异步框架，自动生成API文档，类型提示完善 |
| SQLAlchemy | 成熟的ORM，支持异步操作 |
| PostgreSQL | 功能强大的关系型数据库，支持复杂查询和JSON类型 |
| Redis | 高性能缓存和消息队列 |
| Celery | 强大的异步任务队列，适合参数优化和后台任务 |
| Pydantic | 数据验证和序列化，与FastAPI完美集成 |

#### AI服务
| 技术 | 选择理由 |
|------|---------|
| GLM 4.7 | 国内访问快，支持中文，成本相对较低，API兼容OpenAI格式 |

#### 券商接口
| 技术 | 选择理由 |
|------|---------|
| XTP | 腾讯提供的专业交易接口，支持沪深两市 |
| CTP | 上期所提供的标准化接口，期现套利必备 |

---

## 3. 实施阶段

### Phase 1: Web基础平台 + 实时行情

**时间**: 2-3周
**目标**: 搭建完整的Web平台基础，实现实时行情获取和可视化展示

#### 3.1 后端架构搭建

**目录结构**:
```
backend/
├── api/
│   ├── __init__.py
│   ├── stocks.py          # 股票数据API
│   ├── market.py          # 行情API
│   └── websocket.py       # WebSocket连接
├── core/
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   └── security.py        # 安全认证
├── models/
│   ├── stock.py           # 股票信息模型
│   ├── quote.py           # 行情数据模型
│   └── user.py            # 用户模型
├── services/
│   ├── data_fetcher.py    # 数据获取服务（复用现有）
│   ├── market_service.py  # 行情服务
│   └── cache_service.py   # 缓存服务
├── utils/
│   ├── logger.py          # 日志工具
│   └── validators.py      # 数据验证
└── main.py                # FastAPI入口
```

#### 3.2 前端架构搭建

**目录结构**:
```
frontend/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── components/
│   │   ├── charts/
│   │   ├── stock/
│   │   └── layout/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Market.tsx
│   │   └── StockDetail.tsx
│   ├── services/
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── store/
│   │   ├── marketStore.ts
│   │   └── stockStore.ts
│   ├── types/
│   ├── hooks/
│   └── utils/
├── package.json
└── vite.config.ts
```

#### 3.3 实时行情功能

**实现细节**:

1. **行情数据获取**
   - 优先使用WebSocket实时推送
   - 降级为HTTP轮询（5秒间隔）
   - 支持多股票批量订阅

2. **技术指标计算**
   - 实时计算MA、BOLL等指标
   - 使用缓存减少重复计算
   - 异步计算避免阻塞

3. **数据缓存策略**
   ```
   热门股票: Redis缓存 5秒
   普通股票: Redis缓存 30秒
   历史数据: PostgreSQL持久化
   技术指标: Redis缓存 60秒
   ```

#### 3.4 交付物

- ✅ 可访问的Web平台（http://localhost:3000）
- ✅ 实时行情展示（K线、成交量、MA/BOLL指标）
- ✅ 股票列表和搜索功能
- ✅ 股票详情页面
- ✅ 基础数据持久化
- ✅ API文档（Swagger）
- ✅ 部署脚本（Docker）

---

### Phase 2: AI智能咨询系统

**时间**: 2-3周
**目标**: 集成GLM 4.7，实现智能分析和策略建议

#### 2.1 后端AI服务

**提示词模板**:

1. **持仓分析提示词**
2. **市场行情提示词**
3. **技术指标综合分析提示词**
4. **风险评估提示词**

#### 2.2 前端AI组件

**核心组件**:

1. **AI聊天界面**
   - 支持文本输入
   - 支持快捷提问
   - 流式响应显示
   - 历史记录保存

2. **策略建议卡片**
   - 显示AI生成的策略建议
   - 置信度可视化
   - 一键应用到策略系统

3. **风险提示组件**
   - 三级风险等级（低/中/高）
   - 颜色编码（绿/黄/红）
   - 风险因素列表

4. **技术指标分析**
   - 趋势可视化
   - 买卖信号标识
   - 关键技术位标记

5. **持仓洞察**
   - 盈亏分布图
   - 持仓占比饼图
   - 风险评估仪表盘

#### 2.3 交付物

- ✅ AI智能咨询界面
- ✅ 持仓智能分析
- ✅ 市场行情智能解读
- ✅ 技术指标AI分析
- ✅ 风险提示系统

---

### Phase 3: 策略优化与管理

**时间**: 3-4周
**目标**: 实现策略参数优化、多策略回测、策略池管理

#### 3.1 策略管理系统

**核心功能**:

1. **策略CRUD接口**
2. **策略分组和标签系统**
3. **策略参数配置模板**
4. **策略绩效统计**

#### 3.2 参数优化引擎

**优化算法**:

1. **网格搜索优化器**
   - 遍历所有参数组合
   - 找到最优参数
   - 适合参数空间较小的情况

2. **遗传算法优化器**
   - 模拟自然选择和遗传
   - 适合参数空间较大的情况
   - 支持多目标优化

3. **贝叶斯优化器**
   - 基于概率模型
   - 样本效率高
   - 适合评估成本高的情况

#### 3.3 多策略回测

**核心功能**:

1. **并行回测引擎**
2. **策略相关性分析**
3. **详细绩效指标统计**
4. **优化结果可视化**

#### 3.4 交付物

- ✅ 策略管理系统（CRUD）
- ✅ 策略分组管理
- ✅ 参数优化引擎（网格搜索、遗传算法、贝叶斯）
- ✅ 多策略并行回测
- ✅ 策略相关性分析
- ✅ 详细绩效指标统计
- ✅ 可视化分析工具

---

### Phase 4: 实盘交易系统

**时间**: 3-4周
**目标**: 对接券商API，实现真实订单交易

#### 4.1 交易API集成

**目录结构**:
```
backend/trading/
├── brokers/                  # 券商接口适配
│   ├── base_broker.py        # 券商基类
│   ├── xtp_broker.py         # XTP接口
│   └── ctp_broker.py         # CTP接口
├── order_manager.py          # 订单管理
├── position_manager.py       # 持仓管理
├── account_manager.py        # 账户管理
└── risk_controller.py        # 风险控制
```

#### 4.2 风险控制系统

**风控检查**:

1. **持仓限制检查**
   - 单一持仓限制
   - 总持仓限制
   - 板块持仓限制

2. **日内限制检查**
   - 交易次数限制
   - 日内亏损限制
   - 日内交易金额限制

3. **止损检查**
   - 自动止损触发
   - 止盈保护
   - 动态止损调整

4. **流动性检查**
   - 成交量检查
   - 买卖价差检查
   - 市场深度检查

#### 4.3 实时监控与告警

**监控指标**:

1. **订单指标**
   - 订单总数
   - 成交率
   - 平均延迟

2. **持仓指标**
   - 总持仓数
   - 总市值
   - 总盈亏

3. **系统指标**
   - CPU使用率
   - 内存使用率
   - 磁盘使用率

4. **告警规则**
   - 止损告警
   - 持仓超限告警
   - 系统异常告警

#### 4.4 前端交易界面

**核心页面**:

1. **交易页面**
   - 快速下单
   - 市场深度
   - 最近成交

2. **订单管理**
   - 订单列表
   - 订单详情
   - 订单操作

3. **持仓管理**
   - 持仓列表
   - 持仓详情
   - 盈亏分析

4. **账户信息**
   - 资金概览
   - 资产分布
   - 资金流水

5. **监控页面**
   - 实时监控大屏
   - 告警列表
   - 系统指标

#### 4.5 交付物

- ✅ 券商API对接（XTP/CTP）
- ✅ 订单管理系统
- ✅ 持仓管理系统
- ✅ 账户管理系统
- ✅ 风险控制系统
- ✅ 实时监控系统
- ✅ 告警通知系统
- ✅ Web交易界面
- ✅ 运维监控大屏

---

## 4. 技术栈详情

### 4.1 后端依赖

```txt
# Web框架
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# 数据库
sqlalchemy>=2.0.23
asyncpg>=0.29.0
alembic>=1.13.0

# 缓存
redis>=5.0.0
hiredis>=2.2.0

# 异步任务
celery>=5.3.0
kombu>=5.3.0

# AI服务
openai>=1.6.0

# 数据处理
pandas>=2.1.0
numpy>=1.26.0
scipy>=1.11.0
talib-binary>=0.4.0

# 优化算法
deap>=1.3.0
bayesian-optimization>=1.4.0

# 券商API
pyctp>=1.0.0
xtp-api>=2.0.0

# 监控
prometheus-client>=0.19.0

# 其他
python-dotenv>=1.0.0
python-multipart>=0.0.6
websockets>=12.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
aiofiles>=23.2.0
httpx>=0.25.0
```

### 4.2 前端依赖

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "antd": "^5.12.0",
    "@ant-design/icons": "^5.2.0",
    "@ant-design/charts": "^2.0.0",
    "echarts": "^5.4.0",
    "echarts-for-react": "^3.0.0",
    "@ant-design/pro-components": "^2.6.0",
    "axios": "^1.6.0",
    "dayjs": "^1.11.0",
    "zustand": "^4.4.0",
    "@tanstack/react-query": "^5.0.0",
    "react-markdown": "^9.0.0",
    "highlight.js": "^11.9.0",
    "xss": "^1.0.14",
    "decimal.js": "^10.4.0",
    "recharts": "^2.10.0",
    "socket.io-client": "^4.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/node": "^20.10.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.55.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "prettier": "^3.1.0",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.1.0",
    "@testing-library/jest-dom": "^6.1.0",
    "@testing-library/user-event": "^14.5.0"
  }
}
```

### 4.3 DevOps工具

```yaml
# Docker相关
docker: >=24.0
docker-compose: >=2.20

# 数据库
postgresql: >=15
redis: >=7-alpine

# 监控
prometheus: >=2.48
grafana: >=10.2

# CI/CD
github-actions: 已配置
```

---

## 5. 数据库设计

### 5.1 数据库表结构

#### 用户表 (users)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);
```

#### 股票表 (stocks)
```sql
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    market VARCHAR(10) NOT NULL,
    sector VARCHAR(50),
    industry VARCHAR(100),
    list_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 行情数据表 (quotes)
```sql
CREATE TABLE quotes (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    amount DECIMAL(20,2),
    frequency VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 策略表 (strategies)
```sql
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    params JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 回测结果表 (backtest_results)
```sql
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    stock_code VARCHAR(20),
    start_date DATE,
    end_date DATE,
    frequency VARCHAR(10),
    initial_capital DECIMAL(20,2),
    final_capital DECIMAL(20,2),
    total_return DECIMAL(10,4),
    annual_return DECIMAL(10,4),
    max_drawdown DECIMAL(10,4),
    sharpe_ratio DECIMAL(10,4),
    win_rate DECIMAL(10,4),
    profit_loss_ratio DECIMAL(10,4),
    volatility DECIMAL(10,4),
    calmar_ratio DECIMAL(10,4),
    trade_count INTEGER,
    params JSONB,
    equity_curve JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 订单表 (orders)
```sql
CREATE TABLE orders (
    id VARCHAR(50) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    stock_id INTEGER REFERENCES stocks(id),
    strategy_id INTEGER REFERENCES strategies(id),
    side VARCHAR(10) NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    price DECIMAL(10,2),
    stop_price DECIMAL(10,2),
    quantity INTEGER NOT NULL,
    filled_quantity INTEGER DEFAULT 0,
    avg_fill_price DECIMAL(10,2),
    status VARCHAR(20) NOT NULL,
    commission DECIMAL(10,2) DEFAULT 0,
    remark TEXT,
    broker_order_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    submitted_at TIMESTAMP,
    filled_at TIMESTAMP,
    cancelled_at TIMESTAMP
);
```

#### 持仓表 (positions)
```sql
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    stock_id INTEGER REFERENCES stocks(id),
    quantity INTEGER NOT NULL,
    available_quantity INTEGER,
    cost_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2),
    market_value DECIMAL(20,2),
    pnl_amount DECIMAL(20,2),
    pnl_ratio DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 账户表 (accounts)
```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    broker VARCHAR(50),
    broker_account_id VARCHAR(50),
    total_assets DECIMAL(20,2),
    available_cash DECIMAL(20,2),
    frozen_cash DECIMAL(20,2),
    market_value DECIMAL(20,2),
    pnl_amount DECIMAL(20,2),
    pnl_ratio DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 交易记录表 (trades)
```sql
CREATE TABLE trades (
    id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(id),
    stock_id INTEGER REFERENCES stocks(id),
    side VARCHAR(10) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL,
    amount DECIMAL(20,2) NOT NULL,
    commission DECIMAL(10,2),
    timestamp TIMESTAMP NOT NULL,
    broker_trade_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 告警表 (alerts)
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    rule_name VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    status VARCHAR(20) DEFAULT 'unread',
    channels TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    read_at TIMESTAMP
);
```

#### AI分析记录表 (ai_analyses)
```sql
CREATE TABLE ai_analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    stock_code VARCHAR(20),
    context JSONB,
    prompt TEXT,
    response TEXT,
    suggestions JSONB,
    confidence DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 6. API接口设计

### 6.1 RESTful API规范

**基础URL**: `http://localhost:8000/api/v1`
**认证方式**: JWT Bearer Token
**响应格式**: JSON

**通用响应结构**:
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2026-02-13T14:30:00Z"
}
```

### 6.2 核心API端点

#### 认证相关 (Authentication)

```python
# POST /api/v1/auth/register
# 注册用户
Request: {
  "username": "user123",
  "email": "user@example.com",
  "password": "password123",
  "full_name": "张三"
}

# POST /api/v1/auth/login
# 用户登录
Request: {
  "username": "user123",
  "password": "password123"
}

# POST /api/v1/auth/refresh
# 刷新Token
Request: {
  "refresh_token": "..."
}
```

#### 股票相关 (Stocks)

```python
# GET /api/v1/stocks
# 获取股票列表
Query Params:
  - page: int (default: 1)
  - page_size: int (default: 20)
  - sector: str (optional)

# GET /api/v1/stocks/{code}
# 获取股票详情

# GET /api/v1/stocks/search
# 搜索股票
Query Params:
  - keyword: str
```

#### 行情相关 (Market)

```python
# GET /api/v1/market/quote/{code}
# 获取实时行情

# GET /api/v1/market/kline/{code}
# 获取K线数据
Query Params:
  - frequency: str (1min, 5min, 15min, 30min, 60min, daily)
  - start_date: date
  - end_date: date

# GET /api/v1/market/indicators/{code}
# 获取技术指标
Query Params:
  - frequency: str
  - indicators: str[] (MA, BOLL, RSI, MACD, KDJ)
```

#### 策略相关 (Strategies)

```python
# GET /api/v1/strategies
# 获取策略列表

# POST /api/v1/strategies
# 创建策略
Request: {
  "name": "我的策略",
  "type": "MA",
  "description": "...",
  "params": {
    "short_window": 5,
    "long_window": 20,
    "stop_loss": 0.1
  }
}

# PUT /api/v1/strategies/{id}
# 更新策略

# DELETE /api/v1/strategies/{id}
# 删除策略

# POST /api/v1/strategies/{id}/backtest
# 运行回测
Request: {
  "stock_code": "600771",
  "start_date": "2025-01-01",
  "end_date": "2026-01-01",
  "frequency": "daily",
  "initial_capital": 100000
}

# POST /api/v1/strategies/{id}/optimize
# 参数优化
Request: {
  "method": "grid_search",
  "stock_code": "600771",
  "param_ranges": {
    "short_window": {"min": 5, "max": 20},
    "long_window": {"min": 20, "max": 60}
  },
  "objective": "sharpe_ratio"
}
```

#### 交易相关 (Trading)

```python
# POST /api/v1/trading/orders
# 创建订单
Request: {
  "stock_code": "600771",
  "side": "buy",
  "order_type": "limit",
  "price": 10.50,
  "quantity": 1000
}

# GET /api/v1/trading/orders
# 获取订单列表

# DELETE /api/v1/trading/orders/{id}
# 撤销订单

# GET /api/v1/trading/positions
# 获取持仓列表

# GET /api/v1/trading/account
# 获取账户信息
```

#### AI分析相关 (AI)

```python
# POST /api/v1/ai/analyze
# AI分析
Request: {
  "type": "portfolio",
  "data": {
    "code": "600771",
    "indicators": {...},
    "position": {...}
  }
}

# GET /api/v1/ai/history
# 获取分析历史
```

#### 监控告警相关 (Monitoring)

```python
# GET /api/v1/monitoring/dashboard
# 获取监控面板数据

# GET /api/v1/monitoring/alerts
# 获取告警列表

# PUT /api/v1/monitoring/alerts/{id}/read
# 标记告警为已读
```

### 6.3 WebSocket接口

**WebSocket URL**: `ws://localhost:8000/ws`

**连接认证**:
```javascript
{
  "type": "auth",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**实时行情订阅**:
```javascript
// 订阅行情
{
  "type": "subscribe",
  "channel": "market",
  "codes": ["600771.SH", "000001.SZ"]
}

// 取消订阅
{
  "type": "unsubscribe",
  "channel": "market",
  "codes": ["600771.SH"]
}
```

---

## 7. 部署方案

### 7.1 Docker Compose配置

```yaml
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    container_name: stock_postgres
    environment:
      POSTGRES_DB: stock_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - stock_network

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: stock_redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - stock_network

  # 后端API服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: stock_backend
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/stock_platform
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - GLM_API_KEY=${GLM_API_KEY}
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - stock_network

  # Celery Worker
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: stock_celery_worker
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/stock_platform
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
    command: celery -A tasks.celery_app worker --loglevel=info
    networks:
      - stock_network

  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: stock_frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api/v1
      - VITE_WS_URL=ws://localhost:8000/ws
    command: npm run dev -- --host 0.0.0.0
    networks:
      - stock_network

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: stock_nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - backend
      - frontend
    networks:
      - stock_network

volumes:
  postgres_data:
  redis_data:

networks:
  stock_network:
    driver: bridge
```

### 7.2 环境变量配置

```env
# .env

# 数据库配置
DB_PASSWORD=your_secure_password

# Redis配置
REDIS_PASSWORD=your_redis_password

# JWT配置
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI服务配置
GLM_API_KEY=your_glm_api_key_here
GLM_API_BASE=https://open.bigmodel.cn/api/paas/v4/

# 券商API配置
XTP_BROKER_ID=your_broker_id
XTP_ACCOUNT=your_account
XTP_PASSWORD=your_password
XTP_TRADING_SERVER=your_trading_server
XTP_TRADING_PORT=your_trading_port
XTP_QUOTE_SERVER=your_quote_server
XTP_QUOTE_PORT=your_quote_port

# 告警配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_email_password

ALERT_EMAIL_1=admin@example.com
ALERT_EMAIL_2=trader@example.com

# 企业微信配置
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx

# Grafana配置
GRAFANA_PASSWORD=your_grafana_password

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 7.3 后端Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.4 前端Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制应用代码
COPY . .

# 构建应用
RUN npm run build

# 生产镜像
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 7.5 Nginx配置

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name localhost;

        # 前端代理
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # 后端API代理
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # WebSocket代理
        location /ws {
            proxy_pass http://backend/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_read_timeout 86400;
        }
    }
}
```

### 7.6 部署脚本

```bash
#!/bin/bash
# scripts/deploy.sh

echo "开始部署量化交易平台..."

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装"
    exit 1
fi

# 创建环境变量文件
if [ ! -f .env ]; then
    echo "创建.env文件..."
    cp .env.example .env
    echo "请编辑.env文件，填入必要的配置"
    exit 1
fi

# 构建镜像
echo "构建Docker镜像..."
docker-compose build

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
docker-compose ps

# 运行数据库迁移
echo "运行数据库迁移..."
docker-compose exec backend alembic upgrade head

# 创建初始管理员用户
echo "创建初始管理员用户..."
docker-compose exec backend python scripts/create_admin.py

echo "部署完成！"
echo "前端地址: http://localhost:3000"
echo "后端API: http://localhost:8000"
echo "Grafana: http://localhost:3001 (admin/\${GRAFANA_PASSWORD})"
```

---

## 8. 开发规范

### 8.1 代码风格

**Python代码规范**:
- 遵循PEP 8规范
- 使用Black格式化代码
- 使用isort排序import
- 使用pylint进行代码检查
- 添加类型提示（Type Hints）

**TypeScript代码规范**:
- 遵循ESLint规则
- 使用Prettier格式化代码
- 强制使用类型
- 使用React Hooks最佳实践

### 8.2 Git工作流

**分支策略**:
- `main`: 主分支，生产环境代码
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 修复分支
- `hotfix/*`: 紧急修复分支

**提交规范**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Type类型:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

### 8.3 测试规范

**单元测试**:
- 使用pytest（Python）
- 使用Vitest（前端）
- 测试覆盖率 > 80%

**集成测试**:
- 测试API端点
- 测试数据库操作
- 测试WebSocket连接

### 8.4 文档规范

**API文档**:
- 使用FastAPI自动生成
- 提供请求/响应示例
- 说明错误码

**代码文档**:
- 所有公共函数添加docstring
- 复杂逻辑添加注释
- README说明项目使用方法

---

## 9. 风险评估

### 9.1 技术风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 券商API不稳定 | 中 | 高 | 实现重试机制、降级策略 |
| GLM API限流 | 中 | 中 | 实现请求队列、缓存结果 |
| 数据库性能瓶颈 | 低 | 高 | 读写分离、分库分表、索引优化 |
| WebSocket连接断开 | 高 | 中 | 自动重连、心跳机制 |
| 系统扩展性 | 中 | 高 | 微服务架构、水平扩展 |

### 9.2 业务风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 交易延迟 | 中 | 高 | 优化算法、缓存热点数据 |
| 策略失效 | 高 | 中 | 回测验证、参数优化、风险控制 |
| 数据错误 | 低 | 高 | 数据校验、异常检测、人工审核 |
| 监管变化 | 低 | 中 | 关注政策、灵活调整 |

### 9.3 安全风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| API密钥泄露 | 低 | 高 | 环境变量、加密存储、权限控制 |
| SQL注入 | 低 | 高 | 参数化查询、ORM、输入验证 |
| XSS攻击 | 中 | 中 | 输入过滤、CSP策略、XSS防护 |
| CSRF攻击 | 中 | 中 | Token验证、SameSite Cookie |
| 未授权访问 | 中 | 高 | JWT认证、RBAC权限控制 |

### 9.4 运维风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 服务宕机 | 低 | 高 | 高可用架构、自动故障转移 |
| 数据丢失 | 低 | 高 | 定期备份、异地灾备 |
| 性能下降 | 中 | 中 | 监控告警、自动扩容、负载均衡 |
| 配置错误 | 中 | 高 | 配置管理、版本控制、灰度发布 |

---

## 10. 验收标准

### Phase 1 验收标准

**功能验收**:
- ✅ 用户可以访问Web平台（http://localhost:3000）
- ✅ 可以浏览股票列表并查看详情
- ✅ K线图实时更新，支持多周期切换
- ✅ 支持MA、BOLL等技术指标显示
- ✅ WebSocket连接稳定，自动重连
- ✅ 行情数据延迟 < 500ms
- ✅ 数据持久化到PostgreSQL
- ✅ Redis缓存正常工作

**性能验收**:
- ✅ 页面首次加载时间 < 2s
- ✅ API响应时间 < 100ms
- ✅ WebSocket推送延迟 < 200ms
- ✅ 系统支持100并发用户

**质量验收**:
- ✅ 代码覆盖率 > 80%
- ✅ 所有测试通过
- ✅ 无严重bug
- ✅ API文档完整

### Phase 2 验收标准

**功能验收**:
- ✅ AI聊天界面正常工作
- ✅ 持仓分析功能完整
- ✅ 市场行情分析准确
- ✅ 技术指标AI分析合理
- ✅ 风险提示及时准确
- ✅ 流式响应正常

**性能验收**:
- ✅ AI分析响应时间 < 5s
- ✅ 流式响应首字延迟 < 1s
- ✅ 每日AI调用成本在预算内

**质量验收**:
- ✅ AI分析结果准确率 > 70%
- ✅ 用户满意度评分 > 4.0/5.0
- ✅ 提示词A/B测试有明确结论

### Phase 3 验收标准

**功能验收**:
- ✅ 策略CRUD功能完整
- ✅ 策略分组管理正常
- ✅ 网格搜索优化器正确
- ✅ 遗传算法优化器正确
- ✅ 贝叶斯优化器正确
- ✅ 多策略并行回测稳定
- ✅ 回测结果可视化完整
- ✅ 优化结果对比清晰

**性能验收**:
- ✅ 单策略回测时间 < 30s（6个月数据）
- ✅ 并行回测10个策略 < 60s
- ✅ 网格搜索（1000参数组合）< 5min
- ✅ 遗传算法（50种群×20代）< 10min

**质量验收**:
- ✅ 优化结果收敛
- ✅ 回测准确性 > 98%
- ✅ 参数优化后策略绩效提升 > 5%

### Phase 4 验收标准

**功能验收**:
- ✅ XTP券商API对接成功
- ✅ 订单提交流程完整
- ✅ 订单撤销功能正常
- ✅ 持仓实时同步
- ✅ 风控规则全部生效
- ✅ 告警及时发送
- ✅ 监控大屏实时更新
- ✅ Web交易界面完整

**性能验收**:
- ✅ 订单提交延迟 < 100ms
- ✅ 订单状态更新延迟 < 500ms
- ✅ 系统可用性 > 99.5%
- ✅ 交易成功率 > 99%

**安全验收**:
- ✅ 所有API需要认证
- ✅ 敏感信息加密存储
- ✅ 风控规则全部测试通过
- ✅ 无安全漏洞

**质量验收**:
- ✅ 模拟交易与实盘误差 < 2%
- ✅ 无资金损失事故
- ✅ 用户满意度 > 4.5/5.0

---

## 附录

### A. 术语表

| 术语 | 说明 |
|------|------|
| K线 | 蜡烛图，包含开盘价、收盘价、最高价、最低价 |
| MA | 移动平均线 |
| BOLL | 布林带 |
| RSI | 相对强弱指标 |
| MACD | 指数平滑移动平均线 |
| KDJ | 随机指标 |
| ADX | 平均趋向指标 |
| OBV | 能量潮指标 |
| 回测 | 使用历史数据测试策略 |
| 夏普比率 | 风险调整后的收益率指标 |
| 最大回撤 | 从峰值到谷值的最大跌幅 |
| 止损 | 亏损达到阈值时自动卖出 |
| 止盈 | 盈利达到阈值时自动卖出 |
| 滑点 | 实际成交价格与预期价格的偏差 |
| 券商API | 券商提供的交易接口 |
| XTP | 腾讯提供的券商交易接口 |
| CTP | 中国期货市场交易接口 |

### B. 参考资料

**Python相关**:
- FastAPI官方文档: https://fastapi.tiangolo.com/
- SQLAlchemy文档: https://docs.sqlalchemy.org/
- Celery文档: https://docs.celeryq.dev/

**前端相关**:
- React文档: https://react.dev/
- Ant Design文档: https://ant.design/
- ECharts文档: https://echarts.apache.org/

**量化相关**:
- Backtrader文档: https://www.backtrader.com/
- TA-Lib文档: https://ta-lib.org/
- 量化投资书籍

**AI相关**:
- GLM 4.7 API文档
- Prompt Engineering指南

### C. 联系方式

**项目团队**:
- 项目经理: [联系人]
- 技术负责人: [联系人]
- 后端开发: [联系人]
- 前端开发: [联系人]

**支持渠道**:
- 技术支持: support@example.com
- 问题反馈: https://github.com/yourorg/stock-platform/issues

---

**文档版本**: v1.0
**最后更新**: 2026-02-13
**维护者**: [团队名称]
