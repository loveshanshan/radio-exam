#!/bin/bash

echo "=== 修复Vite构建错误 ==="

cd /opt/radio-exam/frontend

# 1. 清理缓存和依赖
echo "1. 清理缓存和依赖..."
rm -rf node_modules
rm -rf dist
rm -rf .vite
npm cache clean --force

# 2. 重新安装依赖
echo "2. 重新安装依赖..."
npm install

# 3. 升级Vite到稳定版本
echo "3. 升级构建工具..."
npm install vite@^4.5.0 @vitejs/plugin-vue@^4.5.0 --save-dev

# 4. 尝试构建
echo "4. 尝试构建..."
npm run build

if [ $? -eq 0 ]; then
    echo "✓ 构建成功"
else
    echo "✗ 构建失败，尝试降级方案..."
    
    # 5. 降级方案
    echo "5. 使用降级方案..."
    npm install vite@^4.3.0 @vitejs/plugin-vue@^4.3.0 --save-dev
    npm run build
fi

echo "=== 修复完成 ==="