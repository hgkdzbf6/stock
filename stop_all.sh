#!/bin/bash

################################################################################
# 量化交易平台 - 停止服务脚本（含端口清理功能）
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

# 端口定义
BACKEND_PORT=8000
FRONTEND_PORT=3000

################################################################################
# 主流程
################################################################################

print_header "量化交易平台 - 停止服务"

# 1. 检查端口占用情况
print_info "检查端口占用情况..."

BACKEND_PORT_OCCUPIED=false
FRONTEND_PORT_OCCUPIED=false

if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    BACKEND_PID=$(lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t 2>/dev/null)
    print_warning "后端端口 $BACKEND_PORT 被占用 (PID: $BACKEND_PID)"
    BACKEND_PORT_OCCUPIED=true
else
    print_success "后端端口 $BACKEND_PORT 未被占用"
fi

if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    FRONTEND_PID=$(lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t 2>/dev/null)
    print_warning "前端端口 $FRONTEND_PORT 被占用 (PID: $FRONTEND_PID)"
    FRONTEND_PORT_OCCUPIED=true
else
    print_success "前端端口 $FRONTEND_PORT 未被占用"
fi

echo ""

# 2. 停止后端服务
print_info "停止后端服务..."
if [ -f "backend.pid" ]; then
    BACKEND_PID_FILE=$(cat backend.pid)
    if ps -p $BACKEND_PID_FILE > /dev/null 2>&1; then
        kill $BACKEND_PID_FILE
        sleep 1
        if ps -p $BACKEND_PID_FILE > /dev/null 2>&1; then
            print_warning "后端进程未正常终止，强制停止..."
            kill -9 $BACKEND_PID_FILE 2>/dev/null || true
        fi
        print_success "后端服务已停止 (PID: $BACKEND_PID_FILE)"
    else
        print_warning "后端进程不存在 (PID: $BACKEND_PID_FILE)"
    fi
    rm backend.pid
else
    # 通过端口或进程名查找
    if [ "$BACKEND_PORT_OCCUPIED" = true ]; then
        print_info "通过端口停止后端服务..."
        kill $BACKEND_PID 2>/dev/null || true
        sleep 1
        # 强制清理
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
        print_success "后端服务已停止"
    else
        # 通过进程名查找
        pkill -f "python.*main.py" && print_success "后端服务已停止" || print_info "后端服务未运行"
    fi
fi

# 3. 停止前端服务
print_info "停止前端服务..."
if [ -f "frontend.pid" ]; then
    FRONTEND_PID_FILE=$(cat frontend.pid)
    if ps -p $FRONTEND_PID_FILE > /dev/null 2>&1; then
        kill $FRONTEND_PID_FILE
        sleep 1
        if ps -p $FRONTEND_PID_FILE > /dev/null 2>&1; then
            print_warning "前端进程未正常终止，强制停止..."
            kill -9 $FRONTEND_PID_FILE 2>/dev/null || true
        fi
        print_success "前端服务已停止 (PID: $FRONTEND_PID_FILE)"
    else
        print_warning "前端进程不存在 (PID: $FRONTEND_PID_FILE)"
    fi
    rm frontend.pid
else
    # 通过端口或进程名查找
    if [ "$FRONTEND_PORT_OCCUPIED" = true ]; then
        print_info "通过端口停止前端服务..."
        kill $FRONTEND_PID 2>/dev/null || true
        sleep 1
        # 强制清理
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        print_success "前端服务已停止"
    else
        # 通过进程名查找
        pkill -f "vite.*--port" && print_success "前端服务已停止" || print_info "前端服务未运行"
    fi
fi

# 4. 等待进程完全停止
print_info "等待进程完全停止..."
sleep 2

# 5. 检查并清理残留进程
print_info "检查残留进程..."

REMAINING_BACKEND=$(ps aux | grep "python.*main.py" | grep -v grep || echo "")
REMAINING_FRONTEND=$(ps aux | grep "vite.*--port" | grep -v grep || echo "")

if [ -n "$REMAINING_BACKEND" ]; then
    print_warning "发现残留的后端进程，强制停止..."
    pkill -9 -f "python.*main.py"
    sleep 1
fi

if [ -n "$REMAINING_FRONTEND" ]; then
    print_warning "发现残留的前端进程，强制停止..."
    pkill -9 -f "vite.*--port"
    sleep 1
fi

# 6. 最终端口检查
print_info "最终端口检查..."
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_error "后端端口 $BACKEND_PORT 仍被占用"
    print_info "占用进程："
    lsof -Pi :$BACKEND_PORT -sTCP:LISTEN
else
    print_success "后端端口 $BACKEND_PORT 已释放"
fi

if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_error "前端端口 $FRONTEND_PORT 仍被占用"
    print_info "占用进程："
    lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN
else
    print_success "前端端口 $FRONTEND_PORT 已释放"
fi

# 7. 显示停止结果
print_header "✅ 服务停止完成"

print_info "进程状态检查："
if ps aux | grep "python.*main.py" | grep -v grep > /dev/null; then
    print_error "后端服务仍在运行"
    print_info "运行中的进程："
    ps aux | grep "python.*main.py" | grep -v grep
else
    print_success "后端服务已完全停止"
fi

if ps aux | grep "vite.*--port" | grep -v grep > /dev/null; then
    print_error "前端服务仍在运行"
    print_info "运行中的进程："
    ps aux | grep "vite.*--port" | grep -v grep
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
print_info "如需重启服务，请运行: ./restart_all.sh"
echo ""