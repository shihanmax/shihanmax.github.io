#!/bin/bash

# 生产环境博客部署脚本
# 启动博客应用和webhook服务
# 优化版本：增强错误处理和日志显示，只使用venv虚拟环境

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示实时日志的函数
show_live_logs() {
    local service=$1
    local logfile=$2
    local timeout=${3:-10}
    
    log_info "监控 $service 启动日志 (${timeout}秒)..."
    
    local count=0
    while [ $count -lt $timeout ]; do
        if [ -f "$logfile" ]; then
            echo "--- $service 最新日志 ---"
            tail -n 10 "$logfile" 2>/dev/null || echo "暂无日志内容"
            break
        fi
        sleep 1
        ((count++))
    done
    
    if [ ! -f "$logfile" ]; then
        log_error "$service 日志文件未生成: $logfile"
        return 1
    fi
}

# 错误处理函数
handle_error() {
    local line_no=$1
    log_error "脚本在第 $line_no 行出错"
    log_error "显示最近的错误日志..."
    show_recent_logs
    exit 1
}

# 设置错误陷阱
trap 'handle_error $LINENO' ERR

echo "=== 博客生产环境部署脚本 (优化版) ==="

# 进入项目根目录
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)
log_info "项目根目录: $PROJECT_ROOT"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    log_error "未找到python3"
    exit 1
fi

log_success "Python3 环境检查通过"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    log_info "创建虚拟环境..."
    python3 -m venv venv
    log_success "虚拟环境创建完成"
else
    log_info "虚拟环境已存在"
fi

# 配置虚拟环境
if [ -d "venv" ]; then
    log_info "使用现有虚拟环境..."
    # 由于虚拟环境可能有路径问题，直接使用绝对路径
    VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"
    VENV_PIP="$PROJECT_ROOT/venv/bin/pip"
    
    # 检查虚拟环境是否正常
    if [ -f "$VENV_PYTHON" ]; then
        # 重建虚拟环境如果路径不匹配
        if ! "$VENV_PYTHON" -c "import sys; sys.exit(0 if sys.executable.startswith('$PROJECT_ROOT') else 1)" 2>/dev/null; then
            log_warning "虚拟环境路径不匹配，重新创建..."
            rm -rf venv
            python3 -m venv venv
            log_success "虚拟环境重新创建完成"
        fi
        PYTHON_CMD="$VENV_PYTHON"
        PIP_CMD="$VENV_PIP"
    else
        log_warning "虚拟环境损坏，重新创建..."
        rm -rf venv
        python3 -m venv venv
        log_success "虚拟环境重新创建完成"
        PYTHON_CMD="$PROJECT_ROOT/venv/bin/python"
        PIP_CMD="$PROJECT_ROOT/venv/bin/pip"
    fi
else
    log_info "创建新的虚拟环境..."
    python3 -m venv venv
    log_success "虚拟环境创建完成"
    PYTHON_CMD="$PROJECT_ROOT/venv/bin/python"
    PIP_CMD="$PROJECT_ROOT/venv/bin/pip"
fi

log_success "Python 环境配置完成: $PYTHON_CMD"

# 安装依赖
log_info "检查并安装依赖..."
if ! $PIP_CMD install --upgrade pip --quiet; then
    log_error "pip 升级失败"
    exit 1
fi

if ! $PIP_CMD install -r requirements.txt --quiet; then
    log_error "依赖安装失败，查看详细错误:"
    $PIP_CMD install -r requirements.txt
    exit 1
fi

log_success "依赖安装完成"

# 创建日志目录
mkdir -p logs
log_info "日志目录已准备: logs/"

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
    log_info "启动博客应用 (端口8081)..."
    check_port 8081
    
    cd "$PROJECT_ROOT"
    
    # 清空之前的日志
    > logs/blog_app.log
    
    # 设置端口环境变量 (使用8081端口)
    export PORT=8081
    
    # 启动应用
    nohup $PYTHON_CMD app.py > logs/blog_app.log 2>&1 &
    local pid=$!
    echo $pid > logs/blog_app.pid
    
    log_info "博客应用启动中，PID: $pid"
    
    # 等待并检查启动状态
    sleep 3
    
    if kill -0 $pid 2>/dev/null; then
        # 显示启动日志
        show_live_logs "博客应用" "logs/blog_app.log" 5
        
        # 检查端口是否监听
        if lsof -i:8081 &>/dev/null; then
            log_success "博客应用启动成功 (PID: $pid, Port: 8081)"
            log_info "访问地址: http://localhost:8081"
            return 0
        else
            log_error "博客应用启动失败 - 端口8081未监听"
            show_recent_logs "blog_app"
            return 1
        fi
    else
        log_error "博客应用进程异常退出"
        show_recent_logs "blog_app"
        return 1
    fi
}

start_webhook_service() {
    log_info "启动Webhook服务 (端口8082)..."
    check_port 8082
    
    cd "$PROJECT_ROOT/deploy"
    
    # 清空之前的日志
    > ../logs/webhook.log
    
    # 启动webhook服务
    nohup $PYTHON_CMD webhook.py > ../logs/webhook.log 2>&1 &
    local pid=$!
    echo $pid > ../logs/webhook.pid
    
    log_info "Webhook服务启动中，PID: $pid"
    
    # 等待并检查启动状态
    sleep 3
    
    if kill -0 $pid 2>/dev/null; then
        # 显示启动日志
        show_live_logs "Webhook服务" "../logs/webhook.log" 5
        
        # 检查端口是否监听
        if lsof -i:8082 &>/dev/null; then
            log_success "Webhook服务启动成功 (PID: $pid, Port: 8082)"
            log_info "Webhook地址: http://localhost:8082/hook"
            log_info "状态检查: http://localhost:8082/status"
            return 0
        else
            log_error "Webhook服务启动失败 - 端口8082未监听"
            show_recent_logs "webhook"
            return 1
        fi
    else
        log_error "Webhook服务进程异常退出"
        show_recent_logs "webhook"
        return 1
    fi
}

# 停止函数
stop_services() {
    log_info "停止所有服务..."
    
    cd "$PROJECT_ROOT"
    local stopped_count=0
    
    # 停止博客应用
    if [ -f logs/blog_app.pid ]; then
        local pid=$(cat logs/blog_app.pid)
        if kill -0 $pid 2>/dev/null; then
            log_info "停止博客应用 (PID: $pid)..."
            kill $pid 2>/dev/null || true
            sleep 2
            if kill -0 $pid 2>/dev/null; then
                log_warning "强制终止博客应用..."
                kill -9 $pid 2>/dev/null || true
            fi
            stopped_count=$((stopped_count + 1))
        fi
        rm -f logs/blog_app.pid
    fi
    
    # 停止webhook服务
    if [ -f logs/webhook.pid ]; then
        local pid=$(cat logs/webhook.pid)
        if kill -0 $pid 2>/dev/null; then
            log_info "停止Webhook服务 (PID: $pid)..."
            kill $pid 2>/dev/null || true
            sleep 2
            if kill -0 $pid 2>/dev/null; then
                log_warning "强制终止Webhook服务..."
                kill -9 $pid 2>/dev/null || true
            fi
            stopped_count=$((stopped_count + 1))
        fi
        rm -f logs/webhook.pid
    fi
    
    # 强制清理端口
    check_port 8081
    check_port 8082
    
    if [ $stopped_count -gt 0 ]; then
        log_success "已停止 $stopped_count 个服务"
    else
        log_info "没有运行中的服务需要停止"
    fi
}

# 状态检查
check_status() {
    log_info "=== 服务状态 ==="
    
    cd "$PROJECT_ROOT"
    local all_running=true
    
    # 检查博客应用
    if [ -f logs/blog_app.pid ] && kill -0 $(cat logs/blog_app.pid) 2>/dev/null; then
        local pid=$(cat logs/blog_app.pid)
        if lsof -i:8081 &>/dev/null; then
            log_success "博客应用运行中 (PID: $pid, Port: 8081)"
            echo "   访问地址: http://localhost:8081"
        else
            log_warning "博客应用进程存在但端口8081未监听 (PID: $pid)"
            all_running=false
        fi
    else
        log_error "博客应用未运行"
        all_running=false
    fi
    
    # 检查Webhook服务
    if [ -f logs/webhook.pid ] && kill -0 $(cat logs/webhook.pid) 2>/dev/null; then
        local pid=$(cat logs/webhook.pid)
        if lsof -i:8082 &>/dev/null; then
            log_success "Webhook服务运行中 (PID: $pid, Port: 8082)"
            echo "   Webhook地址: http://localhost:8082/hook"
            echo "   状态检查: http://localhost:8082/status"
        else
            log_warning "Webhook服务进程存在但端口8082未监听 (PID: $pid)"
            all_running=false
        fi
    else
        log_error "Webhook服务未运行"
        all_running=false
    fi
    
    # 检查端口占用情况
    echo ""
    log_info "端口占用情况:"
    echo "Port 8081: $(lsof -i:8081 2>/dev/null | wc -l | tr -d ' ') connections"
    echo "Port 8082: $(lsof -i:8082 2>/dev/null | wc -l | tr -d ' ') connections"
    
    if $all_running; then
        log_success "所有服务运行正常"
    else
        log_warning "部分服务存在问题，建议执行重启"
    fi
}

# 重启服务
restart_services() {
    log_info "重启所有服务..."
    
    # 停止服务
    stop_services
    sleep 2
    
    # 启动服务
    log_info "开始启动服务..."
    
    if start_blog_app; then
        sleep 2
        if start_webhook_service; then
            sleep 1
            log_success "所有服务重启完成"
            check_status
        else
            log_error "Webhook服务启动失败"
            show_recent_logs "webhook" 10
            return 1
        fi
    else
        log_error "博客应用启动失败"
        show_recent_logs "blog_app" 10
        return 1
    fi
}

# 显示最近日志的增强函数
show_recent_logs() {
    local service=${1:-"all"}
    local lines=${2:-30}
    
    cd "$PROJECT_ROOT"
    
    if [ "$service" = "all" ] || [ "$service" = "blog_app" ]; then
        echo ""
        log_info "=== 博客应用日志 (最近${lines}行) ==="
        if [ -f logs/blog_app.log ]; then
            tail -n $lines logs/blog_app.log
        else
            log_warning "博客应用日志文件不存在"
        fi
    fi
    
    if [ "$service" = "all" ] || [ "$service" = "webhook" ]; then
        echo ""
        log_info "=== Webhook服务日志 (最近${lines}行) ==="
        if [ -f logs/webhook.log ]; then
            tail -n $lines logs/webhook.log
        else
            log_warning "Webhook服务日志文件不存在"
        fi
    fi
}

# 实时监控日志
monitor_logs() {
    local service=${1:-"all"}
    
    log_info "开始实时监控日志 (按 Ctrl+C 退出)..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$service" = "all" ]; then
        if [ -f logs/blog_app.log ] && [ -f logs/webhook.log ]; then
            tail -f logs/blog_app.log logs/webhook.log
        elif [ -f logs/blog_app.log ]; then
            tail -f logs/blog_app.log
        elif [ -f logs/webhook.log ]; then
            tail -f logs/webhook.log
        else
            log_error "没有找到任何日志文件"
        fi
    elif [ "$service" = "blog" ]; then
        if [ -f logs/blog_app.log ]; then
            tail -f logs/blog_app.log
        else
            log_error "博客应用日志文件不存在"
        fi
    elif [ "$service" = "webhook" ]; then
        if [ -f logs/webhook.log ]; then
            tail -f logs/webhook.log
        else
            log_error "Webhook服务日志文件不存在"
        fi
    fi
}

# 兼容旧的show_logs函数
show_logs() {
    show_recent_logs "all" 20
}

# 主菜单
case "$1" in
    start)
        log_info "启动所有服务..."
        success=true
        
        if start_blog_app; then
            sleep 2
            if start_webhook_service; then
                sleep 1
                log_success "所有服务启动完成"
                check_status
            else
                log_error "Webhook服务启动失败"
                show_recent_logs "webhook" 15
                success=false
            fi
        else
            log_error "博客应用启动失败"
            show_recent_logs "blog_app" 15
            success=false
        fi
        
        if [ "$success" = false ]; then
            log_error "部署失败，请检查上述错误信息"
            exit 1
        fi
        ;;
    stop)
        stop_services
        ;;
    restart)
        if ! restart_services; then
            log_error "重启失败"
            exit 1
        fi
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    monitor)
        monitor_logs "$2"
        ;;
    tail)
        show_recent_logs "${2:-all}" "${3:-50}"
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs|monitor|tail}"
        echo ""
        echo "命令说明:"
        echo "  start             - 启动博客应用和webhook服务"
        echo "  stop              - 停止所有服务"
        echo "  restart           - 重启所有服务"
        echo "  status            - 检查服务状态"
        echo "  logs              - 查看最近的日志"
        echo "  monitor [service] - 实时监控日志 (all|blog|webhook)"
        echo "  tail [service] [lines] - 查看指定行数的日志"
        echo ""f
        echo "示例:"
        echo "  $0 monitor blog     # 监控博客应用日志"
        echo "  $0 tail webhook 100 # 查看webhook最近100行日志"
        echo ""
        echo "GitHub Webhook配置:"
        echo "  URL: http://your-server-ip:8082/hook"
        echo "  Content type: application/json"
        echo "  事件: Just the push event"
        exit 1
        ;;
esac

log_success "操作完成！"