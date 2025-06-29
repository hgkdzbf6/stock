# 量化交易策略回测系统

这是一个基于Python的量化交易策略回测系统，支持分钟级数据和多种经典技术指标策略。

## 功能特性

### 数据获取
- 支持 **分钟级数据**（1分钟、5分钟、15分钟、30分钟、60分钟）
- 支持多种数据源：tushare、akshare
- 内置模拟数据生成器，确保系统在无网络环境下也能运行

### 策略支持
系统内置了8种经典量化策略：

1. **双均线策略 (MA)** - 基于快慢均线交叉
2. **EMA策略** - 指数移动平均线策略
3. **RSI策略** - 相对强弱指标策略
4. **MACD策略** - 指数平滑移动平均线策略
5. **布林带策略 (BOLL)** - 价格通道突破策略
6. **KDJ策略** - 随机指标策略
7. **Dual Thrust策略** - 价格突破策略
8. **网格策略 (Grid)** - 网格交易策略

### 回测功能
- 精确的手续费和滑点计算
- 详细的绩效指标分析
- 多策略对比功能
- 可视化图表展示

## 项目结构

```
stock/
├── src/                    # 源代码目录
│   ├── data_fetcher.py    # 数据获取模块
│   ├── strategy.py        # 策略模块
│   ├── backtest.py        # 回测引擎
│   └── main.py           # 主程序
├── results/              # 结果保存目录
├── test_system.py        # 系统测试脚本
├── requirements.txt      # 依赖包列表
└── README.md            # 说明文档
```

## 安装与配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据源（可选）

如果要使用tushare数据源，需要在 `main.py` 中配置您的token：

```python
token = 'your_tushare_token_here'
```

如果没有tushare token，系统会自动使用akshare或模拟数据。

## 使用方法

### 1. 运行系统测试

```bash
python test_system.py
```

### 2. 运行完整回测

```bash
cd src
python main.py
```

### 3. 自定义策略参数

在 `main.py` 中修改 `strategies_config` 字典来调整策略参数：

```python
strategies_config = {
    'MA': {'short_window': 5, 'long_window': 20, 'stop_loss': 0.10},
    'EMA': {'fast_window': 5, 'slow_window': 20, 'stop_loss': 0.10},
    'RSI': {'rsi_window': 14, 'oversold': 30, 'overbought': 70},
    # ... 其他策略配置
}
```

## 回测结果

系统会生成以下输出：

### 1. 控制台输出
- 各策略的详细性能指标
- 策略性能对比表格

### 2. 可视化图表
- 策略收益曲线对比
- 收益率柱状图
- 最大回撤对比
- 持仓比例变化

### 3. CSV文件
- `results/strategy_summary_YYYYMMDD_HHMMSS.csv` - 策略性能汇总
- `results/策略名称_YYYYMMDD_HHMMSS.csv` - 各策略详细回测结果

## 性能指标说明

| 指标 | 说明 |
|------|------|
| 总收益率 | 整个回测期间的总收益率 |
| 年化收益率 | 按年化计算的收益率 |
| 最大回撤 | 从峰值到谷值的最大跌幅 |
| 夏普比率 | 风险调整后的收益率指标 |
| 胜率 | 盈利交易占总交易的比例 |
| 交易次数 | 总交易次数 |
| 盈亏比 | 平均盈利与平均亏损的比值 |
| 年化波动率 | 收益率的年化标准差 |
| 卡尔马比率 | 年化收益率与最大回撤的比值 |

## 策略详解

### 双均线策略 (MA)
- **原理**：当短期均线上穿长期均线时买入，下穿时卖出
- **参数**：`short_window`（短期窗口）、`long_window`（长期窗口）、`stop_loss`（止损比例）
- **适用场景**：趋势明显的市场

### EMA策略
- **原理**：使用指数移动平均线，对近期价格给予更高权重
- **参数**：`fast_window`（快线周期）、`slow_window`（慢线周期）
- **优势**：对价格变化反应更敏感

### RSI策略
- **原理**：基于价格相对强弱指标，在超买超卖区域进行反向操作
- **参数**：`rsi_window`（RSI周期）、`oversold`（超卖线）、`overbought`（超买线）
- **适用场景**：震荡市场

### MACD策略
- **原理**：基于MACD指标的金叉死叉进行交易
- **参数**：`fast_period`、`slow_period`、`signal_period`
- **特点**：兼具趋势跟踪和震荡特性

### 布林带策略 (BOLL)
- **原理**：价格突破布林带上轨买入，跌破下轨卖出
- **参数**：`period`（周期）、`std_dev`（标准差倍数）
- **适用场景**：突破行情

### KDJ策略
- **原理**：基于随机指标的金叉死叉信号
- **参数**：`k_period`、`d_period`、`j_period`
- **特点**：对短期价格变化敏感

### Dual Thrust策略
- **原理**：基于价格突破动态计算的上下轨道
- **参数**：`window`（回看窗口）、`k1`（上轨系数）、`k2`（下轨系数）
- **优势**：自适应市场波动

### 网格策略 (Grid)
- **原理**：在价格网格间进行高抛低吸
- **参数**：`grid_ratio`（网格间距比例）、`max_grids`（最大网格数）
- **适用场景**：震荡市场

## 注意事项

1. **数据质量**：系统使用模拟数据进行演示，实际使用时请确保数据质量
2. **手续费设置**：默认手续费率为0.03%，请根据实际情况调整
3. **风险控制**：策略仅供学习参考，实际交易请做好风险控制
4. **参数优化**：建议对策略参数进行优化后再使用

## 扩展开发

### 添加新策略

1. 在 `strategy.py` 中继承 `BaseStrategy` 类
2. 实现 `calculate_signals` 方法
3. 在 `StrategyFactory` 中注册新策略

```python
class MyStrategy(BaseStrategy):
    def __init__(self, param1=10):
        super().__init__("我的策略")
        self.param1 = param1
    
    def calculate_signals(self, df):
        df = df.copy()
        # 实现您的策略逻辑
        df['signal'] = 0  # 生成交易信号
        return df
```

### 修改回测参数

在 `backtest.py` 的 `Backtest` 类初始化中修改：

```python
backtest = Backtest(
    initial_capital=100000,  # 初始资金
    commission=0.0003,       # 手续费率
    slippage=0.001          # 滑点
)
```

## 技术支持

如有问题，请检查：
1. 依赖包是否正确安装
2. 运行 `test_system.py` 查看系统状态
3. 查看控制台错误信息

## 更新日志

- v1.0.0: 初始版本，支持8种策略和分钟级数据回测 