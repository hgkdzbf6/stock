"""测试成交量数据获取流程"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.data_fetcher import DataFetcher
from services.backtest_service import BacktestEngine
from loguru import logger


async def test_data_fetcher():
    """测试数据获取器是否返回volume数据"""
    logger.info("=" * 80)
    logger.info("步骤1: 测试数据获取器")
    logger.info("=" * 80)
    
    # 创建数据获取器
    data_fetcher = DataFetcher(source='auto')
    
    # 获取数据
    stock_code = '600771'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 最近90天
    
    logger.info(f"获取股票数据: {stock_code}, {start_date} 到 {end_date}")
    df = await data_fetcher.get_data(
        code=stock_code,
        start_date=start_date,
        end_date=end_date,
        freq='1d'
    )
    
    logger.info(f"获取到 {len(df)} 条数据")
    logger.info(f"DataFrame列: {df.columns.tolist()}")
    logger.info(f"是否有volume列: {'volume' in df.columns}")
    
    if 'volume' in df.columns:
        logger.info(f"volume数据类型: {df['volume'].dtype}")
        logger.info(f"volume非空数量: {df['volume'].notna().sum()}")
        logger.info(f"volume前5行:\n{df['volume'].head()}")
        logger.info(f"volume统计信息:\n{df['volume'].describe()}")
        
        # 检查是否所有volume都是0或NaN
        non_zero_volume = df[df['volume'] > 0]
        logger.info(f"非零volume数量: {len(non_zero_volume)}")
        if len(non_zero_volume) > 0:
            logger.info(f"非零volume示例:\n{non_zero_volume[['volume', 'open', 'high', 'low', 'close']].head()}")
        else:
            logger.warning("⚠️ 所有volume值都是0或NaN！")
    else:
        logger.error("❌ DataFrame中没有volume列！")
    
    return df


async def test_backtest_engine():
    """测试回测引擎是否保留volume数据"""
    logger.info("\n" + "=" * 80)
    logger.info("步骤2: 测试回测引擎")
    logger.info("=" * 80)
    
    # 创建回测引擎
    engine = BacktestEngine(
        initial_capital=100000.0,
        commission=0.0003,
        slippage=0.001
    )
    
    stock_code = '600771'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    logger.info(f"运行回测: {stock_code}, {start_date} 到 {end_date}")
    
    # 运行回测
    result = await engine.run_backtest(
        stock_code=stock_code,
        start_date=start_date,
        end_date=end_date,
        freq='1d',
        strategy_params={'type': 'MA', 'short_window': 5, 'long_window': 20},
        data_source='auto'
    )
    
    # 检查结果
    logger.info(f"回测完成")
    logger.info(f"结果keys: {result.keys()}")
    logger.info(f"equity_curve长度: {len(result['equity_curve'])}")
    
    # 检查equity_curve中的volume数据
    equity_curve = result['equity_curve']
    if equity_curve:
        first_point = equity_curve[0]
        logger.info(f"第一个数据点keys: {first_point.keys()}")
        logger.info(f"第一个数据点是否有volume: {'volume' in first_point}")
        if 'volume' in first_point:
            logger.info(f"第一个数据点volume值: {first_point['volume']}")
            
            # 统计有volume的数据点
            points_with_volume = [p for p in equity_curve if 'volume' in p and p['volume'] > 0]
            logger.info(f"有volume的数据点数量: {len(points_with_volume)}/{len(equity_curve)}")
            
            if points_with_volume:
                logger.info(f"前5个有volume的数据点:")
                for i, p in enumerate(points_with_volume[:5]):
                    logger.info(f"  [{i}] date={p['date']}, volume={p.get('volume')}, close={p.get('close')}")
            else:
                logger.warning("⚠️ equity_curve中所有数据点都没有volume或volume为0！")
        else:
            logger.error("❌ equity_curve数据点中没有volume字段！")
    
    return result


async def test_api_response():
    """测试API响应格式"""
    logger.info("\n" + "=" * 80)
    logger.info("步骤3: 测试API响应格式")
    logger.info("=" * 80)
    
    # 模拟API返回的数据结构
    stock_code = '600771'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    engine = BacktestEngine(initial_capital=100000.0)
    result = await engine.run_backtest(
        stock_code=stock_code,
        start_date=start_date,
        end_date=end_date,
        freq='1d',
        strategy_params={'type': 'MA', 'short_window': 5, 'long_window': 20},
        data_source='auto'
    )
    
    # 构造API响应
    api_response = {
        "code": 200,
        "message": "回测完成",
        "data": result
    }
    
    logger.info(f"API响应结构:")
    logger.info(f"  code: {api_response['code']}")
    logger.info(f"  message: {api_response['message']}")
    logger.info(f"  data keys: {api_response['data'].keys()}")
    
    # 检查equity_curve
    equity_curve = api_response['data']['equity_curve']
    logger.info(f"  equity_curve length: {len(equity_curve)}")
    logger.info(f"  equity_curve first point: {equity_curve[0]}")
    
    # 检查volume
    has_volume = any('volume' in p and p['volume'] > 0 for p in equity_curve)
    logger.info(f"  has_volume: {has_volume}")
    
    return api_response


async def main():
    """主测试函数"""
    try:
        # 测试数据获取
        df = await test_data_fetcher()
        
        # 测试回测引擎
        result = await test_backtest_engine()
        
        # 测试API响应
        api_response = await test_api_response()
        
        logger.info("\n" + "=" * 80)
        logger.info("测试完成！")
        logger.info("=" * 80)
        
        # 总结
        logger.info("\n总结:")
        logger.info("1. 数据获取器: " + ("✓ 包含volume数据" if 'volume' in df.columns and df['volume'].notna().any() else "✗ 不包含volume数据"))
        logger.info("2. 回测引擎: " + ("✓ 保留volume数据" if any('volume' in p and p['volume'] > 0 for p in result['equity_curve']) else "✗ 未保留volume数据"))
        logger.info("3. API响应: " + ("✓ 正确传递volume数据" if any('volume' in p and p['volume'] > 0 for p in api_response['data']['equity_curve']) else "✗ 未传递volume数据"))
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())