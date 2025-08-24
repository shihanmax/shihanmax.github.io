#!/bin/bash

# Webhook服务启动脚本
# 用于启动GitHub自动部署hook服务

echo "=== 启动博客自动部署Webhook服务 ==="

# 进入src目录
cd "$(dirname "$0")"

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "Python版本: $python_version"

# 检查是否有虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装额外依赖
echo "安装webhook服务依赖..."
pip install psutil

# 检查环境
echo "检查环境..."
python -c "import flask, psutil; print('Webhook服务依赖已安装')"

# 启动webhook服务
echo "启动Webhook服务..."
echo "监听地址: http://localhost:8082"
echo "Webhook端点: http://localhost:8082/hook"
echo "状态检查: http://localhost:8082/status"
echo "手动部署: curl -X POST http://localhost:8082/deploy"
echo "按 Ctrl+C 停止服务"
echo ""

# 设置环境变量（可选）
# export WEBHOOK_SECRET="your-github-webhook-secret"

python webhook.py