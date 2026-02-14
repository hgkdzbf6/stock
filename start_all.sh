#!/bin/bash

################################################################################
# 量化交易平台 - 一键启动脚本
################################################################################

set -e  # 遇到错误立即退出

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

# 函数：检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装"
        return 1
    fi
    return 0
}

# 函数：检查端口是否被占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口 $1 已被占用"
        read -p "是否继续启动? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "用户取消启动"
            exit 0
        fi
    fi
}

################################################################################
# 主流程
################################################################################

print_header "量化交易平台 - 一键启动"

# 1. 检查环境
print_info "检查环境依赖..."

if ! check_command python3; then
    print_error "Python 3 未安装，请先安装 Python 3.11+"
    exit 1
fi

if ! check_command node; then
    print_error "Node.js 未安装，请先安装 Node.js 18+"
    exit 1
fi

if ! check_command npm; then
    print_error "npm 未安装，请先安装 npm"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
NODE_VERSION=$(node --version)
print_success "Python 版本: $PYTHON_VERSION"
print_success "Node.js 版本: $NODE_VERSION"

# 检查端口
print_info "检查端口占用情况..."
check_port 8000
check_port 3000

# 2. 后端设置
print_header "后端服务设置"

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    print_info "创建Python虚拟环境..."
    python3 -m venv venv
    print_success "虚拟环境创建成功"
fi

# 激活虚拟环境
print_info "激活虚拟环境..."
source venv/bin/activate

# 安装/更新依赖
print_info "检查后端依赖..."
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt 文件不存在"
    exit 1
fi

print_info "安装Python依赖..."
pip install -q -r requirements.txt
print_success "依赖安装完成"

# 检查环境变量
if [ ! -f ".env" ]; then
    print_warning ".env 文件不存在，从 .env.example 创建..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env 文件已创建"
    else
        print_warning ".env.example 不存在，使用默认配置"
    fi
fi

# 停止旧的后端进程
print_info "停止旧的后端进程..."
pkill -f "python.*main.py" || true
sleep 2

# 启动后端
print_info "启动后端服务..."
nohup python main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
print_success "后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
print_info "等待后端服务启动..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "后端服务启动成功！"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "后端服务启动超时"
        print_info "查看日志: tail -f logs/backend.log"
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

cd ..

# 3. 前端设置
print_header "前端服务设置"

cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    print_info "安装前端依赖..."
    npm install
    print_success "依赖安装完成"
else
    print_info "依赖已存在，跳过安装"
fi

# 停止旧的前端进程
print_info "停止旧的前端进程..."
pkill -f "vite.*--port" || true
sleep 2

# 启动前端
print_info "启动前端服务..."
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
print_success "前端服务已启动 (PID: $FRONTEND_PID)"

# 等待前端启动
print_info "等待前端服务启动..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "前端服务启动成功！"
        break
    fi
    if [ $i -eq 30 ]; then
        print_warning "前端服务启动超时，但后端已运行"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

cd ..

# 4. 显示启动信息
print_header "✅ 服务启动完成！"

echo ""
echo -e "${GREEN}🌐 访问地址：${NC}"
echo -e "   ${BLUE}前端应用:${NC}   http://localhost:3000"
echo -e "   ${BLUE}后端API:${NC}    http://localhost:8000"
echo -e "   ${BLUE}API文档:${NC}    http://localhost:8000/docs"
echo -e "   ${BLUE}健康检查:${NC}   http://localhost:8000/health"
echo ""

echo -e "${GREEN}📊 服务状态：${NC}"
echo -e "   后端PID: ${BLUE}$BACKEND_PID${NC}"
echo -e "   前端PID: ${BLUE}$FRONTEND_PID${NC}"
echo ""

echo -e "${GREEN}📝 常用命令：${NC}"
echo -e "   查看后端日志:   ${BLUE}tail -f logs/backend.log${NC}"
echo -e "   查看前端日志:   ${BLUE}tail -f logs/frontend.log${NC}"
echo -e "   停止所有服务:   ${BLUE}./stop_all.sh${NC}"
echo -e "   重启所有服务:   ${BLUE}./restart_all.sh${NC}"
echo ""

print_info "如果遇到问题，请查看日志文件："
echo "   - logs/backend.log"
echo "   - logs/frontend.log"

echo ""
echo -e "${GREEN}=================================="
echo -e "   🎉 祝您使用愉快！"
echo -e "==================================${NC}"
echo ""