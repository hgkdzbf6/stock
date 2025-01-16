from data_fetcher import DataFetcher
from strategy import MAStrategy
from backtest import Backtest
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

 
plt.rcParams['font.family'] = 'Arial Unicode MS'

def main():
    # 初始化参数
    token = 'bcfab7bccd8e066c2290c423bdb2d399b34690884be7b1ae05db1011'  # 替换为您的tushare token
    stock_code = '600771'  # 以平安银行为例
    initial_capital = 100000  # 初始资金10万
    
    # 获取数据
    fetcher = DataFetcher(token)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 获取一年的数据
    df = fetcher.get_data(stock_code, start_date, end_date)
    
    # 运行策略
    strategy = MAStrategy(short_window=5, long_window=20)
    df = strategy.calculate_signals(df)
    
    # 回测
    backtest = Backtest(initial_capital=initial_capital)
    results = backtest.run(df)
    metrics = backtest.get_metrics()
    
    # 打印回测结果
    print("\n=== 回测结果 ===")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # 绘制资金曲线和持仓情况
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # 绘制资金曲线
    ax1.plot(results.index, results['total_value'], label='策略收益')
    ax1.axhline(y=initial_capital, color='r', linestyle='--', label='初始资金')
    ax1.set_title('策略收益曲线')
    ax1.set_ylabel('账户价值')
    ax1.legend()
    ax1.grid(True)
    
    # 绘制持仓情况
    ax2.fill_between(results.index, 
                     results['shares'] * results['close'] / results['total_value'], 
                     color='skyblue', alpha=0.5, label='持仓仓位')
    ax2.set_title('持仓仓位')
    ax2.set_xlabel('日期')
    ax2.set_ylabel('持仓比例')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main() 