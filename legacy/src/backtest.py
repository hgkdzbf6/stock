import pandas as pd
import numpy as np

class Backtest:
    def __init__(self, initial_capital=100000, commission=0.0003, slippage=0.001):
        self.initial_capital = initial_capital
        self.commission = commission  # 手续费率
        self.slippage = slippage      # 滑点
        self.portfolio = pd.DataFrame()
        
    def run(self, df):
        """运行回测"""
        # 初始化持仓和资金
        self.portfolio = pd.DataFrame(index=df.index).fillna(0.0)
        self.portfolio['cash'] = self.initial_capital
        self.portfolio['close'] = df['close']
        self.portfolio['signal'] = df['signal'].fillna(0)  # 填充NaN值
        self.portfolio['shares'] = 0.0
        
        # 复制其他有用的列
        if 'drawdown' in df.columns:
            self.portfolio['drawdown'] = df['drawdown']
        
        # 记录交易信息
        self.portfolio['trade_type'] = 0  # 0: 无交易, 1: 买入, -1: 卖出
        self.portfolio['trade_price'] = 0.0
        self.portfolio['trade_amount'] = 0.0
        
        # 逐行处理交易信号
        for i in range(len(df)):
            if i == 0:
                # 第一行初始化
                self.portfolio.iloc[i, self.portfolio.columns.get_loc('shares')] = 0
                continue
                
            # 获取前一天的持仓状态
            prev_cash = self.portfolio.iloc[i-1]['cash']
            prev_shares = self.portfolio.iloc[i-1]['shares']
            
            current_signal = self.portfolio.iloc[i]['signal']
            current_price = self.portfolio.iloc[i]['close']
            
            # 处理交易信号
            new_cash, new_shares, trade_type, trade_amount = self._process_signal(
                current_signal, current_price, prev_cash, prev_shares
            )
            
            # 更新持仓
            self.portfolio.iloc[i, self.portfolio.columns.get_loc('cash')] = new_cash
            self.portfolio.iloc[i, self.portfolio.columns.get_loc('shares')] = new_shares
            self.portfolio.iloc[i, self.portfolio.columns.get_loc('trade_type')] = trade_type
            self.portfolio.iloc[i, self.portfolio.columns.get_loc('trade_price')] = current_price if trade_type != 0 else 0
            self.portfolio.iloc[i, self.portfolio.columns.get_loc('trade_amount')] = trade_amount
        
        # 计算每日市值
        self.portfolio['position_value'] = self.portfolio['shares'] * self.portfolio['close']
        self.portfolio['total_value'] = self.portfolio['cash'] + self.portfolio['position_value']
        
        # 计算收益率
        self.portfolio['returns'] = self.portfolio['total_value'].pct_change()
        self.portfolio['cumulative_returns'] = (self.portfolio['total_value'] / self.initial_capital) - 1
        
        # 计算回撤
        self.portfolio['running_max'] = self.portfolio['total_value'].expanding().max()
        self.portfolio['drawdown_pct'] = (self.portfolio['total_value'] - self.portfolio['running_max']) / self.portfolio['running_max']
        
        # 统计交易次数
        self.trade_count = len(self.portfolio[self.portfolio['trade_type'] != 0])
        
        return self.portfolio
    
    def _process_signal(self, signal, price, prev_cash, prev_shares):
        """处理交易信号"""
        trade_type = 0
        trade_amount = 0
        
        # 买入信号
        if signal == 1 and prev_shares == 0:
            # 使用80%的现金买入
            buy_cash = prev_cash * 0.8
            
            # 考虑滑点
            actual_price = price * (1 + self.slippage)
            
            # 计算能买入的股数
            shares_to_buy = buy_cash / actual_price
            
            # 计算实际成本（包含手续费）
            total_cost = shares_to_buy * actual_price * (1 + self.commission)
            
            if total_cost <= prev_cash:
                new_cash = prev_cash - total_cost
                new_shares = shares_to_buy
                trade_type = 1
                trade_amount = total_cost
            else:
                new_cash = prev_cash
                new_shares = prev_shares
                
        # 卖出信号
        elif signal == -1 and prev_shares > 0:
            # 考虑滑点
            actual_price = price * (1 - self.slippage)
            
            # 卖出所有股份
            sell_amount = prev_shares * actual_price
            
            # 扣除手续费
            net_amount = sell_amount * (1 - self.commission)
            
            new_cash = prev_cash + net_amount
            new_shares = 0
            trade_type = -1
            trade_amount = sell_amount
            
        # 无信号或无法交易
        else:
            new_cash = prev_cash
            new_shares = prev_shares
            
        return new_cash, new_shares, trade_type, trade_amount
    
    def get_metrics(self):
        """计算回测指标"""
        if len(self.portfolio) == 0:
            return {}
            
        # 基础指标
        total_return = (self.portfolio['total_value'].iloc[-1] - self.initial_capital) / self.initial_capital
        
        # 计算年化收益率（根据数据频率调整）
        trading_periods = len(self.portfolio)
        if trading_periods > 0:
            # 假设每天240个5分钟周期，每年252个交易日
            periods_per_year = 240 * 252
            years = trading_periods / periods_per_year
            annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        else:
            annual_return = 0
        
        # 最大回撤
        max_drawdown = abs(self.portfolio['drawdown_pct'].min()) if len(self.portfolio) > 0 else 0
        
        # 夏普比率
        returns = self.portfolio['returns'].dropna()
        if len(returns) > 1 and returns.std() != 0:
            # 假设无风险利率为3%
            risk_free_rate = 0.03 / (240 * 252)  # 转换为分钟级别
            excess_returns = returns - risk_free_rate
            sharpe_ratio = np.sqrt(240 * 252) * excess_returns.mean() / returns.std()
        else:
            sharpe_ratio = 0
        
        # 胜率
        winning_trades = len(returns[returns > 0])
        total_trades = len(returns[returns != 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 盈亏比
        winning_returns = returns[returns > 0]
        losing_returns = returns[returns < 0]
        
        if len(winning_returns) > 0 and len(losing_returns) > 0:
            avg_win = winning_returns.mean()
            avg_loss = abs(losing_returns.mean())
            profit_loss_ratio = avg_win / avg_loss if avg_loss != 0 else 0
        else:
            profit_loss_ratio = 0
        
        # 波动率
        volatility = returns.std() * np.sqrt(240 * 252) if len(returns) > 1 else 0
        
        # 卡尔马比率
        calmar_ratio = annual_return / max_drawdown if max_drawdown != 0 else 0
        
        metrics = {
            '总收益率': f"{total_return:.2%}",
            '年化收益率': f"{annual_return:.2%}",
            '最大回撤': f"{max_drawdown:.2%}",
            '夏普比率': f"{sharpe_ratio:.2f}",
            '胜率': f"{win_rate:.2%}",
            '交易次数': f"{self.trade_count}",
            '盈亏比': f"{profit_loss_ratio:.2f}",
            '年化波动率': f"{volatility:.2%}",
            '卡尔马比率': f"{calmar_ratio:.2f}"
        }
        
        return metrics
    
    def get_trade_details(self):
        """获取交易明细"""
        trades = self.portfolio[self.portfolio['trade_type'] != 0].copy()
        
        if len(trades) == 0:
            return pd.DataFrame()
        
        trades['trade_direction'] = trades['trade_type'].map({1: '买入', -1: '卖出'})
        
        # 计算每笔交易的收益
        buy_trades = trades[trades['trade_type'] == 1]
        sell_trades = trades[trades['trade_type'] == -1]
        
        trade_profits = []
        for i in range(min(len(buy_trades), len(sell_trades))):
            buy_price = buy_trades.iloc[i]['trade_price']
            sell_price = sell_trades.iloc[i]['trade_price']
            profit_pct = (sell_price - buy_price) / buy_price
            trade_profits.append(profit_pct)
        
        return trades[['trade_direction', 'trade_price', 'trade_amount', 'cash', 'shares', 'total_value']]
    
    def calculate_max_drawdown(self):
        """计算最大回撤"""
        if len(self.portfolio) == 0:
            return 0
        return abs(self.portfolio['drawdown_pct'].min())
    
    def calculate_sharpe_ratio(self, returns=None):
        """计算夏普比率"""
        if returns is None:
            returns = self.portfolio['returns'].dropna()
        
        if len(returns) <= 1 or returns.std() == 0:
            return 0
            
        risk_free_rate = 0.03 / (240 * 252)  # 年化3%转换为分钟级
        excess_returns = returns - risk_free_rate
        return np.sqrt(240 * 252) * excess_returns.mean() / returns.std()
    
    def calculate_win_rate(self):
        """计算胜率"""
        returns = self.portfolio['returns'].dropna()
        if len(returns) == 0:
            return 0
        winning_days = len(returns[returns > 0])
        total_days = len(returns[returns != 0])
        return winning_days / total_days if total_days > 0 else 0 