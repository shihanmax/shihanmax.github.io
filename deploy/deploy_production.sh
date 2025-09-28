#!/bin/bash

# 简化的博客部署脚本

set -e

# 进入项目根目录
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "=== 博客部署脚本 ==="
echo "项目目录: $PROJECT_ROOT"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 使用虚拟环境
PYTHON_CMD="$PROJECT_ROOT/venv/bin/python"
PIP_CMD="$PROJECT_ROOT/venv/bin/pip"

# 安装依赖
echo "安装依赖..."
$PIP_CMD install -r requirements.txt -q

# 创建日志目录
mkdir -p logs

# 停止端口占用进程
stop_port() {
    local port=$1
    lsof -ti:$port 2>/dev/null | xargs kill -9 2>/dev/null || true
    sleep 1
}

# 启动博客应用
start_blog() {
    echo "启动博客应用..."
    stop_port 8081
    cd "$PROJECT_ROOT"
    export PORT=8081
    nohup $PYTHON_CMD app.py > logs/blog_app.log 2>&1 &
    echo $! > logs/blog_app.pid
    sleep 3  # 增加等待时间
    echo "博客应用已启动 (端口8081)"
}

# 启动webhook服务
start_webhook() {
    echo "启动Webhook服务..."
    stop_port 8082
    cd "$PROJECT_ROOT/deploy"
    nohup $PYTHON_CMD webhook.py > ../logs/webhook.log 2>&1 &
    echo $! > ../logs/webhook.pid
    sleep 3  # 增加等待时间
    echo "Webhook服务已启动 (端口8082)"
}

# 停止服务
stop_services() {
    echo "停止服务..."
    cd "$PROJECT_ROOT"
    
    # 停止博客应用
    if [ -f logs/blog_app.pid ]; then
        kill $(cat logs/blog_app.pid) 2>/dev/null || true
        rm -f logs/blog_app.pid
    fi
    
    # 停止webhook服务
    if [ -f logs/webhook.pid ]; then
        kill $(cat logs/webhook.pid) 2>/dev/null || true
        rm -f logs/webhook.pid
    fi
    
    stop_port 8081
    stop_port 8082
    echo "服务已停止"
}

# 检查状态
check_status() {
    echo "=== 服务状态 ==="
    
    # 检查博客应用
    if [ -f logs/blog_app.pid ] && kill -0 $(cat logs/blog_app.pid) 2>/dev/null; then
        echo "博客应用: 运行中 (PID: $(cat logs/blog_app.pid))"
        echo "  访问地址: http://localhost:8081"
    else
        echo "博客应用: 未运行"
    fi
    
    # 检查Webhook服务
    if [ -f logs/webhook.pid ] && kill -0 $(cat logs/webhook.pid) 2>/dev/null; then
        echo "Webhook服务: 运行中 (PID: $(cat logs/webhook.pid))"
        echo "  Webhook地址: http://localhost:8082/hook"
    else
        echo "Webhook服务: 未运行"
    fi
}

# 显示日志
show_logs() {
    echo "=== 最近日志 ==="
    echo "--- 博客应用 ---"
    tail -n 20 logs/blog_app.log 2>/dev/null || echo "无日志"
    echo "--- Webhook服务 ---"
    tail -n 20 logs/webhook.log 2>/dev/null || echo "无日志"
}

# 主菜单
case "$1" in
    start)
        start_blog
        start_webhook
        check_status
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 1
        start_blog
        start_webhook
        check_status
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "  start   - 启动服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  status  - 检查状态"
        echo "  logs    - 显示日志"
        exit 1
        ;;
esac

echo "操作完成！"