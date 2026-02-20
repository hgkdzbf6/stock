# 股票量化交易系统 - 模块化架构文档

## 目录

1. [系统概览](#系统概览)
2. [后端架构](#后端架构)
3. [前端架构](#前端架构)
4. [数据流](#数据流)
5. [模块依赖关系](#模块依赖关系)
6. [测试框架](#测试框架)

---

## 系统概览

本项目是一个完整的股票量化交易系统，采用前后端分离架构：

- **后端**: Python FastAPI + 异步编程
- **前端**: React + TypeScript + ECharts
- **数据存储**: SQLite + DuckDB + 文件系统
- **数据源**: AkShare, Baostock, Tushare, EastMoney 等

---

## 后端架构

### 目录结构

```
backend/
├── api/                    # API层
│   ├── __init__.py
│   ├── ai.py              # AI咨询API
│   ├── auth.py            # 认证API
│   ├── backtest_reports.py # 回测报告文件管理API
│   ├── data_download.py    # 数据下载API
│   ├── market.py          # 行情API
│   ├── optimization.py    # 参数优化API
│   ├── sector.py          # 板块API
│   ├── stock_code.py      # 股票代码API
│   ├── stocks.py          # 股票API
│   ├── strategies.py      # 策略API
│   ├── trading.py         # 交易API
│   ├── websocket.py       # WebSocket实时推送
│   ├── auth/             # 认证模块
│   ├── market/           # 行情模块
│   └── stocks/           # 股票模块
│
├── ai/                    # AI模块
│   ├── __init__.py
│   ├── ai_service.py     # AI服务
│   ├── llm_client.py     # LLM客户端
│   └── prompt_templates.py # 提示词模板
│
├── core/                  # 核心模块
│   ├── __init__.py
│   ├── base_service.py   # 基础服务类
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接
│   └── security.py       # 安全工具
│
├── data_adapters/         # 数据适配器层
│   ├── __init__.py
│   ├── base.py           # 适配器基类
│   ├── models.py         # 数据模型
│   ├── akshare_adapter.py
│   ├── ashare_adapter.py
│   ├── baostock_adapter.py
│   ├── duckdb_adapter.py
│   ├── eastmoney_adapter.py
│   ├── mock_adapter.py
│   ├── sina_adapter.py
│   ├── tencent_adapter.py
│   └── tushare_adapter.py
│
├── data/                  # 数据存储
│   └── backtest_reports/  # 回测报告文件
│
├── models/               # 数据模型层
│   ├── __init__.py
│   ├── quote.py         # 行情模型
│   ├── stock.py         # 股票模型
│   ├── strategy.py      # 策略模型
│   └── user.py          # 用户模型
│
├── optimizers/           # 参数优化器
│   ├── __init__.py
│   ├── base_optimizer.py
│   ├── bayesian.py
│   ├── genetic.py
│   └── grid_search.py
│
├── services/             # 业务逻辑层
│   ├── __init__.py
│   ├── backtest_service.py    # 回测服务
│   ├── cache_service.py       # 缓存服务
│   ├── data_download_service.py # 数据下载服务
│   ├── data_fetcher.py        # 数据获取器
│   ├── data_storage_service.py # 数据存储服务
│   ├── duckdb_storage_service.py # DuckDB存储
│   ├── market_service.py      # 行情服务
│   ├── optimization_service.py # 优化服务
│   └── stock_code_service.py  # 股票代码服务
│
├── trading/             # 交易模块
│   ├── __init__.py
│   ├── account_manager.py
│   ├── base_broker.py
│   ├── ctp_broker.py
│   ├── order_manager.py
│   ├── position_manager.py
│   ├── risk_controller.py
│   └── xtp_broker.py
│
├── utils/               # 工具模块
│   ├── __init__.py
│   ├── logger.py        # 日志工具
│   └── trading_days.py  # 交易日工具
│
├── test/                # 测试框架
│   ├── api/
│   │   ├── test_endpoints.py
│   │   ├── test_market_api.py
│   │   └── test_simple.py
│   ├── core/
│   ├── data_adapters/
│   │   ├── test_duckdb_adapter.py
│   │   ├── test_minute_download.py
│   │   ├── test_real_sources.py
│   │   └── test_storage.py
│   ├── services/
│   │   ├── test_backtest_volume.py  # 回测成交量测试
│   │   ├── test_data_download_service.py
│   │   └── test_stock_code_service.py
│   └── utils/
│       └── test_startup.py
│
└── main.py             # 应用入口
```

### 后端模块说明

#### 1. API层 (`api/`)

负责处理HTTP请求和响应，定义RESTful API接口。

**核心API**:
- `strategies.py`: 策略管理和回测API
- `backtest_reports.py`: 回测报告文件管理API
- `market.py`: 行情数据API
- `stocks.py`: 股票信息API

**职责**:
- 请求参数验证
- 调用业务逻辑层
- 格式化响应数据
- 错误处理

#### 2. 业务逻辑层 (`services/`)

实现核心业务逻辑，是系统的核心层。

**核心服务**:
- `backtest_service.py`: 回测引擎
  - `BacktestEngine`: 回测核心类
  - 数据获取
  - 指标计算
  - 交易模拟
  - 绩效评估
  
- `data_fetcher.py`: 数据获取器
  - `DataFetcher`: 统一数据获取接口
  - 数据源选择逻辑
  - 数据转换和缓存

- `market_service.py`: 行情服务
  - 实时行情推送
  - 历史行情查询

#### 3. 数据适配器层 (`data_adapters/`)

适配不同的数据源，提供统一接口。

**设计模式**: 适配器模式

**核心类**:
- `BaseAdapter`: 适配器基类
- `AkShareAdapter`: AkShare数据源
- `BaostockAdapter`: Baostock数据源
- `TushareAdapter`: Tushare数据源

#### 4. 数据模型层 (`models/`)

定义数据结构和验证规则。

**核心模型**:
- `StockQuote`: 股票行情
- `KlineData`: K线数据
- `Strategy`: 策略定义

#### 5. 核心模块 (`core/`)

提供基础功能和配置。

**核心组件**:
- `config.py`: 配置管理
- `database.py`: 数据库连接池
- `base_service.py`: 服务基类

---

## 前端架构

### 目录结构

```
frontend/
├── public/
├── src/
│   ├── api/                        # API调用层
│   │   ├── backtestReports.ts      # 回测报告API
│   │   └── ...
│   │
│   ├── components/                 # 组件库
│   │   ├── layout/
│   │   │   └── Sidebar.tsx        # 侧边栏
│   │   └── ...
│   │
│   ├── hooks/                      # 自定义Hooks
│   │   └── ...
│   │
│   ├── pages/                      # 页面组件
│   │   ├── AIAgent.tsx            # AI智能体
│   │   ├── BacktestReport.tsx     # 回测报告
│   │   ├── Strategies.tsx         # 策略管理
│   │   └── ...
│   │
│   ├── pages/components/           # 页面级组件
│   │   └── AIAgent/
│   │       ├── AIConsultant.tsx   # AI咨询
│   │       ├── Header.tsx         # 头部组件
│   │       ├── HistoryDecisions.tsx # 历史决策
│   │       ├── KLineChart.tsx     # K线图表
│   │       └── StockInfo.tsx      # 股票信息
│   │
│   ├── types/                      # TypeScript类型定义
│   │   ├── backtest.ts            # 回测类型
│   │   └── ...
│   │
│   ├── App.tsx                    # 应用根组件
│   ├── App.css
│   ├── index.css
│   └── index.tsx
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

### 前端模块说明

#### 1. 页面层 (`pages/`)

应用的主要页面组件。

**核心页面**:
- `Strategies.tsx`: 策略管理页面
  - 策略列表展示
  - 回测参数配置
  - 回测执行
  - 结果预览
  
- `BacktestReport.tsx`: 回测报告页面
  - K线图表展示
  - 成交量直方图
  - 交易明细
  - 报告文件管理

- `AIAgent.tsx`: AI智能体页面
  - 实时行情
  - AI咨询
  - 历史决策
  - K线分析

#### 2. API层 (`api/`)

封装后端API调用。

**核心模块**:
- `backtestReports.ts`: 回测报告API
  - `getBacktestReports()`: 获取报告列表
  - `saveBacktestReport()`: 保存报告
  - `loadBacktestReport()`: 加载报告
  - `deleteBacktestReport()`: 删除报告

#### 3. 组件层 (`components/`)

可复用的UI组件。

#### 4. 类型层 (`types/`)

TypeScript类型定义。

**核心类型**:
- `backtest.ts`: 回测相关类型
  - `BacktestResult`: 回测结果
  - `EquityPoint`: 净值曲线点
  - `TradeRecord`: 交易记录

---

## 数据流

### 回测数据流

```
用户请求 (Strategies.tsx)
    ↓
HTTP POST /api/v1/strategies/{id}/backtest
    ↓
API层 (strategies.py)
    ↓
服务层 (backtest_service.py)
    ├─ DataFetcher获取数据
    │   └─ 数据适配器 (akshare_adapter.py)
    │       └─ AkShare API
    ├─ 计算技术指标
    ├─ 运行回测模拟
    └─ 生成报告
        └─ 保存到文件系统
    ↓
HTTP Response
    ↓
前端处理 (BacktestReport.tsx)
    ├─ displayData转换
    ├─ ECharts渲染
    └─ 用户交互
```

### 回测报告数据流

```
保存报告:
    ↓
用户点击"保存报告"
    ↓
saveBacktestReport(backtestData, strategyName)
    ↓
HTTP POST /api/v1/backtest-reports
    ↓
API层 (backtest_reports.py)
    ├─ 生成文件名: {stock_code}_{strategy}_{timestamp}.json
    └─ 保存到: backend/data/backtest_reports/
    ↓
返回文件名和元数据
    ↓
刷新报告列表

加载报告:
    ↓
用户选择报告
    ↓
loadBacktestReport(filename)
    ↓
HTTP GET /api/v1/backtest-reports/{filename}
    ↓
API层读取文件
    ↓
返回报告数据
    ↓
前端更新displayData
    ↓
重新渲染图表
```

---

## 模块依赖关系

### 后端依赖图

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ strategies  │  │market        │  │backtest_     │ │
│  │             │  │              │  │reports       │ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼────────────────┼─────────────────┼─────────┘
          │                │                 │
          └────────────────┼─────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
┌─────────▼────────┐ ┌───▼─────────┐ ┌───▼─────────────┐
│  Services Layer  │ │ AI Layer    │ │ Optimizers      │
│  ┌────────────┐  │ │             │ │                 │
│  │backtest_   │  │ │ai_service  │ │bayesian,       │
│  │service     │  │ │            │ │genetic,        │
│  └─────┬──────┘  │ └─────────────┘ │grid_search     │
│        │         │                 │                 │
│  ┌─────▼──────┐  │                 └─────────────────┘
│  │data_fetcher│  │
│  └─────┬──────┘  │
│        │         │
└────────┼─────────┘
         │
         ▼
┌────────────────────────────────────────┐
│      Data Adapters Layer             │
│  ┌────────┐  ┌────────┐  ┌───────┐  │
│  │AkShare │  │Baostock│  │Tushare│  │
│  │        │  │        │  │       │  │
│  └────────┘  └────────┘  └───────┘  │
└────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│      External Data Sources            │
│  ┌──────────────┐  ┌──────────────┐  │
│  │AkShare API   │  │Baostock API  │  │
│  └──────────────┘  └──────────────┘  │
└────────────────────────────────────────┘
```

### 前端依赖图

```
┌─────────────────────────────────────────────────┐
│              App.tsx (Root)                    │
└───────────────┬─────────────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │   Router      │
        └───────┬───────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼──────┐ ┌─▼────────┐ ┌─▼─────────────┐
│Strategies│ │AIAgent   │ │BacktestReport │
│          │ │          │ │               │
└────┬─────┘ └────┬─────┘ └───────┬───────┘
     │            │                 │
     │            │                 │
     │        ┌───▼─────────────────▼───┐
     │        │     API Layer           │
     │        │  backtestReports.ts     │
     │        └───────────┬─────────────┘
     │                    │
     │            ┌───────▼─────────────┐
     │            │   HTTP Requests     │
     │            └───────────┬─────────┘
     │                        │
     │            ┌───────────▼─────────────┐
     │            │    Backend APIs        │
     │            └───────────────────────┘
     │
     └───────────┐
                 │
        ┌────────▼───────────┐
        │  Type Definitions  │
        │  backtest.ts       │
        └────────────────────┘
```

---

## 测试框架

### 测试结构

```
backend/test/
├── api/                      # API测试
│   ├── test_endpoints.py
│   ├── test_market_api.py
│   └── test_simple.py
│
├── core/                     # 核心模块测试
│
├── data_adapters/            # 数据适配器测试
│   ├── test_duckdb_adapter.py
│   ├── test_minute_download.py
│   ├── test_real_sources.py
│   └── test_storage.py
│
├── services/                 # 服务层测试
│   ├── test_backtest_volume.py    # 回测成交量测试 ⭐
│   ├── test_data_download_service.py
│   └── test_stock_code_service.py
│
└── utils/                    # 工具测试
    └── test_startup.py
```

### 回测成交量测试

**文件**: `backend/test/services/test_backtest_volume.py`

**测试流程**:

1. **步骤1: 测试数据获取器**
   - 验证数据适配器是否返回volume数据
   - 检查DataFrame列结构
   - 验证volume数据类型和有效性

2. **步骤2: 测试回测引擎**
   - 验证回测引擎是否保留volume数据
   - 检查portfolio DataFrame中的volume列
   - 验证equity_curve中的volume字段

3. **步骤3: 测试API响应**
   - 验证API响应格式
   - 检查equity_curve数据完整性
   - 确认volume数据正确传递

**运行测试**:

```bash
cd backend
python test/services/test_backtest_volume.py
```

**预期输出**:

```
================================================================================
步骤1: 测试数据获取器
================================================================================
获取到 61 条数据
DataFrame列: ['open', 'high', 'low', 'close', 'volume']
是否有volume列: True
volume数据类型: int64
volume非空数量: 61
非零volume数量: 61

================================================================================
步骤2: 测试回测引擎
================================================================================
第一个数据点keys: dict_keys(['date', 'total_value', 'cumulative_return', 
'drawdown', 'open', 'high', 'low', 'close', 'volume'])
第一个数据点是否有volume: True
第一个数据点volume值: 51144
有volume的数据点数量: 61/61

================================================================================
步骤3: 测试API响应格式
================================================================================
has_volume: True

================================================================================
测试完成！
================================================================================

总结:
1. 数据获取器: ✓ 包含volume数据
2. 回测引擎: ✓ 保留volume数据
3. API响应: ✓ 正确传递volume数据
```

---

## 最佳实践

### 后端

1. **分层架构**: 严格遵循 API → Service → Adapter 分层
2. **依赖注入**: 使用依赖注入管理组件
3. **异步编程**: 使用asyncio提高性能
4. **错误处理**: 统一的错误处理和日志记录
5. **数据验证**: 使用Pydantic进行数据验证

### 前端

1. **组件化**: 合理拆分组件，提高复用性
2. **类型安全**: 充分利用TypeScript类型系统
3. **状态管理**: 合理使用React Hooks和Context
4. **性能优化**: 使用useMemo和useCallback优化性能
5. **错误边界**: 实现错误边界组件

### 测试

1. **单元测试**: 每个服务和方法都应有单元测试
2. **集成测试**: 测试模块间交互
3. **端到端测试**: 测试完整业务流程
4. **测试覆盖率**: 保持高测试覆盖率

---

## 维护指南

### 添加新数据源

1. 在 `data_adapters/` 创建新的适配器
2. 继承 `BaseAdapter` 类
3. 实现所有必需方法
4. 在 `AdapterFactory` 中注册
5. 添加测试用例

### 添加新策略

1. 在 `backtest_service.py` 的 `_calculate_indicators` 中添加新策略类型
2. 实现指标计算逻辑
3. 在前端 `Strategies.tsx` 添加策略选项
4. 添加参数配置UI
5. 编写测试用例

### 修改UI组件

1. 确保类型定义完整
2. 保持组件职责单一
3. 添加适当的错误处理
4. 更新文档
5. 测试各种边界情况

---

## 总结

本文档描述了股票量化交易系统的模块化架构，包括：

- 清晰的分层设计
- 松耦合的模块依赖
- 完善的测试框架
- 标准化的开发流程

通过遵循这些架构原则，系统具有良好的：
- **可维护性**: 模块化设计便于维护和扩展
- **可测试性**: 完善的测试框架确保质量
- **可扩展性**: 易于添加新功能和数据源
- **可重用性**: 组件和服务可复用

---

**文档版本**: 1.0  
**最后更新**: 2026-02-17  
**维护者**: 开发团队