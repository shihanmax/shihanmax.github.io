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
    echo "清理端口 $port..."
    # 找到所有占用该端口的进程并杀死
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "发现端口 $port 被占用，正在清理..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
        # 再次检查
        if lsof -ti:$port >/dev/null 2>&1; then
            echo "警告: 端口 $port 仍被占用"
        else
            echo "端口 $port 已清理"
        fi
    fi
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
    
    # 先清理端口，再清理PID文件
    stop_port 8081
    stop_port 8082
    
    # 清理PID文件
    if [ -f logs/blog_app.pid ]; then
        local pid=$(cat logs/blog_app.pid)
        if kill -0 $pid 2>/dev/null; then
            echo "停止博客应用 (PID: $pid)"
            kill $pid 2>/dev/null || true
            sleep 1
        fi
        rm -f logs/blog_app.pid
    fi
    
    if [ -f logs/webhook.pid ]; then
        local pid=$(cat logs/webhook.pid)
        if kill -0 $pid 2>/dev/null; then
            echo "停止Webhook服务 (PID: $pid)"
            kill $pid 2>/dev/null || true
            sleep 1
        fi
        rm -f logs/webhook.pid
    fi
    
    echo "服务已停止"
}

# 检查状态
check_status() {
    echo "=== 服务状态 ==="
    cd "$PROJECT_ROOT"
    
    # 检查博客应用
    if [ -f logs/blog_app.pid ] && kill -0 $(cat logs/blog_app.pid) 2>/dev/null; then
        local pid=$(cat logs/blog_app.pid)
        # 检查进程是否监听端口（包括127.0.0.1和0.0.0.0）
        if lsof -p $pid -i :8081 >/dev/null 2>&1; then
            echo "博客应用: 运行中 (PID: $pid, 端口:8081)"
            echo "  访问地址: http://localhost:8081"
        else
            echo "博客应用: 进程存在但端口未监听 (PID: $pid)"
            echo "  提示: 请检查日志文件 logs/blog_app.log"
        fi
    else
        echo "博客应用: 未运行"
    fi
    
    # 检查Webhook服务
    if [ -f logs/webhook.pid ] && kill -0 $(cat logs/webhook.pid) 2>/dev/null; then
        local pid=$(cat logs/webhook.pid)
        # 检查进程是否监听端口（包括127.0.0.1和0.0.0.0）
        if lsof -p $pid -i :8082 >/dev/null 2>&1; then
            echo "Webhook服务: 运行中 (PID: $pid, 端口:8082)"
            echo "  Webhook地址: http://localhost:8082/hook"
        else
            echo "Webhook服务: 进程存在但端口未监听 (PID: $pid)"
            echo "  提示: 请检查日志文件 logs/webhook.log"
        fi
    else
        echo "Webhook服务: 未运行"
    fi
    
    # 显示端口占用情况（更详细）
    echo ""
    echo "端口监听情况:"
    local port_8081=$(lsof -i:8081 2>/dev/null | grep LISTEN | head -1)
    local port_8082=$(lsof -i:8082 2>/dev/null | grep LISTEN | head -1)
    
    if [ -n "$port_8081" ]; then
        echo "  8081: 已监听 - $port_8081"
    else
        echo "  8081: 未监听"
    fi
    
    if [ -n "$port_8082" ]; then
        echo "  8082: 已监听 - $port_8082"
    else
        echo "  8082: 未监听"
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