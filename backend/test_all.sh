#!/bin/bash

################################################################################
# 后端测试脚本 - 一键运行所有后端测试
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

print_info "开始运行后端测试..."
echo ""

# 测试统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 运行API测试
print_info "=================================="
print_info "运行API测试"
print_info "=================================="
for test_file in test/api/test_*.py; do
    if [ -f "$test_file" ]; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        print_info "运行: $test_file"
        if python "$test_file"; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
            print_success "$test_file 通过"
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
            print_error "$test_file 失败"
        fi
        echo ""
    fi
done

# 运行服务测试
print_info "=================================="
print_info "运行服务测试"
print_info "=================================="
for test_file in test/services/test_*.py; do
    if [ -f "$test_file" ]; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        print_info "运行: $test_file"
        if python "$test_file"; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
            print_success "$test_file 通过"
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
            print_error "$test_file 失败"
        fi
        echo ""
    fi
done

# 运行数据适配器测试
print_info "=================================="
print_info "运行数据适配器测试"
print_info "=================================="
for test_file in test/data_adapters/test_*.py; do
    if [ -f "$test_file" ]; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        print_info "运行: $test_file"
        if python "$test_file"; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
            print_success "$test_file 通过"
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
            print_error "$test_file 失败"
        fi
        echo ""
    fi
done

# 运行工具测试
print_info "=================================="
print_info "运行工具测试"
print_info "=================================="
for test_file in test/utils/test_*.py; do
    if [ -f "$test_file" ]; then
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        print_info "运行: $test_file"
        if python "$test_file"; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
            print_success "$test_file 通过"
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
            print_error "$test_file 失败"
        fi
        echo ""
    fi
done

# 显示测试结果
echo ""
print_info "=================================="
print_info "测试结果"
print_info "=================================="
echo -e "总测试数: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败: ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    print_success "所有测试通过！"
    exit 0
else
    print_error "有 $FAILED_TESTS 个测试失败"
    exit 1
fi