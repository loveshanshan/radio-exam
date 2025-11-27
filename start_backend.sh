#!/bin/bash

echo "启动后端服务..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "虚拟环境不存在，请先运行安装脚本"
    exit 1
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 进入后端目录
cd backend

# 检查依赖
echo "检查依赖..."
python -c "import jwt" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "安装缺失的依赖..."
    pip install -r requirements.txt
fi

# 启动应用
echo "启动应用..."
python app.py