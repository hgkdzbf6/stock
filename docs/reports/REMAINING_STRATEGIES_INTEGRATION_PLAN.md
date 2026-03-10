# 剩余策略集成计划

## 概述

本文档说明如何继续集成myquant/strategy仓库中的剩余策略。

## 已完成的策略

✅ **已集成**：
1. 双均线策略（MA）
2. RSI策略
3. MACD策略
4. 布林带策略（BOLL）
5. 海龟交易策略（TURTLE）

## 待集成的策略

### 1. KDJ策略 ⭐ 优先级高

**策略描述**：
- 基于随机指标（Stochastic Oscillator）的超买超卖策略
- 适合短线交易和震荡市场
- 信号频率较高

**核心逻辑**：
```python
# 计算KDJ指标
slowk, slowd = talib.STOCH(
    high=high_prices,
    low=low_prices,
    close=close_prices,
    fastk_period=9,      # 快速K线周期
    slowk_period=3,       # 慢速K线周期
    slowk_matype=0,       # K线平滑方法
    slowd_period=3,       # D线周期
    slowd_matype=0        # D线平滑方法
)

# 生成信号
买入条件：slowk < 20 或 slowd < 20（超卖）
卖出条件：slowk > 80 或 slowd > 80（超买）
```

**参数配置**：
- `fastk_period`：快速K线周期，默认9
- `slowk_period`：慢速K线周期，默认3
- `slowd_period`：D线周期，默认3
- `kdj_buy`：买入阈值，默认20
- `kdj_sell`：卖出阈值，默认80

**实现代码**：
```python
def _calculate_kdj_signals(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
    """计算KDJ策略信号"""
    fastk_period = params.get('fastk_period', 9)
    slowk_period = params.get('slowk_period', 3)
    slowd_period = params.get('slowd_period', 3)
    kdj_buy = params.get('kdj_buy', 20)
    kdj_sell = params.get('kdj_sell', 80)
    
    # 计算KDJ
    low_min = df['low'].rolling(window=fastk_period).min()
    high_max = df['high'].rolling(window=fastk_period).max()
    rsv = (df['close'] - low_min) / (high_max - low_min) * 100
    
    df['K'] = rsv.ewm(com=slowk_period-1, adjust=False).mean()
    df['D'] = df['K'].ewm(com=slowd_period-1, adjust=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    
    # 生成信号
    df['signal'] = 0
    df.loc[df['K'] < kdj_buy, 'signal'] = 1  # K线超卖买入
    df.loc[df['K'] > kdj_sell, 'signal'] = -1  # K线超买卖出
    
    # 消除连续信号
    df['signal'] = df['signal'].diff()
    df['signal'] = df['signal'].fillna(0)
    
    return df
```

---

### 2. ATR策略

**策略描述**：
- 基于平均真实波幅（ATR）的波动率策略
- 主要用于止损设置和仓位管理
- 可以单独作为趋势突破策略

**核心逻辑**：
```python
# 计算ATR
high_low = df['high'] - df['low']
high_close = abs(df['high'] - df['close'].shift())
low_close = abs(df['low'] - df['close'].shift())
tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
df['ATR'] = tr.rolling(window=14).mean()

# 基于ATR的突破
df['ATR_upper'] = df['close'] + 2 * df['ATR']
df['ATR_lower'] = df['close'] - 2 * df['ATR']

# 生成信号
买入：突破ATR上轨
卖出：跌破ATR下轨
```

**参数配置**：
- `atr_period`：ATR周期，默认14
- `atr_multiplier`：ATR倍数，默认2

---

### 3. Dual-Thrust策略

**策略描述**：
- 基于区间突破的日内交易策略
- 根据前N日的高低价和开盘价确定突破区间
- 适合期货和股票日内交易

**核心逻辑**：
```python
# 计算Dual-Thrust区间
n_days = params.get('n_days', 5)
k1 = params.get('k1', 0.7)
k2 = params.get('k2', 0.7)

high_range = df['high'].rolling(window=n_days).max()
low_range = df['low'].rolling(window=n_days).min()
open_price = df['open']

# 计算突破区间
upper_bound = open_price + k1 * (high_range - low_range)
lower_bound = open_price - k2 * (high_range - low_range)

# 生成信号
买入：突破上轨
卖出：跌破下轨
```

**参数配置**：
- `n_days`：回看天数，默认5
- `k1`：上轨系数，默认0.7
- `k2`：下轨系数，默认0.7

---

### 4. Hans123策略

**策略描述**：
- 基于开盘后30分钟区间的突破策略
- 经典的日内交易系统
- 适合波动较大的市场

**核心逻辑**：
```python
# 获取开盘后30分钟的区间
morning_high = df['high'].iloc[0:6].max()  # 前30分钟最高价
morning_low = df['low'].iloc[0:6].min()    # 前30分钟最低价

# 计算突破区间
breakout_range = morning_high - morning_low
upper_entry = morning_high + 0.1 * breakout_range
lower_entry = morning_low - 0.1 * breakout_range

# 生成信号
买入：突破上轨
卖出：跌破下轨
```

**参数配置**：
- `session_length`：早盘时长（分钟），默认30
- `breakout_percent`：突破百分比，默认0.1

---

## 集成步骤

### 步骤1：更新回测引擎

在 `backend/services/backtest_service.py` 中添加策略实现：

```python
def _calculate_indicators(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
    # ... 现有代码 ...
    
    # 添加新策略
    elif strategy_type == 'KDJ':
        df = self._calculate_kdj_signals(df, params)
    elif strategy_type == 'ATR':
        df = self._calculate_atr_signals(df, params)
    elif strategy_type == 'DUAL_THRUST':
        df = self._calculate_dual_thrust_signals(df, params)
    elif strategy_type == 'HANS123':
        df = self._calculate_hans123_signals(df, params)
```

### 步骤2：实现策略方法

为每个策略添加计算方法（参考上面的核心逻辑代码）。

### 步骤3：更新API层

在 `backend/api/strategies.py` 中添加策略模板：

```python
STRATEGY_TEMPLATES = {
    # ... 现有策略 ...
    'KDJ': {
        'name': 'KDJ策略',
        'description': '基于随机指标的超买超卖',
        'params': {
            'fastk_period': {'type': 'int', 'default': 9, 'min': 5, 'max': 20, 'description': '快速K线周期'},
            'slowk_period': {'type': 'int', 'default': 3, 'min': 1, 'max': 10, 'description': '慢速K线周期'},
            'slowd_period': {'type': 'int', 'default': 3, 'min': 1, 'max': 10, 'description': 'D线周期'},
            'kdj_buy': {'type': 'int', 'default': 20, 'min': 5, 'max': 40, 'description': '买入阈值'},
            'kdj_sell': {'type': 'int', 'default': 80, 'min': 60, 'max': 95, 'description': '卖出阈值'}
        }
    },
    'ATR': {
        'name': 'ATR策略',
        'description': '基于平均真实波幅的趋势跟踪',
        'params': {
            'atr_period': {'type': 'int', 'default': 14, 'min': 5, 'max': 30, 'description': 'ATR周期'},
            'atr_multiplier': {'type': 'float', 'default': 2.0, 'min': 1.0, 'max': 5.0, 'description': 'ATR倍数'}
        }
    },
    # ... 其他策略 ...
}
```

在策略列表中添加示例数据。

### 步骤4：更新前端

在 `frontend/src/pages/Strategies.tsx` 中：

1. 添加策略到mockStrategies数组
2. 在策略类型下拉框添加选项
3. 添加动态参数表单

### 步骤5：测试验证

1. 使用不同股票测试每个策略
2. 验证参数范围合理性
3. 检查信号产生频率
4. 对比不同策略的表现

## 优先级建议

### 高优先级（立即集成）
1. **KDJ策略** ⭐
   - 信号频率高，容易测试
   - 适合短线交易
   - 实现相对简单

### 中优先级（后续集成）
2. **ATR策略**
   - 可用于止损设置
   - 可以结合其他策略使用
   
3. **Dual-Thrust策略**
   - 适合日内交易
   - 有明确的区间概念

### 低优先级（可选）
4. **Hans123策略**
   - 需要处理早盘数据
   - 实现相对复杂

## 增强功能

### 1. 参数优化

实现参数优化功能，自动寻找最优参数：

```python
from optimizers import GridSearchOptimizer

# 定义参数空间
param_space = {
    'period': [10, 15, 20, 25, 30],
    'stop_loss': [0.05, 0.1, 0.15]
}

# 运行优化
optimizer = GridSearchOptimizer()
best_params = optimizer.optimize(
    strategy='TURTLE',
    param_space=param_space,
    stock_code='600771',
    evaluation_metric='sharpe_ratio'
)
```

### 2. 多策略组合

实现多策略组合回测：

```python
class MultiStrategyBacktester:
    def __init__(self):
        self.strategies = ['MA', 'RSI', 'TURTLE']
        self.weights = [0.3, 0.3, 0.4]
    
    def run_backtest(self, df, params_list):
        signals = []
        for strategy, weight in zip(self.strategies, self.weights):
            signal = self._calculate_signal(df, strategy, params[strategy])
            signals.append(signal * weight)
        
        combined_signal = sum(signals)
        return self._execute_trades(combined_signal)
```

### 3. 实时交易信号

将回测策略转换为实时交易信号：

```python
class RealtimeSignalGenerator:
    def __init__(self, strategy_type, params):
        self.strategy = BacktestEngine()
        self.strategy_type = strategy_type
        self.params = params
        self.history = []
    
    def on_new_bar(self, bar_data):
        self.history.append(bar_data)
        df = pd.DataFrame(self.history)
        
        if len(df) >= self._min_required_bars():
            signals = self._calculate_indicators(df, self.params)
            latest_signal = signals.iloc[-1]['signal']
            
            if latest_signal != 0:
                self._send_signal(latest_signal, bar_data)
    
    def _send_signal(self, signal, bar_data):
        # 发送实时信号
        if signal == 1:
            self._notify_buy(bar_data)
        elif signal == -1:
            self._notify_sell(bar_data)
```

## 测试建议

### 1. 单策略测试

对每个策略进行单独测试：
```bash
# 测试KDJ策略
curl -X POST "http://localhost:8000/api/v1/strategies/6/backtest" \
  -d '{
    "stock_code": "600771",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "strategy_type": "KDJ",
    "custom_params": {
      "fastk_period": 9,
      "slowk_period": 3,
      "kdj_buy": 20,
      "kdj_sell": 80
    }
  }'
```

### 2. 参数优化测试

测试不同参数组合：
```python
test_periods = [5, 10, 15, 20, 25, 30]
results = []

for period in test_periods:
    result = backtest(stock='600771', strategy='TURTLE', params={'period': period})
    results.append({
        'period': period,
        'return': result['total_return'],
        'sharpe': result['sharpe_ratio']
    })

# 找到最优参数
best = max(results, key=lambda x: x['sharpe'])
print(f"Best period: {best['period']}, Sharpe: {best['sharpe']}")
```

### 3. 多策略对比

对比不同策略的表现：
```python
strategies = ['MA', 'RSI', 'MACD', 'BOLL', 'TURTLE', 'KDJ']
comparison = []

for strategy in strategies:
    result = backtest(stock='600771', strategy=strategy)
    comparison.append({
        'strategy': strategy,
        'return': result['total_return'],
        'sharpe': result['sharpe_ratio'],
        'max_dd': result['max_drawdown']
    })

# 生成对比报告
df_comparison = pd.DataFrame(comparison)
print(df_comparison)
```

## 总结

### 当前状态
- ✅ 已集成5个基础策略
- ✅ 海龟策略有详细文档
- ✅ 前端界面完整
- ⏳ 待集成4个高级策略

### 下一步行动
1. **立即**：集成KDJ策略（高优先级）
2. **本周**：集成ATR和Dual-Thrust策略
3. **下周**：集成Hans123策略
4. **持续**：实现参数优化和多策略组合

### 预期效果
集成完成后，系统将拥有：
- 9个完整策略（5个基础 + 4个高级）
- 参数优化功能
- 多策略组合能力
- 实时交易信号生成

---

**文档版本**：v1.0  
**创建时间**：2026-02-22