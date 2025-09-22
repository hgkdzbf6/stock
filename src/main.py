from data_fetcher import DataFetcher
from strategies.strategy_factory import StrategyFactory
from backtest import Backtest
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import platform
import matplotlib.font_manager as fm

def setup_chinese_font():
    """根据操作系统设置合适的中文字体"""
    system = platform.system()
    
    if system == "Windows":
        # Windows系统使用SimHei字体
        font_name = 'SimHei'
    elif system == "Darwin":  # macOS
        # macOS系统使用PingFang SC字体
        font_name = 'PingFang SC'
    else:  # Linux或其他系统
        # 尝试使用常见的中文字体
        font_name = 'DejaVu Sans'
    
    # 检查字体是否可用
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    if font_name in available_fonts:
        plt.rcParams['font.family'] = font_name
        print(f"使用字体: {font_name}")
    else:
        # 如果指定字体不可用，尝试其他中文字体
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', 'WenQuanYi Micro Hei', 'DejaVu Sans']
        
        for font in chinese_fonts:
            if font in available_fonts:
                plt.rcParams['font.family'] = font
                print(f"使用备用字体: {font}")
                break
        else:
            # 如果所有中文字体都不可用，使用默认字体
            plt.rcParams['font.family'] = 'DejaVu Sans'
            print("警告: 未找到合适的中文字体，使用默认字体")
    
    # 设置负号显示
    plt.rcParams['axes.unicode_minus'] = False

# 设置中文字体
setup_chinese_font()

def plot_single_strategy(strategy_name, results, initial_capital, save_dir=None):
    """绘制单个策略的详细图表"""
    import os
    
    # 创建单个策略保存目录
    if save_dir:
        safe_name = strategy_name.replace(' ', '_').replace('/', '_')
        strategy_dir = os.path.join(save_dir, f'{safe_name}')
        if not os.path.exists(strategy_dir):
            os.makedirs(strategy_dir)
    
    # 1. 策略收益曲线
    plt.figure(figsize=(12, 8))
    plt.plot(results.index, results['total_value'], label='策略收益', linewidth=2, color='blue')
    plt.axhline(y=initial_capital, color='red', linestyle='--', alpha=0.7, label='基准线')
    plt.title(f'{strategy_name} - 收益曲线', fontsize=16, fontweight='bold')
    plt.ylabel('账户价值 (元)', fontsize=12)
    plt.xlabel('时间', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 设置x轴日期格式 - 自适应密度
    ax = plt.gca()
    data_days = (results.index[-1] - results.index[0]).days
    if data_days <= 7:
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    elif data_days <= 30:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    elif data_days <= 180:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    plt.tight_layout()
    if save_dir:
        plt.savefig(os.path.join(strategy_dir, '1_收益曲线.png'), dpi=300, bbox_inches='tight')
        plt.close()  # 关闭图形释放内存
    
    # 2. 回撤曲线
    cumulative = results['total_value']
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max * 100
    
    plt.figure(figsize=(12, 8))
    plt.fill_between(results.index, drawdown, 0, color='red', alpha=0.3, label='回撤')
    plt.plot(results.index, drawdown, color='red', linewidth=1)
    plt.title(f'{strategy_name} - 回撤曲线', fontsize=16, fontweight='bold')
    plt.ylabel('回撤 (%)', fontsize=12)
    plt.xlabel('时间', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 设置x轴日期格式 - 自适应密度
    ax = plt.gca()
    data_days = (results.index[-1] - results.index[0]).days
    if data_days <= 7:
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    elif data_days <= 30:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    else:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    plt.tight_layout()
    if save_dir:
        plt.savefig(os.path.join(strategy_dir, '2_回撤曲线.png'), dpi=300, bbox_inches='tight')
        plt.close()  # 关闭图形释放内存
    
    # 3. 持仓变化
    plt.figure(figsize=(12, 8))
    position_ratio = results['shares'] * results['close'] / results['total_value']
    plt.fill_between(results.index, position_ratio, color='skyblue', alpha=0.7, label='持仓比例')
    plt.title(f'{strategy_name} - 持仓比例变化', fontsize=16, fontweight='bold')
    plt.ylabel('持仓比例', fontsize=12)
    plt.xlabel('时间', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 设置x轴日期格式 - 自适应密度
    ax = plt.gca()
    data_days = (results.index[-1] - results.index[0]).days
    if data_days <= 7:
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    elif data_days <= 30:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    else:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    plt.tight_layout()
    if save_dir:
        plt.savefig(os.path.join(strategy_dir, '3_持仓比例变化.png'), dpi=300, bbox_inches='tight')
        plt.close()  # 关闭图形释放内存
    
    # 4. 交易信号图
    if 'signal' in results.columns:
        plt.figure(figsize=(12, 8))
        plt.plot(results.index, results['close'], label='价格', linewidth=1, color='black')
        
        # 买入信号
        buy_signals = results[results['signal'] == 1]
        if not buy_signals.empty:
            plt.scatter(buy_signals.index, buy_signals['close'], 
                       color='red', marker='^', s=100, label='买入信号', zorder=5)
        
        # 卖出信号
        sell_signals = results[results['signal'] == -1]
        if not sell_signals.empty:
            plt.scatter(sell_signals.index, sell_signals['close'], 
                       color='green', marker='v', s=100, label='卖出信号', zorder=5)
        
        plt.title(f'{strategy_name} - 交易信号', fontsize=16, fontweight='bold')
        plt.ylabel('价格 (元)', fontsize=12)
        plt.xlabel('时间', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 设置x轴日期格式 - 自适应密度
        ax = plt.gca()
        data_days = (results.index[-1] - results.index[0]).days
        if data_days <= 7:
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        elif data_days <= 30:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        else:
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        plt.tight_layout()
        if save_dir:
            plt.savefig(os.path.join(strategy_dir, '4_交易信号.png'), dpi=300, bbox_inches='tight')
            plt.close()  # 关闭图形释放内存

def run_single_strategy(strategy_name, df, initial_capital, save_dir=None, **strategy_params):
    """运行单个策略"""
    print(f"\n=== 运行{strategy_name}策略 ===")
    
    # 创建策略
    strategy = StrategyFactory.create_strategy(strategy_name, **strategy_params)
    
    # 计算信号
    df_with_signals = strategy.calculate_signals(df)
    
    # 回测
    backtest = Backtest(initial_capital=initial_capital)
    results = backtest.run(df_with_signals)
    metrics = backtest.get_metrics()
    
    # 打印结果
    print(f"策略名称: {strategy.name}")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # 生成单个策略图表
    if save_dir:
        print(f"正在生成 {strategy.name} 的详细图表...")
        plot_single_strategy(strategy.name, results, initial_capital, save_dir)
    
    return results, metrics, strategy.name

def plot_comparison_results(results_dict, initial_capital, save_dir=None):
    """绘制多策略比较图 - 分成四张独立图表并保存"""
    import os
    
    # 创建对比图表保存目录
    if save_dir:
        comparison_dir = os.path.join(save_dir, '策略对比图表')
        if not os.path.exists(comparison_dir):
            os.makedirs(comparison_dir)
    
    # 1. 策略收益曲线对比
    plt.figure(figsize=(12, 8))
    for strategy_name, results in results_dict.items():
        plt.plot(results.index, results['total_value'], label=strategy_name, linewidth=2)
    
    plt.axhline(y=initial_capital, color='red', linestyle='--', alpha=0.7, label='基准线')
    plt.title('策略收益曲线对比', fontsize=16, fontweight='bold')
    plt.ylabel('账户价值 (元)', fontsize=12)
    plt.xlabel('时间', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # 设置x轴日期格式 - 自适应密度
    ax = plt.gca()
    first_results = list(results_dict.values())[0]
    data_days = (first_results.index[-1] - first_results.index[0]).days
    if data_days <= 7:
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    elif data_days <= 30:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    else:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    plt.tight_layout()
    if save_dir:
        plt.savefig(os.path.join(comparison_dir, '1_策略收益曲线对比.png'), dpi=300, bbox_inches='tight')
        print(f"✓ 保存: 策略收益曲线对比图")
        plt.close()  # 关闭图形释放内存
    
    # 2. 收益率对比
    returns_data = []
    strategy_names = []
    
    for strategy_name, results in results_dict.items():
        total_return = (results['total_value'].iloc[-1] - initial_capital) / initial_capital
        returns_data.append(total_return * 100)
        strategy_names.append(strategy_name)
    
    plt.figure(figsize=(12, 8))
    colors = plt.cm.Set3(np.linspace(0, 1, len(strategy_names)))
    bars = plt.bar(strategy_names, returns_data, color=colors)
    plt.title('策略总收益率对比 (%)', fontsize=16, fontweight='bold')
    plt.ylabel('收益率 (%)', fontsize=12)
    plt.xlabel('策略名称', fontsize=12)
    plt.grid(True, alpha=0.3, axis='y')
    
    # 在柱状图上显示数值
    for bar, value in zip(bars, returns_data):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + (0.1 if height >= 0 else -0.1),
                f'{value:.2f}%', ha='center', va='bottom' if height >= 0 else 'top')
    
    plt.setp(plt.gca().xaxis.get_majorticklabels(), rotation=45)
    plt.tight_layout()
    if save_dir:
        plt.savefig(os.path.join(comparison_dir, '2_策略收益率对比.png'), dpi=300, bbox_inches='tight')
        print(f"✓ 保存: 策略收益率对比图")
        plt.close()  # 关闭图形释放内存
    
    # 3. 回撤对比
    drawdown_data = []
    for strategy_name, results in results_dict.items():
        cumulative = results['total_value']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min()) * 100
        drawdown_data.append(max_drawdown)
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(strategy_names, drawdown_data, color=colors)
    plt.title('策略最大回撤对比 (%)', fontsize=16, fontweight='bold')
    plt.ylabel('最大回撤 (%)', fontsize=12)
    plt.xlabel('策略名称', fontsize=12)
    plt.grid(True, alpha=0.3, axis='y')
    
    # 在柱状图上显示数值
    for bar, value in zip(bars, drawdown_data):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{value:.2f}%', ha='center', va='bottom')
    
    plt.setp(plt.gca().xaxis.get_majorticklabels(), rotation=45)
    plt.tight_layout()
    if save_dir:
        plt.savefig(os.path.join(comparison_dir, '3_策略回撤对比.png'), dpi=300, bbox_inches='tight')
        print(f"✓ 保存: 策略回撤对比图")
        plt.close()  # 关闭图形释放内存
    
    # 4. 持仓比例变化 (以表现最好的策略为例)
    # 找到收益率最高的策略
    best_strategy_name = strategy_names[np.argmax(returns_data)]
    best_strategy_results = results_dict[best_strategy_name]
    
    plt.figure(figsize=(12, 8))
    position_ratio = best_strategy_results['shares'] * best_strategy_results['close'] / best_strategy_results['total_value']
    plt.fill_between(best_strategy_results.index, position_ratio, 
                     color='skyblue', alpha=0.7, label=f'持仓比例 ({best_strategy_name})')
    plt.title(f'持仓比例变化 - {best_strategy_name}', fontsize=16, fontweight='bold')
    plt.xlabel('时间', fontsize=12)
    plt.ylabel('持仓比例', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 设置x轴日期格式 - 自适应密度
    ax = plt.gca()
    data_days = (best_strategy_results.index[-1] - best_strategy_results.index[0]).days
    if data_days <= 7:
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    elif data_days <= 30:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    else:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    plt.tight_layout()
    if save_dir:
        plt.savefig(os.path.join(comparison_dir, '4_持仓比例变化.png'), dpi=300, bbox_inches='tight')
        print(f"✓ 保存: 持仓比例变化图")
        plt.close()  # 关闭图形释放内存

def main():
    """主函数"""
    print("=== 量化交易策略回测系统 ===")
    
    # 初始化参数
    token = 'bcfab7bccd8e066c2290c423bdb2d399b34690884be7b1ae05db1011'  # tushare token
    stock_code = '600771'  # 股票代码
    initial_capital = 100000  # 初始资金10万
    
    # 时间设置 - 获取最近7天的分钟数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    print(f"回测时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    print(f"股票代码: {stock_code}")
    print(f"初始资金: {initial_capital:,} 元")
    
    # 获取数据
    print("\n正在获取数据...")
    try:
        # 优先使用akshare，如果失败则使用tushare
        fetcher = DataFetcher(source='akshare')
        df = fetcher.get_data(stock_code, start_date, end_date, freq='1d')  # 5分钟数据
    except Exception as e:
        print(f"使用akshare获取数据失败: {e}")
        print("尝试使用tushare...")
        fetcher = DataFetcher(token=token, source='tushare')
        df = fetcher.get_data(stock_code, start_date, end_date, freq='1d')
    
    print(f"数据获取完成，共{len(df)}条记录")
    print(f"数据时间范围: {df.index[0]} 到 {df.index[-1]}")
    
    # 定义要测试的策略 - 使用改进的参数
    strategies_config = StrategyFactory.get_default_params()
    
    # 可以选择测试的策略子集
    selected_strategies = [
        'MA', 'EMA', 'RSI', 'MACD', 'BOLL', 'KDJ', 'DualThrust', 'Grid',
        'MeanReversion', 'TrendFollowing', 'WilliamsR'  # 添加新策略
    ]
    
    # 过滤出选定的策略
    strategies_config = {k: v for k, v in strategies_config.items() if k in selected_strategies}
    
    # 创建保存目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    import os
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results', str(timestamp))
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # 运行所有策略
    results_dict = {}
    metrics_dict = {}
    
    for strategy_name, params in strategies_config.items():
        try:
            results, metrics, display_name = run_single_strategy(
                strategy_name, df, initial_capital, results_dir, **params
            )
            results_dict[display_name] = results
            metrics_dict[display_name] = metrics
        except Exception as e:
            print(f"策略 {strategy_name} 运行失败: {e}")
            continue
    
    # 策略性能总结
    print("\n" + "="*60)
    print("策略性能总结")
    print("="*60)
    
    summary_data = []
    for strategy_name, metrics in metrics_dict.items():
        summary_data.append({
            '策略名称': strategy_name,
            '总收益率': metrics['总收益率'],
            '年化收益率': metrics['年化收益率'],
            '最大回撤': metrics['最大回撤'],
            '夏普比率': metrics['夏普比率'],
            '胜率': metrics['胜率'],
            '交易次数': metrics['交易次数']
        })
    
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    
    # 绘制对比图表
    if results_dict:
        print("\n正在生成策略对比图表...")
        plot_comparison_results(results_dict, initial_capital, results_dir)
    
    # 保存结果到CSV
    print("\n正在保存CSV结果...")
    
    # 保存策略性能总结
    summary_df.to_csv(os.path.join(results_dir, f'strategy_summary_{timestamp}.csv'), 
                      index=False, encoding='utf-8-sig')
    
    # 保存详细回测结果
    for strategy_name, results in results_dict.items():
        safe_name = strategy_name.replace(' ', '_').replace('/', '_')
        filename = os.path.join(results_dir, f'{safe_name}_{timestamp}.csv')
        results.to_csv(filename, encoding='utf-8-sig')
    
    print(f"结果已保存到 {results_dir} 目录")
    print("回测完成！")

if __name__ == "__main__":
    main() 