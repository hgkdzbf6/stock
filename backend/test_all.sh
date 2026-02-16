#!/bin/bash
# 完整测试脚本 - 启动前运行所有测试

echo "========================================"
echo "  DuckDB存储系统完整测试"
echo "========================================"
echo ""

# 1. 测试DuckDB存储服务
echo "1️⃣ 测试DuckDB存储服务..."
python test_duckdb_storage.py
if [ $? -ne 0 ]; then
    echo "❌ DuckDB存储服务测试失败"
    exit 1
fi
echo "✅ DuckDB存储服务测试通过"
echo ""

# 2. 测试数据下载服务
echo "2️⃣ 测试数据下载服务..."
python test_data_download_service.py
if [ $? -ne 0 ]; then
    echo "❌ 数据下载服务测试失败"
    exit 1
fi
echo "✅ 数据下载服务测试通过"
echo ""

# 3. 测试集成功能
echo "3️⃣ 测试集成功能..."
python test_duckdb.py
if [ $? -ne 0 ]; then
    echo "❌ 集成测试失败"
    exit 1
fi
echo "✅ 集成测试通过"
echo ""

echo "========================================"
echo "  ✅ 所有测试通过！"
echo "========================================"