#!/bin/bash

# 博客启动脚本
# 自动安装依赖并启动Flask应用

echo "=== 启动 Shihanmax's Blog ==="

# 进入项目根目录
cd "$(dirname "$0")/.."

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

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查环境
echo "检查环境..."
python -c "import flask, frontmatter, markdown; print('所有依赖已安装')"

# 启动应用
echo "启动博客应用..."
echo "访问地址: http://localhost:8080"
echo "按 Ctrl+C 停止服务"
echo ""

python app.py