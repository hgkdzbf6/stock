# 海龟交易策略详解

## 什么是海龟交易策略？

### 历史背景

海龟交易策略（Turtle Trading System）是由著名的美国商品交易员**理查德·丹尼斯**（Richard Dennis）在1983年创立的经典趋势跟踪策略。

**传奇故事**：
- 1983年，理查德·丹尼斯和威廉·埃克哈特进行了一场著名的赌约
- **争议焦点**：成功的交易员是"天生的"还是"可以培养的"？
- **实验设计**：丹尼斯招募了一群完全没有交易经验的人（包括厨师、保安、演员等）
- **培训过程**：仅用两周时间教授他们一套完整的交易系统
- **惊人成果**：这些被称为"海龟"的新手，在4年内创造了年均80%以上的收益率
- **历史意义**：证明了交易技能是可以系统化学习和复制的

### 核心思想

海龟交易策略的核心是**趋势跟踪**（Trend Following），基于以下原则：

1. **趋势延续性**：市场趋势一旦形成，往往会持续一段时间
2. **突破交易**：当价格突破历史高点或低点时，趋势可能开始或反转
3. **让利润奔跑**：不轻易止损，让利润最大化
4. **严格止损**：一旦判断错误，立即止损

### 原始海龟交易系统

完整的海龟交易系统包含：

#### 1. 入场规则
- **唐奇安通道突破**：价格突破过去N日最高价/最低价
- **系统1**：20日突破（短期系统）
- **系统2**：55日突破（长期系统）
- 海龟通常同时运行两个系统，资金分配各50%

#### 2. 止损规则
- 使用ATR（Average True Range，平均真实波幅）设置止损
- 止损距离 = 2 × ATR
- 如果价格反向突破止损位，立即平仓

#### 3. 仓位管理
- 基于账户净值和ATR计算每手交易数量
- 单个头寸不超过账户净值的2%
- 高度相关品种总仓位不超过6%
- 所有品种总仓位不超过12%

#### 4. 加仓规则
- 如果价格朝有利方向移动0.5ATR，可以加仓
- 最多加仓3次
- 每次加仓后调整止损位

## 我们的简化实现

### 当前实现逻辑

```python
def _calculate_turtle_signals(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
    """计算海龟交易策略信号（唐奇安通道突破）"""
    period = params.get('period', 20)  # 突破周期
    
    # 计算唐奇安通道
    df['turtle_high'] = df['high'].rolling(window=period).max()
    df['turtle_low'] = df['low'].rolling(window=period).min()
    
    # 生成信号
    df['signal'] = 0
    df.loc[df['close'] > df['turtle_high'].shift(1), 'signal'] = 1  # 突破上轨买入
    df.loc[df['close'] < df['turtle_low'].shift(1), 'signal'] = -1  # 跌破下轨卖出
    
    # 消除连续信号
    df['signal'] = df['signal'].diff()
    df['signal'] = df['signal'].fillna(0)
    
    return df
```

### 为什么没有交易信号？

可能的原因：

#### 1. **数据量不足** ⚠️ 最常见
- **问题**：如果回测数据少于period（默认20天），rolling窗口会返回NaN
- **结果**：无法计算唐奇安通道，自然没有突破信号
- **解决方案**：确保回测周期至少是period的2-3倍

**示例**：
```
回测周期：2024-01-01 到 2024-01-15（15天）
突破周期：20天
结果：前20天的turtle_high和turtle_low都是NaN，无法产生信号
```

#### 2. **市场波动小**
- **问题**：在横盘震荡市场中，价格很少突破20日高低点
- **结果**：突破信号稀少
- **特征**：这是海龟策略的正常现象，它在趋势市场表现更好

#### 3. **突破条件严格**
```python
df.loc[df['close'] > df['turtle_high'].shift(1), 'signal'] = 1
```
- 必须是收盘价严格大于前一天的最高通道值
- 如果价格盘中突破但收盘回落，不会产生信号

#### 4. **信号被diff()消除**
```python
df['signal'] = df['signal'].diff()
```
- 这行代码会消除连续的信号
- 如果出现连续多个买入/卖出信号，会被合并为一个

## 调试建议

### 1. 检查数据量

```python
# 在回测时添加日志
logger.info(f"回测数据点数: {len(df)}")
logger.info(f"所需周期: {period}")
logger.info(f"有效数据点数: {len(df.dropna(subset=['turtle_high']))}")
```

### 2. 查看中间结果

```python
# 打印前30行数据，检查通道计算
print(df[['close', 'turtle_high', 'turtle_low', 'signal']].head(30))
```

### 3. 降低突破周期测试

```python
# 将period从20改为10或5，增加信号产生频率
period = 10  # 更容易产生信号
```

### 4. 选择波动大的股票

- 选择近期有大幅涨跌的股票
- 选择成交活跃的热门股
- 避免长期横盘的股票

## 改进建议

### 1. 添加数据量检查

```python
if len(df) < period * 2:
    raise Exception(f"数据量不足：需要至少{period*2}天数据，当前只有{len(df)}天")
```

### 2. 添加ATR止损（更接近原始策略）

```python
# 计算ATR
high_low = df['high'] - df['low']
high_close = np.abs(df['high'] - df['close'].shift())
low_close = np.abs(df['low'] - df['close'].shift())
tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
df['ATR'] = tr.rolling(window=14).mean()

# 基于ATR设置止损
df['stop_loss_long'] = df['close'] - 2 * df['ATR']
df['stop_loss_short'] = df['close'] + 2 * df['ATR']
```

### 3. 添加加仓功能

```python
# 当价格朝有利方向移动时加仓
if position_size > 0 and price > entry_price * (1 + 0.5 * atr_percent):
    add_position()
```

### 4. 同时运行两个系统

```python
# 系统1：20日突破
system1_signals = calculate_turtle(df, period=20)

# 系统2：55日突破
system2_signals = calculate_turtle(df, period=55)

# 合并信号（权重各50%）
final_signals = (system1_signals + system2_signals) / 2
```

## 实际使用建议

### 1. 选择合适的回测周期

```
短期回测（1-3个月）：period=10
中期回测（3-6个月）：period=20
长期回测（6个月以上）：period=55
```

### 2. 选择合适的股票

**适合海龟策略的股票**：
- ✅ 趋势明显的股票
- ✅ 波动较大的股票
- ✅ 成交活跃的热门股
- ✅ 有题材炒作的股票

**不适合海龟策略的股票**：
- ❌ 长期横盘的股票
- ❌ 波动极小的蓝筹股
- ❌ 指数基金ETF
- ❌ 价格变化平缓的债券

### 3. 参数优化

```python
# 可以尝试不同的period值
period_options = [5, 10, 15, 20, 30, 55]

# 回测对比，找到最适合当前市场环境的参数
for period in period_options:
    result = backtest(stock, period=period)
    print(f"Period={period}, Return={result['total_return']}")
```

### 4. 结合其他指标

可以将海龟策略与其他指标结合：
- **MACD**：确认趋势方向
- **RSI**：避免在极端超买超卖时交易
- **成交量**：突破时应该有放量

## 总结

海龟交易策略是：
- ✅ **经典**：经过30多年市场验证
- ✅ **简单**：规则清晰，易于理解
- ✅ **有效**：在趋势市场表现优异
- ⚠️ **信号少**：需要耐心等待
- ⚠️ **震荡市场表现差**：需要选择合适的股票

**没有信号是正常的**！这恰恰说明策略在严格执行规则，避免在不确定的市场中交易。如果想要更多交易机会，可以：
1. 降低period参数（从20改为10）
2. 选择波动更大的股票
3. 扩大回测周期
4. 结合其他策略（如MACD）

---

**文档版本**：v1.0  
**创建时间**：2026-02-22