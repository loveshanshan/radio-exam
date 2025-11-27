#!/bin/bash

echo "=== 重启业余无线电考试系统 ==="

# 1. 重启后端服务
echo "1. 重启后端服务..."
sudo systemctl restart radio-exam-backend
if [ $? -eq 0 ]; then
    echo "✓ 后端服务重启成功"
else
    echo "✗ 后端服务重启失败"
    exit 1
fi

# 2. 重新构建前端
echo "2. 重新构建前端..."
cd /opt/radio-exam/frontend
npm run build
if [ $? -eq 0 ]; then
    echo "✓ 前端构建成功"
else
    echo "✗ 前端构建失败"
    exit 1
fi

# 3. 重启Nginx
echo "3. 重启Nginx服务..."
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