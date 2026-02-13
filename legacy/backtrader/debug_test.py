#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试测试脚本
用于单步调试 Backtrader 量化交易框架
"""

import sys
import os
from datetime import datetime, timedelta

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_feed import DataFeedManager
from strategies import TestStrategy, DualMovingAverageStrategy
import backtrader as bt

def debug_data_feed():
    """调试数据源"""
    print("=== 调试数据源 ===")
    
    # 创建数据源管理器
    manager = DataFeedManager(token='bcfab7bccd8e066c2290c423bdb2d399b34690884be7b1ae05db1011')
    
    # 测试参数
    stock_code = '600771'
    end_date = datetime(2024, 12, 31)
    start_date = end_date - timedelta(days=7)  # 只测试7天数据
    
    print(f"股票代码: {stock_code}")
    print(f"时间范围: {start_date} 到 {end_date}")
    
    # 获取数据源
    data_feed = manager.get_data_feed(stock_code, start_date, end_date, '1d', 'akshare')
    
    # 检查数据
    data = data_feed._dataname
    print(f"数据形状: {data.shape}")
    print(f"数据列: {data.columns.tolist()}")
    print("前3行数据:")
    print(data.head(3))
    
    return data_feed

def debug_strategy():
    """调试策略"""
    print("\n=== 调试策略 ===")
    
    # 创建测试数据
    data_feed = debug_data_feed()
    
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(TestStrategy)
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)
    
    print(f"初始资金: {cerebro.broker.getvalue():.2f}")
    
    # 运行回测
    print("开始回测...")
    results = cerebro.run()
    
    print(f"最终资金: {cerebro.broker.getvalue():.2f}")
    print("策略调试完成！")

def debug_dual_ma_strategy():
    """调试双均线策略"""
    print("\n=== 调试双均线策略 ===")
    
    # 创建测试数据
    data_feed = debug_data_feed()
    
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(DualMovingAverageStrategy, ma_fast=5, ma_slow=20, printlog=True)
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)
    
    print(f"初始资金: {cerebro.broker.getvalue():.2f}")
    
    # 运行回测
    print("开始回测...")
    results = cerebro.run()
    
    print(f"最终资金: {cerebro.broker.getvalue():.2f}")
    print("双均线策略调试完成！")

def debug_step_by_step():
    """逐步调试"""
    print("\n=== 逐步调试 ===")
    
    # 步骤1：创建数据源
    print("步骤1：创建数据源")
    manager = DataFeedManager(token='bcfab7bccd8e066c2290c423bdb2d399b34690884be7b1ae05db1011')
    stock_code = '600771'
    end_date = datetime(2024, 12, 31)
    start_date = end_date - timedelta(days=3)  # 只测试3天数据
    
    data_feed = manager.get_data_feed(stock_code, start_date, end_date, '1d', 'akshare')
    print("✓ 数据源创建成功")
    
    # 步骤2：创建策略
    print("步骤2：创建策略")
    strategy_class = TestStrategy
    print("✓ 策略类获取成功")
    
    # 步骤3：创建 Cerebro 引擎
    print("步骤3：创建 Cerebro 引擎")
    cerebro = bt.Cerebro()
    print("✓ Cerebro 引擎创建成功")
    
    # 步骤4：添加数据
    print("步骤4：添加数据到 Cerebro")
    cerebro.adddata(data_feed)
    print("✓ 数据添加成功")
    
    # 步骤5：添加策略
    print("步骤5：添加策略到 Cerebro")
    cerebro.addstrategy(strategy_class)
    print("✓ 策略添加成功")
    
    # 步骤6：设置经纪人
    print("步骤6：设置经纪人参数")
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)
    print(f"✓ 初始资金: {cerebro.broker.getvalue():.2f}")
    
    # 步骤7：运行回测
    print("步骤7：运行回测")
    results = cerebro.run()
    print(f"✓ 最终资金: {cerebro.broker.getvalue():.2f}")
    
    print("✓ 逐步调试完成！")

def main():
    """主函数"""
    print("=== Backtrader 调试测试 ===")
    print("选择调试模式：")
    print("1. 调试数据源")
    print("2. 调试测试策略")
    print("3. 调试双均线策略")
    print("4. 逐步调试")
    print("5. 全部调试")
    
    choice = input("请选择 (1-5): ").strip()
    
    if choice == '1':
        debug_data_feed()
    elif choice == '2':
        debug_strategy()
    elif choice == '3':
        debug_dual_ma_strategy()
    elif choice == '4':
        debug_step_by_step()
    elif choice == '5':
        debug_data_feed()
        debug_strategy()
        debug_dual_ma_strategy()
        debug_step_by_step()
    else:
        print("无效选择，运行逐步调试...")
        debug_step_by_step()

if __name__ == "__main__":
    main()
