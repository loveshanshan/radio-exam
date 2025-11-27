#!/bin/bash

echo "修复前端构建问题..."

# 进入前端目录
cd frontend

# 清理缓存和依赖
echo "清理缓存..."
rm -rf node_modules/.cache
rm -rf dist

# 重新安装依赖
echo "重新安装依赖..."
npm install

# 清理npm缓存
npm cache clean --force

echo "修复完成！"
echo ""
echo "现在可以运行：npm run dev"
echo ""