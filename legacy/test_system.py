#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
量化交易系统测试脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def test_data_fetcher():
    """测试数据获取模块"""
    print("=== 测试数据获取模块 ===")
    
    try:
        from data_fetcher import DataFetcher
        
        # 测试模拟数据生成
        fetcher = DataFetcher(source='akshare')
        end_date = datetime.now()
        start_date = end_date - timedelta(days=2)
        
        df = fetcher._generate_mock_minute_data('600771', start_date, end_date, '5min')
        
        print(f"✓ 模拟数据生成成功，数据量: {len(df)} 条")
        print(f"✓ 数据列: {list(df.columns)}")
        print(f"✓ 时间范围: {df.index[0]} 到 {df.index[-1]}")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据获取模块测试失败: {e}")
        return False

def test_strategies():
    """测试策略模块"""
    print("\n=== 测试策略模块 ===")
    
    try:
        from strategy import StrategyFactory
        
        # 生成测试数据
        dates = pd.date_range(start='2024-01-01 09:30:00', periods=100, freq='5T')
        np.random.seed(42)
        
        base_price = 10.0
        prices = []
        for i in range(100):
            base_price *= (1 + np.random.normal(0, 0.01))
            prices.append(base_price)
        
        test_df = pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
            'close': prices,
            'volume': np.random.randint(1000, 5000, 100)
        }, index=dates)
        
        # 测试所有策略
        strategies = StrategyFactory.get_available_strategies()
        print(f"✓ 可用策略: {strategies}")
        
        for strategy_name in strategies[:3]:  # 测试前3个策略
            try:
                strategy = StrategyFactory.create_strategy(strategy_name)
                result_df = strategy.calculate_signals(test_df)
                
                signal_count = len(result_df[result_df['signal'] != 0])
                print(f"✓ {strategy.name} 测试成功，生成 {signal_count} 个信号")
                
            except Exception as e:
                print(f"✗ {strategy_name} 策略测试失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ 策略模块测试失败: {e}")
        return False

def test_backtest():
    """测试回测模块"""
    print("\n=== 测试回测模块 ===")
    
    try:
        from backtest import Backtest
        from strategy import MAStrategy
        
        # 生成测试数据
        dates = pd.date_range(start='2024-01-01 09:30:00', periods=100, freq='5T')
        np.random.seed(42)
        
        base_price = 10.0
        prices = []
        for i in range(100):
            base_price *= (1 + np.random.normal(0, 0.01))
            prices.append(base_price)
        
        test_df = pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
            'close': prices,
            'volume': np.random.randint(1000, 5000, 100)
        }, index=dates)
        
        # 应用策略
        strategy = MAStrategy(short_window=5, long_window=10)
        test_df = strategy.calculate_signals(test_df)
        
        # 运行回测
        backtest = Backtest(initial_capital=100000)
        results = backtest.run(test_df)
        metrics = backtest.get_metrics()
        
        print(f"✓ 回测完成，最终资产: {results['total_value'].iloc[-1]:.2f}")
        print(f"✓ 交易次数: {metrics['交易次数']}")
        print(f"✓ 总收益率: {metrics['总收益率']}")
        
        return True
        
    except Exception as e:
        print(f"✗ 回测模块测试失败: {e}")
        return False

def test_full_system():
    """测试完整系统"""
    print("\n=== 测试完整系统 ===")
    
    try:
        # 模拟运行主程序的部分功能
        from data_fetcher import DataFetcher
        from strategy import StrategyFactory
        from backtest import Backtest
        
        # 获取模拟数据
        fetcher = DataFetcher(source='akshare')
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        df = fetcher._generate_mock_minute_data('600771', start_date, end_date, '5min')
        
        # 运行一个简单策略
        strategy = StrategyFactory.create_strategy('MA', short_window=5, long_window=10)
        df_with_signals = strategy.calculate_signals(df)
        
        # 回测
        backtest = Backtest(initial_capital=100000)
        results = backtest.run(df_with_signals)
        metrics = backtest.get_metrics()
        
        print(f"✓ 完整系统测试成功")
        print(f"✓ 数据量: {len(df)} 条")
        print(f"✓ 策略: {strategy.name}")
        print(f"✓ 最终收益率: {metrics['总收益率']}")
        
        return True
        
    except Exception as e:
        print(f"✗ 完整系统测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("量化交易系统测试开始")
    print("=" * 50)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("数据获取模块", test_data_fetcher()))
    test_results.append(("策略模块", test_strategies()))
    test_results.append(("回测模块", test_backtest()))
    test_results.append(("完整系统", test_full_system()))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(test_results)} 项测试通过")
    
    if passed == len(test_results):
        print("🎉 所有测试通过！系统可以正常运行。")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 