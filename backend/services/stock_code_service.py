"""股票代码映射服务 - 支持股票列表下载和模糊搜索"""
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger
import re


class StockCodeService:
    """股票代码映射服务"""
    
    def __init__(self, data_dir: str = 'data'):
        """
        初始化股票代码服务
        
        Args:
            data_dir: 数据目录
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.stock_list_file = self.data_dir / 'stock_list.csv'
        self.stock_list_df = None
        
        # 初始化时加载数据
        self._load_stock_list()
        
        logger.info(f"股票代码服务初始化完成，数据目录: {self.data_dir}")
    
    def _load_stock_list(self):
        """从本地文件加载股票列表"""
        if self.stock_list_file.exists():
            try:
                self.stock_list_df = pd.read_csv(self.stock_list_file, encoding='utf-8-sig')
                logger.info(f"成功加载股票列表: {len(self.stock_list_df)} 只股票")
            except Exception as e:
                logger.error(f"加载股票列表失败: {e}")
                self.stock_list_df = pd.DataFrame()
        else:
            self.stock_list_df = pd.DataFrame()
            logger.warning("股票列表文件不存在")
    
    def save_stock_list(self, stock_list: List[Dict]) -> bool:
        """
        保存股票列表到本地
        
        Args:
            stock_list: 股票列表数据
            
        Returns:
            是否成功
        """
        try:
            if not stock_list:
                logger.warning("股票列表为空")
                return False
            
            # 转换为DataFrame
            df = pd.DataFrame(stock_list)
            
            # 添加市场标识
            if 'market' not in df.columns:
                df['market'] = df['代码'].apply(self._detect_market)
            
            # 添加更新时间
            df['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 保存到CSV
            df.to_csv(self.stock_list_file, index=False, encoding='utf-8-sig')
            
            # 更新内存中的数据
            self.stock_list_df = df
            
            logger.info(f"成功保存股票列表: {len(df)} 只股票 -> {self.stock_list_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存股票列表失败: {e}")
            return False
    
    @staticmethod
    def _detect_market(stock_code: str) -> str:
        """
        根据股票代码检测市场
        
        Args:
            stock_code: 股票代码
            
        Returns:
            市场标识
        """
        # 移除后缀
        code = stock_code.split('.')[0] if '.' in stock_code else stock_code
        
        # 沪市主板 (600xxx, 601xxx, 603xxx, 605xxx)
        if re.match(r'^60[0135]\d{3}$', code):
            return '沪市主板'
        
        # 沪市科创板 (688xxx)
        if re.match(r'^688\d{3}$', code):
            return '科创板'
        
        # 深市主板 (000xxx, 001xxx, 003xxx)
        if re.match(r'^00[013]\d{3}$', code):
            return '深市主板'
        
        # 深市创业板 (300xxx)
        if re.match(r'^300\d{3}$', code):
            return '创业板'
        
        # 北交所 (83xxxx, 87xxxx, 43xxxx)
        if re.match(r'^[48][37]\d{4}$', code):
            return '北交所'
        
        return '未知'
    
    def search_by_code(self, code: str, limit: int = 10) -> List[Dict]:
        """
        根据股票代码精确搜索
        
        Args:
            code: 股票代码
            limit: 返回数量限制
            
        Returns:
            匹配的股票列表
        """
        try:
            if self.stock_list_df is None or self.stock_list_df.empty:
                logger.warning("股票列表为空")
                return []
            
            # 确保代码列是字符串类型
            df = self.stock_list_df.copy()
            df['代码'] = df['代码'].astype(str)
            
            # 精确匹配代码
            mask = df['代码'].str.contains(code, case=False, na=False)
            results = df[mask].head(limit)
            
            return self._format_results(results)
            
        except Exception as e:
            logger.error(f"根据代码搜索失败: {e}")
            return []
    
    def search_by_name(self, name: str, limit: int = 10) -> List[Dict]:
        """
        根据股票名称模糊搜索
        
        Args:
            name: 股票名称（支持部分匹配）
            limit: 返回数量限制
            
        Returns:
            匹配的股票列表
        """
        try:
            if self.stock_list_df is None or self.stock_list_df.empty:
                logger.warning("股票列表为空")
                return []
            
            # 确保名称列是字符串类型
            df = self.stock_list_df.copy()
            df['名称'] = df['名称'].astype(str)
            
            # 模糊匹配名称
            mask = df['名称'].str.contains(name, case=False, na=False)
            results = df[mask].head(limit)
            
            return self._format_results(results)
            
        except Exception as e:
            logger.error(f"根据名称搜索失败: {e}")
            return []
    
    def search_by_prefix(self, prefix: str, limit: int = 10, search_field: str = 'name') -> List[Dict]:
        """
        根据前缀搜索
        
        Args:
            prefix: 前缀字符
            limit: 返回数量限制
            search_field: 搜索字段 ('name' 或 'code')
            
        Returns:
            匹配的股票列表
        """
        try:
            if self.stock_list_df is None or self.stock_list_df.empty:
                logger.warning("股票列表为空")
                return []
            
            # 确保列是字符串类型
            df = self.stock_list_df.copy()
            df['代码'] = df['代码'].astype(str)
            df['名称'] = df['名称'].astype(str)
            
            # 根据搜索字段选择
            if search_field == 'code':
                mask = df['代码'].str.startswith(prefix, na=False)
            else:
                mask = df['名称'].str.startswith(prefix, na=False)
            
            results = df[mask].head(limit)
            
            return self._format_results(results)
            
        except Exception as e:
            logger.error(f"根据前缀搜索失败: {e}")
            return []
    
    def fuzzy_search(self, keyword: str, limit: int = 10) -> List[Dict]:
        """
        模糊搜索（同时搜索代码和名称）
        
        Args:
            keyword: 关键词
            limit: 返回数量限制
            
        Returns:
            匹配的股票列表
        """
        try:
            if self.stock_list_df is None or self.stock_list_df.empty:
                logger.warning("股票列表为空")
                return []
            
            # 确保代码和名称列是字符串类型
            df = self.stock_list_df.copy()
            df['代码'] = df['代码'].astype(str)
            df['名称'] = df['名称'].astype(str)
            
            # 同时搜索代码和名称
            code_mask = df['代码'].str.contains(keyword, case=False, na=False)
            name_mask = df['名称'].str.contains(keyword, case=False, na=False)
            
            # 优先匹配名称，然后是代码
            results = df[name_mask | code_mask].head(limit)
            
            return self._format_results(results)
            
        except Exception as e:
            logger.error(f"模糊搜索失败: {e}")
            return []
    
    def get_stock_info(self, code: str) -> Optional[Dict]:
        """
        获取股票详细信息
        
        Args:
            code: 股票代码
            
        Returns:
            股票信息字典
        """
        try:
            if self.stock_list_df is None or self.stock_list_df.empty:
                logger.warning("股票列表为空")
                return None
            
            # 精确匹配
            mask = self.stock_list_df['代码'] == code
            results = self.stock_list_df[mask]
            
            if len(results) == 0:
                logger.warning(f"未找到股票: {code}")
                return None
            
            return self._format_results(results)[0]
            
        except Exception as e:
            logger.error(f"获取股票信息失败: {e}")
            return None
    
    def get_stocks_by_market(self, market: str, limit: int = 100) -> List[Dict]:
        """
        根据市场获取股票列表
        
        Args:
            market: 市场名称 ('沪市主板', '深市主板', '科创板', '创业板', '北交所')
            limit: 返回数量限制
            
        Returns:
            股票列表
        """
        try:
            if self.stock_list_df is None or self.stock_list_df.empty:
                logger.warning("股票列表为空")
                return []
            
            # 根据市场筛选
            if 'market' in self.stock_list_df.columns:
                mask = self.stock_list_df['market'] == market
                results = self.stock_list_df[mask].head(limit)
            else:
                # 如果没有market列，动态计算
                results = self.stock_list_df.copy()
                results['market'] = results['代码'].apply(self._detect_market)
                mask = results['market'] == market
                results = results[mask].head(limit)
            
            return self._format_results(results)
            
        except Exception as e:
            logger.error(f"根据市场获取股票失败: {e}")
            return []
    
    def _format_results(self, df: pd.DataFrame) -> List[Dict]:
        """
        格式化搜索结果
        
        Args:
            df: DataFrame结果
            
        Returns:
            格式化后的字典列表
        """
        if df.empty:
            return []
        
        results = []
        for _, row in df.iterrows():
            result = {
                'code': row.get('代码', ''),
                'name': row.get('名称', ''),
                'price': row.get('最新价', 0),
                'change': row.get('涨跌额', 0),
                'change_pct': row.get('涨跌幅', 0),
                'volume': row.get('成交量', 0),
                'amount': row.get('成交额', 0),
                'market_cap': row.get('市值', 0),
                'market': row.get('market', self._detect_market(row.get('代码', ''))),
                'open': row.get('开盘', 0),
                'high': row.get('最高', 0),
                'low': row.get('最低', 0),
                'pre_close': row.get('昨收', 0),
                'update_time': row.get('update_time', '')
            }
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        获取股票列表统计信息
        
        Returns:
            统计信息字典
        """
        try:
            if self.stock_list_df is None or self.stock_list_df.empty:
                return {
                    'total': 0,
                    'by_market': {}
                }
            
            stats = {
                'total': len(self.stock_list_df),
                'by_market': {}
            }
            
            # 统计各市场股票数量
            if 'market' in self.stock_list_df.columns:
                market_counts = self.stock_list_df['market'].value_counts()
                for market, count in market_counts.items():
                    stats['by_market'][market] = int(count)
            else:
                # 动态计算
                markets = self.stock_list_df['代码'].apply(self._detect_market)
                market_counts = markets.value_counts()
                for market, count in market_counts.items():
                    stats['by_market'][market] = int(count)
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                'total': 0,
                'by_market': {}
            }
    
    def refresh(self) -> bool:
        """
        刷新股票列表（重新加载）
        
        Returns:
            是否成功
        """
        try:
            self._load_stock_list()
            return True
        except Exception as e:
            logger.error(f"刷新股票列表失败: {e}")
            return False


# 全局实例
stock_code_service = StockCodeService()