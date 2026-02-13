#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据获取测试脚本
用于验证数据获取器的功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_fetcher import DataFetcher
from datetime import datetime, timedelta
import pandas as pd

def test_data_fetcher():
    """测试数据获取器"""
    
    # 测试参数
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    print('=== 数据获取测试 ===')
    print(f'请求时间范围: {start_date.strftime("%Y-%m-%d")} 到 {end_date.strftime("%Y-%m-%d")}')
    print(f'请求天数: {(end_date - start_date).days}天')
    
    # 计算预期数据量
    work_days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # 周一到周五
            work_days += 1
        current += timedelta(days=1)
    
    print(f'预期工作日: {work_days}天')
    print(f'30分钟频率预期数据量: {work_days * 8}条 (每天8个30分钟区间)')
    
    # 测试数据获取
    try:
        fetcher = DataFetcher(source='akshare')
        df = fetcher.get_data('600771', start_date, end_date, freq='30min')
        
        print(f'\n=== 实际获取结果 ===')
        print(f'实际数据条数: {len(df)}')
        if len(df) > 0:
            print(f'时间范围: {df.index[0]} 到 {df.index[-1]}')
            print(f'数据列: {list(df.columns)}')
            
            # 检查第一天的数据时间点
            first_day = df.index[0].date()
            first_day_data = df[df.index.date == first_day]
            print(f'\n第一天({first_day})的时间点:')
            for time_point in first_day_data.index:
                print(f'  {time_point.strftime("%H:%M:%S")}')
            
            # 检查数据质量
            print(f'\n=== 数据质量检查 ===')
            print(f'价格范围: {df["close"].min():.2f} - {df["close"].max():.2f}')
            print(f'成交量范围: {df["volume"].min()} - {df["volume"].max()}')
            print(f'缺失值: {df.isnull().sum().sum()}')
            
            # 检查每日数据点数
            daily_counts = df.groupby(df.index.date).size()
            print(f'\n每日数据点数统计:')
            print(f'平均每日: {daily_counts.mean():.1f}条')
            print(f'最少: {daily_counts.min()}条')
            print(f'最多: {daily_counts.max()}条')
            
        else:
            print('未获取到数据！')
            
    except Exception as e:
        print(f'测试失败: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_data_fetcher() 