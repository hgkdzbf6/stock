import pandas as pd
import random
from datetime import datetime, timedelta
import os
import json

def generate_test_stock_data(num_stocks=1000):
    """
    生成测试用的股票数据
    模拟真实的市场数据分布
    """
    print(f"正在生成 {num_stocks} 只股票的测试数据...")
    
    # 市场分布配置
    markets = {
        'SH': 0.30,  # 沪市 30%
        'SZ': 0.65,  # 深市 65%
        'BJ': 0.05   # 北交所 5%
    }
    
    # 价格区间配置
    price_ranges = [
        (0, 5, 0.10),    # 10% 的股票价格在 0-5 元
        (5, 10, 0.20),   # 20% 的股票价格在 5-10 元
        (10, 50, 0.40),  # 40% 的股票价格在 10-50 元
        (50, 100, 0.20), # 20% 的股票价格在 50-100 元
        (100, 500, 0.09), # 9% 的股票价格在 100-500 元
        (500, 1000, 0.01)  # 1% 的股票价格在 500-1000 元
    ]
    
    data = []
    
    # 生成随机股票数据
    for i in range(num_stocks):
        # 随机选择市场
        rand_market = random.random()
        market = 'SZ'
        cumulative = 0
        for m, prob in markets.items():
            cumulative += prob
            if rand_market <= cumulative:
                market = m
                break
        
        # 生成股票代码
        if market == 'SH':
            # 沪市主板 (600-605) 70%, 科创板 (688) 30%
            if random.random() < 0.7:
                prefix = random.choice(['600', '601', '603', '605'])
            else:
                prefix = '688'
            code = f"{prefix}{random.randint(0, 999):03d}.SH"
        elif market == 'SZ':
            # 深市主板 (000-002) 40%, 创业板 (300) 60%
            if random.random() < 0.4:
                prefix = random.choice(['000', '001', '002', '003'])
            else:
                prefix = '300'
            code = f"{prefix}{random.randint(0, 999):03d}.SZ"
        else:  # BJ
            # 北交所 (43, 83, 87, 43, 83, 87 等，6位数字)
            prefix = random.choice(['43', '83', '87'])
            suffix = random.randint(0, 9999)
            code = f"{prefix}{suffix:04d}.BJ"
        
        # 生成股票名称
        stock_types = ['科技', '生物', '制药', '能源', '地产', '金融', '制造', '电子', '化工', '材料']
        stock_suffixes = ['股份', '集团', '控股', '有限', '实业', '投资', '发展', '建设', '国际', '科技']
        
        stock_type = random.choice(stock_types)
        stock_suffix = random.choice(stock_suffixes)
        stock_name = f"{stock_type}{stock_suffix}"
        
        # 生成价格
        rand_price = random.random()
        price = 0
        cumulative = 0
        for min_p, max_p, prob in price_ranges:
            cumulative += prob
            if rand_price <= cumulative:
                price = random.uniform(min_p, max_p)
                break
        
        # 生成涨跌额和涨跌幅
        change_percent = random.uniform(-10, 10)  # -10% 到 +10%
        change_amount = price * change_percent / 100
        
        # 生成成交量 (手，1手=100股）
        volume = random.randint(1000, 10000000) * 100  # 股数
        
        # 生成成交额 (元)
        turnover = price * volume
        
        # 生成开高低收价格
        # 当前价作为基准
        current_price = price
        
        # 涨跌方向决定开高低收
        if change_percent > 0:
            # 上涨：昨收 < 当前价
            close_price = current_price - change_amount
            open_price = random.uniform(close_price, current_price)
            high_price = max(open_price, current_price)
            low_price = min(close_price, current_price)
        elif change_percent < 0:
            # 下跌：昨收 > 当前价
            close_price = current_price - change_amount
            open_price = random.uniform(current_price, close_price)
            high_price = max(open_price, close_price)
            low_price = min(current_price, close_price)
        else:
            # 平盘
            close_price = current_price
            open_price = random.uniform(current_price * 0.995, current_price * 1.005)
            high_price = max(open_price, close_price, current_price)
            low_price = min(open_price, close_price, current_price)
        
        # 确保价格逻辑合理
        high_price = max(high_price, open_price, close_price, current_price)
        low_price = min(low_price, open_price, close_price, current_price)
        
        # 生成市场状态
        market_status = '沪市' if market == 'SH' else ('深市' if market == 'SZ' else '北交所')
        
        # 生成时间戳（当前时间）
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        data.append({
            '代码': code,
            '名称': stock_name,
            '当前价': round(current_price, 2),
            '涨跌额': round(change_amount, 2),
            '涨跌幅': round(change_percent, 2),
            '成交量': volume,
            '成交额': round(turnover, 2),
            '状态': 0,  # 0 表示正常交易
            '开盘': round(open_price, 2),
            '最高': round(high_price, 2),
            '最低': round(low_price, 2),
            '收盘': round(close_price, 2),
            '市场状态': market_status,
            '时间': timestamp
        })
    
    # 转换为 DataFrame
    df = pd.DataFrame(data)
    
    # 列顺序
    column_order = ['代码', '名称', '当前价', '涨跌额', '涨跌幅', '成交量', '成交额', 
                   '状态', '开盘', '最高', '最低', '收盘', '市场状态', '时间']
    df = df[column_order]
    
    return df

def save_test_data(df, filename='stock_list.csv'):
    """保存测试数据到 CSV 文件"""
    # 确保数据目录存在
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    file_path = os.path.join(data_dir, filename)
    
    # 保存为 UTF-8-BOM 编码的 CSV 文件
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    return file_path

def generate_sample_stocks():
    """生成一些知名的样本股票数据"""
    # 知名股票列表（包含代码、名称）
    sample_stocks = [
        ('600519.SH', '贵州茅台', 1650.0),
        ('000858.SZ', '五 粮 液', 105.0),
        ('000001.SZ', '平安银行', 10.9),
        ('600036.SH', '招商银行', 32.5),
        ('601318.SH', '中国平安', 48.5),
        ('000002.SZ', '万 科Ａ', 4.97),
        ('600900.SH', '长江电力', 28.5),
        ('601888.SH', '中国神华', 43.5),
        ('600030.SH', '中信证券', 22.5),
        ('000725.SZ', '京东方Ａ', 4.18),
        ('002415.SZ', '海康威视', 32.38),
        ('300059.SZ', '东方财富', 25.5),
        ('688981.SH', '中芯国际', 116.93),
        ('600276.SH', '恒瑞医药', 58.5),
        ('000568.SZ', '泸州老窖', 116.25),
        ('002594.SZ', '比亚迪', 90.27),
        ('601012.SH', '隆基绿能', 21.5),
        ('300750.SZ', '宁德时代', 165.5),
        ('000858.SZ', '五 粮 液', 105.0),
        ('600690.SH', '海尔智家', 30.5),
    ]
    
    data = []
    base_time = datetime.now()
    
    for code, name, base_price in sample_stocks:
        # 为每个样本股票生成随机的涨跌
        change_percent = random.uniform(-8, 8)
        change_amount = base_price * change_percent / 100
        current_price = base_price + change_amount
        
        # 生成成交量
        volume = random.randint(500000, 50000000) * 100  # 股数
        
        # 生成成交额
        turnover = current_price * volume
        
        # 生成开高低收
        if change_percent > 0:
            close_price = base_price
            open_price = random.uniform(base_price, current_price)
            high_price = max(open_price, current_price)
            low_price = min(base_price, current_price)
        elif change_percent < 0:
            close_price = base_price
            open_price = random.uniform(current_price, base_price)
            high_price = max(open_price, close_price)
            low_price = min(current_price, close_price)
        else:
            close_price = base_price
            open_price = random.uniform(base_price * 0.995, base_price * 1.005)
            high_price = max(open_price, close_price, base_price)
            low_price = min(open_price, close_price, base_price)
        
        # 判断市场
        if '.SH' in code:
            market_status = '沪市'
        elif '.SZ' in code:
            market_status = '深市'
        else:
            market_status = '其他'
        
        # 生成时间戳（稍微有些变化以模拟实时）
        random_seconds = random.randint(0, 300)
        timestamp = (base_time - timedelta(seconds=random_seconds)).strftime('%Y-%m-%d %H:%M:%S')
        
        data.append({
            '代码': code,
            '名称': name,
            '当前价': round(current_price, 2),
            '涨跌额': round(change_amount, 2),
            '涨跌幅': round(change_percent, 2),
            '成交量': volume,
            '成交额': round(turnover, 2),
            '状态': 0,
            '开盘': round(open_price, 2),
            '最高': round(high_price, 2),
            '最低': round(low_price, 2),
            '收盘': round(close_price, 2),
            '市场状态': market_status,
            '时间': timestamp
        })
    
    # 转换为 DataFrame
    df = pd.DataFrame(data)
    
    # 列顺序
    column_order = ['代码', '名称', '当前价', '涨跌额', '涨跌幅', '成交量', '成交额', 
                   '状态', '开盘', '最高', '最低', '收盘', '市场状态', '时间']
    df = df[column_order]
    
    return df

def main():
    print("=== 测试数据生成器 ===\n")
    
    # 1. 生成随机测试数据
    print("步骤 1: 生成随机市场数据...")
    random_df = generate_test_stock_data(num_stocks=500)
    print(f"生成 {len(random_df)} 只随机股票数据")
    
    # 2. 生成样本数据（知名股票）
    print("\n步骤 2: 生成知名股票样本数据...")
    sample_df = generate_sample_stocks()
    print(f"生成 {len(sample_df)} 只知名股票数据")
    
    # 3. 合并数据
    print("\n步骤 3: 合并数据...")
    combined_df = pd.concat([sample_df, random_df], ignore_index=True)
    print(f"总共生成 {len(combined_df)} 只股票数据")
    
    # 4. 保存数据
    print("\n步骤 4: 保存数据文件...")
    file_path = save_test_data(combined_df)
    print(f"数据已保存到: {file_path}")
    
    # 5. 显示数据统计
    print("\n=== 数据统计 ===")
    print(f"总股票数: {len(combined_df)}")
    
    # 市场分布
    print("\n市场分布:")
    market_dist = combined_df['代码'].apply(lambda x: x.split('.')[1]).value_counts()
    for market, count in market_dist.items():
        print(f"  {market}: {count}只")
    
    # 价格分布
    print("\n价格分布:")
    price_ranges = [
        (0, 10, '0-10元'),
        (10, 50, '10-50元'),
        (50, 100, '50-100元'),
        (100, float('inf'), '>100元')
    ]
    for min_p, max_p, label in price_ranges:
        count = len(combined_df[(combined_df['当前价'] >= min_p) & (combined_df['当前价'] < max_p)])
        print(f"  {label}: {count}只")
    
    # 涨跌分布
    print("\n涨跌分布:")
    rising = len(combined_df[combined_df['涨跌额'] > 0])
    falling = len(combined_df[combined_df['涨跌额'] < 0])
    flat = len(combined_df[combined_df['涨跌额'] == 0])
    print(f"  上涨: {rising}只")
    print(f"  下跌: {falling}只")
    print(f"  平盘: {flat}只")
    
    # 6. 显示数据样本
    print("\n=== 数据样本 (前10条) ===")
    print(combined_df.head(10).to_string(index=False))
    
    print("\n=== 数据样本 (最后5条) ===")
    print(combined_df.tail(5).to_string(index=False))
    
    # 7. 数据验证
    print("\n=== 数据验证 ===")
    # 验证必填字段
    required_fields = ['代码', '名称', '当前价', '涨跌额', '涨跌幅', '成交量', '成交额']
    missing_fields = []
    for field in required_fields:
        if field not in combined_df.columns:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"警告: 缺少必填字段: {missing_fields}")
    else:
        print("✓ 所有必填字段都存在")
    
    # 验证代码格式
    invalid_codes = combined_df[~combined_df['代码'].str.match(r'^\d{6}\.(SH|SZ|BJ)$', na=False)]
    if len(invalid_codes) > 0:
        print(f"警告: 发现 {len(invalid_codes)} 个无效代码格式")
        print(invalid_codes['代码'].head(10).tolist())
    else:
        print("✓ 所有代码格式都正确")
    
    # 验证价格范围
    invalid_prices = combined_df[(combined_df['当前价'] <= 0) | (combined_df['当前价'] > 10000)]
    if len(invalid_prices) > 0:
        print(f"警告: 发现 {len(invalid_prices)} 个无效价格")
        print(invalid_prices[['代码', '名称', '当前价']].head(10).to_string(index=False))
    else:
        print("✓ 所有价格都在合理范围内")
    
    print("\n=== 生成完成 ===")
    print(f"✓ 测试数据文件: {file_path}")
    print("✓ 可以运行导入脚本将数据导入数据库")
    print(f"✓ 导入命令: cd /Users/zbf/ws/stock/scripts && python import_market_snapshot.py")

if __name__ == '__main__':
    main()