import akshare as ak
import pandas as pd
from datetime import datetime
import os
import re

def get_stock_data_and_save_csv():
    """
    获取全市场A股数据，整理为标准格式并保存为CSV文件
    
    修复说明：
    1. 修正股票代码市场后缀的判断逻辑
    2. 统一输出字段名，确保与 import_market_snapshot.py 兼容
    3. 添加数据清洗和验证逻辑
    """
    # 1. 获取A股实时行情数据
    print("正在获取全市场A股数据...")
    try:
        # 使用东方财富数据源（包含全市场、字段全）
        stock_df = ak.stock_zh_a_spot_em()
        print(f"成功获取 {len(stock_df)} 只股票原始数据")
    except Exception as e:
        print(f"获取数据失败：{e}")
        # 尝试备用数据源
        try:
            stock_df = ak.stock_zh_a_spot()
            print(f"备用数据源成功获取 {len(stock_df)} 只股票原始数据")
        except Exception as e2:
            print(f"备用数据源也失败：{e2}")
            return
    
    # 2. 保存原始数据（用于调试）
    raw_filename = f"data/stock_list_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs("data", exist_ok=True)
    stock_df.to_csv(raw_filename, index=False, encoding='utf-8-sig')
    print(f"原始数据已保存到：{raw_filename}")
    
    # 3. 检查数据字段
    print("\n原始数据字段：")
    print(stock_df.columns.tolist())
    
    # 4. 创建标准化的结果DataFrame
    # 字段映射：匹配 import_market_snapshot.py 的期望格式
    # 期望格式：代码, 名称, 当前价, 涨跌额, 涨跌幅%, 成交量, 成交额, 状态, 开盘, 最高, 最低, 收盘, 市场状态, 时间
    
    # 初始化DataFrame
    result_df = pd.DataFrame()
    
    # 提取并处理股票代码
    def add_market_suffix(code):
        """
        根据股票代码数字开头判断市场后缀（更准确的方法）
        
        规则：
        - 沪市主板：6开头
        - 沪市科创板：68开头（注意：688开头的确是科创板，600/601/603等是主板）
        - 沪市B股：900开头
        - 深市主板：000、001、002、003开头
        - 深市中小板：002开头
        - 深市创业板：300、301开头
        - 北交所：43开头、83开头、87开头、832、834等
        """
        if pd.isna(code) or code == '':
            return 'Unknown.Unknown'
        
        code_str = str(code).zfill(6)  # 补全到6位
        prefix = code_str[:3]     # 前3位
        prefix_full = code_str[:2] # 前2位
        
        # 沪市
        if prefix == '688':
            return f"{code_str}.SH"  # 科创板
        elif prefix_full == '60':
            return f"{code_str}.SH"  # 沪市主板（600/601/603/605等）
        elif prefix == '900':
            return f"{code_str}.SH"  # 沪市B股
        
        # 深市
        elif prefix_full in ['00', '30']:
            return f"{code_str}.SZ"  # 深市（00主板，30创业板）
        
        # 北交所
        elif prefix in ['43', '83', '87']:
            return f"{code_str}.BJ"  # 北交所
        
        # 其他情况（包含一些特殊的深市代码如200开头B股）
        elif code_str.startswith('2'):
            return f"{code_str}.SZ"  # 深市（200开头B股）
        
        else:
            print(f"警告：无法识别代码后缀：{code_str}，默认使用.SZ")
            return f"{code_str}.SZ"
    
    # 应用代码后缀逻辑
    result_df['代码'] = stock_df['代码'].apply(add_market_suffix)
    result_df['名称'] = stock_df['名称'].fillna('未知')
    
    # 价格字段映射
    price_mapping = {
        '最新价': '当前价',
        '今开': '开盘',
        '最高': '最高',
        '最低': '最低',
        '昨收': '收盘',
        '涨跌': '涨跌额',
        '涨跌幅': '涨跌幅',
        '成交量': '成交量',
        '成交额': '成交额',
        '总市值': '市值'
    }
    
    # 字段映射并处理
    for old_name, new_name in price_mapping.items():
        if old_name in stock_df.columns:
            if new_name == '当前价' or new_name == '涨跌额' or new_name == '开盘' or new_name == '最高' or new_name == '最低' or new_name == '收盘':
                result_df[new_name] = stock_df[old_name].fillna(0).round(2)
            elif new_name == '涨跌幅':
                # 涨跌幅保持为百分比格式，不需要乘以100（东方财富数据已经带%）
                result_df[new_name] = stock_df[old_name].fillna(0)
                # 确保是浮点数
                try:
                    result_df[new_name] = pd.to_numeric(result_df[new_name].str.replace('%', '').str.replace('nan', '0'), errors='coerce').fillna(0)
                except:
                    result_df[new_name] = 0
            elif new_name in ['成交量', '成交额', '市值']:
                if new_name == '成交量':
                    result_df[new_name] = stock_df[old_name].fillna(0).astype('Int64')
                elif new_name in ['成交额', '市值']:
                    # 成交额单位处理：东方财富的成交额单位是万元，需要转换为元
                    # 市值单位处理：东方财富的市值单位是亿，需要转换为元
                    try:
                        if old_name == '成交额':
                            result_df[new_name] = (stock_df[old_name].fillna(0) * 10000).astype('Int64')
                        elif old_name == '总市值':
                            result_df[new_name] = (stock_df[old_name].fillna(0) * 100000000).astype('Int64')
                    except:
                        result_df[new_name] = 0
        else:
            # 字段不存在，填充默认值
            if new_name == '当前价' or new_name == '涨跌额' or new_name == '开盘' or new_name == '最高' or new_name == '最低' or new_name == '收盘':
                result_df[new_name] = 0.0
            elif new_name == '涨跌幅':
                result_df[new_name] = 0.0
            elif new_name == '成交量':
                result_df[new_name] = 0
            elif new_name in ['成交额', '市值']:
                result_df[new_name] = 0
    
    # 添加状态字段（0表示正常交易）
    result_df['状态'] = 0
    
    # 添加市场状态字段
    def get_market_status(code):
        """根据代码判断市场状态"""
        try:
            market = code.split('.')[1]
            if market == 'SH':
                return '沪市'
            elif market == 'SZ':
                return '深市'
            elif market == 'BJ':
                return '北交所'
            else:
                return '其他'
        except:
            return '其他'
    
    result_df['市场状态'] = result_df['代码'].apply(get_market_status)
    
    # 添加时间戳字段
    result_df['时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 5. 数据清洗和验证
    # 过滤价格异常的数据（价格 <= 0）
    result_df = result_df[result_df['当前价'] > 0]
    
    # 过滤代码异常的数据
    result_df = result_df[result_df['代码'].str.match(r'^\d{6}\.(SH|SZ|BJ)$', na=False)]
    
    # 去重（按代码）
    result_df = result_df.drop_duplicates(subset=['代码'])
    
    # 6. 调整列顺序以匹配导入脚本期望的格式
    column_order = ['代码', '名称', '当前价', '涨跌额', '涨跌幅', '成交量', '成交额', '状态', '开盘', '最高', '最低', '收盘', '市场状态', '时间']
    
    # 确保所有列都存在
    for col in column_order:
        if col not in result_df.columns:
            print(f"警告：列 {col} 不存在，添加默认值")
            if col in ['当前价', '涨跌额', '涨跌幅', '开盘', '最高', '最低', '收盘']:
                result_df[col] = 0.0
            elif col == '成交量':
                result_df[col] = 0
            elif col == '成交额':
                result_df[col] = 0
            elif col == '状态':
                result_df[col] = 0
            else:
                result_df[col] = ''
    
    result_df = result_df[column_order]
    
    # 7. 保存为CSV文件（UTF-8-BOM编码，Excel兼容）
    csv_filename = "data/stock_list.csv"
    result_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    
    print(f"\n数据已成功保存！文件名称：{csv_filename}")
    print(f"共获取 {len(result_df)} 只A股数据（过滤后）")
    
    # 8. 数据统计和验证
    print(f"\n=== 数据统计与验证 ===")
    
    # 代码后缀统计
    print("\n市场分布（按代码后缀）：")
    suffix_counts = result_df['代码'].apply(lambda x: x.split('.')[1] if '.' in x else '').value_counts()
    for suffix, count in suffix_counts.items():
        print(f"  {suffix}: {count}只")
    
    # 市场状态统计
    print("\n市场状态分布：")
    market_counts = result_df['市场状态'].value_counts()
    for market, count in market_counts.items():
        print(f"  {market}: {count}只")
    
    # 价格区间统计
    print("\n价格区间分布：")
    price_ranges = [
        (0, 10, '0-10元'),
        (10, 50, '10-50元'),
        (50, 100, '50-100元'),
        (100, float('inf'), '>100元')
    ]
    for min_p, max_p, label in price_ranges:
        count = len(result_df[(result_df['当前价'] >= min_p) & (result_df['当前价'] < max_p)])
        print(f"  {label}: {count}只")
    
    # 涨跌分布
    print("\n涨跌分布：")
    rising = len(result_df[result_df['涨跌额'] > 0])
    falling = len(result_df[result_df['涨跌额'] < 0])
    flat = len(result_df[result_df['涨跌额'] == 0])
    print(f"  上涨: {rising}只")
    print(f"  下跌: {falling}只")
    print(f"  平盘: {flat}只")
    
    # 9. 样本数据展示
    print("\n=== 数据样本（前5条）===")
    print(result_df.head().to_string(index=False))
    
    print("\n=== 数据样本（最后3条）===")
    print(result_df.tail(3).to_string(index=False))
    
    # 10. 数据质量检查
    print("\n=== 数据质量检查 ===")
    
    # 检查缺失值
    missing_values = result_df.isnull().sum()
    if missing_values.sum() > 0:
        print("警告：发现缺失值：")
        print(missing_values[missing_values > 0])
    else:
        print("✓ 无缺失值")
    
    # 检查异常值
    abnormal_codes = result_df[~result_df['代码'].str.match(r'^\d{6}\.(SH|SZ|BJ)$', na=False)]
    if len(abnormal_codes) > 0:
        print(f"警告：发现 {len(abnormal_codes)} 个异常代码格式：")
        print(abnormal_codes['代码'].head(10).tolist())
    else:
        print("✓ 代码格式正确")
    
    # 检查价格异常
    abnormal_prices = result_df[(result_df['当前价'] <= 0) | (result_df['当前价'] > 1000)]
    if len(abnormal_prices) > 0:
        print(f"警告：发现 {len(abnormal_prices)} 个异常价格（<=0 或 >1000）：")
        print(abnormal_prices[['代码', '名称', '当前价']].head(10).to_string(index=False))
    else:
        print("✓ 价格范围正常")
    
    print("\n=== 处理完成 ===")
    print(f"✓ 数据文件已保存：{csv_filename}")
    print("✓ 文件格式已标准化，可直接用于导入")
    
    return result_df

if __name__ == "__main__":
    # 执行主函数
    df = get_stock_data_and_save_csv()