#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtrader 量化交易框架启动脚本
提供多种运行模式
"""

import sys
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

def setup_chinese_font():
    """根据操作系统设置合适的中文字体"""
    system = platform.system()
    
    if system == "Windows":
        # Windows系统使用SimHei字体
        font_name = 'SimHei'
    elif system == "Darwin":  # macOS
        # macOS系统使用PingFang SC字体
        font_name = 'PingFang SC'
    else:  # Linux或其他系统
        # 尝试使用常见的中文字体
        font_name = 'DejaVu Sans'
    
    # 检查字体是否可用
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    if font_name in available_fonts:
        plt.rcParams['font.family'] = font_name
        print(f"使用字体: {font_name}")
    else:
        # 如果指定字体不可用，尝试其他中文字体
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', 'WenQuanYi Micro Hei', 'DejaVu Sans']
        
        for font in chinese_fonts:
            if font in available_fonts:
                plt.rcParams['font.family'] = font
                print(f"使用备用字体: {font}")
                break
        else:
            # 如果所有中文字体都不可用，使用默认字体
            plt.rcParams['font.family'] = 'DejaVu Sans'
            print("警告: 未找到合适的中文字体，使用默认字体")
    
    # 设置负号显示
    plt.rcParams['axes.unicode_minus'] = False



def setup_environment():
    """设置环境"""
    # 添加当前目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    
    setup_chinese_font()

def run_simple_test():
    """运行简化测试（使用模拟数据）"""
    print("=== 运行简化测试 ===")
    from test_simple import run_backtest
    run_backtest()

def run_real_data_test():
    """运行真实数据测试"""
    print("=== 运行真实数据测试 ===")
    try:
        from main import main
        main()
    except Exception as e:
        print(f"真实数据测试失败: {e}")
        print("建议先运行简化测试验证框架功能")

def run_single_strategy():
    """运行单策略测试"""
    print("=== 运行单策略测试 ===")
    try:
        from main import run_single_strategy
        run_single_strategy()
    except Exception as e:
        print(f"单策略测试失败: {e}")
        print("建议先运行简化测试验证框架功能")

def show_menu():
    """显示菜单"""
    print("\n" + "="*50)
    print("Backtrader 量化交易框架")
    print("="*50)
    print("1. 简化测试 (使用模拟数据)")
    print("2. 真实数据测试 (需要网络连接)")
    print("3. 单策略测试")
    print("4. 查看帮助")
    print("5. 退出")
    print("="*50)

def show_help():
    """显示帮助信息"""
    print("\n" + "="*60)
    print("Backtrader 量化交易框架使用说明")
    print("="*60)
    print("""
1. 简化测试 (推荐首次使用)
   - 使用模拟数据进行测试
   - 验证框架基本功能
   - 无需网络连接

2. 真实数据测试
   - 使用 akshare 获取真实股票数据
   - 运行多个策略对比
   - 需要网络连接

3. 单策略测试
   - 运行单个策略的详细回测
   - 显示交易信号和图表
   - 需要网络连接

支持的策略:
- 移动平均策略 (MA)
- 双均线策略 (DualMA)
- RSI 策略
- MACD 策略
- 布林带策略 (BOLL)
- KDJ 策略
- 均值回归策略
- 网格交易策略

文件结构:
- main.py: 主程序
- backtest_engine.py: 回测引擎
- strategies.py: 策略定义
- data_feed.py: 数据源集成
- test_simple.py: 简化测试
- run_backtrader.py: 启动脚本

注意事项:
- 首次使用建议选择"简化测试"
- 真实数据测试需要网络连接
- 回测结果仅供参考，不构成投资建议
    """)

def main():
    """主函数"""
    setup_environment()
    
    while True:
        show_menu()
        try:
            choice = input("\n请选择操作 (1-5): ").strip()
            
            if choice == '1':
                run_simple_test()
            elif choice == '2':
                run_real_data_test()
            elif choice == '3':
                run_single_strategy()
            elif choice == '4':
                show_help()
            elif choice == '5':
                print("感谢使用 Backtrader 量化交易框架！")
                break
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")
            print("请检查环境配置或联系技术支持")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()
