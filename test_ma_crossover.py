"""测试MA交叉逻辑"""
import pandas as pd
import numpy as np

# 创建测试数据
dates = pd.date_range('2025-08-14', periods=30, freq='B')
prices = np.array([21.55, 21.91, 22.92, 21.47, 21.44, 21.23, 21.32, 21.48, 21.21, 
                  20.76, 20.36, 20.22, 20.32, 20.04, 19.87, 19.68, 20.12, 20.05, 
                  20.06, 19.98, 19.85, 19.72, 19.59, 19.80, 20.10, 19.96, 
                  20.15, 20.30, 20.45, 21.20])

df = pd.DataFrame({
    'close': prices
}, index=dates)

# 计算MA
df['MA_short'] = df['close'].rolling(window=5).mean()
df['MA_long'] = df['close'].rolling(window=10).mean()

print("=" * 80)
print("MA交叉测试")
print("=" * 80)
print(f"\n数据点数: {len(df)}")
print("\n原始数据和MA值:")
print(df[['close', 'MA_short', 'MA_long']].round(2))

# 方法1: 当前代码的逻辑
print("\n" + "=" * 80)
print("方法1: 当前代码逻辑 (先设置信号，再diff)")
print("=" * 80)

df1 = df.copy()
df1['signal_raw'] = 0
df1.loc[df1['MA_short'] > df1['MA_long'], 'signal_raw'] = 1
df1.loc[df1['MA_short'] < df1['MA_long'], 'signal_raw'] = -1
df1['signal'] = df1['signal_raw'].diff().fillna(0)

print("\n信号分析:")
print(f"signal_raw 值分布:\n{df1['signal_raw'].value_counts()}")
print(f"\nsignal 值分布:\n{df1['signal'].value_counts()}")
print(f"\n有信号的数据点:\n{df1[df1['signal'] != 0][['close', 'MA_short', 'MA_long', 'signal_raw', 'signal']]}")

# 方法2: 正确的交叉检测逻辑
print("\n" + "=" * 80)
print("方法2: 正确的交叉检测 (检测相邻两天的变化)")
print("=" * 80)

df2 = df.copy()
df2['position'] = 0  # 当前持仓状态
df2.loc[df2['MA_short'] > df2['MA_long'], 'position'] = 1
df2.loc[df2['MA_short'] < df2['MA_long'], 'position'] = -1

df2['position_prev'] = df2['position'].shift(1)
df2['signal_correct'] = df2['position'] - df2['position_prev']
df2['signal_correct'] = df2['signal_correct'].fillna(0)

print("\n信号分析:")
print(f"position 值分布:\n{df2['position'].value_counts()}")
print(f"\nsignal_correct 值分布:\n{df2['signal_correct'].value_counts()}")
print(f"\n有信号的数据点:\n{df2[df2['signal_correct'] != 0][['close', 'MA_short', 'MA_long', 'position', 'position_prev', 'signal_correct']]}")

print("\n" + "=" * 80)
print("总结:")
print("=" * 80)
print(f"方法1产生的交易信号数: {len(df1[df1['signal'] != 0])}")
print(f"方法2产生的交易信号数: {len(df2[df2['signal_correct'] != 0])}")