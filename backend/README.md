# Stock Platform Backend

AI驱动的量化交易平台 - 后端服务

## 技术栈

- **框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy
- **缓存**: Redis
- **认证**: JWT
- **日志**: Loguru

## 安装

1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置
```

4. 初始化数据库
```bash
# 创建数据库表
python -c "from core.database import init_db; import asyncio; asyncio.run(init_db())"
```

## 运行

### 开发模式
```bash
python main.py
```

### 生产模式
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API文档

启动服务后，访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── api/                 # API路由
│   ├── auth.py          # 认证API
│   ├── stocks.py        # 股票API
│   ├── market.py        # 行情API
│   └── strategies.py    # 策略API
├── core/                # 核心配置
│   ├── config.py        # 配置管理
│   ├── database.py      # 数据库连接
│   └── security.py      # 安全认证
├── models/              # 数据模型
│   ├── user.py
│   ├── stock.py
│   ├── quote.py
│   └── strategy.py
├── services/            # 业务逻辑
│   ├── data_fetcher.py  # 数据获取
│   ├── market_service.py # 市场服务
│   └── cache_service.py # 缓存服务
├── utils/               # 工具类
├── main.py              # 应用入口
└── requirements.txt     # 依赖清单
```

## 环境变量

见 `.env.example` 文件

## 开发说明

1. 代码风格遵循PEP 8
2. 使用异步编程
3. 所有API需要有完整的文档
4. 使用loguru记录日志

## 测试

```bash
# 运行测试
pytest

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```
