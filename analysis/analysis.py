import pandas as pd

# 读取汇总数据
summary_file = '../results/20251228_162148/strategy_summary_20251228_162148.csv'
df = pd.read_csv(summary_file)

# 转换数据类型
df['总收益率数值'] = df['总收益率'].str.rstrip('%').astype(float)
df['最大回撤数值'] = df['最大回撤'].str.rstrip('%').astype(float)
df['胜率数值'] = df['胜率'].str.rstrip('%').astype(float)

print('='*80)
print('策略回测结果分析报告')
print('='*80)
print()

# 按收益率排序
df_sorted = df.sort_values('总收益率数值', ascending=False)
print('📊 策略收益率排名：')
print('-'*80)
for idx, row in df_sorted.iterrows():
    status = '✅' if row['总收益率数值'] > 0 else '❌' if row['总收益率数值'] < 0 else '⚪'
    print(f"{status} {row['策略名称']:20s} | 收益率: {row['总收益率']:>8s} | 夏普: {row['夏普比率']:>7.2f} | 回撤: {row['最大回撤']:>7s} | 胜率: {row['胜率']:>7s} | 交易: {row['交易次数']:>3d}")
print()

# 盈利策略
profitable = df[df['总收益率数值'] > 0]
if len(profitable) > 0:
    print('✅ 盈利策略：')
    print('-'*80)
    for idx, row in profitable.iterrows():
        print(f"  • {row['策略名称']:20s} | 收益率: {row['总收益率']:>8s} | 夏普: {row['夏普比率']:>7.2f} | 胜率: {row['胜率']:>7s} | 交易: {row['交易次数']:>3d}次")
    print()

# 亏损策略
loss = df[df['总收益率数值'] < 0]
if len(loss) > 0:
    print('❌ 亏损策略：')
    print('-'*80)
    for idx, row in loss.iterrows():
        print(f"  • {row['策略名称']:20s} | 收益率: {row['总收益率']:>8s} | 夏普: {row['夏普比率']:>7.2f} | 胜率: {row['胜率']:>7s} | 交易: {row['交易次数']:>3d}次")
    print()

# 无交易策略
no_trade = df[df['交易次数'] == 0]
if len(no_trade) > 0:
    print('⚪ 无交易策略：')
    print('-'*80)
    for idx, row in no_trade.iterrows():
        print(f"  • {row['策略名称']:20s} | 未产生任何交易信号")
    print()

# 最佳策略
best_idx = df['总收益率数值'].idxmax()
best = df.loc[best_idx]
print('🏆 最佳策略：')
print('-'*80)
print(f"  策略名称: {best['策略名称']}")
print(f"  总收益率: {best['总收益率']}")
print(f"  年化收益率: {best['年化收益率']}")
print(f"  最大回撤: {best['最大回撤']}")
print(f"  夏普比率: {best['夏普比率']:.4f}")
print(f"  胜率: {best['胜率']}")
print(f"  交易次数: {best['交易次数']}次")
print()

# 风险分析
print('⚠️  风险分析：')
print('-'*80)
high_drawdown = df[df['最大回撤数值'] > 0].copy()
if len(high_drawdown) > 0:
    worst_dd_idx = high_drawdown['最大回撤数值'].idxmax()
    worst_dd = high_drawdown.loc[worst_dd_idx]
    print(f"  最大回撤策略: {worst_dd['策略名称']} ({worst_dd['最大回撤']})")
    
    avg_drawdown = high_drawdown['最大回撤数值'].mean()
    print(f"  平均最大回撤: {avg_drawdown:.2f}%")
print()

# 交易频率分析
print('📈 交易频率分析：')
print('-'*80)
traded = df[df['交易次数'] > 0]
if len(traded) > 0:
    avg_trades = traded['交易次数'].mean()
    max_trades_idx = traded['交易次数'].idxmax()
    min_trades_idx = traded['交易次数'].idxmin()
    print(f"  平均交易次数: {avg_trades:.1f}次")
    print(f"  最多交易: {traded.loc[max_trades_idx, '策略名称']} ({traded.loc[max_trades_idx, '交易次数']}次)")
    print(f"  最少交易: {traded.loc[min_trades_idx, '策略名称']} ({traded.loc[min_trades_idx, '交易次数']}次)")
print()

# 夏普比率分析
print('📊 风险调整收益分析（夏普比率）：')
print('-'*80)
sharpe_sorted = df[df['交易次数'] > 0].sort_values('夏普比率', ascending=False)
for idx, row in sharpe_sorted.head(5).iterrows():
    print(f"  {row['策略名称']:20s} | 夏普比率: {row['夏普比率']:>7.2f} | 收益率: {row['总收益率']:>8s}")
print()

print('='*80)
print('💡 关键发现：')
print('-'*80)
print('1. 布林带策略表现最佳，收益率2.06%，夏普比率10.07')
print('2. 均值回归策略也有盈利，收益率1.02%，胜率60%')
print('3. 双均线和KDJ策略未产生交易信号，可能需要调整参数')
print('4. 大部分策略在测试期间表现不佳，可能市场环境不适合')
print('5. 建议进一步优化盈利策略的参数，或考虑组合策略')
print('='*80)
