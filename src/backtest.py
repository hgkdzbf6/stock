import pandas as pd
import numpy as np

class Backtest:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.portfolio = pd.DataFrame()
        
    def run(self, df, commission=0.0003):
        """运行回测"""
        # 初始化持仓和资金
        self.portfolio = pd.DataFrame(index=df.index).fillna(0.0)
        self.portfolio['cash'] = self.initial_capital
        self.portfolio['close'] = df['close']
        self.portfolio['signal'] = df['signal']
        self.portfolio['drawdown'] = df['drawdown']
        
        # 计算持仓
        for i in range(1, len(df)):
            # 获取前一天的现金和持仓
            prev_cash = self.portfolio['cash'].iloc[i-1]
            prev_shares = self.portfolio['shares'].iloc[i-1] if 'shares' in self.portfolio.columns and i > 1 else 0
            
            current_signal = df['signal'].iloc[i]
            current_drawdown = df['drawdown'].iloc[i]
            
            # 止损检查
            if prev_shares > 0 and current_drawdown <= -0.20:
                # 强制卖出
                sell_amount = prev_shares * df['close'].iloc[i]
                commission_fee = sell_amount * commission
                self.portfolio.loc[df.index[i], 'shares'] = 0
                self.portfolio.loc[df.index[i], 'cash'] = prev_cash + sell_amount - commission_fee
                continue
            
            # 买入信号（T+1）
            if current_signal == 1 and prev_shares == 0:
                # 使用50%的现金买入
                buy_amount = prev_cash * 0.5
                shares = buy_amount / df['close'].iloc[i]
                commission_fee = buy_amount * commission
                
                self.portfolio.loc[df.index[i], 'shares'] = shares
                self.portfolio.loc[df.index[i], 'cash'] = prev_cash - buy_amount - commission_fee
                
            # 卖出信号
            elif current_signal == -1 and prev_shares > 0:
                sell_amount = prev_shares * df['close'].iloc[i]
                commission_fee = sell_amount * commission
                
                self.portfolio.loc[df.index[i], 'shares'] = 0
                self.portfolio.loc[df.index[i], 'cash'] = prev_cash + sell_amount - commission_fee
            else:
                # 保持前一天的持仓
                self.portfolio.loc[df.index[i], 'shares'] = prev_shares
                self.portfolio.loc[df.index[i], 'cash'] = prev_cash
        
        # 计算每日市值
        self.portfolio['position_value'] = self.portfolio['shares'] * self.portfolio['close']
        self.portfolio['total_value'] = self.portfolio['cash'] + self.portfolio['position_value']
        
        # 记录交易次数
        self.portfolio['trade'] = self.portfolio['shares'].diff() != 0
        self.trade_count = self.portfolio['trade'].sum()
        
        return self.portfolio
    
    def get_metrics(self):
        """计算回测指标"""
        total_return = (self.portfolio['total_value'].iloc[-1] - self.initial_capital) / self.initial_capital
        daily_returns = self.portfolio['total_value'].pct_change()
        
        metrics = {
            '总收益率': f"{total_return:.2%}",
            '年化收益率': f"{(total_return / (len(self.portfolio) / 252)):.2%}",
            '最大回撤': f"{self.calculate_max_drawdown():.2%}",
            '夏普比率': f"{self.calculate_sharpe_ratio(daily_returns):.2f}",
            '胜率': f"{self.calculate_win_rate():.2%}",
            '交易次数': f"{self.trade_count}"
        }
        
        return metrics
    
    def calculate_max_drawdown(self):
        """计算最大回撤"""
        cumulative = self.portfolio['total_value']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return abs(drawdown.min())
    
    def calculate_sharpe_ratio(self, returns):
        """计算夏普比率"""
        risk_free_rate = 0.03  # 假设无风险利率为3%
        excess_returns = returns - risk_free_rate/252
        return np.sqrt(252) * excess_returns.mean() / returns.std()
    
    def calculate_win_rate(self):
        """计算胜率"""
        daily_returns = self.portfolio['total_value'].pct_change()
        winning_days = len(daily_returns[daily_returns > 0])
        total_days = len(daily_returns[daily_returns != 0])
        return winning_days / total_days if total_days > 0 else 0 