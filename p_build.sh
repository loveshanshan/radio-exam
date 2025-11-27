#!/bin/bash

echo "=== 重启业余无线电考试系统 ==="

# 设置非交互模式
export DEBIAN_FRONTEND=noninteractive
export PNPM_HOME=/usr/local/bin
export PATH="$PNPM_HOME:$PATH"

# 设置资源限制
ulimit -n 65536  # 增加文件描述符限制
export NODE_OPTIONS="--max-old-space-size=4096"

# 0. 拉取最新代码
echo "0. 拉取最新代码..."
cd /opt/radio-exam

# 检查git状态
if ! git status > /dev/null 2>&1; then
    echo "✗ Git仓库状态检查失败，请检查git配置"
    exit 1
fi

# 拉取最新代码
echo "正在从远程仓库拉取最新代码..."
if ! git pull origin master; then
    echo "✗ Git拉取失败，请检查："
    echo "  1. 网络连接是否正常"
    echo "  2. Git远程仓库地址是否正确"
    echo "  3. 是否有权限访问仓库"
    echo "  4. 本地是否有未提交的更改冲突"
    exit 1
fi

echo "✓ 代码拉取成功"

# 检查系统资源
echo "检查系统资源..."
AVAILABLE_MEMORY=$(free -m | awk 'NR==2{printf "%.0f", $7}')
DISK_SPACE=$(df /opt | awk 'NR==2 {print $4}')

echo "可用内存: ${AVAILABLE_MEMORY}MB"
echo "可用磁盘空间: ${DISK_SPACE}KB"

if [ "$AVAILABLE_MEMORY" -lt 1024 ]; then
    echo "⚠️  警告: 可用内存不足 1GB，可能导致安装失败"
fi

if [ "$DISK_SPACE" -lt 1048576 ]; then
    echo "⚠️  警告: 可用磁盘空间不足 1GB，可能导致安装失败"
fi



# 1. 安装后端依赖
echo "1. 安装后端依赖..."
cd /opt/radio-exam/backend
pip install -r requirements.txt

# 2. 重启后端服务
echo "2. 重启后端服务..."
sudo systemctl restart radio-exam-backend
if [ $? -eq 0 ]; then
    echo "✓ 后端服务重启成功"
else
    echo "✗ 后端服务重启失败"
    exit 1
fi

# 3. 重新构建前端
echo "3. 重新构建前端..."
cd /opt/radio-exam/frontend


# 设置 pnpm 配置以减少内存使用
export PNPM_REGISTRY=https://registry.npmjs.org/
export PNPM_STORE_DIR=/tmp/pnpm-store
export NODE_OPTIONS="--max-old-space-size=2048"

# 尝试安装依赖，增加重试机制
echo "安装前端依赖..."
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "尝试安装 (第 $((RETRY_COUNT + 1)) 次)..."
    
    if pnpm install --force --no-optional --prefer-offline; then
        echo "✓ 依赖安装成功"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "✗ 安装失败，等待 10 秒后重试..."
        sleep 10
        
        # 清理可能损坏的缓存
        pnpm store prune --force || true
        
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            echo "✗ 依赖安装失败，已达到最大重试次数"
            echo "尝试使用 npm 作为备选方案..."
            
        fi
    fi
done

# 构建前端
echo "构建前端项目..."
if command -v pnpm &> /dev/null && [ -f "pnpm-lock.yaml" ]; then
    pnpm  build
fi
if [ $? -eq 0 ]; then
    echo "✓ 前端构建成功"
else
    echo "✗ 前端构建失败"
    exit 1
fi

# 3. 重启Nginx
echo "4. 重启Nginx服务..."
sudo systemctl restart nginx
if [ $? -eq 0 ]; then
    echo "✓ Nginx服务重启成功"
else
    echo "✗ Nginx服务重启失败"
    exit 1
fi

# 4. 验证服务
echo "4. 验证服务状态..."
sleep 3

# 检查服务状态
sudo systemctl is-active --quiet radio-exam-backend && echo "✓ 后端服务运行正常" || echo "✗ 后端服务异常"
sudo systemctl is-active --quiet nginx && echo "✓ Nginx服务运行正常" || echo "✗ Nginx服务异常"

# 测试API
curl -s http://localhost:5000/api/questions > /dev/null && echo "✓ 后端API响应正常" || echo "✗ 后端API响应异常"
curl -s http://localhost/api/questions > /dev/null && echo "✓ Nginx代理正常" || echo "✗ Nginx代理异常"

echo "=== 重启完成 ==="