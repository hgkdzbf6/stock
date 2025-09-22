#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtrader 回测引擎
提供完整的回测功能和结果分析
"""

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_feed import create_data_feed
from strategies import get_strategy

class BacktestEngine:
    """Backtrader 回测引擎"""
    
    def __init__(self, initial_capital=100000, commission=0.0003, slippage=0.001):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            commission: 手续费率
            slippage: 滑点
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.results = {}
        
    def run_backtest(self, stock_code, start_date, end_date, strategy_name, 
                    strategy_params=None, data_source='akshare', freq='1d', 
                    token=None, plot=False, save_dir=None):
        """
        运行回测
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            strategy_name: 策略名称
            strategy_params: 策略参数
            data_source: 数据源
            freq: 数据频率
            token: TuShare token
            plot: 是否绘图
            save_dir: 保存目录
        
        Returns:
            回测结果字典
        """
        print(f"\n=== 运行 {strategy_name} 策略回测 ===")
        print(f"股票代码: {stock_code}")
        print(f"回测时间: {start_date} 到 {end_date}")
        print(f"初始资金: {self.initial_capital:,} 元")
        
        # 创建 Cerebro 引擎
        cerebro = bt.Cerebro()
        
        # 设置初始资金
        cerebro.broker.setcash(self.initial_capital)
        
        # 设置手续费和滑点
        cerebro.broker.setcommission(commission=self.commission)
        cerebro.broker.set_slippage_perc(self.slippage)
        
        # 添加数据源
        try:
            data_feed = create_data_feed(stock_code, start_date, end_date, 
                                       freq, data_source, token)
            cerebro.adddata(data_feed)
        except Exception as e:
            print(f"数据获取失败: {e}")
            return None
        
        # 添加策略
        strategy_params = strategy_params or {}
        strategy_class = get_strategy(strategy_name)
        cerebro.addstrategy(strategy_class, **strategy_params)
        
        # 添加分析器
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
        
        # 运行回测
        print("开始回测...")
        results = cerebro.run()
        
        # 获取结果
        strat = results[0]
        
        # 计算性能指标
        final_value = cerebro.broker.getvalue()
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        
        # 获取分析器结果
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        returns = strat.analyzers.returns.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        sqn = strat.analyzers.sqn.get_analysis()
        
        # 计算年化收益率
        days = (end_date - start_date).days
        annual_return = (final_value / self.initial_capital) ** (365 / days) - 1
        
        # 构建结果字典
        sharpe_ratio = sharpe.get('sharperatio', 0)
        if sharpe_ratio is None:
            sharpe_ratio = 0
            
        sqn_value = sqn.get('sqn', 0)
        if sqn_value is None:
            sqn_value = 0
            
        result = {
            'strategy_name': strategy_name,
            'stock_code': stock_code,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return * 100,
            'max_drawdown': drawdown.get('max', {}).get('drawdown', 0),
            'sharpe_ratio': sharpe_ratio,
            'sqn': sqn_value,
            'total_trades': trades.get('total', {}).get('total', 0),
            'winning_trades': trades.get('won', {}).get('total', 0),
            'losing_trades': trades.get('lost', {}).get('total', 0),
            'win_rate': (trades.get('won', {}).get('total', 0) / 
                        max(trades.get('total', {}).get('total', 1), 1)) * 100,
            'cerebro': cerebro,
            'strategy': strat
        }
        
        # 打印结果
        self._print_results(result)
        
        # 保存结果
        if save_dir:
            self._save_results(result, save_dir)
        
        # 绘图
        if plot:
            self._plot_results(cerebro, result, save_dir)
        
        return result
    
    def _print_results(self, result):
        """打印回测结果"""
        print("\n" + "="*50)
        print("回测结果")
        print("="*50)
        print(f"策略名称: {result['strategy_name']}")
        print(f"股票代码: {result['stock_code']}")
        print(f"初始资金: {result['initial_capital']:,.2f} 元")
        print(f"期末资金: {result['final_value']:,.2f} 元")
        print(f"总收益率: {result['total_return']:.2f}%")
        print(f"年化收益率: {result['annual_return']:.2f}%")
        print(f"最大回撤: {result['max_drawdown']:.2f}%")
        print(f"夏普比率: {result['sharpe_ratio']:.4f}")
        print(f"SQN: {result['sqn']:.4f}")
        print(f"总交易次数: {result['total_trades']}")
        print(f"盈利交易: {result['winning_trades']}")
        print(f"亏损交易: {result['losing_trades']}")
        print(f"胜率: {result['win_rate']:.2f}%")
    
    def _save_results(self, result, save_dir):
        """保存回测结果"""
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # 保存结果到CSV
        result_df = pd.DataFrame([{
            '策略名称': result['strategy_name'],
            '股票代码': result['stock_code'],
            '初始资金': result['initial_capital'],
            '期末资金': result['final_value'],
            '总收益率(%)': result['total_return'],
            '年化收益率(%)': result['annual_return'],
            '最大回撤(%)': result['max_drawdown'],
            '夏普比率': result['sharpe_ratio'],
            'SQN': result['sqn'],
            '总交易次数': result['total_trades'],
            '盈利交易': result['winning_trades'],
            '亏损交易': result['losing_trades'],
            '胜率(%)': result['win_rate']
        }])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{result['strategy_name']}_{timestamp}.csv"
        filepath = os.path.join(save_dir, filename)
        result_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"结果已保存到: {filepath}")
    
    def _plot_results(self, cerebro, result, save_dir=None):
        """绘制回测结果图表"""
        try:
            # 设置中文字体
            plt.rcParams['font.family'] = ['Hiragino Sans GB', 'SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 创建图表
            fig, axes = plt.subplots(2, 1, figsize=(15, 10))
            
            # 绘制价格和指标
            cerebro.plot(style='candlestick', volume=False, iplot=False, 
                        show=False, figsize=(15, 10))
            
            if save_dir:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{result['strategy_name']}_chart_{timestamp}.png"
                filepath = os.path.join(save_dir, filename)
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                print(f"图表已保存到: {filepath}")
            
            plt.show()
            
        except Exception as e:
            print(f"绘图失败: {e}")
    
    def run_multiple_strategies(self, stock_code, start_date, end_date, 
                              strategies_config, data_source='akshare', 
                              freq='1d', token=None, save_dir=None):
        """
        运行多个策略对比回测
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            strategies_config: 策略配置字典
            data_source: 数据源
            freq: 数据频率
            token: TuShare token
            save_dir: 保存目录
        
        Returns:
            所有策略的回测结果
        """
        print(f"\n=== 运行多策略对比回测 ===")
        print(f"股票代码: {stock_code}")
        print(f"回测时间: {start_date} 到 {end_date}")
        print(f"策略数量: {len(strategies_config)}")
        
        all_results = {}
        
        for strategy_name, params in strategies_config.items():
            try:
                result = self.run_backtest(
                    stock_code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    strategy_name=strategy_name,
                    strategy_params=params,
                    data_source=data_source,
                    freq=freq,
                    token=token,
                    plot=False,
                    save_dir=save_dir
                )
                
                if result:
                    all_results[strategy_name] = result
                    
            except Exception as e:
                print(f"策略 {strategy_name} 运行失败: {e}")
                continue
        
        # 生成对比报告
        if all_results:
            self._generate_comparison_report(all_results, save_dir)
        
        return all_results
    
    def _generate_comparison_report(self, results, save_dir=None):
        """生成策略对比报告"""
        print("\n" + "="*80)
        print("策略对比报告")
        print("="*80)
        
        # 创建对比表格
        comparison_data = []
        for strategy_name, result in results.items():
            comparison_data.append({
                '策略名称': strategy_name,
                '总收益率(%)': f"{result['total_return']:.2f}",
                '年化收益率(%)': f"{result['annual_return']:.2f}",
                '最大回撤(%)': f"{result['max_drawdown']:.2f}",
                '夏普比率': f"{result['sharpe_ratio']:.4f}",
                '胜率(%)': f"{result['win_rate']:.2f}",
                '交易次数': result['total_trades']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        print(comparison_df.to_string(index=False))
        
        # 保存对比报告
        if save_dir:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"strategy_comparison_{timestamp}.csv"
            filepath = os.path.join(save_dir, filename)
            comparison_df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"\n对比报告已保存到: {filepath}")

def main():
    """主函数 - 示例用法"""
    # 初始化回测引擎
    engine = BacktestEngine(initial_capital=100000, commission=0.0003, slippage=0.001)
    
    # 设置参数
    stock_code = '600771'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # 策略配置
    strategies_config = {
        'DualMA': {'ma_fast': 5, 'ma_slow': 20},
        'RSI': {'rsi_period': 14, 'rsi_upper': 70, 'rsi_lower': 30},
        'MACD': {'macd_fast': 12, 'macd_slow': 26, 'macd_signal': 9},
        'BOLL': {'bb_period': 20, 'bb_dev': 2},
    }
    
    # 创建保存目录
    save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results', 'backtrader')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 运行多策略回测
    results = engine.run_multiple_strategies(
        stock_code=stock_code,
        start_date=start_date,
        end_date=end_date,
        strategies_config=strategies_config,
        data_source='akshare',
        save_dir=save_dir
    )
    
    print(f"\n回测完成！结果保存在: {save_dir}")

if __name__ == "__main__":
    main()
