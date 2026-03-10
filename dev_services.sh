#!/usr/bin/env bash

set -euo pipefail

# Unified service manager for frontend/backend.
# Default action is restart, so one-click usage is:
#   ./dev_services.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOG_DIR="$ROOT_DIR/logs"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

BACKEND_PID_FILE="$ROOT_DIR/backend.pid"
FRONTEND_PID_FILE="$ROOT_DIR/frontend.pid"

ACTION="${1:-restart}"

info() { printf '[INFO] %s\n' "$1"; }
ok() { printf '[OK]   %s\n' "$1"; }
warn() { printf '[WARN] %s\n' "$1"; }
err() { printf '[ERR]  %s\n' "$1"; }

ensure_dirs() {
  mkdir -p "$LOG_DIR"
  if [[ ! -d "$BACKEND_DIR" || ! -d "$FRONTEND_DIR" ]]; then
    err "backend/frontend 目录不存在，请在仓库根目录运行脚本"
    exit 1
  fi
}

kill_pid_file() {
  local pid_file="$1"
  local name="$2"

  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && ps -p "$pid" >/dev/null 2>&1; then
      kill "$pid" 2>/dev/null || true
      sleep 1
      if ps -p "$pid" >/dev/null 2>&1; then
        kill -9 "$pid" 2>/dev/null || true
      fi
      ok "通过 PID 文件停止 $name (PID: $pid)"
    fi
    rm -f "$pid_file"
  fi
}

kill_by_port() {
  local port="$1"
  local name="$2"
  local pids

  pids="$(lsof -ti :"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    warn "$name 端口 $port 被占用，正在清理"
    for pid in $pids; do
      kill "$pid" 2>/dev/null || true
    done
    sleep 1
    pids="$(lsof -ti :"$port" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "$pids" ]]; then
      for pid in $pids; do
        kill -9 "$pid" 2>/dev/null || true
      done
    fi
    ok "$name 端口 $port 已清理"
  fi
}

kill_by_pattern() {
  local pattern="$1"
  local name="$2"

  if pkill -f "$pattern" 2>/dev/null; then
    sleep 1
    ok "通过进程名停止 $name"
  fi
}

stop_services() {
  info "停止现有服务..."

  kill_pid_file "$BACKEND_PID_FILE" "后端"
  kill_pid_file "$FRONTEND_PID_FILE" "前端"

  kill_by_port "$BACKEND_PORT" "后端"
  kill_by_port "$FRONTEND_PORT" "前端"

  kill_by_pattern "python.*main.py" "后端"
  kill_by_pattern "vite.*--port" "前端"

  rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"
  ok "服务停止完成"
}

wait_http() {
  local url="$1"
  local name="$2"
  local attempts="${3:-30}"

  for ((i = 1; i <= attempts; i++)); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      ok "$name 已就绪: $url"
      return 0
    fi
    sleep 1
  done

  warn "$name 启动超时: $url"
  return 1
}

start_backend() {
  info "启动后端..."
  (
    cd "$BACKEND_DIR"
    nohup python main.py > "$LOG_DIR/backend.log" 2>&1 &
    echo $! > "$BACKEND_PID_FILE"
  )
  ok "后端已启动 (PID: $(cat "$BACKEND_PID_FILE"))"
  wait_http "http://localhost:${BACKEND_PORT}/health" "后端" 40 || true
}

start_frontend() {
  info "启动前端..."
  (
    cd "$FRONTEND_DIR"
    nohup npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" > "$LOG_DIR/frontend.log" 2>&1 &
    echo $! > "$FRONTEND_PID_FILE"
  )
  ok "前端已启动 (PID: $(cat "$FRONTEND_PID_FILE"))"
  wait_http "http://localhost:${FRONTEND_PORT}" "前端" 40 || true
}

start_services() {
  start_backend
  start_frontend
  printf '\n'
  ok "全部服务已启动"
  printf '    前端: http://localhost:%s\n' "$FRONTEND_PORT"
  printf '    后端: http://localhost:%s\n' "$BACKEND_PORT"
  printf '    日志: %s/backend.log, %s/frontend.log\n' "$LOG_DIR" "$LOG_DIR"
}

status_services() {
  info "服务状态"
  if lsof -ti :"$BACKEND_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    ok "后端监听在 :$BACKEND_PORT"
  else
    warn "后端未监听 :$BACKEND_PORT"
  fi

  if lsof -ti :"$FRONTEND_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    ok "前端监听在 :$FRONTEND_PORT"
  else
    warn "前端未监听 :$FRONTEND_PORT"
  fi

  [[ -f "$BACKEND_PID_FILE" ]] && info "backend pid: $(cat "$BACKEND_PID_FILE")"
  [[ -f "$FRONTEND_PID_FILE" ]] && info "frontend pid: $(cat "$FRONTEND_PID_FILE")"
}

ensure_dirs

case "$ACTION" in
  stop)
    stop_services
    ;;
  start)
    start_services
    ;;
  restart)
    stop_services
    start_services
    ;;
  status)
    status_services
    ;;
  *)
    err "未知命令: $ACTION"
    printf '用法: %s [start|stop|restart|status]\n' "$(basename "$0")"
    exit 1
    ;;
esac
