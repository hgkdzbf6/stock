import sqlite3
import csv
import os
from datetime import datetime
import sys

# 配置
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'stock_market.db')
# 默认使用 generate_stock_list.py 生成的文件
DEFAULT_DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'stock_list.csv')

def create_database():
    """初始化数据库表结构"""
    # 确保数据目录存在
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            stock_name TEXT,
            price REAL,
            change REAL,
            change_percent REAL,
            volume BIGINT,
            turnover REAL,
            status INTEGER,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            close_price REAL,
            market TEXT,
            snapshot_time TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引以提高查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_code ON stock_quotes(stock_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshot_time ON stock_quotes(snapshot_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshot_code_time ON stock_quotes(stock_code, snapshot_time)')
    
    conn.commit()
    conn.close()
    print(f"数据库已初始化: {DB_PATH}")

def clean_numeric(value):
    """清理并转换数值字符串"""
    if value is None:
        return None
    # 移除可能的千位分隔符
    cleaned = str(value).replace(',', '').strip()
    if cleaned == '':
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None

def parse_csv_row(row, headers):
    """解析CSV行并映射到数据库字段"""
    record = {}
    
    # 创建字典映射（处理可能的空格或其他格式问题）
    row_dict = dict(zip(headers, row))
    
    # 字段映射：根据 generate_stock_list.py 的输出格式
    # 输出格式：代码,名称,当前价,涨跌额,涨跌幅,成交量,成交额,状态,开盘,最高,最低,收盘,市场状态,时间
    
    record['stock_code'] = row_dict.get('代码', '')
    record['stock_name'] = row_dict.get('名称', '')
    
    # 价格字段
    record['price'] = clean_numeric(row_dict.get('当前价'))
    record['change'] = clean_numeric(row_dict.get('涨跌额'))
    record['change_percent'] = clean_numeric(row_dict.get('涨跌幅'))
    
    # 数量字段
    record['volume'] = int(clean_numeric(row_dict.get('成交量'))) if row_dict.get('成交量') else 0
    record['turnover'] = clean_numeric(row_dict.get('成交额'))
    
    # 状态字段
    status_str = row_dict.get('状态', '0')
    try:
        record['status'] = int(status_str) if status_str else 0
    except ValueError:
        record['status'] = 0
    
    # 开高低收
    record['open_price'] = clean_numeric(row_dict.get('开盘'))
    record['high_price'] = clean_numeric(row_dict.get('最高'))
    record['low_price'] = clean_numeric(row_dict.get('最低'))
    record['close_price'] = clean_numeric(row_dict.get('收盘'))
    
    # 市场状态和时间
    record['market'] = row_dict.get('市场状态', '其他')
    record['timestamp'] = row_dict.get('时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return record

def validate_record(record):
    """验证记录的完整性"""
    # 检查必填字段
    if not record.get('stock_code') or record['stock_code'] == '':
        return False, "股票代码为空"
    
    # 检查价格是否有效
    price = record.get('price')
    if price is None or price <= 0:
        return False, "价格无效"
    
    # 检查代码格式 (XXXXXX.SH/SZ/BJ)
    code = record['stock_code']
    import re
    if not re.match(r'^\d{6}\.(SH|SZ|BJ)$', code):
        return False, f"代码格式错误: {code}"
    
    return True, "验证通过"

def import_data(file_path, batch_size=1000):
    """从CSV文件导入数据到数据库"""
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 {file_path}")
        print(f"请先运行 generate_stock_list.py 生成数据文件，或检查路径是否正确。")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    count = 0
    errors = 0
    skipped = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            
            # 读取标题行
            headers = next(reader)
            print(f"检测到CSV列: {headers}")
            
            # 批量插入列表
            batch_data = []
            
            for row_num, row in enumerate(reader, start=2):  # 从第2行开始（跳过标题）
                try:
                    # 解析CSV行
                    record = parse_csv_row(row, headers)
                    
                    # 验证记录
                    is_valid, message = validate_record(record)
                    if not is_valid:
                        errors += 1
                        if errors <= 5:  # 只显示前5个错误
                            print(f"跳过第{row_num}行: {message}")
                        continue
                    
                    # 添加到批量列表
                    batch_data.append((
                        record['stock_code'],
                        record['stock_name'],
                        record['price'],
                        record['change'],
                        record['change_percent'],
                        record['volume'],
                        record['turnover'],
                        record['status'],
                        record['open_price'],
                        record['high_price'],
                        record['low_price'],
                        record['close_price'],
                        record['market'],
                        record['timestamp']
                    ))
                    
                    count += 1
                    
                    # 批量插入
                    if len(batch_data) >= batch_size:
                        cursor.executemany('''
                            INSERT INTO stock_quotes (
                                stock_code, stock_name, price, change, change_percent,
                                volume, turnover, status, open_price, high_price,
                                low_price, close_price, market, snapshot_time
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', batch_data)
                        conn.commit()
                        print(f"已处理 {count} 条数据...")
                        batch_data = []
                
                except Exception as e:
                    errors += 1
                    print(f"处理第{row_num}行时出错: {e}")
                    continue
            
            # 插入剩余记录
            if batch_data:
                cursor.executemany('''
                    INSERT INTO stock_quotes (
                        stock_code, stock_name, price, change, change_percent,
                        volume, turnover, status, open_price, high_price,
                        low_price, close_price, market, snapshot_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', batch_data)
                conn.commit()
            
            print(f"\n导入完成!")
            print(f"成功导入: {count} 条记录")
            print(f"跳过错误: {errors} 条记录")
            
            # 显示导入统计
            show_import_statistics(cursor)
            
    except Exception as e:
        print(f"导入过程中发生严重错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def show_import_statistics(cursor):
    """显示导入统计信息"""
    print("\n=== 导入统计信息 ===")
    
    # 总记录数
    cursor.execute("SELECT COUNT(*) FROM stock_quotes")
    total = cursor.fetchone()[0]
    print(f"数据库总记录数: {total}")
    
    # 最新导入时间
    cursor.execute("SELECT snapshot_time FROM stock_quotes ORDER BY id DESC LIMIT 1")
    latest_time = cursor.fetchone()
    if latest_time:
        print(f"最新导入时间: {latest_time[0]}")
    
    # 市场分布
    cursor.execute("SELECT market, COUNT(*) FROM stock_quotes GROUP BY market")
    market_dist = cursor.fetchall()
    print("\n市场分布:")
    for market, count in market_dist:
        print(f"  {market}: {count}只")
    
    # 价格区间统计
    cursor.execute('''
        SELECT 
            SUM(CASE WHEN price >= 100 THEN 1 ELSE 0 END) as high_price,
            SUM(CASE WHEN price >= 10 AND price < 100 THEN 1 ELSE 0 END) as mid_price,
            SUM(CASE WHEN price < 10 THEN 1 ELSE 0 END) as low_price
        FROM stock_quotes
    ''')
    price_dist = cursor.fetchone()
    print("\n价格区间分布:")
    print(f"  高价股(≥100元): {price_dist[0]}")
    print(f"  中价股(10-100元): {price_dist[1]}")
    print(f"  低价股(<10元): {price_dist[2]}")
    
    # 涨跌统计
    cursor.execute('''
        SELECT 
            SUM(CASE WHEN change > 0 THEN 1 ELSE 0 END) as rising,
            SUM(CASE WHEN change < 0 THEN 1 ELSE 0 END) as falling,
            SUM(CASE WHEN change = 0 THEN 1 ELSE 0 END) as flat
        FROM stock_quotes
    ''')
    change_dist = cursor.fetchone()
    print("\n涨跌分布:")
    print(f"  上涨: {change_dist[0]}")
    print(f"  下跌: {change_dist[1]}")
    print(f"  平盘: {change_dist[2]}")

def main():
    print("=== 股票市场数据导入工具 (v2.0) ===")
    print("兼容 generate_stock_list.py 生成的数据格式\n")
    
    # 1. 初始化数据库
    create_database()
    
    # 2. 检查默认数据文件
    if os.path.exists(DEFAULT_DATA_FILE_PATH):
        file_path = DEFAULT_DATA_FILE_PATH
        print(f"检测到默认数据文件: {file_path}")
    else:
        print(f"默认数据文件不存在: {DEFAULT_DATA_FILE_PATH}")
        print("请先运行以下命令生成数据文件:")
        print("  cd /Users/zbf/ws/stock/backend")
        print("  python generate_stock_list.py")
        
        # 询问用户是否指定其他文件
        file_path = input("\n请输入CSV文件路径 (直接回车退出): ").strip()
        if not file_path:
            print("未指定文件，程序退出。")
            return
    
    # 3. 导入数据
    print(f"开始从 {file_path} 导入数据...")
    import_data(file_path)
    
    # 4. 完成
    print("\n=== 导入完成 ===")
    print(f"数据库文件: {DB_PATH}")
    print("\n可以使用以下SQL查询数据库:")
    print("  SELECT * FROM stock_quotes ORDER BY snapshot_time DESC LIMIT 10;")

if __name__ == '__main__':
    main()