"""
基础策略类
定义所有策略的通用接口和基础功能
"""

import pandas as pd
import numpy as np

class BaseStrategy:
    """策略基类"""
    def __init__(self, name="BaseStrategy"):
        self.name = name
        self.position = 0  # 当前持仓：1为多头，-1为空头，0为空仓
        self.entry_price = 0  # 入场价格
        self.stop_loss = None  # 止损价格
        self.take_profit = None  # 止盈价格
    
    def calculate_signals(self, df):
        """
        计算交易信号，子类需要实现此方法
        返回包含signal列的DataFrame，signal值：
        1: 买入信号
        -1: 卖出信号  
        0: 无信号
        """
        raise NotImplementedError("子类必须实现calculate_signals方法")
    
    def set_risk_management(self, stop_loss_pct=0.05, take_profit_pct=0.10):
        """设置风险管理参数"""
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
    
    def calculate_position_size(self, price, capital, risk_pct=0.02):
        """计算仓位大小"""
        risk_amount = capital * risk_pct
        if self.stop_loss_pct:
            position_size = risk_amount / (price * self.stop_loss_pct)
            return min(position_size, capital / price)  # 不超过总资金
        return capital / price  # 全仓
    
    def apply_risk_management(self, df):
        """应用风险管理规则"""
        df = df.copy()
        
        # 添加止损止盈信号
        for i in range(len(df)):
            if self.position == 1:  # 持多头
                # 止损
                if df['low'].iloc[i] <= self.stop_loss:
                    df.loc[df.index[i], 'signal'] = -1
                # 止盈
                elif df['high'].iloc[i] >= self.take_profit:
                    df.loc[df.index[i], 'signal'] = -1
            elif self.position == -1:  # 持空头
                # 止损
                if df['high'].iloc[i] >= self.stop_loss:
                    df.loc[df.index[i], 'signal'] = 1
                # 止盈
                elif df['low'].iloc[i] <= self.take_profit:
                    df.loc[df.index[i], 'signal'] = 1
        
        return df
    
    def update_position(self, signal, price):
        """更新持仓状态"""
        if signal == 1 and self.position <= 0:  # 买入
            self.position = 1
            self.entry_price = price
            if hasattr(self, 'stop_loss_pct'):
                self.stop_loss = price * (1 - self.stop_loss_pct)
                self.take_profit = price * (1 + self.take_profit_pct)
        elif signal == -1 and self.position >= 0:  # 卖出
            self.position = -1
            self.entry_price = price
            if hasattr(self, 'stop_loss_pct'):
                self.stop_loss = price * (1 + self.stop_loss_pct)
                self.take_profit = price * (1 - self.take_profit_pct)
        elif signal == 0:  # 平仓
            self.position = 0
            self.entry_price = 0
            self.stop_loss = None
            self.take_profit = None 