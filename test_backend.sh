#!/bin/bash

echo "=================================="
echo "  启动后端服务（测试模式）"
echo "=================================="

cd backend

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

# 安装依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 启动后端服务
echo "🚀 启动后端服务..."
python3 main.py &
BACKEND_PID=$!

echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo "🌐 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待后端进程
wait $BACKEND_PID