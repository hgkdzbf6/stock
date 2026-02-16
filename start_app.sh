#!/bin/bash

# 统一启动脚本 - 同时启动前后端服务

set -e

echo "======================================"
echo "  股票量化交易平台 - 统一启动"
echo "======================================"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 端口定义
BACKEND_PORT=8000
FRONTEND_PORT=3000

# PID文件
BACKEND_PID_FILE=".backend.pid"
FRONTEND_PID_FILE=".frontend.pid"

# 函数：清理端口占用
cleanup_ports() {
    echo -e "${YELLOW}[1/4] 清理端口占用...${NC}"
    
    # 清理后端端口
    if lsof -ti:$BACKEND_PORT > /dev/null 2>&1; then
        echo "清理后端端口 $BACKEND_PORT..."
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    fi
    
    # 清理前端端口
    if lsof -ti:$FRONTEND_PORT > /dev/null 2>&1; then
        echo "清理前端端口 $FRONTEND_PORT..."
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓ 端口清理完成${NC}"
}

# 函数：启动后端服务
start_backend() {
    echo -e "${YELLOW}[2/4] 启动后端服务...${NC}"
    
    # 检查后端依赖
    if [ ! -d "backend/venv" ]; then
        echo "创建Python虚拟环境..."
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd ..
    fi
    
    # 启动后端
    cd backend
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    nohup python main.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../$BACKEND_PID_FILE
    
    cd ..
    
    echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID, 端口: $BACKEND_PORT)${NC}"
}

# 函数：启动前端服务
start_frontend() {
    echo -e "${YELLOW}[3/4] 启动前端服务...${NC}"
    
    # 检查前端依赖
    if [ ! -d "frontend/node_modules" ]; then
        echo "安装前端依赖..."
        cd frontend
        npm install
        cd ..
    fi
    
    # 启动前端
    cd frontend
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../$FRONTEND_PID_FILE
    cd ..
    
    echo -e "${GREEN}✓ 前端服务已启动 (PID: $FRONTEND_PID, 端口: $FRONTEND_PORT)${NC}"
}

# 函数：等待服务启动
wait_for_services() {
    echo -e "${YELLOW}[4/4] 等待服务启动...${NC}"
    
    # 等待后端服务
    echo "等待后端服务..."
    for i in {1..30}; do
        if curl -s http://localhost:$BACKEND_PORT > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 后端服务就绪${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}✗ 后端服务启动超时${NC}"
            echo "请查看日志: tail -f logs/backend.log"
            exit 1
        fi
        sleep 1
    done
    
    # 等待前端服务
    echo "等待前端服务..."
    for i in {1..30}; do
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 前端服务就绪${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}✗ 前端服务启动超时${NC}"
            echo "请查看日志: tail -f logs/frontend.log"
            exit 1
        fi
        sleep 1
    done
}

# 函数：显示访问信息
show_info() {
    echo ""
    echo "======================================"
    echo -e "${GREEN}  ✓ 所有服务已成功启动！${NC}"
    echo "======================================"
    echo ""
    echo "服务访问地址："
    echo -e "  ${BLUE}前端应用:${NC}  http://localhost:$FRONTEND_PORT"
    echo -e "  ${BLUE}后端API:${NC}   http://localhost:$BACKEND_PORT"
    echo -e "  ${BLUE}API文档:${NC}   http://localhost:$BACKEND_PORT/docs"
    echo ""
    echo "数据下载页面："
    echo -e "  ${BLUE}http://localhost:$FRONTEND_PORT/data-download${NC}"
    echo ""
    echo "管理命令："
    echo -e "  ${GREEN}停止所有服务:${NC}  ./stop_app.sh"
    echo -e "  ${GREEN}查看后端日志:${NC}  tail -f logs/backend.log"
    echo -e "  ${GREEN}查看前端日志:${NC}  tail -f logs/frontend.log"
    echo ""
    echo "======================================"
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p logs
    
    # 执行启动流程
    cleanup_ports
    start_backend
    sleep 2  # 等待后端初始化
    start_frontend
    wait_for_services
    show_info
}

# 捕获退出信号
trap 'echo "启动被中断"; exit 1' INT TERM

# 执行主函数
main