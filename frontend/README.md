# Stock Platform Frontend

AI驱动的量化交易平台 - 前端应用

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Ant Design
- **状态管理**: Zustand + React Query
- **图表**: ECharts
- **路由**: React Router v6
- **HTTP客户端**: Axios

## 安装

```bash
npm install
```

## 开发

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

## 构建

```bash
npm run build
```

## 预览生产构建

```bash
npm run preview
```

## 代码规范

```bash
# 代码检查
npm run lint

# 代码格式化
npm run format
```

## 项目结构

```
frontend/
├── src/
│   ├── components/      # 组件
│   │   ├── charts/     # 图表组件
│   │   ├── stock/      # 股票组件
│   │   └── layout/     # 布局组件
│   ├── pages/          # 页面
│   ├── services/       # API服务
│   ├── store/          # 状态管理
│   ├── types/          # TypeScript类型
│   ├── hooks/          # 自定义Hooks
│   ├── utils/          # 工具函数
│   ├── App.tsx        # 主应用组件
│   └── main.tsx       # 应用入口
├── public/             # 静态资源
├── index.html          # HTML模板
├── package.json        # 项目配置
├── vite.config.ts      # Vite配置
└── tsconfig.json       # TypeScript配置
```

## 功能模块

- [x] 仪表板
- [x] 行情列表
- [x] 股票详情（待完善）
- [x] 策略管理
- [ ] K线图组件
- [ ] 技术指标图表
- [ ] AI智能咨询
- [ ] 策略回测
- [ ] 参数优化
- [ ] 实盘交易

## 开发说明

1. 使用TypeScript编写代码
2. 遵循React Hooks最佳实践
3. 组件采用函数式组件
4. 使用Ant Design组件库
5. 使用React Query管理服务端状态
6. 使用Zustand管理全局状态
7. 使用ECharts绘制图表

## 环境变量

创建 `.env` 文件：

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

## 注意事项

- 确保后端API服务已启动
- 开发模式下，API请求会通过Vite代理转发
- 生产构建前请检查所有环境变量配置
