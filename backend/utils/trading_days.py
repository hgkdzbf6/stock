"""交易日工具"""
from datetime import datetime, timedelta
from loguru import logger
import pandas as pd


def get_latest_trading_day(days_back: int = 7) -> datetime:
    """
    获取最近的交易日（使用pandas工作日逻辑）
    
    Args:
        days_back: 最多往前查找的天数
        
    Returns:
        最近交易日的datetime对象，如果找不到返回今天的日期
    """
    try:
        current_date = datetime.now()
        
        # 从今天往前查找最近的工作日（排除周末）
        for days_back in range(0, days_back):
            date = current_date - timedelta(days=days_back)
            
            # 周六=5, 周日=6
            if date.weekday() < 5:  # 0-4是周一到周五
                logger.info(f"找到最近交易日: {date.strftime('%Y-%m-%d')}")
                return date
        
        logger.warning(f"过去{days_back}天没找到交易日，返回今天")
        return current_date
        
    except Exception as e:
        logger.error(f"获取最近交易日失败: {e}")
        return datetime.now()


def get_trading_days_between(start_date: datetime, end_date: datetime) -> list:
    """
    获取两个日期之间的所有交易日（使用pandas工作日逻辑）
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        交易日列表（datetime对象列表）
    """
    try:
        # 使用pandas生成工作日
        trading_days = []
        current = start_date
        
        while current <= end_date:
            # 排除周末
            if current.weekday() < 5:  # 0-4是周一到周五
                trading_days.append(current)
            current += timedelta(days=1)
        
        logger.info(f"获取到 {len(trading_days)} 个交易日")
        return trading_days
        
    except Exception as e:
        logger.error(f"获取交易日列表失败: {e}")
        return []


def is_trading_day(date: datetime) -> bool:
    """
    判断指定日期是否是交易日（使用pandas工作日逻辑）
    
    Args:
        date: 要检查的日期
        
    Returns:
        True是交易日，False不是
    """
    try:
        # 周六=5, 周日=6
        is_weekday = date.weekday() < 5  # 0-4是周一到周五
        return is_weekday
        
    except Exception as e:
        logger.error(f"判断交易日失败: {e}")
        return False


if __name__ == '__main__':
    # 测试
    print("测试获取最近交易日:")
    latest = get_latest_trading_day()
    print(f"最近交易日: {latest.strftime('%Y-%m-%d')}")
    
    print("\n测试获取交易日列表:")
    trading_days = get_trading_days_between(
        datetime(2024, 2, 1),
        datetime(2024, 2, 10)
    )
    print(f"交易日: {[d.strftime('%Y-%m-%d') for d in trading_days]}")
    
    print("\n测试判断交易日:")
    test_date = datetime(2024, 2, 5)  # 周一
    print(f"{test_date.strftime('%Y-%m-%d')} 是交易日: {is_trading_day(test_date)}")