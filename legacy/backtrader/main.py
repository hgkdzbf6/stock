
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtrader 量化交易主程序
集成 akshare/tushare 数据源，支持多种策略回测
"""

import sys
import os
from datetime import datetime, timedelta

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtest_engine import BacktestEngine
from strategies import STRATEGY_MAP

def setup_chinese_font():
    """设置中文字体"""
    import matplotlib.pyplot as plt
    import platform
    
    system = platform.system()
    
    if system == "Windows":
        font_name = 'SimHei'
    elif system == "Darwin":  # macOS
        font_name = 'PingFang SC'
    else:  # Linux或其他系统
        font_name = 'DejaVu Sans'
    
    plt.rcParams['font.family'] = font_name
    plt.rcParams['axes.unicode_minus'] = False

def main():
    """主函数"""
    print("=== Backtrader 量化交易回测系统 ===")
    
    # 设置中文字体
    setup_chinese_font()
    
    # 初始化回测引擎
    engine = BacktestEngine(
        initial_capital=100000,  # 初始资金10万
        commission=0.0003,       # 手续费0.03%
        slippage=0.001          # 滑点0.1%
    )
    
    # 设置回测参数
    stock_code = '600771'  # 股票代码
    end_date = datetime(2024, 12, 31)  # 使用2024年的数据
    start_date = end_date - timedelta(days=180)  # 回测6个月
    
    print(f"回测时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    print(f"股票代码: {stock_code}")
    print(f"初始资金: {engine.initial_capital:,} 元")
    
    # 定义策略配置
    strategies_config = {
        'Test': {
        },
        'DualMA': {
            'ma_fast': 5,
            'ma_slow': 20,
            'printlog': False
        },
        'RSI': {
            'rsi_period': 14,
            'rsi_upper': 70,
            'rsi_lower': 30,
            'printlog': False
        },
        'MACD': {
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'printlog': False
        },
        'BOLL': {
            'bb_period': 20,
            'bb_dev': 2,
            'printlog': False
        },
        'KDJ': {
            'kdj_period': 9,
            'kdj_upper': 80,
            'kdj_lower': 20,
            'printlog': False
        },
        'MeanReversion': {
            'lookback': 20,
            'threshold': 2,
            'printlog': False
        }
    }
    
    # 创建保存目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results', f'backtrader_{timestamp}')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    print(f"\n结果将保存到: {save_dir}")
    
    # 运行多策略回测
    try:
        results = engine.run_multiple_strategies(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            strategies_config=strategies_config,
            data_source='akshare',  # 优先使用 akshare
            freq='1d',
            save_dir=save_dir
        )
        
        if results:
            print(f"\n✅ 回测完成！共运行 {len(results)} 个策略")
            
            # 找出最佳策略
            best_strategy = max(results.values(), key=lambda x: x['total_return'])
            print(f"\n🏆 最佳策略: {best_strategy['strategy_name']}")
            print(f"   总收益率: {best_strategy['total_return']:.2f}%")
            print(f"   夏普比率: {best_strategy['sharpe_ratio']:.4f}")
            print(f"   最大回撤: {best_strategy['max_drawdown']:.2f}%")
            
        else:
            print("❌ 所有策略运行失败")
            
    except Exception as e:
        print(f"❌ 回测运行失败: {e}")
        import traceback
        traceback.print_exc()

def run_single_strategy():
    """运行单个策略示例"""
    print("=== 单策略回测示例 ===")
    
    # 设置中文字体
    setup_chinese_font()
    
    # 初始化回测引擎
    engine = BacktestEngine(initial_capital=100000)
    
    # 运行单个策略
    result = engine.run_backtest(
        stock_code='600771',
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        strategy_name='Test',
        strategy_params={},
        data_source='tushare',
        plot=True,
        token='bcfab7bccd8e066c2290c423bdb2d399b34690884be7b1ae05db1011'
    )
    
    if result:
        print("单策略回测完成！")

if __name__ == "__main__":
    # 可以选择运行多策略或单策略
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'single':
        run_single_strategy()
    else:
        main()