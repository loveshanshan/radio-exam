#!/bin/bash

echo "=== 502错误诊断脚本 ==="

# 1. 检查后端服务状态
echo "1. 检查后端服务状态..."
sudo systemctl is-active --quiet radio-exam-backend && echo "✓ 后端服务运行正常" || echo "✗ 后端服务未运行"

# 2. 检查端口占用
echo "2. 检查5000端口..."
netstat -tlnp | grep 5000 && echo "✓ 5000端口已监听" || echo "✗ 5000端口未监听"

# 3. 测试后端API
echo "3. 测试后端API..."
curl -s http://localhost:5000/api/questions > /dev/null && echo "✓ 后端API响应正常" || echo "✗ 后端API无响应"

# 4. 检查Nginx状态
echo "4. 检查Nginx状态..."
sudo systemctl is-active --quiet nginx && echo "✓ Nginx运行正常" || echo "✗ Nginx未运行"

# 5. 检查Nginx配置
echo "5. 测试Nginx配置..."
sudo nginx -t && echo "✓ Nginx配置正确" || echo "✗ Nginx配置错误"

# 6. 查看最近的错误日志
echo "6. 最近的Nginx错误日志："
sudo tail -5 /var/log/nginx/error.log 2>/dev/null || echo "无法读取Nginx错误日志"

echo "=== 诊断完成 ==="