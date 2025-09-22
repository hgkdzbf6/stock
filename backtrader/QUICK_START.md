# Backtrader 量化交易框架 - 快速开始指南

## 🚀 快速开始

### 1. 运行简化测试（推荐首次使用）
```bash
cd backtrader
python3 test_simple.py
```

### 2. 运行交互式菜单
```bash
cd backtrader
python3 run_backtrader.py
```

### 3. 运行真实数据回测
```bash
cd backtrader
python3 main.py
```

## 📁 文件结构

```
backtrader/
├── main.py              # 主程序（真实数据回测）
├── test_simple.py       # 简化测试（模拟数据）
├── run_backtrader.py    # 交互式启动脚本
├── backtest_engine.py   # 回测引擎
├── strategies.py        # 策略定义
├── data_feed.py         # 数据源集成
├── README.md           # 详细文档
└── QUICK_START.md      # 快速开始指南
```

## 🎯 功能特性

✅ **多数据源支持**: akshare + tushare  
✅ **8种策略**: MA、双均线、RSI、MACD、布林带、KDJ、均值回归、网格交易  
✅ **完整回测**: 收益率、夏普比率、最大回撤、胜率等指标  
✅ **可视化**: 自动生成图表和对比报告  
✅ **跨平台**: Windows、macOS、Linux  
✅ **中文字体**: 自动适配系统字体  

## 📊 测试结果示例

刚才的测试显示：
- ✅ 框架运行正常
- ✅ 策略逻辑正确
- ✅ 交易信号生成
- ✅ 性能指标计算
- ✅ 图表生成

## 🔧 自定义使用

### 修改策略参数
编辑 `main.py` 中的 `strategies_config`：

```python
strategies_config = {
    'DualMA': {
        'ma_fast': 5,      # 快线周期
        'ma_slow': 20,     # 慢线周期
        'printlog': False  # 是否打印日志
    },
    # ... 更多策略
}
```

### 修改股票代码
```python
stock_code = '600771'  # 改为你想要的股票代码
```

### 修改回测时间
```python
start_date = end_date - timedelta(days=180)  # 回测天数
```

## ⚠️ 注意事项

1. **首次使用**: 建议先运行 `test_simple.py` 验证框架功能
2. **网络连接**: 真实数据回测需要网络连接
3. **数据源**: akshare 免费，tushare 需要注册
4. **字体警告**: 可以忽略字体相关的警告信息

## 🆘 故障排除

### 常见问题

1. **字体警告**: 正常现象，不影响功能
2. **数据获取失败**: 检查网络连接
3. **策略运行错误**: 检查参数设置

### 调试模式
在策略参数中设置 `printlog=True` 查看详细日志。

## 📈 下一步

1. 尝试不同的策略参数
2. 测试不同的股票代码
3. 添加自定义策略
4. 优化回测参数

## 🎉 恭喜！

您已经成功搭建了完整的 Backtrader 量化交易框架！

框架特点：
- 🚀 **开箱即用**: 无需复杂配置
- 📊 **功能完整**: 从数据获取到结果分析
- 🔧 **易于扩展**: 模块化设计
- 🌐 **跨平台**: 支持主流操作系统

开始您的量化交易之旅吧！ 🚀📈
