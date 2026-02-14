"""调试回测信号生成"""
import asyncio
import pandas as pd
from datetime import datetime
from services.backtest_service import BacktestEngine
from services.data_fetcher import DataFetcher

async def debug_backtest():
    """调试回测过程"""
    print("=" * 60)
    print("调试回测信号生成")
    print("=" * 60)
    
    # 1. 获取数据
    print("\n1. 获取历史数据...")
    data_fetcher = DataFetcher(source='auto')
    df = await data_fetcher.get_data(
        code="600771",
        start_date=datetime(2025, 8, 14),
        end_date=datetime(2026, 2, 14),
        freq='daily'
    )
    
    print(f"获取到 {len(df)} 条数据")
    print("\n前5行数据:")
    print(df.head())
    
    # 2. 计算技术指标
    print("\n2. 计算技术指标...")
    engine = BacktestEngine(initial_capital=100000)
    params = {
        'type': 'MA',
        'short_window': 5,
        'long_window': 20
    }
    
    df_with_indicators = engine._calculate_indicators(df, params)
    
    print(f"\n添加了MA指标后的数据 (前25行):")
    cols_to_show = ['open', 'close', 'MA_short', 'MA_long', 'signal']
    print(df_with_indicators[cols_to_show].head(25))
    
    # 3. 检查信号
    print("\n3. 信号统计:")
    signal_counts = df_with_indicators['signal'].value_counts()
    print(f"信号值分布:\n{signal_counts}")
    
    # 4. 显示有信号的数据点
    print("\n4. 有信号的数据点:")
    signal_points = df_with_indicators[df_with_indicators['signal'] != 0]
    if len(signal_points) > 0:
        print(f"共 {len(signal_points)} 个信号")
        print(signal_points[['close', 'MA_short', 'MA_long', 'signal']].head(10))
    else:
        print("警告: 没有生成任何交易信号!")
        
    # 5. 检查MA交叉情况
    print("\n5. MA交叉情况检查:")
    df_with_indicators['ma_cross'] = 0
    df_with_indicators['ma_cross'][df_with_indicators['MA_short'] > df_with_indicators['MA_long']] = 1
    df_with_indicators['ma_cross'][df_with_indicators['MA_short'] < df_with_indicators['MA_long']] = -1
    
    cross_changes = df_with_indicators['ma_cross'].diff()
    print(f"MA交叉变化统计:")
    print(cross_changes.value_counts())
    
    # 6. 运行完整回测
    print("\n6. 运行完整回测...")
    try:
        result = await engine.run_backtest(
            stock_code="600771",
            start_date=datetime(2025, 8, 14),
            end_date=datetime(2026, 2, 14),
            freq='daily',
            strategy_params=params,
            data_source='auto'
        )
        
        print(f"\n回测结果:")
        print(f"交易次数: {result['metrics']['trade_count']}")
        print(f"总收益率: {result['metrics']['total_return']:.2%}")
        
        if result['trades']:
            print(f"\n交易明细 (共{len(result['trades'])}笔):")
            for trade in result['trades'][:5]:
                print(f"  {trade['date']} - {trade['type']} @ {trade['price']:.2f}")
        else:
            print("警告: 没有任何交易!")
            
    except Exception as e:
        print(f"回测出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_backtest())