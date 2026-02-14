"""交易日工具"""
from datetime import datetime, timedelta
from loguru import logger
import baostock as bs


def get_latest_trading_day(days_back: int = 7) -> datetime:
    """
    获取最近的交易日
    
    Args:
        days_back: 最多往前查找的天数
        
    Returns:
        最近交易日的datetime对象，如果找不到返回今天的日期
    """
    try:
        lg = bs.login()
        if lg.error_code != '0':
            logger.warning(f"BaoStock登录失败，返回今天: {lg.error_msg}")
            return datetime.now()
        
        current_date = datetime.now()
        
        # 从今天往前查找最近的交易日
        for days_back in range(0, days_back):
            date = current_date - timedelta(days=days_back)
            day_str = date.strftime('%Y-%m-%d')
            
            # 尝试获取交易日期
            rs = bs.query_trade_dates(
                start_date=day_str,
                end_date=day_str
            )
            
            if rs.error_code == '0':
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())
                
                # 如果找到数据且是交易日
                if data_list and len(data_list[0]) >= 2:
                    is_trading_day = data_list[0][1] == '1'
                    if is_trading_day:
                        logger.info(f"找到最近交易日: {day_str}")
                        bs.logout()
                        return date
        
        bs.logout()
        logger.warning(f"过去{days_back}天没找到交易日，返回今天")
        return datetime.now()
        
    except Exception as e:
        logger.error(f"获取最近交易日失败: {e}")
        return datetime.now()


def get_trading_days_between(start_date: datetime, end_date: datetime) -> list:
    """
    获取两个日期之间的所有交易日
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        交易日列表（datetime对象列表）
    """
    try:
        lg = bs.login()
        if lg.error_code != '0':
            logger.warning(f"BaoStock登录失败，返回空列表: {lg.error_msg}")
            return []
        
        trading_days = []
        
        rs = bs.query_trade_dates(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        if rs.error_code == '0':
            while (rs.error_code == '0') & rs.next():
                row = rs.get_row_data()
                if len(row) >= 2 and row[1] == '1':  # 1表示是交易日
                    trading_days.append(datetime.strptime(row[0], '%Y-%m-%d'))
        
        bs.logout()
        logger.info(f"获取到 {len(trading_days)} 个交易日")
        return trading_days
        
    except Exception as e:
        logger.error(f"获取交易日列表失败: {e}")
        return []


def is_trading_day(date: datetime) -> bool:
    """
    判断指定日期是否是交易日
    
    Args:
        date: 要检查的日期
        
    Returns:
        True是交易日，False不是
    """
    try:
        lg = bs.login()
        if lg.error_code != '0':
            return False
        
        day_str = date.strftime('%Y-%m-%d')
        
        rs = bs.query_trade_dates(
            start_date=day_str,
            end_date=day_str
        )
        
        if rs.error_code == '0':
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if data_list and len(data_list[0]) >= 2:
                is_trading_day = data_list[0][1] == '1'
                bs.logout()
                return is_trading_day
        
        bs.logout()
        return False
        
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