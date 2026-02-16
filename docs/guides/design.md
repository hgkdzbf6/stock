# 量化交易平台系统设计文档

## 1. 项目概述

### 1.1 项目目标
构建一个基于AI驱动的全功能量化交易平台，支持：
- 实时A股市场数据获取与展示
- 智能交易策略回测与优化
- AI辅助投资分析与咨询
- 多数据源整合与容错机制
- 可视化图表与交互界面

### 1.2 核心特性
- **多数据源支持**：集成多个A股数据源，自动容错切换
- **智能缓存机制**：Redis缓存 + 内存缓存，提升响应速度
- **AI咨询系统**：基于GLM大语言模型的智能投资顾问
- **策略优化引擎**：支持网格搜索、遗传算法、贝叶斯优化
- **实时数据推送**：WebSocket实时行情推送
- **可视化图表**：K线图、技术指标图表、回测结果可视化

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ 行情展示 │  │ 策略管理 │  │ AI咨询   │  │ 回测分析 │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓ WebSocket / HTTP
┌─────────────────────────────────────────────────────────────┐
│                         API层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ 行情API  │  │ 策略API  │  │ AI API   │  │ 交易API  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       服务层                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │数据获取  │  │ 策略引擎 │  │ AI服务   │  │ 风控模块 │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │缓存服务  │  │ 回测服务 │  │ 优化引擎 │  │ 订单管理 │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       数据层                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ PostgreSQL│  │  Redis   │  │ DuckDB   │  │ 文件存储 │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       数据源层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Baostock │  │ Akshare  │  │ Tushare  │  │ Eastmoney│     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈

#### 前端技术栈
- **框架**：React 18 + TypeScript
- **UI组件**：Ant Design
- **图表库**：ECharts + Lightweight Charts
- **状态管理**：Zustand
- **数据请求**：React Query + Axios
- **路由**：React Router
- **构建工具**：Vite
- **样式**：Tailwind CSS + CSS Modules

#### 后端技术栈
- **框架**：FastAPI
- **语言**：Python 3.11+
- **数据库**：PostgreSQL (主数据库), DuckDB (数据仓库)
- **缓存**：Redis (缓存层)
- **异步任务**：Celery + Redis
- **ORM**：SQLAlchemy
- **验证**：Pydantic
- **日志**：Loguru
- **测试**：Pytest

#### AI/机器学习
- **LLM**：GLM-4.7 (智谱AI)
- **优化算法**：SciPy (网格搜索), DEAP (遗传算法), Optuna (贝叶斯优化)
- **回测引擎**：Backtrader
- **技术指标**：TA-Lib

### 2.3 数据源设计

#### 数据源优先级
1. **Baostock** - 免费、稳定、数据完整
2. **Akshare** - 数据丰富、更新及时
3. **Tushare** - 专业数据、需token
4. **Eastmoney** - 实时行情、接口开放

#### 数据源适配器模式
```python
class BaseAdapter(ABC):
    """数据源适配器基类"""
    
    @abstractmethod
    def get_kline_data(self, symbol: str, start_date: str, 
                      end_date: str, freq: str) -> pd.DataFrame:
        """获取K线数据"""
        pass
    
    @abstractmethod
    def get_realtime_quote(self, symbol: str) -> dict:
        """获取实时行情"""
        pass
    
    @abstractmethod
    def get_stock_list(self, page: int, page_size: int) -> list:
        """获取股票列表"""
        pass
```

#### 数据源容错机制
- 自动故障切换：当主数据源失败时，自动切换到备用数据源
- 超时控制：设置合理的超时时间，避免长时间等待
- 错误重试：网络错误时自动重试（最多3次）
- 数据验证：对返回数据进行格式和完整性验证
- 缓存降级：当所有数据源失败时，使用缓存数据

## 3. 核心模块设计

### 3.1 数据获取模块 (Data Fetcher)

#### 功能特性
- 多数据源聚合
- 智能缓存策略
- 异步数据加载
- 数据格式标准化

#### 缓存策略
```
L1: 内存缓存 (LRU, 1000条, 5分钟过期)
    ↓ 缓存未命中
L2: Redis缓存 (30分钟过期)
    ↓ 缓存未命中
L3: 数据源获取
    ↓
写入 L2 和 L1 缓存
```

#### 数据流程
1. 检查内存缓存
2. 检查Redis缓存
3. 按优先级尝试数据源
4. 数据标准化处理
5. 写入缓存
6. 返回数据

### 3.2 策略引擎模块 (Strategy Engine)

#### 策略基类
```python
class BaseStrategy(ABC):
    """策略基类"""
    
    @abstractmethod
    def initialize(self, context: Context):
        """策略初始化"""
        pass
    
    @abstractmethod
    def handle_data(self, context: Context, data: BarData):
        """处理行情数据"""
        pass
    
    @abstractmethod
    def generate_signals(self, context: Context) -> List[Signal]:
        """生成交易信号"""
        pass
```

#### 内置策略
1. **移动平均线策略 (MA Crossover)**
   - 双均线金叉/死叉
   - 可配置周期（5/10/20/60日）
   - 成交量确认

2. **MACD策略**
   - MACD金叉/死叉
   - DIF与DEA交叉
   - 柱状图背离

3. **布林带策略 (Bollinger Bands)**
   - 价格突破上轨/下轨
   - 收缩突破
   - 回归中轨

4. **RSI策略**
   - 超买超卖信号
   - 背离信号
   - RSI与价格交叉

### 3.3 参数优化模块 (Optimizer)

#### 优化算法对比

| 算法 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 网格搜索 | 简单直观、可并行 | 计算量大、效率低 | 参数空间小 |
| 遗传算法 | 全局搜索、不依赖梯度 | 参数调优复杂、收敛慢 | 参数空间大、非线性 |
| 贝叶斯优化 | 样本效率高、智能采样 | 易陷入局部最优 | 参数少、计算成本高 |

#### 优化流程
1. 定义参数空间
2. 选择优化算法
3. 执行回测评估
4. 更新参数建议
5. 迭代优化
6. 输出最优参数

### 3.4 回测模块 (Backtest)

#### 回测引擎特性
- 事件驱动架构
- 滑点模拟
- 手续费计算
- 多策略回测
- 并行回测
- 结果可视化

#### 性能指标
- **收益率指标**：总收益率、年化收益率、累计收益
- **风险指标**：最大回撤、波动率、夏普比率、Sortino比率
- **交易指标**：胜率、盈亏比、交易次数、平均持仓天数
- **其他指标**：Alpha、Beta、信息比率、卡尔玛比率

### 3.5 AI咨询模块 (AI Service)

#### 功能设计
1. **市场分析**
   - 大盘走势分析
   - 行业热点解读
   - 个股基本面分析

2. **策略建议**
   - 基于技术指标的策略推荐
   - 风险评估
   - 仓位建议

3. **知识问答**
   - 投资知识问答
   - 策略原理解释
   - 技术指标说明

#### Prompt模板设计
```python
MARKET_ANALYSIS_PROMPT = """
你是一位专业的股票投资顾问。请基于以下市场数据进行分析：

{market_data}

请提供：
1. 市场整体趋势分析
2. 行业板块表现
3. 投资建议
4. 风险提示

要求：专业、客观、数据驱动。
"""
```

### 3.6 风控模块 (Risk Control)

#### 风控规则
1. **仓位控制**
   - 单只股票最大仓位限制
   - 行业最大仓位限制
   - 总仓位上限

2. **止损止盈**
   - 移动止损
   - 固定止损比例
   - 时间止损

3. **交易频率**
   - 单日最大交易次数
   - 最小交易间隔
   - 冷却期机制

4. **风险指标监控**
   - 实时监控回撤
   - 波动率告警
   - 相关性检查

## 4. 数据库设计

### 4.1 PostgreSQL表结构

#### 股票表 (stocks)
```sql
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    market VARCHAR(20),
    industry VARCHAR(50),
    listed_date DATE,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 策略表 (strategies)
```sql
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    parameters JSONB,
    description TEXT,
    status VARCHAR(20),
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 回测结果表 (backtest_results)
```sql
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    symbol VARCHAR(20),
    start_date DATE,
    end_date DATE,
    total_return DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    win_rate DECIMAL(5, 2),
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Redis数据结构

#### 实时行情缓存
```
Key: quote:{symbol}
Type: Hash
Fields: price, change, change_pct, volume, timestamp
TTL: 5分钟
```

#### K线数据缓存
```
Key: kline:{symbol}:{freq}:{start_date}:{end_date}
Type: String (JSON)
TTL: 30分钟
```

#### 股票列表缓存
```
Key: stock_list:{page}:{page_size}
Type: String (JSON)
TTL: 1小时
```

### 4.3 DuckDB数据仓库

#### 历史K线数据表
```sql
CREATE TABLE kline_data (
    symbol VARCHAR(20),
    date DATE,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    volume BIGINT,
    amount DECIMAL(20, 2),
    PRIMARY KEY (symbol, date)
);
```

#### 技术指标表
```sql
CREATE TABLE technical_indicators (
    symbol VARCHAR(20),
    date DATE,
    ma5 DECIMAL(10, 2),
    ma10 DECIMAL(10, 2),
    ma20 DECIMAL(10, 2),
    macd DECIMAL(10, 4),
    dif DECIMAL(10, 4),
    dea DECIMAL(10, 4),
    rsi DECIMAL(5, 2),
    PRIMARY KEY (symbol, date)
);
```

## 5. API设计

### 5.1 行情API

#### 获取实时行情
```
GET /api/v1/market/quote/{symbol}
Response: {
  "code": 200,
  "message": "success",
  "data": {
    "stock_code": "sh600000.SZ",
    "price": 10.5,
    "change": 0.3,
    "change_pct": 2.94,
    "volume": 1000000,
    "timestamp": "2024-01-01T10:00:00"
  }
}
```

#### 获取K线数据
```
GET /api/v1/market/kline/{symbol}?start_date=2024-01-01&end_date=2024-01-31&freq=daily
Response: {
  "code": 200,
  "message": "success",
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00",
      "open": 10.0,
      "high": 10.5,
      "low": 9.8,
      "close": 10.2,
      "volume": 1000000
    }
  ]
}
```

### 5.2 策略API

#### 创建策略
```
POST /api/v1/strategies
Request: {
  "name": "双均线策略",
  "type": "ma_crossover",
  "parameters": {
    "short_period": 5,
    "long_period": 20
  }
}
Response: {
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "双均线策略",
    "type": "ma_crossover"
  }
}
```

#### 执行回测
```
POST /api/v1/strategies/{id}/backtest
Request: {
  "symbol": "sh600000.SZ",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
Response: {
  "code": 200,
  "message": "success",
  "data": {
    "total_return": 0.25,
    "max_drawdown": -0.08,
    "sharpe_ratio": 1.5,
    "win_rate": 0.6
  }
}
```

### 5.3 AI API

#### AI咨询
```
POST /api/v1/ai/consult
Request: {
  "question": "请分析贵州茅台的投资价值",
  "context": {
    "symbol": "sh600519.SZ",
    "market_data": {...}
  }
}
Response: {
  "code": 200,
  "message": "success",
  "data": {
    "answer": "...",
    "analysis": {...}
  }
}
```

## 6. 部署架构

### 6.1 容器化部署

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (反向代理)                      │
└─────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            ↓                           ↓
┌─────────────────────┐     ┌─────────────────────┐
│   Frontend (React)  │     │   Backend (FastAPI) │
│   Port: 3000        │     │   Port: 8000        │
└─────────────────────┘     └─────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ↓                       ↓                       ↓
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   PostgreSQL        │  │   Redis             │  │   Celery Worker      │
│   Port: 5432        │  │   Port: 6379        │  │   异步任务处理        │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

### 6.2 环境配置

#### 开发环境
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENV=development
      - DATABASE_URL=postgresql://user:pass@postgres:5432/stock
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    depends_on:
      - backend

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=stock
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### 生产环境
- 使用Kubernetes编排
- 配置自动扩缩容
- 设置资源限制
- 配置健康检查
- 日志聚合（ELK Stack）
- 监控告警（Prometheus + Grafana）

## 7. 开发路线图

### Phase 1: 基础平台 ✅ (已完成)
- [x] 后端基础架构
- [x] 前端基础架构
- [x] 多数据源集成
- [x] 行情数据展示
- [x] K线图组件
- [x] WebSocket实时推送
- [x] 缓存机制

### Phase 2: AI智能咨询 ✅ (已完成)
- [x] GLM-4.7 API集成
- [x] Prompt模板设计
- [x] AI聊天界面
- [x] 市场分析功能
- [x] 策略建议功能

### Phase 3: 策略优化 (进行中)
- [ ] 策略参数配置
- [x] 网格搜索优化
- [x] 遗传算法优化
- [x] 贝叶斯优化
- [x] 回测引擎
- [ ] 回测结果可视化

### Phase 4: 实盘交易 (计划中)
- [ ] 券商API对接
- [ ] 订单管理系统
- [ ] 持仓管理
- [ ] 风险控制
- [ ] 监控告警

### Phase 5: 高级功能 (计划中)
- [ ] 多策略组合
- [ ] 投资组合优化
- [ ] 因子分析
- [ ] 机器学习预测
- [ ] 社区分享

## 8. 性能优化

### 8.1 前端优化
- 代码分割和懒加载
- 虚拟滚动（大列表）
- 图表数据聚合
- 防抖和节流
- Service Worker缓存

### 8.2 后端优化
- 数据库索引优化
- 查询优化
- 连接池配置
- 异步IO
- 批量处理
- 数据压缩

### 8.3 缓存优化
- 多级缓存策略
- 缓存预热
- 缓存击穿保护
- 缓存雪崩防护

## 9. 安全设计

### 9.1 认证授权
- JWT Token认证
- RBAC权限控制
- API限流
- CORS配置

### 9.2 数据安全
- 数据加密传输
- 敏感信息脱敏
- SQL注入防护
- XSS防护

### 9.3 交易安全
- 双重验证
- 操作日志
- 异常交易告警
- 资金安全锁

## 10. 监控与运维

### 10.1 监控指标
- 系统资源监控（CPU、内存、磁盘）
- 数据库性能监控
- API响应时间
- 错误率监控
- 交易成功率

### 10.2 日志管理
- 结构化日志
- 日志分级
- 日志聚合
- 日志保留策略

### 10.3 告警机制
- 系统异常告警
- 交易异常告警
- 数据异常告警
- 性能告警

## 11. 测试策略

### 11.1 单元测试
- 覆盖率目标：80%+
- 核心业务逻辑100%覆盖
- 使用pytest框架

### 11.2 集成测试
- API接口测试
- 数据库集成测试
- 第三方服务测试

### 11.3 回测验证
- 历史数据回测
- 样本外测试
- 滑点和手续费模拟

### 11.4 压力测试
- 并发用户测试
- 数据量测试
- 极限情况测试

## 12. 未来规划

### 12.1 功能扩展
- 期货、期权支持
- 港股、美股支持
- 数字货币支持
- 社交交易功能
- 策略市场

### 12.2 技术升级
- 微服务架构
- 事件驱动架构
- 区块链技术应用
- 边缘计算

### 12.3 生态建设
- 开放API平台
- 策略开发者社区
- 数据生态合作
- 教育培训体系

---

**文档版本**: v2.0  
**最后更新**: 2026-02-16  
**维护者**: Stock Platform Team