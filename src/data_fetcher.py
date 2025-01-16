import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self, token):
        ts.set_token(token)
        self.pro = ts.pro_api()
    
    def get_data(self, code, start_date, end_date):
        """获取股票数据"""
        # 将代码转换为tushare格式（例如：000001.SZ）
        if code.startswith('6'):
            ts_code = f"{code}.SH"
        else:
            ts_code = f"{code}.SZ"
            
        df = self.pro.daily(
            ts_code=ts_code,
            start_date=start_date.strftime('%Y%m%d'),
            end_date=end_date.strftime('%Y%m%d')
        )
        
        # 按日期正序排列
        df = df.sort_values('trade_date')
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.set_index('trade_date', inplace=True)
        
        return df 