#!/bin/bash

# 统一停止脚本 - 停止前后端服务

set -e

echo "======================================"
echo "  停止股票量化交易平台"
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

# 函数：停止后端服务
stop_backend() {
    echo -e "${YELLOW}[1/2] 停止后端服务...${NC}"
    
    # 从PID文件读取
    if [ -f "$BACKEND_PID_FILE" ]; then
        PID=$(cat $BACKEND_PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID 2>/dev/null || true
            sleep 1
            # 强制杀死
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID 2>/dev/null || true
            fi
            echo -e "${GREEN}✓ 后端服务已停止 (PID: $PID)${NC}"
        else
            echo -e "${YELLOW}后端服务未运行${NC}"
        fi
        rm -f $BACKEND_PID_FILE
    else
        echo -e "${YELLOW}后端PID文件不存在${NC}"
    fi
    
    # 清理端口
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
}

# 函数：停止前端服务
stop_frontend() {
    echo -e "${YELLOW}[2/2] 停止前端服务...${NC}"
    
    # 从PID文件读取
    if [ -f "$FRONTEND_PID_FILE" ]; then
        PID=$(cat $FRONTEND_PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID 2>/dev/null || true
            sleep 1
            # 强制杀死
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID 2>/dev/null || true
            fi
            echo -e "${GREEN}✓ 前端服务已停止 (PID: $PID)${NC}"
        else
            echo -e "${YELLOW}前端服务未运行${NC}"
        fi
        rm -f $FRONTEND_PID_FILE
    else
        echo -e "${YELLOW}前端PID文件不存在${NC}"
    fi
    
    # 清理端口
    lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
}

# 主函数
main() {
    stop_backend
    stop_frontend
    
    echo ""
    echo "======================================"
    echo -e "${GREEN}  ✓ 所有服务已停止${NC}"
    echo "======================================"
    echo ""
    echo "日志文件："
    echo -e "  ${BLUE}后端日志:${NC}  logs/backend.log"
    echo -e "  ${BLUE}前端日志:${NC}  logs/frontend.log"
    echo ""
    echo "重新启动服务："
    echo -e "  ${GREEN}./start_app.sh${NC}"
    echo ""
    echo "======================================"
}

# 执行主函数
main