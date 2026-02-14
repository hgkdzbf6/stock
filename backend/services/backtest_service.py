"""回测引擎服务"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from loguru import logger
import asyncio
from data_adapters import AdapterFactory
from .data_fetcher import DataFetcher


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 100000.0, 
                 commission: float = 0.0003,
                 slippage: float = 0.001):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            commission: 手续费率（默认0.03%）
            slippage: 滑点（默认0.1%）
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.portfolio = None
        self.trade_count = 0
        
    async def run_backtest(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        freq: str = 'daily',
        strategy_params: Dict = None,
        data_source: str = 'auto'
    ) -> Dict:
        """
        运行回测
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            freq: 数据频率
            strategy_params: 策略参数
            data_source: 数据源
            
        Returns:
            回测结果字典
        """
        try:
            logger.info(f"开始回测: {stock_code}, {start_date} 到 {end_date}")
            
            # 1. 获取历史数据
            data_fetcher = DataFetcher(source=data_source)
            df = await data_fetcher.get_data(
                code=stock_code,
                start_date=start_date,
                end_date=end_date,
                freq=freq
            )
            
            if df is None or len(df) == 0:
                raise Exception("无法获取历史数据")
            
            logger.info(f"获取到 {len(df)} 条历史数据")
            
            # 2. 计算技术指标和信号
            df = self._calculate_indicators(df, strategy_params)
            
            # 3. 运行回测
            self.portfolio = self._run_backtest_simulation(df)
            
            # 4. 计算绩效指标
            metrics = self._calculate_metrics()
            
            # 5. 获取交易明细
            trades = self._get_trade_details()
            
            # 6. 生成净值曲线数据
            equity_curve = self._generate_equity_curve()
            
            result = {
                'stock_code': stock_code,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'frequency': freq,
                'initial_capital': self.initial_capital,
                'final_capital': float(self.portfolio['total_value'].iloc[-1]),
                'metrics': metrics,
                'trades': trades,
                'equity_curve': equity_curve,
                'data_points': len(df),
                'trading_days': len(df)
            }
            
            logger.info(f"回测完成: 总收益率 {metrics['total_return']:.2%}")
            return result
            
        except Exception as e:
            logger.error(f"回测失败: {e}")
            raise
    
    def _calculate_indicators(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """
        计算技术指标和交易信号
        
        Args:
            df: 原始数据
            params: 策略参数
            
        Returns:
            添加了技术指标的DataFrame
        """
        df = df.copy()
        
        # 确保数据按时间排序
        df = df.sort_index()
        
        # 获取策略类型
        strategy_type = params.get('type', 'MA')
        
        if strategy_type == 'MA':
            df = self._calculate_ma_signals(df, params)
        elif strategy_type == 'RSI':
            df = self._calculate_rsi_signals(df, params)
        elif strategy_type == 'BOLL':
            df = self._calculate_boll_signals(df, params)
        elif strategy_type == 'MACD':
            df = self._calculate_macd_signals(df, params)
        else:
            # 默认使用双均线策略
            df = self._calculate_ma_signals(df, params)
        
        return df
    
    def _calculate_ma_signals(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """计算均线策略信号"""
        short_window = params.get('short_window', 5)
        long_window = params.get('long_window', 20)
        
        # 计算移动平均线
        df['MA_short'] = df['close'].rolling(window=short_window).mean()
        df['MA_long'] = df['close'].rolling(window=long_window).mean()
        
        # 生成信号
        df['signal'] = 0
        df.loc[df['MA_short'] > df['MA_long'], 'signal'] = 1  # 买入
        df.loc[df['MA_short'] < df['MA_long'], 'signal'] = -1  # 卖出
        
        # 消除连续信号
        df['signal'] = df['signal'].diff()
        df['signal'] = df['signal'].fillna(0)
        
        return df
    
    def _calculate_rsi_signals(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """计算RSI策略信号"""
        rsi_window = params.get('rsi_window', 14)
        oversold = params.get('oversold', 30)
        overbought = params.get('overbought', 70)
        
        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 生成信号
        df['signal'] = 0
        df.loc[df['RSI'] < oversold, 'signal'] = 1  # 超卖买入
        df.loc[df['RSI'] > overbought, 'signal'] = -1  # 超买卖出
        
        # 消除连续信号
        df['signal'] = df['signal'].diff()
        df['signal'] = df['signal'].fillna(0)
        
        return df
    
    def _calculate_boll_signals(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """计算布林带策略信号"""
        window = params.get('boll_window', 20)
        num_std = params.get('num_std', 2)
        
        # 计算布林带
        df['BOLL_mid'] = df['close'].rolling(window=window).mean()
        df['BOLL_std'] = df['close'].rolling(window=window).std()
        df['BOLL_upper'] = df['BOLL_mid'] + num_std * df['BOLL_std']
        df['BOLL_lower'] = df['BOLL_mid'] - num_std * df['BOLL_std']
        
        # 生成信号
        df['signal'] = 0
        df.loc[df['close'] < df['BOLL_lower'], 'signal'] = 1  # 价格低于下轨买入
        df.loc[df['close'] > df['BOLL_upper'], 'signal'] = -1  # 价格高于上轨卖出
        
        # 消除连续信号
        df['signal'] = df['signal'].diff()
        df['signal'] = df['signal'].fillna(0)
        
        return df
    
    def _calculate_macd_signals(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """计算MACD策略信号"""
        fast = params.get('fast', 12)
        slow = params.get('slow', 26)
        signal = params.get('signal', 9)
        
        # 计算MACD
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        df['MACD'] = ema_fast - ema_slow
        df['MACD_signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']
        
        # 生成信号
        df['signal'] = 0
        df.loc[df['MACD_hist'] > 0, 'signal'] = 1  # MACD柱状图大于0买入
        df.loc[df['MACD_hist'] < 0, 'signal'] = -1  # MACD柱状图小于0卖出
        
        # 消除连续信号
        df['signal'] = df['signal'].diff()
        df['signal'] = df['signal'].fillna(0)
        
        return df
    
    def _run_backtest_simulation(self, df: pd.DataFrame) -> pd.DataFrame:
        """运行回测模拟"""
        # 初始化
        self.portfolio = pd.DataFrame(index=df.index)
        self.portfolio['cash'] = self.initial_capital
        self.portfolio['close'] = df['close']
        self.portfolio['signal'] = df['signal'].fillna(0)
        self.portfolio['shares'] = 0.0
        
        # 记录交易信息
        self.portfolio['trade_type'] = 0  # 0: 无交易, 1: 买入, -1: 卖出
        self.portfolio['trade_price'] = 0.0
        self.portfolio['trade_amount'] = 0.0
        
        # 逐行处理
        for i in range(len(df)):
            if i == 0:
                self.portfolio.iloc[i, self.portfolio.columns.get_loc('shares')] = 0
                continue
                
            prev_cash = self.portfolio.iloc[i-1]['cash']
            prev_shares = self.portfolio.iloc[i-1]['shares']
            
            current_signal = self.portfolio.iloc[i]['signal']
            current_price = self.portfolio.iloc[i]['close']
            
            new_cash, new_shares, trade_type, trade_amount = self._process_signal(
                current_signal, current_price, prev_cash, prev_shares
            )
            
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
    
    def _process_signal(self, signal: int, price: float, 
                       prev_cash: float, prev_shares: float) -> Tuple:
        """处理交易信号"""
        trade_type = 0
        trade_amount = 0.0
        
        # 买入信号
        if signal == 1 and prev_shares == 0:
            buy_cash = prev_cash * 0.8  # 使用80%现金
            actual_price = price * (1 + self.slippage)
            shares_to_buy = buy_cash / actual_price
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
            actual_price = price * (1 - self.slippage)
            sell_amount = prev_shares * actual_price
            net_amount = sell_amount * (1 - self.commission)
            
            new_cash = prev_cash + net_amount
            new_shares = 0
            trade_type = -1
            trade_amount = sell_amount
            
        else:
            new_cash = prev_cash
            new_shares = prev_shares
            
        return new_cash, new_shares, trade_type, trade_amount
    
    def _calculate_metrics(self) -> Dict:
        """计算绩效指标"""
        if self.portfolio is None or len(self.portfolio) == 0:
            return {}
        
        total_return = (self.portfolio['total_value'].iloc[-1] - self.initial_capital) / self.initial_capital
        
        # 年化收益率
        trading_periods = len(self.portfolio)
        if trading_periods > 0:
            periods_per_year = 252  # 日线数据
            years = trading_periods / periods_per_year
            annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        else:
            annual_return = 0
        
        # 最大回撤
        max_drawdown = abs(self.portfolio['drawdown_pct'].min()) if len(self.portfolio) > 0 else 0
        
        # 夏普比率
        returns = self.portfolio['returns'].dropna()
        if len(returns) > 1 and returns.std() != 0:
            risk_free_rate = 0.03 / 252
            excess_returns = returns - risk_free_rate
            sharpe_ratio = np.sqrt(252) * excess_returns.mean() / returns.std()
        else:
            sharpe_ratio = 0
        
        # 胜率
        trade_returns = self.portfolio['returns'].dropna()
        winning_trades = len(trade_returns[trade_returns > 0])
        total_trades = len(trade_returns[trade_returns != 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 盈亏比
        winning_returns = trade_returns[trade_returns > 0]
        losing_returns = trade_returns[trade_returns < 0]
        
        if len(winning_returns) > 0 and len(losing_returns) > 0:
            avg_win = winning_returns.mean()
            avg_loss = abs(losing_returns.mean())
            profit_loss_ratio = avg_win / avg_loss if avg_loss != 0 else 0
        else:
            profit_loss_ratio = 0
        
        # 波动率
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
        
        # 卡尔马比率
        calmar_ratio = annual_return / max_drawdown if max_drawdown != 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'trade_count': self.trade_count,
            'profit_loss_ratio': profit_loss_ratio,
            'volatility': volatility,
            'calmar_ratio': calmar_ratio
        }
    
    def _get_trade_details(self) -> List[Dict]:
        """获取交易明细"""
        trades = self.portfolio[self.portfolio['trade_type'] != 0].copy()
        
        if len(trades) == 0:
            return []
        
        trades_list = []
        for idx, row in trades.iterrows():
            trades_list.append({
                'date': idx.strftime('%Y-%m-%d %H:%M:%S'),
                'type': '买入' if row['trade_type'] == 1 else '卖出',
                'price': float(row['trade_price']),
                'amount': float(row['trade_amount']),
                'cash': float(row['cash']),
                'shares': float(row['shares']),
                'total_value': float(row['total_value'])
            })
        
        return trades_list
    
    def _generate_equity_curve(self) -> List[Dict]:
        """生成净值曲线数据"""
        if self.portfolio is None:
            return []
        
        equity_curve = []
        for idx, row in self.portfolio.iterrows():
            equity_curve.append({
                'date': idx.strftime('%Y-%m-%d %H:%M:%S'),
                'total_value': float(row['total_value']),
                'cumulative_return': float(row['cumulative_returns']),
                'drawdown': float(row['drawdown_pct'])
            })
        
        return equity_curve