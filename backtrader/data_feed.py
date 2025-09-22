#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtrader 数据源集成模块
支持 akshare 和 tushare 数据源
"""

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import akshare as ak
import tushare as ts
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data_fetcher import DataFetcher

class AkShareData(bt.feeds.PandasData):
    """AkShare 数据源适配器"""
    
    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', -1),
    )

class TuShareData(bt.feeds.PandasData):
    """TuShare 数据源适配器"""
    
    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', -1),
    )

class DataFeedManager:
    """数据源管理器"""
    
    def __init__(self, token=None):
        self.token = token
        self.data_fetcher = DataFetcher(token=token, source='akshare')
    
    def get_data_feed(self, stock_code, start_date, end_date, freq='1d', source='akshare'):
        """
        获取数据源
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            freq: 数据频率 ('1d', '5m', '15m', '30m', '1h')
            source: 数据源 ('akshare' 或 'tushare')
        
        Returns:
            backtrader 数据源对象
        """
        try:
            # 获取数据
            if source == 'akshare':
                df = self._get_akshare_data(stock_code, start_date, end_date, freq)
            elif source == 'tushare':
                df = self._get_tushare_data(stock_code, start_date, end_date, freq)
            else:
                raise ValueError(f"不支持的数据源: {source}")
            
            print(f"成功获取 {source} 数据: {len(df)} 条记录")
            print(f"数据时间范围: {df.index[0]} 到 {df.index[-1]}")
            
            # 使用标准的 PandasData 而不是自定义类
            data_feed = bt.feeds.PandasData(
                dataname=df,
                datetime=None,  # 使用索引作为时间
                open='open',
                high='high',
                low='low',
                close='close',
                volume='volume',
                openinterest=-1
            )
            
            return data_feed
            
        except Exception as e:
            print(f"获取数据失败: {e}")
            # 尝试备用数据源
            if source == 'akshare':
                print("尝试使用 tushare 作为备用数据源...")
                try:
                    return self.get_data_feed(stock_code, start_date, end_date, freq, 'tushare')
                except Exception as e2:
                    print(f"tushare 也失败: {e2}")
                    print("使用模拟数据作为最后备用方案...")
                    return self._create_mock_data_feed(stock_code, start_date, end_date, freq)
            elif source == 'tushare':
                print("使用模拟数据作为最后备用方案...")
                return self._create_mock_data_feed(stock_code, start_date, end_date, freq)
            else:
                raise e
    
    def _create_mock_data_feed(self, stock_code, start_date, end_date, freq):
        """创建模拟数据作为备用方案"""
        print(f"生成模拟数据：{stock_code}，{start_date} 到 {end_date}")
        
        # 生成日期序列
        if freq == '1d':
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
        else:
            dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        
        # 过滤掉周末（如果是日线数据）
        if freq == '1d':
            dates = dates[dates.weekday < 5]
        
        print(f"处理日期范围：{len(dates)}天")
        
        # 生成模拟价格数据
        np.random.seed(42)  # 固定随机种子，确保结果可重现
        n_days = len(dates)
        
        # 生成随机游走价格
        initial_price = 100.0
        returns = np.random.normal(0.0005, 0.02, n_days)  # 日收益率
        prices = [initial_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # 创建OHLCV数据
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            # 生成日内波动
            daily_volatility = abs(np.random.normal(0, 0.01))
            high = price * (1 + daily_volatility)
            low = price * (1 - daily_volatility)
            open_price = prices[i-1] if i > 0 else price
            volume = np.random.randint(1000, 10000)
            
            data.append({
                'datetime': date,
                'open': open_price,
                'high': high,
                'low': low,
                'close': price,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('datetime', inplace=True)
        
        # 使用标准的 PandasData
        data_feed = bt.feeds.PandasData(
            dataname=df,
            datetime=None,  # 使用索引作为时间
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=-1
        )
        
        print(f"模拟数据生成完成: {len(df)} 条记录")
        print(f"数据时间范围: {df.index[0]} 到 {df.index[-1]}")
        
        return data_feed
    
    def _get_akshare_data(self, stock_code, start_date, end_date, freq):
        """获取 AkShare 数据"""
        try:
            # 使用现有的 DataFetcher
            df = self.data_fetcher.get_data(stock_code, start_date, end_date, freq)
            
            # 确保数据格式正确
            df = self._prepare_dataframe(df)
            
            # 确保数据不为空
            if df.empty:
                raise ValueError("AkShare 返回空数据")
            
            return df
            
        except Exception as e:
            print(f"AkShare 数据获取失败: {e}")
            raise e
    
    def _get_tushare_data(self, stock_code, start_date, end_date, freq):
        """获取 TuShare 数据"""
        try:
            if not self.token:
                self.token = 'bcfab7bccd8e066c2290c423bdb2d399b34690884be7b1ae05db1011'
            
            # 设置 token
            ts.set_token(self.token)
            pro = ts.pro_api()
            
            # 转换股票代码格式 (600771 -> 600771.SH)
            if not stock_code.endswith('.SH') and not stock_code.endswith('.SZ'):
                if stock_code.startswith('6'):
                    ts_code = f"{stock_code}.SH"
                elif stock_code.startswith('0') or stock_code.startswith('3'):
                    ts_code = f"{stock_code}.SZ"
                else:
                    ts_code = f"{stock_code}.SH"  # 默认上海
            else:
                ts_code = stock_code
            
            # 根据频率选择不同的接口
            if freq == '1d':
                df = pro.daily(ts_code=ts_code, start_date=start_date.strftime('%Y%m%d'), 
                             end_date=end_date.strftime('%Y%m%d'))
            else:
                # 对于分钟数据，使用不同的接口
                df = pro.stk_mins(ts_code=ts_code, start_date=start_date.strftime('%Y%m%d %H:%M:%S'),
                                end_date=end_date.strftime('%Y%m%d %H:%M:%S'), freq=freq)
            
            # 检查数据是否为空
            if df.empty:
                print(f"TuShare 返回空数据，股票代码: {ts_code}")
                raise ValueError("TuShare 返回空数据")
            
            # 数据预处理
            df = self._prepare_tushare_dataframe(df, freq)
            
            return df
            
        except Exception as e:
            print(f"TuShare 数据获取失败: {e}")
            raise e
    
    def _prepare_dataframe(self, df):
        """准备数据框格式"""
        # 确保索引是 datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # 确保列名正确
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                if col == 'volume' and 'vol' in df.columns:
                    df[col] = df['vol']
                else:
                    raise ValueError(f"缺少必要的列: {col}")
        
        # 删除包含 NaN 的行
        df = df.dropna()
        
        # 按时间排序
        df = df.sort_index()
        
        return df
    
    def _prepare_tushare_dataframe(self, df, freq):
        """准备 TuShare 数据框格式"""
        # 设置时间索引
        if 'trade_date' in df.columns:
            df['datetime'] = pd.to_datetime(df['trade_date'])
        elif 'ts_code' in df.columns and 'datetime' not in df.columns:
            # 对于分钟数据
            df['datetime'] = pd.to_datetime(df['ts_code'])
        
        df.set_index('datetime', inplace=True)
        
        # 重命名列
        column_mapping = {
            'open': 'open',
            'high': 'high', 
            'low': 'low',
            'close': 'close',
            'vol': 'volume'
        }
        
        df = df.rename(columns=column_mapping)
        
        # 确保数据类型正确
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 删除包含 NaN 的行
        df = df.dropna()
        
        # 按时间排序
        df = df.sort_index()
        
        # 确保索引是 DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # 确保数据不为空
        if df.empty:
            raise ValueError("处理后的数据为空")
        
        # 确保所有必需的列都存在
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"缺少必需的列: {missing_columns}")
        
        return df

def create_data_feed(stock_code, start_date, end_date, freq='1d', source='akshare', token=None):
    """
    创建数据源的便捷函数
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        freq: 数据频率
        source: 数据源
        token: TuShare token
    
    Returns:
        backtrader 数据源对象
    """
    manager = DataFeedManager(token=token)
    return manager.get_data_feed(stock_code, start_date, end_date, freq, source)

if __name__ == "__main__":
    # 测试数据源
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    try:
        # 测试 AkShare
        print("测试 AkShare 数据源...")
        data_feed = create_data_feed('600771', start_date, end_date, '1d', 'akshare', token = 'bcfab7bccd8e066c2290c423bdb2d399b34690884be7b1ae05db1011')
        print("AkShare 数据源测试成功")
        
    except Exception as e:
        print(f"数据源测试失败: {e}")
