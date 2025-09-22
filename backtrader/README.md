# Backtrader 量化交易框架

这是一个基于 Backtrader 的完整量化交易回测框架，集成了 akshare 和 tushare 数据源，支持多种技术分析策略。

## 功能特性

- 🚀 **多数据源支持**: 集成 akshare 和 tushare 数据源
- 📊 **多种策略**: 支持移动平均、RSI、MACD、布林带、KDJ、均值回归、网格交易等策略
- 📈 **完整回测**: 提供完整的回测引擎和性能分析
- 🎨 **可视化**: 自动生成回测图表和对比报告
- 🔧 **易于扩展**: 模块化设计，易于添加新策略
- 🌐 **跨平台**: 支持 Windows、macOS、Linux

## 文件结构

```
backtrader/
├── main.py              # 主程序入口
├── backtest_engine.py   # 回测引擎
├── strategies.py        # 策略定义
├── data_feed.py         # 数据源集成
└── README.md           # 使用说明
```

## 安装依赖

```bash
pip install backtrader pandas numpy matplotlib akshare tushare
```

## 快速开始

### 1. 运行多策略回测

```bash
cd backtrader
python main.py
```

这将运行所有预定义策略的对比回测。

### 2. 运行单策略回测

```bash
cd backtrader
python main.py single
```

这将运行单个策略的详细回测，并显示图表。

### 3. 自定义策略参数

修改 `main.py` 中的 `strategies_config` 字典来自定义策略参数：

```python
strategies_config = {
    'DualMA': {
        'ma_fast': 5,      # 快线周期
        'ma_slow': 20,     # 慢线周期
        'printlog': False  # 是否打印日志
    },
    'RSI': {
        'rsi_period': 14,  # RSI周期
        'rsi_upper': 70,   # 超买线
        'rsi_lower': 30,   # 超卖线
        'printlog': False
    },
    # ... 更多策略
}
```

## 支持的策略

### 1. 移动平均策略 (MA)
- **参数**: `ma_period` - 移动平均周期
- **逻辑**: 价格上穿均线买入，下穿均线卖出

### 2. 双均线策略 (DualMA)
- **参数**: `ma_fast`, `ma_slow` - 快慢线周期
- **逻辑**: 快线上穿慢线买入，下穿卖出

### 3. RSI 策略
- **参数**: `rsi_period`, `rsi_upper`, `rsi_lower` - RSI周期和阈值
- **逻辑**: RSI超卖买入，超买卖出

### 4. MACD 策略
- **参数**: `macd_fast`, `macd_slow`, `macd_signal` - MACD参数
- **逻辑**: MACD金叉买入，死叉卖出

### 5. 布林带策略 (BOLL)
- **参数**: `bb_period`, `bb_dev` - 布林带周期和标准差倍数
- **逻辑**: 价格触及下轨买入，触及上轨卖出

### 6. KDJ 策略
- **参数**: `kdj_period`, `kdj_upper`, `kdj_lower` - KDJ参数
- **逻辑**: KDJ超卖买入，超买卖出

### 7. 均值回归策略 (MeanReversion)
- **参数**: `lookback`, `threshold` - 回望期和阈值
- **逻辑**: 价格偏离均值过多时反向操作

### 8. 网格交易策略 (Grid)
- **参数**: `grid_size`, `max_position` - 网格大小和最大持仓
- **逻辑**: 在预设价格网格上买卖

## 回测结果

框架会自动生成以下结果：

1. **控制台输出**: 实时显示回测进度和结果
2. **CSV报告**: 详细的策略性能对比表
3. **图表**: 价格走势和交易信号图
4. **性能指标**: 收益率、夏普比率、最大回撤、胜率等

## 性能指标说明

- **总收益率**: 整个回测期间的总收益百分比
- **年化收益率**: 按年化计算的收益率
- **最大回撤**: 从峰值到谷底的最大跌幅
- **夏普比率**: 风险调整后的收益指标
- **SQN**: 系统质量指标
- **胜率**: 盈利交易占总交易的比例

## 自定义策略

要添加新策略，请参考 `strategies.py` 中的示例：

```python
class MyStrategy(BaseStrategy):
    """我的自定义策略"""
    
    params = (
        ('my_param', 10),
        ('printlog', True),
    )
    
    def add_indicators(self):
        # 添加技术指标
        self.my_indicator = bt.indicators.SMA(self.datas[0], period=self.params.my_param)
    
    def next(self):
        # 策略逻辑
        if not self.position:
            if self.my_condition():
                self.buy()
        else:
            if self.my_exit_condition():
                self.sell()
```

## 数据源配置

### AkShare (推荐)
- 免费使用，无需注册
- 数据更新及时
- 支持A股、港股、美股等

### TuShare
- 需要注册获取token
- 数据质量较高
- 有使用限制

## 注意事项

1. **数据获取**: 确保网络连接正常，数据源可用
2. **参数调优**: 不同市场环境需要调整策略参数
3. **风险控制**: 回测结果不代表未来表现，请注意风险
4. **资金管理**: 建议设置合理的仓位管理和止损机制

## 故障排除

### 常见问题

1. **字体显示问题**: 系统会自动检测并设置合适的中文字体
2. **数据获取失败**: 检查网络连接和数据源状态
3. **策略运行错误**: 检查策略参数和逻辑是否正确

### 调试模式

在策略参数中设置 `printlog=True` 可以查看详细的交易日志。

## 扩展功能

框架支持以下扩展：

1. **新数据源**: 在 `data_feed.py` 中添加新的数据源适配器
2. **新策略**: 在 `strategies.py` 中实现新的策略类
3. **新指标**: 使用 Backtrader 的内置指标或自定义指标
4. **新分析器**: 添加自定义的性能分析器

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个框架！
