"""数据存储服务 - 管理已下载的历史数据"""
import os
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
from loguru import logger


class DataStorageService:
    """数据存储服务"""
    
    def __init__(self, db_path: str = "stock.db", data_dir: str = "data"):
        """
        初始化数据存储服务
        
        Args:
            db_path: 数据库路径
            data_dir: 数据文件存储目录
        """
        self.db_path = db_path
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        
        logger.info(f"数据存储服务初始化完成: {db_path}, {data_dir}")
    
    def _init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建已下载数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS downloaded_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code VARCHAR(20) NOT NULL,
                stock_name VARCHAR(50),
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                frequency VARCHAR(10) NOT NULL,
                data_count INTEGER NOT NULL,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source VARCHAR(20),
                file_path VARCHAR(255),
                
                UNIQUE(stock_code, start_date, end_date, frequency)
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stock_code 
            ON downloaded_data(stock_code)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_start_date 
            ON downloaded_data(start_date)
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("数据库表初始化完成")
    
    def save_downloaded_data(
        self,
        stock_code: str,
        stock_name: Optional[str],
        start_date: datetime,
        end_date: datetime,
        frequency: str,
        data: pd.DataFrame,
        source: str = "auto"
    ) -> int:
        """
        保存已下载数据
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            data: 数据DataFrame
            source: 数据源
            
        Returns:
            数据库记录ID
        """
        try:
            # 生成文件名
            file_name = f"{stock_code}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{frequency}.csv"
            file_path = self.data_dir / file_name
            
            # 保存为CSV文件
            data.to_csv(file_path, index=True)
            
            # 保存到数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO downloaded_data 
                (stock_code, stock_name, start_date, end_date, frequency, 
                 data_count, downloaded_at, updated_at, source, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stock_code,
                stock_name,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                frequency,
                len(data),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                source,
                str(file_path)
            ))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"数据保存成功: {stock_code}, 记录ID: {record_id}, 文件: {file_path}")
            return record_id
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            raise
    
    def load_downloaded_data(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str
    ) -> Optional[pd.DataFrame]:
        """
        加载已下载数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            
        Returns:
            数据DataFrame，如果不存在返回None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT file_path 
                FROM downloaded_data 
                WHERE stock_code = ? 
                  AND start_date = ? 
                  AND end_date = ? 
                  AND frequency = ?
            """, (
                stock_code,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                frequency
            ))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                file_path = result[0]
                if os.path.exists(file_path):
                    data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                    logger.info(f"数据加载成功: {file_path}, {len(data)}条记录")
                    return data
                else:
                    logger.warning(f"数据文件不存在: {file_path}")
                    return None
            else:
                logger.info(f"未找到数据: {stock_code}, {start_date} - {end_date}")
                return None
                
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            raise
    
    def get_downloaded_data(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str
    ) -> Optional[Dict]:
        """
        获取已下载数据的元数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            
        Returns:
            数据元数据字典，如果不存在返回None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, stock_code, stock_name, start_date, end_date, 
                       frequency, data_count, downloaded_at, updated_at, 
                       source, file_path
                FROM downloaded_data 
                WHERE stock_code = ? 
                  AND start_date = ? 
                  AND end_date = ? 
                  AND frequency = ?
            """, (
                stock_code,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                frequency
            ))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'stock_code': row[1],
                    'stock_name': row[2],
                    'start_date': row[3],
                    'end_date': row[4],
                    'frequency': row[5],
                    'data_count': row[6],
                    'downloaded_at': row[7],
                    'updated_at': row[8],
                    'source': row[9],
                    'file_path': row[10]
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"获取数据元数据失败: {e}")
            return None
    
    def check_data_exists(
        self,
        stock_code: str,
        start_date: datetime,
        end_date: datetime,
        frequency: str
    ) -> Optional[Dict]:
        """
        检查数据是否存在
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            frequency: 数据频率
            
        Returns:
            包含存在状态和重叠类型的信息字典
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查找所有相同股票和频率的数据
            cursor.execute("""
                SELECT id, stock_code, stock_name, start_date, end_date, 
                       frequency, data_count, downloaded_at, file_path
                FROM downloaded_data 
                WHERE stock_code = ? 
                  AND frequency = ?
                ORDER BY start_date DESC
            """, (stock_code, frequency))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return {'exists': False, 'overlap_type': None}
            
            # 检查重叠
            new_start = start_date.date() if isinstance(start_date, datetime) else start_date
            new_end = end_date.date() if isinstance(end_date, datetime) else end_date
            
            for row in rows:
                existing_start = datetime.strptime(row[3], '%Y-%m-%d').date()
                existing_end = datetime.strptime(row[4], '%Y-%m-%d').date()
                
                # 完全包含
                if existing_start <= new_start and existing_end >= new_end:
                    return {
                        'exists': True,
                        'overlap_type': 'exact',
                        'data': {
                            'id': row[0],
                            'stock_code': row[1],
                            'stock_name': row[2],
                            'start_date': row[3],
                            'end_date': row[4],
                            'frequency': row[5],
                            'data_count': row[6],
                            'downloaded_at': row[7],
                            'file_path': row[8]
                        }
                    }
                
                # 部分重叠
                if not (existing_end < new_start or existing_start > new_end):
                    return {
                        'exists': True,
                        'overlap_type': 'partial',
                        'data': {
                            'id': row[0],
                            'stock_code': row[1],
                            'stock_name': row[2],
                            'start_date': row[3],
                            'end_date': row[4],
                            'frequency': row[5],
                            'data_count': row[6],
                            'downloaded_at': row[7],
                            'file_path': row[8]
                        }
                    }
            
            return {'exists': False, 'overlap_type': None}
            
        except Exception as e:
            logger.error(f"检查数据存在性失败: {e}")
            return {'exists': False, 'overlap_type': None}
    
    def get_downloaded_data_list(
        self,
        stock_code: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, any]:
        """
        获取已下载数据列表
        
        Args:
            stock_code: 股票代码（可选，用于过滤）
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            包含数据列表和总数的字典
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 构建查询条件
            where_clause = ""
            params = []
            
            if stock_code:
                where_clause = "WHERE stock_code = ?"
                params.append(stock_code)
            
            # 获取总数
            count_query = f"SELECT COUNT(*) FROM downloaded_data {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # 获取列表
            query = f"""
                SELECT id, stock_code, stock_name, start_date, end_date, 
                       frequency, data_count, downloaded_at, updated_at, 
                       source, file_path
                FROM downloaded_data 
                {where_clause}
                ORDER BY downloaded_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [limit, offset])
            
            rows = cursor.fetchall()
            conn.close()
            
            downloads = []
            for row in rows:
                # 获取文件大小
                file_size = 0
                if os.path.exists(row[10]):
                    file_size = os.path.getsize(row[10])
                    file_size_str = self._format_file_size(file_size)
                else:
                    file_size_str = "N/A"
                
                downloads.append({
                    'id': row[0],
                    'stock_code': row[1],
                    'stock_name': row[2],
                    'start_date': row[3],
                    'end_date': row[4],
                    'frequency': row[5],
                    'data_count': row[6],
                    'downloaded_at': row[7],
                    'updated_at': row[8],
                    'source': row[9],
                    'file_path': row[10],
                    'file_size': file_size,
                    'file_size_str': file_size_str
                })
            
            return {
                'downloads': downloads,
                'total': total
            }
            
        except Exception as e:
            logger.error(f"获取数据列表失败: {e}")
            raise
    
    def delete_downloaded_data(self, record_id: int) -> bool:
        """
        删除已下载数据
        
        Args:
            record_id: 数据库记录ID
            
        Returns:
            是否删除成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取文件路径
            cursor.execute("SELECT file_path FROM downloaded_data WHERE id = ?", (record_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                file_path = result[0]
                
                # 删除文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"数据文件已删除: {file_path}")
            
            # 删除数据库记录
            cursor.execute("DELETE FROM downloaded_data WHERE id = ?", (record_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"数据记录已删除: {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除数据失败: {e}")
            return False
    
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f}{unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.2f}TB"