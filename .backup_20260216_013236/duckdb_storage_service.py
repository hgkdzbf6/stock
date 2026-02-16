"""DuckDB存储服务 - 高性能列式数据库存储"""
import os
import duckdb
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from loguru import logger


class DuckDBStorageService:
    """DuckDB存储服务"""
    
    def __init__(self, db_path: str = 'data/stock_data.duckdb'):
        """
        初始化DuckDB存储服务
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 连接数据库
        self.con = duckdb.connect(str(self.db_path))
        
        # 初始化表结构
        self._init_tables()
        
        logger.info(f"[DuckDB] 初始化完成: {db_path}")
    
    def _init_tables(self):
        """初始化表结构"""
        try:
            # 创建K线数据表
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS kline_data (
                    id INTEGER PRIMARY KEY,
                    stock_code VARCHAR(20) NOT NULL,
                    date TIMESTAMP NOT NULL,
                    frequency VARCHAR(10) NOT NULL,
                    open DOUBLE NOT NULL,
                    high DOUBLE NOT NULL,
                    low DOUBLE NOT NULL,
                    close DOUBLE NOT NULL,
                    volume BIGINT NOT NULL,
                    amount DOUBLE DEFAULT 0.0,
                    -- 扩展字段
                    pe_ratio DOUBLE,
                    pb_ratio DOUBLE,
                    turnover_rate DOUBLE,
                    -- 元数据
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(stock_code, date, frequency)
                )
            """)
            
            # 创建索引
            self.con.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_date 
                ON kline_data(stock_code, date)
            """)
            
            self.con.execute("""
                CREATE INDEX IF NOT EXISTS idx_frequency 
                ON kline_data(frequency)
            """)
            
            # 创建股票元数据表
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS stock_info (
                    stock_code VARCHAR(20) PRIMARY KEY,
                    stock_name VARCHAR(100),
                    market VARCHAR(10),
                    sector VARCHAR(50),
                    industry VARCHAR(50),
                    list_date DATE,
                    -- JSON元数据支持动态字段
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            logger.info("[DuckDB] 表结构初始化完成")
            
        except Exception as e:
            logger.error(f"[DuckDB] 初始化表结构失败: {e}")
            raise
    
    def save_kline_data(
        self,
        df: pd.DataFrame,
        stock_code: str,
        frequency: str = 'daily'
    ) -> int:
        """
        保存K线数据
        
        Args:
            df: K线数据DataFrame
            stock_code: 股票代码
            frequency: 频率
            
        Returns:
            保存的记录数
        """
        try:
            # 重置索引为列
            df_reset = df.reset_index()
            
            # 列名映射（中文 -> 英文）
            column_map = {
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'amount',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change',
                '换手率': 'turnover_rate',
                '振幅': 'amplitude'
            }
            
            # 重命名列
            df_reset = df_reset.rename(columns=column_map)
            
            # 转换为小写
            df_reset.columns = [col.lower() for col in df_reset.columns]
            
            # 确保有date列
            if 'date' not in df_reset.columns:
                # 尝试从索引获取
                if hasattr(df, 'index'):
                    df_reset['date'] = df.index
                else:
                    raise ValueError("数据中缺少日期列")
            
            # 添加必需字段
            df_reset['stock_code'] = stock_code
            df_reset['frequency'] = frequency
            df_reset['created_at'] = datetime.now()
            df_reset['updated_at'] = datetime.now()
            
            # 确保所有必需列存在
            required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df_reset.columns:
                    if col == 'volume':
                        df_reset[col] = 0
                    else:
                        df_reset[col] = 0.0
            
            # 添加可选列（如果不存在）
            optional_columns = {
                'amount': 0.0,
                'pe_ratio': None,
                'pb_ratio': None,
                'turnover_rate': None
            }
            for col, default_val in optional_columns.items():
                if col not in df_reset.columns:
                    df_reset[col] = default_val
            
            # 生成ID
            max_id_result = self.con.execute(
                "SELECT COALESCE(MAX(id), 0) FROM kline_data"
            ).fetchone()
            max_id = max_id_result[0] if max_id_result else 0
            df_reset['id'] = range(max_id + 1, max_id + 1 + len(df_reset))
            
            # 只选择表结构中的列
            table_columns = self.con.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'kline_data'
                ORDER BY ordinal_position
            """).fetchall()
            table_columns = [row[0] for row in table_columns]
            
            # 选择并排序列
            df_insert = df_reset[table_columns]
            
            # 删除已存在的数据
            self.con.execute("""
                DELETE FROM kline_data 
                WHERE stock_code = ? AND frequency = ?
            """, [stock_code, frequency])
            
            # 批量插入
            self.con.execute("INSERT INTO kline_data SELECT * FROM df_insert")
            
            count = len(df_reset)
            logger.info(f"[DuckDB] 保存K线数据: {stock_code}, {frequency}, {count}条")
            return count
            
        except Exception as e:
            logger.error(f"[DuckDB] 保存K线数据失败: {e}")
            raise
    
    def load_kline_data(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'daily'
    ) -> Optional[pd.DataFrame]:
        """
        加载K线数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 频率
            
        Returns:
            K线数据DataFrame
        """
        try:
            # 使用索引查询
            query = """
                SELECT date, open, high, low, close, volume, amount,
                       pe_ratio, pb_ratio, turnover_rate
                FROM kline_data
                WHERE stock_code = ? 
                  AND frequency = ?
                  AND date >= ? 
                  AND date <= ?
                ORDER BY date
            """
            
            df = self.con.execute(
                query, 
                [stock_code, frequency, start_date, end_date]
            ).df()
            
            if df.empty:
                logger.warning(f"[DuckDB] 未找到数据: {stock_code}")
                return None
            
            # 设置日期为索引
            df = df.set_index('date')
            df.index.name = ''
            
            logger.info(f"[DuckDB] 加载K线数据: {stock_code}, {len(df)}条")
            return df
            
        except Exception as e:
            logger.error(f"[DuckDB] 加载K线数据失败: {e}")
            return None
    
    def update_kline_fields(
        self,
        stock_code: str,
        date: datetime,
        updates: Dict[str, any]
    ) -> bool:
        """
        更新K线数据的特定字段
        
        Args:
            stock_code: 股票代码
            date: 日期
            updates: 要更新的字段字典
            
        Returns:
            是否成功
        """
        try:
            # 构建SET子句
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values())
            values.append(stock_code)
            values.append(date)
            
            query = f"""
                UPDATE kline_data
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE stock_code = ? AND date = ?
            """
            
            self.con.execute(query, values)
            
            logger.info(f"[DuckDB] 更新字段: {stock_code}, {date}, {list(updates.keys())}")
            return True
            
        except Exception as e:
            logger.error(f"[DuckDB] 更新字段失败: {e}")
            return False
    
    def add_kline_column(
        self,
        column_name: str,
        column_type: str = 'DOUBLE',
        default_value: any = None
    ) -> bool:
        """
        动态添加K线数据表的列
        
        Args:
            column_name: 列名
            column_type: 列类型 (DOUBLE, INTEGER, VARCHAR, JSON)
            default_value: 默认值
            
        Returns:
            是否成功
        """
        try:
            # 检查列是否已存在
            columns = self.con.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'kline_data'
            """).fetchall()
            
            if column_name in [c[0] for c in columns]:
                logger.warning(f"[DuckDB] 列已存在: {column_name}")
                return False
            
            # 添加列
            if default_value is not None:
                query = f"ALTER TABLE kline_data ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
            else:
                query = f"ALTER TABLE kline_data ADD COLUMN {column_name} {column_type}"
            
            self.con.execute(query)
            
            logger.info(f"[DuckDB] 添加列: {column_name} ({column_type})")
            return True
            
        except Exception as e:
            logger.error(f"[DuckDB] 添加列失败: {e}")
            return False
    
    def get_downloaded_data_list(
        self,
        stock_code: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict:
        """
        获取已下载的数据列表
        
        Args:
            stock_code: 股票代码（可选）
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            数据列表
        """
        try:
            # 构建查询
            where_clause = ""
            params = []
            
            if stock_code:
                where_clause = "WHERE stock_code = ?"
                params.append(stock_code)
            
            # 查询每个股票的数据概览
            query = f"""
                SELECT 
                    stock_code,
                    MIN(date) as start_date,
                    MAX(date) as end_date,
                    frequency,
                    COUNT(*) as data_count,
                    MIN(created_at) as downloaded_at,
                    MAX(updated_at) as updated_at
                FROM kline_data
                {where_clause}
                GROUP BY stock_code, frequency
                ORDER BY downloaded_at DESC
                LIMIT ? OFFSET ?
            """
            
            params.extend([limit, offset])
            
            results = self.con.execute(query, params).fetchall()
            total = self.con.execute(f"""
                SELECT COUNT(DISTINCT stock_code) 
                FROM kline_data
                {where_clause}
            """, params[:1] if stock_code else []).fetchone()[0]
            
            downloads = []
            for row in results:
                downloads.append({
                    'stock_code': row[0],
                    'start_date': row[1].strftime('%Y-%m-%d') if row[1] else None,
                    'end_date': row[2].strftime('%Y-%m-%d') if row[2] else None,
                    'frequency': row[3],
                    'data_count': row[4],
                    'downloaded_at': row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else None,
                    'updated_at': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None,
                    'stock_name': None,
                    'file_path': f"{stock_code}_{row[1].strftime('%Y%m%d') if row[1] else ''}_" \
                               f"{row[2].strftime('%Y%m%d') if row[2] else ''}_{row[3]}.duckdb"
                })
            
            return {
                'downloads': downloads,
                'total': total
            }
            
        except Exception as e:
            logger.error(f"[DuckDB] 获取数据列表失败: {e}")
            return {'downloads': [], 'total': 0}
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息
        """
        try:
            # 总记录数
            total_records = self.con.execute(
                "SELECT COUNT(*) FROM kline_data"
            ).fetchone()[0]
            
            # 股票数量
            total_stocks = self.con.execute("""
                SELECT COUNT(DISTINCT stock_code) 
                FROM kline_data
            """).fetchone()[0]
            
            # 频率分布
            freq_dist = self.con.execute("""
                SELECT frequency, COUNT(*) as count
                FROM kline_data
                GROUP BY frequency
            """).fetchall()
            
            freq_distribution = {row[0]: row[1] for row in freq_dist}
            
            # 总成交量
            total_volume = self.con.execute("""
                SELECT SUM(volume) 
                FROM kline_data
            """).fetchone()[0] or 0
            
            return {
                'total_records': total_records,
                'total_stocks': total_stocks,
                'total_data_points': total_records,
                'total_volume': int(total_volume),
                'frequency_distribution': freq_distribution
            }
            
        except Exception as e:
            logger.error(f"[DuckDB] 获取统计信息失败: {e}")
            return {
                'total_records': 0,
                'total_stocks': 0,
                'total_data_points': 0,
                'total_volume': 0,
                'frequency_distribution': {}
            }
    
    def delete_data(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'daily'
    ) -> int:
        """
        删除K线数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 频率
            
        Returns:
            删除的记录数
        """
        try:
            query = """
                DELETE FROM kline_data
                WHERE stock_code = ? 
                  AND frequency = ?
                  AND date >= ? 
                  AND date <= ?
            """
            
            # 先查询要删除的记录数
            count_result = self.con.execute("""
                SELECT COUNT(*) FROM kline_data
                WHERE stock_code = ? 
                  AND frequency = ?
                  AND date >= ? 
                  AND date <= ?
            """, [stock_code, frequency, start_date, end_date]).fetchone()
            
            count = count_result[0] if count_result else 0
            
            # 执行删除
            self.con.execute(query, [stock_code, frequency, start_date, end_date])
            
            logger.info(f"[DuckDB] 删除数据: {stock_code}, {count}条")
            return count
            
        except Exception as e:
            logger.error(f"[DuckDB] 删除数据失败: {e}")
            return 0
    
    def check_data_exists(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'daily'
    ) -> Optional[Dict]:
        """
        检查数据是否存在
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 频率
            
        Returns:
            数据信息
        """
        try:
            query = """
                SELECT 
                    MIN(date) as start_date,
                    MAX(date) as end_date,
                    COUNT(*) as data_count,
                    MAX(updated_at) as updated_at
                FROM kline_data
                WHERE stock_code = ? AND frequency = ?
            """
            
            result = self.con.execute(query, [stock_code, frequency]).fetchone()
            
            if result[0] is None:
                return None
            
            # 计算重叠类型
            existing_start = result[0]
            existing_end = result[1]
            
            if existing_start <= start_date and existing_end >= end_date:
                overlap_type = 'exact'
            elif existing_start <= start_date and existing_end >= start_date:
                overlap_type = 'partial_start'
            elif existing_end >= end_date and existing_start <= end_date:
                overlap_type = 'partial_end'
            else:
                overlap_type = 'none'
            
            return {
                'stock_code': stock_code,
                'start_date': existing_start.strftime('%Y-%m-%d'),
                'end_date': existing_end.strftime('%Y-%m-%d'),
                'frequency': frequency,
                'data_count': result[2],
                'updated_at': result[3].strftime('%Y-%m-%d %H:%M:%S') if result[3] else None,
                'overlap_type': overlap_type
            }
            
        except Exception as e:
            logger.error(f"[DuckDB] 检查数据失败: {e}")
            return None
    
    def close(self):
        """关闭数据库连接"""
        if self.con:
            self.con.close()
            logger.info("[DuckDB] 数据库连接已关闭")
    
    def __del__(self):
        """析构函数"""
        self.close()