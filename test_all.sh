#!/bin/bash

################################################################################
# 全局测试脚本 - 一键运行所有测试
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

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "=================================="
echo "  量化交易平台 - 运行所有测试"
echo "=================================="
echo ""

# 解析命令行参数
TEST_BACKEND=false
TEST_FRONTEND=false
TEST_ALL=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            TEST_BACKEND=true
            TEST_ALL=false
            shift
            ;;
        --frontend)
            TEST_FRONTEND=true
            TEST_ALL=false
            shift
            ;;
        --all)
            TEST_ALL=true
            shift
            ;;
        *)
            print_warning "未知参数: $1"
            echo "用法: $0 [--backend|--frontend|--all]"
            exit 1
            ;;
    esac
done

# 如果没有指定参数，默认运行所有测试
if [ "$TEST_ALL" = true ]; then
    TEST_BACKEND=true
    TEST_FRONTEND=true
fi

# 总体测试统计
TOTAL_BACKEND=0
PASSED_BACKEND=0
FAILED_BACKEND=0
TOTAL_FRONTEND=0
PASSED_FRONTEND=0
FAILED_FRONTEND=0

# 运行后端测试
if [ "$TEST_BACKEND" = true ]; then
    print_info "=================================="
    print_info "运行后端测试"
    print_info "=================================="
    echo ""
    
    if [ -f "backend/test_all.sh" ]; then
        chmod +x backend/test_all.sh
        cd backend
        bash test_all.sh
        BACKEND_EXIT_CODE=$?
        cd ..
        
        if [ $BACKEND_EXIT_CODE -eq 0 ]; then
            print_success "后端测试全部通过"
        else
            print_error "后端测试有失败"
            FAILED_BACKEND=1
        fi
    else
        print_warning "后端测试脚本不存在: backend/test_all.sh"
        FAILED_BACKEND=1
    fi
    echo ""
fi

# 运行前端测试
if [ "$TEST_FRONTEND" = true ]; then
    print_info "=================================="
    print_info "运行前端测试"
    print_info "=================================="
    echo ""
    
    if [ -d "frontend" ]; then
        cd frontend
        npm test 2>&1 || FRONTEND_EXIT_CODE=1
        cd ..
        
        if [ $FRONTEND_EXIT_CODE -eq 0 ]; then
            print_success "前端测试全部通过"
        else
            print_warning "前端测试尚未实现"
            FAILED_FRONTEND=1
        fi
    else
        print_warning "前端目录不存在"
        FAILED_FRONTEND=1
    fi
    echo ""
fi

# 显示总体测试结果
print_info "=================================="
print_info "总体测试结果"
print_info "=================================="
echo ""

if [ "$TEST_BACKEND" = true ]; then
    if [ $FAILED_BACKEND -eq 0 ]; then
        echo -e "后端: ${GREEN}✅ 通过${NC}"
    else
        echo -e "后端: ${RED}❌ 失败${NC}"
    fi
fi

if [ "$TEST_FRONTEND" = true ]; then
    if [ $FAILED_FRONTEND -eq 0 ]; then
        echo -e "前端: ${GREEN}✅ 通过${NC}"
    else
        echo -e "前端: ${YELLOW}⚠️  开发中${NC}"
    fi
fi

echo ""

if [ $FAILED_BACKEND -eq 0 ] && [ $FAILED_FRONTEND -eq 0 ]; then
    print_success "所有测试通过！"
    exit 0
else
    print_warning "部分测试未通过或尚未实现"
    exit 1
fi