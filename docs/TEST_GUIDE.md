# 测试指南

## 概述

本项目采用模块化的测试组织结构，所有测试按照功能模块分类存储，便于维护和扩展。

## 测试目录结构

### 后端测试 (backend/test/)

```
backend/test/
├── api/                    # API层测试
│   ├── test_endpoints.py    # API端点测试
│   ├── test_market_api.py   # 市场API测试
│   └── test_simple.py      # 简单API测试
├── services/               # 服务层测试
│   ├── test_data_download_service.py    # 数据下载服务测试
│   └── test_stock_code_service.py      # 股票代码服务测试
├── data_adapters/          # 数据适配器测试
│   ├── test_duckdb_adapter.py         # DuckDB适配器测试
│   ├── test_minute_download.py         # 分钟数据下载测试
│   ├── test_real_sources.py           # 真实数据源测试
│   └── test_storage.py               # 存储服务测试
├── utils/                  # 工具类测试
│   └── test_startup.py     # 启动测试
└── core/                   # 核心功能测试
```

### 前端测试 (frontend/test/)

```
frontend/test/
├── components/             # 组件测试
├── services/              # 服务测试
└── utils/                # 工具类测试
```

## 测试脚本

### 全局测试脚本 (test_all.sh)

位于项目根目录，用于一键运行所有测试。

**使用方法：**

```bash
# 运行所有测试（默认）
./test_all.sh

# 仅运行后端测试
./test_all.sh --backend

# 仅运行前端测试
./test_all.sh --frontend

# 运行所有测试（显式指定）
./test_all.sh --all
```

**功能特性：**
- 彩色输出，清晰易读
- 按模块分类运行测试
- 统计测试结果（总数/通过/失败）
- 支持命令行参数选择测试范围

### 后端测试脚本 (backend/test_all.sh)

用于一键运行所有后端测试。

**使用方法：**

```bash
cd backend
./test_all.sh
```

**功能特性：**
- 自动运行所有测试模块
- 按模块分类显示测试结果
- 统计总体测试结果
- 彩色输出

### 前端测试脚本

通过npm脚本运行：

```bash
cd frontend

# 运行所有测试
npm test

# 仅运行组件测试
npm run test:components

# 仅运行服务测试
npm run test:services
```

## 测试模块说明

### API测试 (test/api/)

测试API端点的功能正确性，包括：
- 市场数据API
- 股票信息API
- 数据下载API
- 认证API

### 服务测试 (test/services/)

测试业务逻辑层，包括：
- 数据下载服务
- 股票代码服务
- 市场服务
- 缓存服务

### 数据适配器测试 (test/data_adapters/)

测试数据源适配器，包括：
- DuckDB适配器
- 真实数据源（BaoStock, AkShare等）
- 数据存储服务

### 工具测试 (test/utils/)

测试工具函数和辅助类，包括：
- 系统启动测试
- 配置工具
- 数据转换工具

## 运行单个测试文件

### 后端

```bash
cd backend

# 运行特定的测试文件
python test/api/test_market_api.py
python test/services/test_stock_code_service.py
python test/data_adapters/test_real_sources.py
```

### 前端

前端测试框架待实现，当前为预留接口。

## 测试覆盖率

目前测试覆盖以下模块：
- ✅ API端点测试
- ✅ 数据下载服务测试
- ✅ 股票代码服务测试
- ✅ 数据适配器测试
- ✅ 真实数据源测试
- ⏳ 前端组件测试（待实现）
- ⏳ 前端服务测试（待实现）

## 添加新测试

### 后端测试

1. 在对应的模块目录下创建测试文件
2. 文件命名格式：`test_<模块名>.py`
3. 使用标准Python测试框架（pytest或unittest）

示例：

```python
# backend/test/services/test_new_service.py
import pytest

def test_new_function():
    # 测试代码
    assert True
```

### 前端测试

1. 在对应的模块目录下创建测试文件
2. 使用Jest或React Testing Library
3. 文件命名格式：`<组件名>.test.tsx`

示例：

```typescript
// frontend/test/components/NewComponent.test.tsx
import { render, screen } from '@testing-library/react';
import NewComponent from '../../src/components/NewComponent';

describe('NewComponent', () => {
  it('renders correctly', () => {
    render(<NewComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

## 测试最佳实践

1. **测试隔离**：每个测试应该独立运行，不依赖其他测试
2. **清晰命名**：测试名称应该清楚描述测试的内容
3. **快速执行**：测试应该尽可能快地运行
4. **覆盖边界**：测试应该覆盖正常和异常情况
5. **保持更新**：代码变更时及时更新对应的测试

## 故障排查

### 测试失败

1. 查看测试输出日志
2. 检查测试环境和配置
3. 确保所有依赖已安装
4. 验证数据源连接状态

### 端口占用

如果测试过程中遇到端口占用：

```bash
# 查看端口占用
lsof -ti:8000
lsof -ti:3000

# 使用stop_all.sh清理
./stop_all.sh
```

## 持续集成

测试脚本可以集成到CI/CD流程中：

```yaml
# .github/workflows/test.yml 示例
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run backend tests
        run: ./test_all.sh --backend
      - name: Run frontend tests
        run: ./test_all.sh --frontend
```

## 联系支持

如果遇到测试相关的问题：
1. 查看日志文件：`logs/backend.log`, `logs/frontend.log`
2. 检查环境配置
3. 参考项目文档：`docs/` 目录