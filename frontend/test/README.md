# 前端测试文档

## 概述
本项目使用 Vitest 作为测试框架，配合 Testing Library 进行组件测试和服务测试。

## 测试框架

### 技术栈
- **Vitest**: 快速的单元测试框架
- **Testing Library**: React 组件测试工具
- **jsdom**: 浏览器环境模拟
- **Vitest UI**: 可视化测试界面

### 项目结构
```
frontend/test/
├── setup.ts              # 测试环境配置
├── services/             # 服务层测试
│   └── trading.test.ts  # 交易服务测试
└── README.md            # 测试文档
```

## 安装依赖

在运行测试之前，确保已安装所有测试依赖：

```bash
cd frontend
npm install
```

## 运行测试

### 运行所有测试
```bash
npm test
```

### 运行测试并进入监听模式
```bash
npm run test
```

### 运行测试（一次性）
```bash
npm run test:run
```

### 运行测试并生成覆盖率报告
```bash
npm run test:coverage
```

### 使用可视化界面运行测试
```bash
npm run test:ui
```

## 交易服务测试

### 测试文件
`frontend/test/services/trading.test.ts`

### 测试覆盖范围

#### 1. 连接交易系统 (`connectTrading`)
- ✅ 成功连接
- ✅ 连接失败处理

#### 2. 创建订单 (`createOrder`)
- ✅ 成功创建订单
- ✅ 订单创建失败处理
- ✅ 风控检查未通过处理

#### 3. 获取订单列表 (`getOrders`)
- ✅ 成功获取订单列表
- ✅ 使用过滤器获取订单
- ✅ 获取订单失败处理

#### 4. 撤销订单 (`cancelOrder`)
- ✅ 成功撤销订单
- ✅ 撤销订单失败处理

#### 5. 获取订单统计 (`getOrderStatistics`)
- ✅ 成功获取订单统计
- ✅ 获取统计失败处理

#### 6. 获取持仓列表 (`getPositions`)
- ✅ 成功获取持仓列表
- ✅ 获取持仓失败处理

#### 7. 获取账户信息 (`getAccount`)
- ✅ 成功获取账户信息
- ✅ 获取账户失败处理

#### 8. API 响应数据提取
- ✅ 正确提取 `data` 字段
- ✅ 处理嵌套数据结构

### 测试重点

这个测试套件特别关注以下问题：

1. **API 响应数据提取**
   - 验证服务正确提取后端返回的 `data` 字段
   - 确保不会返回 `{code, message, data}` 包装对象

2. **错误处理**
   - 验证所有方法正确处理 API 错误
   - 确保错误能够正确抛出

3. **数据结构**
   - 验证返回的数据结构符合类型定义
   - 确保嵌套数据结构正确处理

### 运行交易服务测试

```bash
# 运行所有测试
npm test

# 或只运行交易服务测试
npm test -- trading.test.ts
```

## 编写新测试

### 服务测试示例

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { myService } from '@/services/myService';
import apiClient from '@/services/api';

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('My Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should do something', async () => {
    const mockResponse = {
      code: 200,
      message: 'success',
      data: { result: 'test' },
    };
    
    (apiClient.get as any).mockResolvedValue(mockResponse);
    
    const result = await myService.doSomething();
    
    expect(result).toEqual({ result: 'test' });
  });
});
```

### 组件测试示例

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MyComponent from '@/components/MyComponent';

describe('My Component', () => {
  it('should render correctly', () => {
    render(<MyComponent />);
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

## 测试最佳实践

### 1. 测试命名
- 描述性测试名称
- 使用 "should" 格式
- 清晰表达测试意图

### 2. 测试隔离
- 使用 `beforeEach` 清理 mocks
- 每个测试独立运行
- 不依赖测试顺序

### 3. Mock 策略
- 只 mock 外部依赖
- 使用 vi.mock() 进行模块 mock
- 使用 vi.fn() 创建函数 mock

### 4. 断言清晰
- 使用明确的断言
- 避免过于复杂的断言
- 专注于测试业务逻辑

## 常见问题

### 1. TypeScript 错误
如果在测试文件中看到 TypeScript 错误，确保：
- 已安装所有依赖 (`npm install`)
- Vitest 配置正确 (`vitest.config.ts`)
- 类型定义文件存在

### 2. Mock 不工作
如果 mock 不生效：
- 使用 `vi.mock()` 在文件顶部进行 mock
- 确保导入路径正确
- 检查 mock 的实现

### 3. 异步测试失败
异步测试失败时：
- 使用 `async/await` 语法
- 确保 await 所有异步操作
- 使用 `expect().resolves` 或 `expect().rejects`

## 持续集成

### GitHub Actions 示例

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm ci
      - run: cd frontend && npm run test:run
      - run: cd frontend && npm run test:coverage
```

## 覆盖率目标

- **服务层**: 80%+
- **组件层**: 70%+
- **整体**: 75%+

## 参考资源

- [Vitest 官方文档](https://vitest.dev/)
- [Testing Library 文档](https://testing-library.com/)
- [React Testing Library 文档](https://testing-library.com/react)

## 贡献指南

在添加新功能时，请：

1. 为新功能编写测试
2. 确保所有测试通过
3. 维持或提高测试覆盖率
4. 遵循现有测试风格和模式

## 联系方式

如有测试相关问题，请联系开发团队。