#!/bin/bash

# 股票数据管理流水线脚本
# 功能：生成市场数据 -> 导入数据库
# 作者：自动生成
# 日期：2026-02-16

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"
DATA_DIR="$PROJECT_DIR/data"
SCRIPTS_DIR="$PROJECT_DIR/scripts"

# 日志文件
LOG_FILE="$DATA_DIR/pipeline_$(date +%Y%m%d_%H%M%S).log"

echo "=========================================="
echo "  股票市场数据管理流水线 v2.0"
echo "=========================================="
echo ""

# 创建日志目录
mkdir -p "$DATA_DIR"
mkdir -p "$SCRIPTS_DIR/log"

# 记录日志函数
log() {
    local level=$1
    shift
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message"
    echo -e "$message" | tee -a "$LOG_FILE"
}

# 检查Python环境
log "INFO" "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        log "ERROR" "未找到Python，请先安装Python 3.7+"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

log "INFO" "Python命令: $PYTHON_CMD"
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
log "INFO" "Python版本: $PYTHON_VERSION"

# 进入后端目录
cd "$BACKEND_DIR"
log "INFO" "工作目录: $(pwd)"

# 步骤1: 生成股票列表
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}步骤 1: 生成股票市场数据${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

log "INFO" "开始生成股票数据..."
if $PYTHON_CMD generate_stock_list.py; then
    log "SUCCESS" "股票数据生成成功"
    CSV_FILE="$DATA_DIR/stock_list.csv"
    if [ -f "$CSV_FILE" ]; then
        NUM_STOCKS=$(tail -n +2 "$CSV_FILE" | wc -l)
        log "INFO" "生成了 $NUM_STOCKS 只股票数据"
        
        # 显示数据统计
        echo ""
        log "INFO" "数据统计:"
        log "INFO" "  文件大小: $(du -h "$CSV_FILE" | cut -f1)"
        log "INFO" "  行数: $(wc -l < "$CSV_FILE")"
    else
        log "ERROR" "CSV文件未找到: $CSV_FILE"
        exit 1
    fi
else
    log "ERROR" "股票数据生成失败，请检查日志: $LOG_FILE"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}步骤 2: 导入数据到数据库${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

log "INFO" "开始导入数据到SQLite数据库..."
cd "$SCRIPTS_DIR"

if $PYTHON_CMD import_market_snapshot.py; then
    log "SUCCESS" "数据导入成功"
    
    # 显示数据库统计
    DB_FILE="$DATA_DIR/stock_market.db"
    if [ -f "$DB_FILE" ]; then
        log "INFO" "数据库统计:"
        log "INFO" "  文件大小: $(du -h "$DB_FILE" | cut -f1)"
        
        # 使用sqlite3查询数据库
        if command -v sqlite3 &> /dev/null; then
            TOTAL_RECORDS=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM stock_quotes;")
            LATEST_TIME=$(sqlite3 "$DB_FILE" "SELECT snapshot_time FROM stock_quotes ORDER BY id DESC LIMIT 1;")
            
            log "INFO" "  总记录数: $TOTAL_RECORDS"
            log "INFO" "  最新时间: $LATEST_TIME"
        fi
    fi
else
    log "ERROR" "数据导入失败，请检查日志: $LOG_FILE"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}处理完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

log "INFO" "流水线执行完成"
log "INFO" "数据文件: $DATA_DIR/stock_list.csv"
log "INFO" "数据库文件: $DATA_DIR/stock_market.db"
log "INFO" "日志文件: $LOG_FILE"

echo ""
echo -e "${YELLOW}后续操作:${NC}"
echo -e "  1. 查询数据库: sqlite3 $DATA_DIR/stock_market.db"
echo -e "  2. 查看数据文件: cat $DATA_DIR/stock_list.csv | head -n 10"
echo -e "  3. 查看日志: tail -n 50 $LOG_FILE"

exit 0