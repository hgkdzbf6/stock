# Phase 2 实施计划：AI智能咨询系统

**开始日期**: 2026-02-14
**预计时间**: 2-3周
**优先级**: 高

---

## 📋 Phase 2 目标

集成GLM 4.7，实现智能分析和策略建议

### 核心功能

1. **后端AI服务**
   - GLM 4.7 API集成
   - 提示词模板系统
   - AI分析服务

2. **前端AI组件**
   - AI聊天界面
   - 策略建议卡片
   - 风险提示组件
   - 技术指标分析
   - 持仓洞察

---

## 🎯 实施步骤

### 第1步：后端AI服务搭建（3-4天）

#### 1.1 目录结构
```
backend/
├── ai/
│   ├── __init__.py
│   ├── llm_client.py          # LLM客户端封装
│   ├── prompt_templates.py    # 提示词模板
│   ├── ai_service.py          # AI分析服务
│   └── models.py              # AI相关数据模型
├── api/
│   └── ai.py                  # AI API端点
└── models/
    └── ai_analysis.py         # AI分析记录模型
```

#### 1.2 LLM客户端（LLM Client）
- 封装GLM 4.7 API调用
- 支持流式响应
- 错误处理和重试机制
- Token统计

#### 1.3 提示词模板
- **持仓分析提示词**
  - 分析当前持仓
  - 评估风险
  - 提供调仓建议

- **市场行情提示词**
  - 分析市场趋势
  - 识别机会和风险
  - 提供操作建议

- **技术指标提示词**
  - 综合分析多个技术指标
  - 识别买卖信号
  - 提供策略建议

- **风险评估提示词**
  - 评估当前风险水平
  - 提供风控建议
  - 预警提醒

#### 1.4 AI分析服务
- 统一的AI分析接口
- 上下文管理
- 结果缓存
- 历史记录保存

#### 1.5 API端点
- `POST /api/v1/ai/analyze` - AI分析
- `GET /api/v1/ai/history` - 分析历史
- `DELETE /api/v1/ai/history/{id}` - 删除历史
- `GET /api/v1/ai/templates` - 获取提示词模板

---

### 第2步：前端AI组件开发（4-5天）

#### 2.1 AI聊天界面
```
frontend/src/components/ai/
├── ChatInterface.tsx          # AI聊天界面
├── MessageBubble.tsx          # 消息气泡
├── QuickQuestions.tsx        # 快捷提问
└── StreamResponse.tsx        # 流式响应显示
```

**功能**:
- 文本输入框
- 快捷提问按钮
- 流式响应显示
- 消息历史
- 复制消息
- Markdown渲染
- 代码高亮

#### 2.2 策略建议卡片
```
frontend/src/components/ai/
├── StrategyCard.tsx          # 策略建议卡片
└── ConfidenceMeter.tsx        # 置信度仪表盘
```

**功能**:
- 显示AI生成的策略建议
- 置信度可视化
- 一键应用到策略系统
- 相关性分析

#### 2.3 风险提示组件
```
frontend/src/components/ai/
└── RiskAlert.tsx             # 风险提示组件
```

**功能**:
- 三级风险等级（低/中/高）
- 颜色编码（绿/黄/红）
- 风险因素列表
- 详细说明
- 历史风险趋势

#### 2.4 技术指标分析
```
frontend/src/components/ai/
└── IndicatorAnalysis.tsx     # 技术指标分析
```

**功能**:
- 趋势可视化
- 买卖信号标识
- 关键技术位标记
- 指标解读

#### 2.5 持仓洞察
```
frontend/src/components/ai/
└── PortfolioInsights.tsx     # 持仓洞察
```

**功能**:
- 盈亏分布图
- 持仓占比饼图
- 风险评估仪表盘
- 集中度分析

---

### 第3步：集成到现有页面（2-3天）

#### 3.1 Dashboard页面
- 添加AI快速入口
- 显示AI建议摘要
- 风险提示卡片

#### 3.2 StockDetail页面
- 技术指标AI分析
- AI建议标签
- 智能策略推荐

#### 3.3 Strategies页面
- AI策略优化建议
- 参数优化建议
- 策略风险评估

---

### 第4步：数据库设计（1-2天）

#### AI分析记录表
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
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### AI对话历史表
```sql
CREATE TABLE ai_conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200),
    messages JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 第5步：测试和优化（2-3天）

#### 5.1 单元测试
- LLM客户端测试
- AI服务测试
- API端点测试
- 组件测试

#### 5.2 集成测试
- 端到端AI分析流程
- 流式响应测试
- 错误处理测试

#### 5.3 性能优化
- 响应缓存
- 流式响应优化
- Token优化

#### 5.4 提示词优化
- A/B测试
- 效果评估
- 迭代改进

---

## 📊 交付物

### 后端交付物
- ✅ LLM客户端封装
- ✅ 提示词模板系统
- ✅ AI分析服务
- ✅ AI API端点
- ✅ 数据库表和迁移
- ✅ 单元测试

### 前端交付物
- ✅ AI聊天界面
- ✅ 策略建议卡片
- ✅ 风险提示组件
- ✅ 技术指标分析
- ✅ 持仓洞察
- ✅ 集成到现有页面

### 文档交付物
- ✅ AI服务API文档
- ✅ 前端组件使用文档
- ✅ 提示词模板说明
- ✅ 部署和配置指南

---

## 🔧 技术细节

### LLM API配置
```python
# config.py
GLM_API_KEY = os.getenv("GLM_API_KEY")
GLM_API_BASE = "https://open.bigmodel.cn/api/paas/v4/"
GLM_MODEL = "glm-4"
GLM_MAX_TOKENS = 2000
GLM_TEMPERATURE = 0.7
```

### 提示词模板示例
```python
# prompt_templates.py

PORTFOLIO_ANALYSIS_TEMPLATE = """
你是一个专业的量化投资顾问。请分析以下持仓数据：

持仓信息：
{position_info}

市场环境：
{market_info}

技术指标：
{indicators}

请提供：
1. 整体风险评估（低/中/高）
2. 持仓配置建议
3. 风险控制建议
4. 优化建议

请以JSON格式返回，包含以下字段：
- risk_level: 风险等级
- suggestions: 建议列表
- risk_factors: 风险因素
- confidence: 置信度（0-1）
"""
```

### AI分析接口
```python
# ai_service.py

class AIService:
    async def analyze_portfolio(
        self,
        user_id: int,
        positions: List[Position],
        market_data: Dict
    ) -> AIAnalysis:
        """分析持仓"""
        pass
    
    async def analyze_market(
        self,
        stock_code: str,
        market_data: Dict
    ) -> AIAnalysis:
        """分析市场"""
        pass
    
    async def analyze_indicators(
        self,
        indicators: Dict
    ) -> AIAnalysis:
        """分析技术指标"""
        pass
```

### AI API端点
```python
# api/ai.py

@router.post("/analyze")
async def analyze(
    request: AIAnalyzeRequest,
    current_user: User = Depends(get_current_user)
):
    """AI分析"""
    result = await ai_service.analyze(
        type=request.type,
        context=request.context,
        user_id=current_user.id
    )
    return result
```

---

## ✅ 验收标准

### 功能验收
- ✅ AI聊天界面正常工作
- ✅ 持仓分析功能完整
- ✅ 市场行情分析准确
- ✅ 技术指标AI分析合理
- ✅ 风险提示及时准确
- ✅ 流式响应正常

### 性能验收
- ✅ AI分析响应时间 < 5s
- ✅ 流式响应首字延迟 < 1s
- ✅ 每日AI调用成本在预算内

### 质量验收
- ✅ AI分析结果准确率 > 70%
- ✅ 用户满意度评分 > 4.0/5.0
- ✅ 提示词A/B测试有明确结论

---

## 📌 注意事项

### 安全性
- API Key安全存储（环境变量）
- 用户认证和授权
- 敏感信息过滤
- Rate limiting

### 成本控制
- Token使用监控
- 响应缓存
- 批量分析优化
- 成本预警

### 用户体验
- 流式响应显示
- 加载状态提示
- 错误处理友好
- 快捷操作

### 可扩展性
- 支持多个LLM提供商
- 提示词模板可配置
- 分析结果可缓存
- 支持自定义分析类型

---

## 🚀 实施优先级

### P0（必须）
- LLM客户端封装
- 基础提示词模板
- AI分析服务
- AI聊天界面
- API端点

### P1（重要）
- 策略建议卡片
- 风险提示组件
- 技术指标分析
- 持仓洞察
- 数据库集成

### P2（可选）
- 历史记录
- A/B测试
- 提示词优化
- 高级功能

---

**计划创建时间**: 2026-02-14 11:04
**预计开始时间**: 2026-02-14 11:10
**预计完成时间**: 2026-02-28