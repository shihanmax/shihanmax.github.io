#!/bin/bash

# 生产环境博客部署脚本
# 启动博客应用和webhook服务

echo "=== 博客生产环境部署脚本 ==="

# 进入项目根目录
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)
echo "项目根目录: $PROJECT_ROOT"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip3 install -r requirements.txt

# 创建日志目录
mkdir -p logs

# 检查端口占用
check_port() {
    local port=$1
    if lsof -i:$port &> /dev/null; then
        echo "端口 $port 被占用，正在尝试释放..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# 启动函数
start_blog_app() {
    echo "启动博客应用 (端口8080)..."
    check_port 8080
    
    cd "$PROJECT_ROOT"
    # 设置端口环境变量
    export PORT=8080
    nohup python3 app.py > logs/blog_app.log 2>&1 &
    echo $! > logs/blog_app.pid
    
    echo "博客应用已启动，PID: $(cat logs/blog_app.pid)"
}

start_webhook_service() {
    echo "启动Webhook服务 (端口8082)..."
    check_port 8082
    
    cd "$PROJECT_ROOT/deploy"
    nohup python3 webhook.py > ../logs/webhook.log 2>&1 &
    echo $! > ../logs/webhook.pid
    
    echo "Webhook服务已启动，PID: $(cat ../logs/webhook.pid)"
}

# 停止函数
stop_services() {
    echo "停止所有服务..."
    
    cd "$PROJECT_ROOT"
    if [ -f logs/blog_app.pid ]; then
        kill $(cat logs/blog_app.pid) 2>/dev/null || true
        rm -f logs/blog_app.pid
    fi
    
    if [ -f logs/webhook.pid ]; then
        kill $(cat logs/webhook.pid) 2>/dev/null || true
        rm -f logs/webhook.pid
    fi
    
    # 强制清理端口
    check_port 8080
    check_port 8082
    
    echo "所有服务已停止"
}

# 状态检查
check_status() {
    echo "=== 服务状态 ==="
    
    cd "$PROJECT_ROOT"
    if [ -f logs/blog_app.pid ] && kill -0 $(cat logs/blog_app.pid) 2>/dev/null; then
        echo "✅ 博客应用运行中 (PID: $(cat logs/blog_app.pid))"
        echo "   访问地址: http://localhost:8080"
    else
        echo "❌ 博客应用未运行"
    fi
    
    if [ -f logs/webhook.pid ] && kill -0 $(cat logs/webhook.pid) 2>/dev/null; then
        echo "✅ Webhook服务运行中 (PID: $(cat logs/webhook.pid))"
        echo "   Webhook地址: http://localhost:8082/hook"
        echo "   状态检查: http://localhost:8082/status"
    else
        echo "❌ Webhook服务未运行"
    fi
}

# 重启服务
restart_services() {
    echo "重启所有服务..."
    stop_services
    sleep 3
    start_blog_app
    sleep 2
    start_webhook_service
    sleep 2
    check_status
}

# 查看日志
show_logs() {
    echo "=== 最近的日志 ==="
    cd "$PROJECT_ROOT"
    echo "--- 博客应用日志 ---"
    tail -n 20 logs/blog_app.log 2>/dev/null || echo "无日志文件"
    echo ""
    echo "--- Webhook服务日志 ---"
    tail -n 20 logs/webhook.log 2>/dev/null || echo "无日志文件"
}

# 主菜单
case "$1" in
    start)
        echo "启动所有服务..."
        start_blog_app
        sleep 2
        start_webhook_service
        sleep 2
        check_status
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
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
        echo "命令说明:"
        echo "  start   - 启动博客应用和webhook服务"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  status  - 检查服务状态"
        echo "  logs    - 查看最近的日志"
        echo ""
        echo "GitHub Webhook配置:"
        echo "  URL: http://your-server-ip:8082/hook"
        echo "  Content type: application/json"
        echo "  事件: Just the push event"
        exit 1
        ;;
esac

echo "完成！"