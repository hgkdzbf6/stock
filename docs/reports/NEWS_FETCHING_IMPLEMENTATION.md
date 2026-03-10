# 新闻获取功能实施报告

## 概述

新闻获取功能允许用户从网络获取股票和板块的最新RSS新闻订阅信息，并结合基本面数据进行总结，输出可直接用于舆情分析页面分析的信息。

## 实施日期

2026年2月20日

## 功能特性

### 1. 新闻获取服务

#### 1.1 获取股票新闻
- 支持按股票代码和名称获取相关新闻
- 自动从多个RSS源获取新闻
- 基于关键词过滤相关新闻
- 去重和按时间排序

#### 1.2 获取板块新闻
- 支持按板块名称获取相关新闻
- 从财经和板块专用RSS源获取
- 自动过滤板块相关新闻

#### 1.3 基本面数据总结
- 支持输入基本面指标（市值、PE、PB、ROE等）
- 自动生成基本面总结文本
- 估值分析、盈利能力、成长性、股息率分析
- 可视化展示关键指标

#### 1.4 格式化新闻用于舆情分析
- 将新闻列表格式化为舆情分析API所需格式
- 可选地将基本面信息添加到新闻内容
- 生成可直接用于舆情分析的数据

## 技术架构

### 后端

#### 1. NewsFetcher服务 (`backend/services/news_fetcher.py`)

```python
class NewsFetcher:
    """新闻获取服务"""
    
    async def fetch_rss_news(rss_url: str, limit: int = 20)
    async def fetch_stock_news(stock_code: str, stock_name: str, ...)
    async def fetch_sector_news(sector_name: str, limit: int = 20)
    async def summarize_fundamentals(stock_code: str, stock_name: str, ...)
    def format_news_for_sentiment(news_list: List, fundamentals: Optional[Dict])
```

**主要功能：**
- RSS订阅解析（使用feedparser）
- HTTP异步请求（使用httpx）
- 新闻去重和过滤
- 基本面数据智能总结
- 文本清理和格式化

**默认RSS源：**
- 财经: 新浪财经RSS
- 股票: 新浪股票RSS
- 银行: 新浪银行RSS
- 科技: 新浪科技RSS

#### 2. 新闻API (`backend/api/news.py`)

**端点：**

1. `GET /api/v1/news/health`
   - 健康检查
   - 返回可用RSS源列表

2. `POST /api/v1/news/fetch/stock`
   - 获取股票新闻
   - 请求: FetchStockNewsRequest
   - 响应: NewsResponse

3. `POST /api/v1/news/fetch/sector`
   - 获取板块新闻
   - 请求: FetchSectorNewsRequest
   - 响应: NewsResponse

4. `POST /api/v1/news/summarize/fundamentals`
   - 总结基本面信息
   - 请求: SummarizeFundamentalsRequest
   - 响应: FundamentalsSummary

5. `POST /api/v1/news/format`
   - 格式化新闻用于舆情分析
   - 请求: FormatNewsRequest
   - 响应: NewsResponse

### 前端

#### 1. 新闻页面 (`frontend/src/pages/News.tsx`)

**功能区域：**

1. **获取新闻区域**
   - 选择新闻类型（股票/板块）
   - 输入股票代码和名称
   - 输入板块名称
   - 获取新闻按钮

2. **基本面数据输入**
   - 市值、PE、PB、ROE
   - 营收、净利润
   - 营收增长率、净利润增长率
   - 股息率、所属行业
   - 总结基本面按钮

3. **基本面总结展示**
   - 智能生成的总结文本
   - 关键指标统计卡片
   - 估值、盈利能力、成长性分析

4. **新闻列表**
   - 展示获取的新闻
   - 显示标题、内容、来源、时间
   - 可点击跳转到原文
   - 发送到舆情分析按钮

#### 2. 新闻服务 (`frontend/src/services/news.ts`)

```typescript
export const newsService = {
  async healthCheck()
  async fetchStockNews(request: FetchStockNewsRequest)
  async fetchSectorNews(request: FetchSectorNewsRequest)
  async summarizeFundamentals(...)
  async formatNewsForSentiment(...)
}
```

#### 3. 类型定义 (`frontend/src/types/news.ts`)

```typescript
interface NewsItem
interface FundamentalsData
interface FundamentalsSummary
interface FetchStockNewsRequest
interface FetchSectorNewsRequest
interface NewsResponse
```

## 数据流程

### 1. 获取股票新闻流程

```
用户输入股票信息
    ↓
调用 fetchStockNews API
    ↓
NewsFetcher 从多个RSS源获取新闻
    ↓
过滤相关新闻（基于股票名称和代码）
    ↓
去重和按时间排序
    ↓
返回新闻列表
    ↓
前端展示新闻
```

### 2. 基本面总结流程

```
用户输入基本面数据
    ↓
调用 summarizeFundamentals API
    ↓
NewsFetcher 分析各项指标
    ↓
生成智能总结文本
    ↓
返回总结和关键指标
    ↓
前端展示总结卡片
```

### 3. 发送到舆情分析流程

```
用户点击"发送到舆情分析"
    ↓
调用 formatNewsForSentiment API
    ↓
NewsFetcher 格式化新闻
    ↓
可选添加基本面信息
    ↓
返回格式化后的新闻
    ↓
导航到舆情分析页面
    ↓
传递新闻数据用于分析
```

## 基本面分析逻辑

### 1. 估值分析（PE）
- PE < 15: "市盈率较低，估值相对便宜"
- 15 ≤ PE ≤ 30: "市盈率处于合理水平"
- PE > 30: "市盈率较高，估值相对昂贵"

### 2. 盈利能力（ROE）
- ROE > 15%: "净资产收益率高，盈利能力强"
- 10% < ROE ≤ 15%: "净资产收益率中等，盈利能力尚可"
- ROE ≤ 10%: "净资产收益率较低，盈利能力偏弱"

### 3. 成长性（净利润增长率）
- 增长率 > 20%: "净利润增长率高，成长性好"
- 10% < 增长率 ≤ 20%: "净利润增长率中等，成长性尚可"
- 0% < 增长率 ≤ 10%: "净利润有增长"
- 增长率 ≤ 0%: "净利润增长为负，成长性较差"

### 4. 股息率
- 股息率 > 3%: "股息率高，分红回报好"
- 1% < 股息率 ≤ 3%: "股息率中等，有一定分红"
- 股息率 ≤ 1%: "股息率较低，分红回报少"

## 依赖项

### 后端
- feedparser>=6.0.10: RSS订阅解析
- httpx>=0.25.0: HTTP异步请求
- loguru>=0.7.0: 日志记录

### 前端
- React 18: 前端框架
- Ant Design: UI组件库
- axios: HTTP客户端
- react-router-dom: 路由管理

## 使用指南

### 1. 启动服务

```bash
# 后端
cd backend
python main.py

# 前端
cd frontend
npm run dev
```

### 2. 访问新闻获取页面

打开浏览器访问: `http://localhost:5173/news`

### 3. 获取股票新闻

1. 选择"股票新闻"
2. 输入股票代码（如: 600000）
3. 输入股票名称（如: 浦发银行）
4. 可选输入板块名称（如: 银行）
5. 点击"获取新闻"
6. 查看获取的新闻列表

### 4. 输入基本面数据

1. 在基本面数据区域输入各项指标
2. 点击"总结基本面"
3. 查看生成的总结和关键指标

### 5. 发送到舆情分析

1. 获取新闻后，点击"发送到舆情分析"
2. 自动跳转到舆情分析页面
3. 新闻数据已自动填充，可直接进行分析

## API示例

### 获取股票新闻

```bash
curl -X POST http://localhost:8000/api/v1/news/fetch/stock \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600000",
    "stock_name": "浦发银行",
    "sector_name": "银行",
    "limit": 10
  }'
```

### 总结基本面

```bash
curl -X POST http://localhost:8000/api/v1/news/summarize/fundamentals \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600000",
    "stock_name": "浦发银行",
    "fundamentals": {
      "market_cap": "5000亿",
      "pe_ratio": 5.5,
      "pb_ratio": 0.6,
      "roe": 12.5,
      "revenue": "1800亿",
      "net_profit": "200亿",
      "revenue_growth": 8.5,
      "profit_growth": 15.2,
      "dividend_yield": 4.2,
      "industry": "银行"
    }
  }'
```

### 格式化新闻

```bash
curl -X POST http://localhost:8000/api/v1/news/format \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "news_list": [
      {
        "id": "news_001",
        "title": "浦发银行发布重大利好消息",
        "content": "公司发布业绩预告...",
        "source": "财经新闻",
        "published_time": "2026-02-20T12:00:00"
      }
    ],
    "fundamentals": {
      "market_cap": "5000亿",
      "pe_ratio": 5.5
    }
  }'
```

## 文件清单

### 新增文件

1. `backend/services/news_fetcher.py` - 新闻获取服务
2. `backend/api/news.py` - 新闻API
3. `frontend/src/types/news.ts` - 新闻类型定义
4. `frontend/src/services/news.ts` - 新闻服务层
5. `frontend/src/pages/News.tsx` - 新闻获取页面
6. `frontend/src/pages/News.css` - 新闻页面样式

### 更新文件

1. `backend/requirements.txt` - 添加feedparser依赖
2. `backend/api/__init__.py` - 注册新闻路由
3. `frontend/src/services/auth.ts` - 添加getAuthHeader方法
4. `frontend/src/App.tsx` - 添加新闻路由
5. `frontend/src/components/layout/Sidebar.tsx` - 添加新闻菜单

## 集成说明

### 与舆情分析页面的集成

新闻获取页面可以直接将数据发送到舆情分析页面：

1. 在新闻获取页面获取新闻
2. 点击"发送到舆情分析"按钮
3. 自动跳转到舆情分析页面
4. 新闻数据已自动填充
5. 可直接进行舆情分析

### 数据传递

通过React Router的state参数传递数据：

```typescript
navigate('/sentiment', {
  state: {
    stockCode: stockCode || sectorName,
    stockName: stockName || sectorName,
    sectorName: sectorName,
    newsData: formatted.news
  }
});
```

## 注意事项

1. **RSS源可用性**: RSS源可能随时变化，需要定期更新
2. **网络连接**: 获取新闻需要稳定的网络连接
3. **新闻时效性**: RSS源更新频率不同，可能存在延迟
4. **数据质量**: 基本面数据的准确性影响总结质量
5. **API限制**: 某些RSS源可能有访问频率限制

## 未来改进

1. **更多RSS源**: 添加更多财经新闻源
2. **新闻分类**: 自动分类新闻（正面/负面/中性）
3. **新闻去重**: 更智能的去重算法
4. **实时更新**: WebSocket实时推送新闻
5. **新闻搜索**: 搜索历史新闻
6. **自定义源**: 允许用户添加自定义RSS源
7. **新闻收藏**: 保存重要新闻
8. **导出功能**: 导出新闻为PDF或Excel

## 测试

### 手动测试

1. 测试获取股票新闻
2. 测试获取板块新闻
3. 测试基本面总结
4. 测试格式化新闻
5. 测试发送到舆情分析

### 自动化测试

建议添加以下测试：
- 单元测试：NewsFetcher各方法
- 集成测试：API端点
- E2E测试：完整用户流程

## 总结

新闻获取功能已完整实施，包括：

✅ RSS新闻订阅获取
✅ 股票和板块新闻过滤
✅ 基本面数据总结
✅ 新闻格式化用于舆情分析
✅ 与舆情分析页面集成
✅ 完整的前后端API
✅ 用户友好的界面

该功能为舆情分析提供了数据基础，用户可以方便地获取新闻并结合基本面数据进行舆情分析。