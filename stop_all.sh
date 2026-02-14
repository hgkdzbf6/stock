#!/bin/bash

################################################################################
# 量化交易平台 - 停止脚本
################################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo "=================================="
    echo "  $1"
    echo "=================================="
    echo ""
}

################################################################################
# 主流程
################################################################################

print_header "量化交易平台 - 停止服务"

# 1. 停止后端
print_info "停止后端服务..."
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        print_success "后端服务已停止 (PID: $BACKEND_PID)"
    else
        print_warning "后端进程不存在 (PID: $BACKEND_PID)"
    fi
    rm backend.pid
else
    # 通过进程名查找
    pkill -f "python.*main.py" && print_success "后端服务已停止" || print_warning "后端服务未运行"
fi

# 2. 停止前端
print_info "停止前端服务..."
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        print_success "前端服务已停止 (PID: $FRONTEND_PID)"
    else
        print_warning "前端进程不存在 (PID: $FRONTEND_PID)"
    fi
    rm frontend.pid
else
    # 通过进程名查找
    pkill -f "vite.*--port" && print_success "前端服务已停止" || print_warning "前端服务未运行"
fi

# 3. 等待进程完全停止
print_info "等待进程完全停止..."
sleep 2

# 4. 检查是否还有残留进程
print_info "检查残留进程..."
REMAINING_BACKEND=$(ps aux | grep "python.*main.py" | grep -v grep || echo "")
REMAINING_FRONTEND=$(ps aux | grep "vite.*--port" | grep -v grep || echo "")

if [ -n "$REMAINING_BACKEND" ]; then
    print_warning "发现残留的后端进程，强制停止..."
    pkill -9 -f "python.*main.py"
fi

if [ -n "$REMAINING_FRONTEND" ]; then
    print_warning "发现残留的前端进程，强制停止..."
    pkill -9 -f "vite.*--port"
fi

# 5. 显示停止结果
print_header "✅ 服务已停止"

print_info "进程状态检查："
if ps aux | grep "python.*main.py" | grep -v grep > /dev/null; then
    print_error "后端服务仍在运行"
else
    print_success "后端服务已完全停止"
fi

if ps aux | grep "vite.*--port" | grep -v grep > /dev/null; then
    print_error "前端服务仍在运行"
else
    print_success "前端服务已完全停止"
fi

echo ""
print_info "日志文件已保留："
echo "   - logs/backend.log"
echo "   - logs/frontend.log"
echo ""
print_info "如需重新启动，请运行: ./start_all.sh"
echo ""