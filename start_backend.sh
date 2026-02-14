#!/bin/bash

echo "=================================="
echo "  量化交易平台 - 快速启动"
echo "=================================="
echo ""

# 检查Python
if ! command -v python &> /dev/null; then
    echo "❌ Python未安装"
    exit 1
fi

echo "✅ Python版本: $(python --version)"
echo ""

# 检查后端依赖
cd backend
echo "检查后端依赖..."
python -c "import fastapi; import uvicorn; import sqlalchemy; print('✅ 依赖已安装')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⏳ 安装后端依赖..."
    pip install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ 依赖安装完成"
    else
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

echo ""
echo "=================================="
echo "  启动后端服务..."
echo "=================================="
echo ""

# 启动后端
python -c "
import sys
sys.path.insert(0, '.')
from main import app
print('✅ 后端服务准备启动')
print('📡 API地址: http://localhost:8000')
print('📚 API文档: http://localhost:8000/docs')
print()
"

echo "启动命令："
echo "  方式1: uvicorn main:app --reload"
echo "  方式2: python main.py"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""
echo "=================================="
