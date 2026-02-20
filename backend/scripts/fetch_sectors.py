#!/usr/bin/env python3
"""
从公开渠道获取板块数据并保存到CSV文件
"""
import pandas as pd
import csv
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
import akshare as ak
from data_adapters.tushare_adapter import TushareAdapter
from core.config import settings


def fetch_sectors_from_akshare():
    """
    从AkShare获取板块数据
    """
    logger.info("从AkShare获取板块数据...")
    
    try:
        sectors = []
        
        # 获取行业板块
        try:
            industry_df = ak.stock_board_industry_name_em()
            if industry_df is not None and not industry_df.empty:
                logger.info(f"获取到 {len(industry_df)} 个行业板块")
                for _, row in industry_df.iterrows():
                    sectors.append({
                        'code': row.get('板块代码', row.get('板块名称', '')),  # 使用板块代码作为code
                        'name': row.get('板块名称', ''),
                        'type': 'industry',
                        'market': 'A股',
                        'description': f"行业板块"
                    })
        except Exception as e:
            logger.warning(f"从AkShare获取行业板块失败: {e}")
        
        # 获取概念板块
        try:
            concept_df = ak.stock_board_concept_name_em()
            if concept_df is not None and not concept_df.empty:
                logger.info(f"获取到 {len(concept_df)} 个概念板块")
                for _, row in concept_df.iterrows():
                    sectors.append({
                        'code': row.get('板块代码', row.get('板块名称', '')),  # 使用板块代码作为code
                        'name': row.get('板块名称', ''),
                        'type': 'concept',
                        'market': 'A股',
                        'description': f"概念板块"
                    })
        except Exception as e:
            logger.warning(f"从AkShare获取概念板块失败: {e}")
        
        return sectors
        
    except Exception as e:
        logger.error(f"从AkShare获取板块数据失败: {e}")
        return []


def fetch_sectors_from_tushare():
    """
    从Tushare获取板块数据
    """
    logger.info("从Tushare获取板块数据...")
    
    try:
        adapter = TushareAdapter(token=getattr(settings, 'TUSHARE_TOKEN', None))
        sectors = []
        
        # 获取行业分类
        try:
            df = adapter.pro.index_classify(level='L1', src='SW2021')
            if df is not None and not df.empty:
                logger.info(f"获取到 {len(df)} 个申万行业分类")
                for _, row in df.iterrows():
                    sectors.append({
                        'code': row.get('index_name', ''),
                        'name': row.get('index_name', ''),
                        'type': 'industry',
                        'market': '申万',
                        'description': f"申万一级行业"
                    })
        except Exception as e:
            logger.warning(f"从Tushare获取行业分类失败: {e}")
        
        return sectors
        
    except Exception as e:
        logger.error(f"从Tushare获取板块数据失败: {e}")
        return []


def save_sectors_to_csv(sectors, filepath='data/sectors.csv'):
    """
    将板块数据保存到CSV文件
    
    Args:
        sectors: 板块数据列表
        filepath: CSV文件路径
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 去重（基于板块名称）
        unique_sectors = {}
        for sector in sectors:
            key = sector['name']
            if key not in unique_sectors:
                unique_sectors[key] = sector
        
        unique_sectors_list = list(unique_sectors.values())
        
        # 保存到CSV
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['code', 'name', 'type', 'market', 'description']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_sectors_list)
        
        logger.info(f"成功保存 {len(unique_sectors_list)} 个板块到 {filepath}")
        
        # 同时保存为Excel文件，方便查看
        df = pd.DataFrame(unique_sectors_list)
        excel_path = filepath.replace('.csv', '.xlsx')
        df.to_excel(excel_path, index=False, engine='openpyxl')
        logger.info(f"成功保存板块数据到 {excel_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"保存板块数据到CSV失败: {e}")
        return False


def load_sectors_from_csv(filepath='data/sectors.csv'):
    """
    从CSV文件加载板块数据
    
    Args:
        filepath: CSV文件路径
    
    Returns:
        板块数据列表
    """
    try:
        if not os.path.exists(filepath):
            logger.warning(f"板块数据文件不存在: {filepath}")
            return []
        
        sectors = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sectors.append(row)
        
        logger.info(f"从 {filepath} 加载了 {len(sectors)} 个板块")
        return sectors
        
    except Exception as e:
        logger.error(f"从CSV加载板块数据失败: {e}")
        return []


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始获取板块数据")
    logger.info("=" * 60)
    
    all_sectors = []
    
    # 1. 从AkShare获取板块数据
    akshare_sectors = fetch_sectors_from_akshare()
    all_sectors.extend(akshare_sectors)
    
    # 2. 从Tushare获取板块数据（如果配置了token）
    tushare_token = getattr(settings, 'TUSHARE_TOKEN', None)
    if tushare_token:
        tushare_sectors = fetch_sectors_from_tushare()
        all_sectors.extend(tushare_sectors)
    
    if not all_sectors:
        logger.error("未能获取到任何板块数据")
        return
    
    # 3. 保存到CSV文件
    success = save_sectors_to_csv(all_sectors)
    
    if success:
        logger.info("=" * 60)
        logger.info("板块数据获取完成！")
        logger.info(f"总计: {len(all_sectors)} 个板块")
        logger.info("数据已保存到: data/sectors.csv 和 data/sectors.xlsx")
        logger.info("=" * 60)
    else:
        logger.error("保存板块数据失败")


if __name__ == '__main__':
    main()