#!/bin/bash

echo "=================================="
echo "  量化交易平台 - 启动脚本"
echo "=================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建.env文件..."
    cp .env.example .env
    echo "✅ .env文件已创建"
    echo "⚠️  请根据需要修改.env文件中的配置"
fi

# 构建并启动服务
echo "🚀 构建并启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 显示服务状态
echo ""
echo "📊 服务状态："
docker-compose ps

echo ""
echo "=================================="
echo "✅ 服务启动完成！"
echo "=================================="
echo ""
echo "🌐 访问地址："
echo "   前端应用: http://localhost:3000"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"
echo ""
echo "📝 常用命令："
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo "=================================="
