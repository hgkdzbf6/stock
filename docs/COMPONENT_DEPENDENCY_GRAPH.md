# 组件依赖关系图

本文档使用Mermaid图表展示系统的组件依赖关系。

## 系统整体架构

```mermaid
graph TB
    subgraph "前端 Frontend"
        A[App.tsx]
        B[Router]
        C[Strategies.tsx]
        D[BacktestReport.tsx]
        E[AIAgent.tsx]
        F[API Layer]
        G[Type Definitions]
        
        A --> B
        B --> C
        B --> D
        B --> E
        C --> F
        D --> F
        E --> F
        D --> G
        C --> G
        E --> G
    end
    
    subgraph "后端 Backend"
        H[API Layer]
        I[Services Layer]
        J[Data Adapters]
        K[External Data Sources]
        L[AI Layer]
        M[Optimizers]
        
        H --> I
        H --> L
        H --> M
        I --> J
        J --> K
    end
    
    F -.HTTP.-> H
```

## 回测流程详细依赖图

```mermaid
sequenceDiagram
    participant U as 用户
    participant S as Strategies.tsx
    participant API as strategies.py
    participant BS as backtest_service.py
    participant DF as DataFetcher
    participant AD as akshare_adapter.py
    participant AK as AkShare API
    
    U->>S: 点击回测
    S->>S: 收集参数
    S->>API: POST /strategies/{id}/backtest
    API->>BS: run_backtest()
    BS->>DF: get_data()
    DF->>AD: get_kline_data()
    AD->>AK: 获取K线数据
    AK-->>AD: OHLCV数据
    AD-->>DF: KlineData[]
    DF-->>BS: DataFrame with volume
    BS->>BS: _calculate_indicators()
    BS->>BS: _run_backtest_simulation()
    BS->>BS: _calculate_metrics()
    BS->>BS: _generate_equity_curve()
    BS-->>API: BacktestResult with volume
    API-->>S: HTTP Response
    S->>S: 更新backtestResult
    S->>U: 显示预览
    U->>S: 点击查看详细报告
    S->>D: navigate with state
```

## 回测报告文件管理流程

```mermaid
graph LR
    subgraph "保存流程"
        A[用户点击保存] --> B[saveBacktestReport]
        B --> C[POST /backtest-reports]
        C --> D[backtest_reports.py]
        D --> E[生成文件名]
        E --> F[保存JSON文件]
        F --> G[返回元数据]
        G --> H[刷新列表]
    end
    
    subgraph "加载流程"
        I[用户选择报告] --> J[loadBacktestReport]
        J --> K[GET /backtest-reports/{filename}]
        K --> L[backtest_reports.py]
        L --> M[读取文件]
        M --> N[返回报告数据]
        N --> O[更新displayData]
        O --> P[重新渲染图表]
    end
    
    subgraph "删除流程"
        Q[用户点击删除] --> R[deleteBacktestReport]
        R --> S[DELETE /backtest-reports/{filename}]
        S --> T[backtest_reports.py]
        T --> U[删除文件]
        U --> V[刷新列表]
    end
```

## 后端分层架构依赖图

```mermaid
graph TB
    subgraph "API Layer"
        A1[strategies.py]
        A2[backtest_reports.py]
        A3[market.py]
        A4[stocks.py]
        A5[trading.py]
    end
    
    subgraph "Services Layer"
        S1[backtest_service.py]
        S2[data_fetcher.py]
        S3[market_service.py]
        S4[cache_service.py]
        S5[optimization_service.py]
    end
    
    subgraph "Data Adapters Layer"
        D1[akshare_adapter.py]
        D2[baostock_adapter.py]
        D3[tushare_adapter.py]
        D4[duckdb_adapter.py]
        D5[base.py]
    end
    
    subgraph "Models Layer"
        M1[quote.py]
        M2[stock.py]
        M3[strategy.py]
    end
    
    subgraph "Core Layer"
        C1[config.py]
        C2[database.py]
        C3[base_service.py]
        C4[security.py]
    end
    
    subgraph "AI Layer"
        AI1[ai_service.py]
        AI2[llm_client.py]
        AI3[prompt_templates.py]
    end
    
    subgraph "Optimizers"
        O1[bayesian.py]
        O2[genetic.py]
        O3[grid_search.py]
    end
    
    A1 --> S1
    A1 --> S5
    A2 --> S1
    A3 --> S3
    A4 --> S2
    A5 --> S1
    
    S1 --> S2
    S1 --> S4
    S1 --> M3
    S2 --> D5
    S2 --> D1
    S2 --> D2
    S2 --> D3
    S3 --> M1
    S4 --> C2
    
    D1 --> D5
    D2 --> D5
    D3 --> D5
    D4 --> D5
    
    M1 --> C3
    M2 --> C3
    M3 --> C3
    
    A1 --> AI1
    AI1 --> AI2
    AI1 --> AI3
    
    S5 --> O1
    S5 --> O2
    S5 --> O3
    
    C3 --> C1
    C3 --> C2
    C3 --> C4
```

## 前端组件依赖图

```mermaid
graph TB
    subgraph "页面层 Pages"
        P1[Strategies.tsx]
        P2[BacktestReport.tsx]
        P3[AIAgent.tsx]
    end
    
    subgraph "页面组件 Page Components"
        PC1[AIConsultant.tsx]
        PC2[Header.tsx]
        PC3[HistoryDecisions.tsx]
        PC4[KLineChart.tsx]
        PC5[StockInfo.tsx]
    end
    
    subgraph "布局组件 Layout Components"
        LC1[Sidebar.tsx]
    end
    
    subgraph "API层 API Layer"
        API1[backtestReports.ts]
        API2[market.ts]
        API3[stocks.ts]
    end
    
    subgraph "类型层 Type Definitions"
        T1[backtest.ts]
        T2[market.ts]
        T3[stock.ts]
    end
    
    subgraph "工具库 Libraries"
        L1[React ECharts]
        L2[React Router]
        L3[Axios]
        L4[Lucide React]
    end
    
    P1 --> API1
    P1 --> API2
    P1 --> T3
    
    P2 --> API1
    P2 --> T1
    P2 --> L1
    
    P3 --> PC1
    P3 --> PC2
    P3 --> PC3
    P3 --> PC4
    P3 --> PC5
    P3 --> API2
    P3 --> T2
    
    PC1 --> API2
    PC4 --> T1
    PC4 --> L1
    
    P1 --> L2
    P2 --> L2
    P3 --> L2
    
    P1 --> L4
    P2 --> L4
    P3 --> L4
```

## 数据流转图 - 回测成交量数据

```mermaid
graph TB
    subgraph "数据源 Data Source"
        DS[AkShare API]
    end
    
    subgraph "数据适配器 Data Adapter"
        DA[AkShareAdapter]
        DM[Data Models<br/>KlineData]
    end
    
    subgraph "数据获取器 Data Fetcher"
        DF[DataFetcher]
        DT[DataTransformer]
    end
    
    subgraph "回测引擎 Backtest Engine"
        BE[BacktestEngine]
        CI[_calculate_indicators]
        RB[_run_backtest_simulation]
        CM[_calculate_metrics]
        GE[_generate_equity_curve]
    end
    
    subgraph "API层 API Layer"
        API[strategies.py]
        R[Response]
    end
    
    subgraph "前端 Frontend"
        BR[BacktestReport.tsx]
        DD[displayData]
        EC[ECharts]
    end
    
    DS --> DA
    DA --> DM
    DA --> DF
    DF --> DT
    DF --> BE
    BE --> CI
    BE --> RB
    BE --> CM
    BE --> GE
    GE -.contains.-> R
    R --> API
    API --> BR
    BR --> DD
    DD --> EC
```

## 成交量数据验证流程

```mermaid
flowchart TD
    Start[开始测试] --> Step1[测试数据获取器]
    Step1 --> Check1{DataFrame有volume列?}
    Check1 -->|否| Error1[❌ 数据源未返回volume]
    Check1 -->|是| Check2{volume数据有效?}
    Check2 -->|否| Error2[❌ volume全为0或NaN]
    Check2 -->|是| Step2[测试回测引擎]
    
    Step2 --> Check3{portfolio有volume列?}
    Check3 -->|否| Error3[❌ 回测引擎未保留volume]
    Check3 -->|是| Check4{equity_curve有volume?}
    Check4 -->|否| Error4[❌ _generate_equity_curve未添加volume]
    Check4 -->|是| Step3[测试API响应]
    
    Step3 --> Check5{API响应包含volume?}
    Check5 -->|否| Error5[❌ API未传递volume]
    Check5 -->|是| Success[✅ 所有测试通过]
    
    Error1 --> End[结束]
    Error2 --> End
    Error3 --> End
    Error4 --> End
    Error5 --> End
    Success --> End
```

## 测试框架结构图

```mermaid
graph TB
    subgraph "测试框架 Test Framework"
        T[backend/test/]
        
        subgraph "API测试 API Tests"
            TA[test_endpoints.py]
            TM[test_market_api.py]
            TS[test_simple.py]
        end
        
        subgraph "数据适配器测试 Adapter Tests"
            TD[test_duckdb_adapter.py]
            TMN[test_minute_download.py]
            TR[test_real_sources.py]
            TST[test_storage.py]
        end
        
        subgraph "服务测试 Service Tests"
            TBV[test_backtest_volume.py ⭐]
            TDD[test_data_download_service.py]
            TSC[test_stock_code_service.py]
        end
        
        subgraph "工具测试 Utils Tests"
            TU[test_startup.py]
        end
    end
    
    TBV --> S1[backtest_service.py]
    TBV --> S2[data_fetcher.py]
    TBV --> S3[AkShareAdapter]
    
    TDD --> S4[data_download_service.py]
    TSC --> S5[stock_code_service.py]
```

## 完整系统依赖关系（简化版）

```mermaid
graph LR
    subgraph "用户界面 UI"
        UI[浏览器]
    end
    
    subgraph "前端 Frontend"
        FE[React App]
    end
    
    subgraph "API网关 API Gateway"
        API[FastAPI Server]
    end
    
    subgraph "业务逻辑 Business Logic"
        BL[Services]
    end
    
    subgraph "数据访问 Data Access"
        DA[Adapters]
    end
    
    subgraph "数据源 Data Sources"
        DS[AkShare, Baostock, etc.]
    end
    
    subgraph "存储 Storage"
        DB[(SQLite/DuckDB)]
        FS[(File System)]
    end
    
    UI --> FE
    FE --> API
    API --> BL
    BL --> DA
    DA --> DS
    BL --> DB
    BL --> FS
```

## 模块依赖关系矩阵

| 模块 | API | Services | Adapters | Models | Core | Frontend | 测试 |
|------|-----|----------|----------|--------|------|----------|------|
| API Layer | - | ✓ | - | ✓ | ✓ | - | ✓ |
| Services Layer | ✓ | - | ✓ | ✓ | - | - | ✓ |
| Data Adapters | - | ✓ | - | ✓ | - | - | ✓ |
| Models | ✓ | ✓ | ✓ | - | - | - | ✓ |
| Core | - | ✓ | ✓ | ✓ | - | - | ✓ |
| Frontend | ✓ | - | - | - | - | - | - |
| 测试 | ✓ | ✓ | ✓ | ✓ | ✓ | - | - |

图例：
- ✓ 表示有依赖关系
- - 表示无直接依赖

## 使用说明

### 在GitHub上查看

Mermaid图表在GitHub上会自动渲染，直接查看此文件即可。

### 在本地预览

1. 安装VS Code的Mermaid插件
2. 或使用在线预览工具：https://mermaid.live/
3. 复制Mermaid代码块到编辑器中预览

### 生成图片

```bash
# 安装mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# 生成PNG图片
mmdc -i COMPONENT_DEPENDENCY_GRAPH.md -o dependency-graph.png

# 生成SVG图片
mmdc -i COMPONENT_DEPENDENCY_GRAPH.md -o dependency-graph.svg
```

---

**文档版本**: 1.0  
**最后更新**: 2026-02-17  
**维护者**: 开发团队