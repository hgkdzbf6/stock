#!/bin/bash

################################################################################
# 修复端口占用问题的诊断和修复脚本
################################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_header "🔍 诊断端口占用问题"

# 1. 检查端口占用
print_info "检查端口8000和3000的占用情况..."
echo ""

PORT_8000_PID=$(lsof -ti :8000 2>/dev/null)
PORT_3000_PID=$(lsof -ti :3000 2>/dev/null)

if [ -n "$PORT_8000_PID" ]; then
    echo "端口8000被占用，PID: $PORT_8000_PID"
    ps -p $PORT_8000_PID -o pid,command
    echo ""
else
    echo "端口8000未被占用"
    echo ""
fi

if [ -n "$PORT_3000_PID" ]; then
    echo "端口3000被占用，PID: $PORT_3000_PID"
    ps -p $PORT_3000_PID -o pid,command
    echo ""
else
    echo "端口3000未被占用"
    echo ""
fi

# 2. 检查PID文件
print_header "📄 检查PID文件"

if [ -f "backend.pid" ]; then
    BACKEND_PID_FILE=$(cat backend.pid)
    echo "backend.pid存在，记录的PID: $BACKEND_PID_FILE"
    if ps -p $BACKEND_PID_FILE > /dev/null 2>&1; then
        echo "  → 该进程存在"
    else
        echo "  → ${RED}该进程不存在（PID文件过期）${NC}"
    fi
else
    echo "backend.pid不存在"
fi

if [ -f "frontend.pid" ]; then
    FRONTEND_PID_FILE=$(cat frontend.pid)
    echo "frontend.pid存在，记录的PID: $FRONTEND_PID_FILE"
    if ps -p $FRONTEND_PID_FILE > /dev/null 2>&1; then
        echo "  → 该进程存在"
    else
        echo "  → ${RED}该进程不存在（PID文件过期）${NC}"
    fi
else
    echo "frontend.pid不存在"
fi

echo ""

# 3. 检查所有相关进程
print_header "🔍 检查所有相关进程"

echo "所有Python进程："
ps aux | grep -i python | grep -v grep | grep -E "(main.py|backend|8000)" || echo "  未找到相关Python进程"
echo ""

echo "所有Node进程："
ps aux | grep -i node | grep -v grep | grep -E "(vite|frontend|3000)" || echo "  未找到相关Node进程"
echo ""

# 4. 问题诊断
print_header "📋 问题诊断"

if [ -f "backend.pid" ] && [ -n "$BACKEND_PID_FILE" ]; then
    if ! ps -p $BACKEND_PID_FILE > /dev/null 2>&1; then
        print_warning "backend.pid记录的PID $BACKEND_PID_FILE 与实际运行的进程不匹配"
    fi
fi

if [ -f "frontend.pid" ] && [ -n "$FRONTEND_PID_FILE" ]; then
    if ! ps -p $FRONTEND_PID_FILE > /dev/null 2>&1; then
        print_warning "frontend.pid记录的PID $FRONTEND_PID_FILE 与实际运行的进程不匹配"
    fi
fi

if [ -n "$PORT_8000_PID" ] && [ -n "$PORT_3000_PID" ]; then
    print_warning "端口8000和3000都被占用，但PID文件可能不正确"
fi

# 5. 提供修复选项
print_header "🛠️ 修复选项"

echo "请选择修复方案："
echo "  1) 强制终止所有占用端口的进程并清理PID文件"
echo "  2) 只清理PID文件（不终止进程）"
echo "  3) 显示详细进程信息然后手动决定"
echo "  4) 退出（不执行任何操作）"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        print_header "执行方案1: 强制终止所有进程并清理"
        
        # 终止占用8000端口的进程
        if [ -n "$PORT_8000_PID" ]; then
            print_info "终止PID $PORT_8000_PID (端口8000)..."
            kill -9 $PORT_8000_PID 2>/dev/null && print_success "已终止" || print_warning "终止失败"
        fi
        
        # 终止占用3000端口的进程
        if [ -n "$PORT_3000_PID" ]; then
            print_info "终止PID $PORT_3000_PID (端口3000)..."
            kill -9 $PORT_3000_PID 2>/dev/null && print_success "已终止" || print_warning "终止失败"
        fi
        
        # 清理PID文件
        print_info "清理PID文件..."
        rm -f backend.pid frontend.pid .backend.pid .frontend.pid
        print_success "PID文件已清理"
        
        sleep 2
        
        # 验证
        print_info "验证端口状态..."
        if lsof -ti :8000 > /dev/null 2>&1; then
            print_error "端口8000仍被占用"
        else
            print_success "端口8000已释放"
        fi
        
        if lsof -ti :3000 > /dev/null 2>&1; then
            print_error "端口3000仍被占用"
        else
            print_success "端口3000已释放"
        fi
        ;;
        
    2)
        print_header "执行方案2: 只清理PID文件"
        print_info "清理PID文件..."
        rm -f backend.pid frontend.pid .backend.pid .frontend.pid
        print_success "PID文件已清理"
        print_warning "进程仍在运行，端口仍被占用"
        ;;
        
    3)
        print_header "执行方案3: 显示详细进程信息"
        echo "占用端口的进程详细信息："
        echo ""
        
        if [ -n "$PORT_8000_PID" ]; then
            echo "=== 端口8000的进程 (PID: $PORT_8000_PID) ==="
            ps -p $PORT_8000_PID -o pid,ppid,user,%cpu,%mem,vsz,rss,stat,start,time,command
            echo ""
        fi
        
        if [ -n "$PORT_3000_PID" ]; then
            echo "=== 端口3000的进程 (PID: $PORT_3000_PID) ==="
            ps -p $PORT_3000_PID -o pid,ppid,user,%cpu,%mem,vsz,rss,stat,start,time,command
            echo ""
        fi
        
        read -p "是否要终止这些进程? (y/n): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            [ -n "$PORT_8000_PID" ] && kill -9 $PORT_8000_PID 2>/dev/null
            [ -n "$PORT_3000_PID" ] && kill -9 $PORT_3000_PID 2>/dev/null
            rm -f backend.pid frontend.pid .backend.pid .frontend.pid
            print_success "进程已终止，PID文件已清理"
        else
            print_info "未执行终止操作"
        fi
        ;;
        
    4)
        print_info "退出，不执行任何操作"
        exit 0
        ;;
        
    *)
        print_error "无效选项"
        exit 1
        ;;
esac

print_header "✅ 修复完成"

print_info "现在可以重新启动服务："
echo "   ./start_all.sh"
echo ""