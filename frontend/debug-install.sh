#!/bin/bash

echo "=== 前端依赖安装诊断脚本 ==="

cd /opt/radio-exam/frontend

# 1. 检查 Node.js 版本
echo "1. Node.js 版本信息："
node --version
npm --version
if command -v pnpm &> /dev/null; then
    pnpm --version
else
    echo "pnpm 未安装"
fi

echo ""

# 2. 检查系统资源
echo "2. 系统资源："
echo "可用内存: $(free -h | awk 'NR==2{print $7}')"
echo "可用磁盘: $(df -h /opt | awk 'NR==2{print $4}')"
echo ""

# 3. 尝试逐步安装
echo "3. 逐步安装测试："

# 先安装核心依赖
echo "安装 Vue 核心依赖..."
npm install vue@^3.3.0 --save

echo "安装构建工具..."
npm install vite@^4.4.0 @vitejs/plugin-vue@^4.4.0 --save-dev

echo "安装路由..."
npm install vue-router@^4.6.3 --save

echo "安装 HTTP 客户端..."
npm install axios@^1.5.0 --save

echo "安装 TDesign 组件库（可能的问题源）..."
if npm install tdesign-vue-next@^1.3.0 --save; then
    echo "✓ TDesign 安装成功"
else
    echo "✗ TDesign 安装失败，尝试其他版本..."
    
    # 尝试更新版本
    echo "尝试安装 TDesign 最新版本..."
    npm install tdesign-vue-next@latest --save
    
    # 如果还是失败，尝试稳定版本
    if [ $? -ne 0 ]; then
        echo "尝试安装 TDesign 稳定版本..."
        npm install tdesign-vue-next@1.9.0 --save
    fi
fi

echo ""

# 4. 检查依赖冲突
echo "4. 检查依赖冲突："
npm ls --depth=0

echo ""

# 5. 尝试构建
echo "5. 尝试构建测试："
npm run build

echo ""
echo "=== 诊断完成 ==="