#!/bin/bash

echo "=== 部署业余无线电考试系统（带认证功能）==="

# 1. 安装后端依赖
echo "1. 安装后端依赖..."
cd /opt/radio-exam/backend
pip3 install -r requirements.txt

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
npm install
npm run build
if [ $? -eq 0 ]; then
    echo "✓ 前端构建成功"
else
    echo "✗ 前端构建失败"
    exit 1
fi

# 4. 重启Nginx
echo "4. 重启Nginx服务..."
sudo systemctl restart nginx
if [ $? -eq 0 ]; then
    echo "✓ Nginx服务重启成功"
else
    echo "✗ Nginx服务重启失败"
    exit 1
fi

# 5. 验证服务
echo "5. 验证服务状态..."
sleep 3

# 检查服务状态
sudo systemctl is-active --quiet radio-exam-backend && echo "✓ 后端服务运行正常" || echo "✗ 后端服务异常"
sudo systemctl is-active --quiet nginx && echo "✓ Nginx服务运行正常" || echo "✗ Nginx服务异常"

# 测试API
curl -s http://localhost:5000/api/auth/login > /dev/null && echo "✓ 认证API响应正常" || echo "✗ 认证API响应异常"
curl -s http://localhost/ > /dev/null && echo "✓ 前端页面访问正常" || echo "✗ 前端页面访问异常"

echo ""
echo "=== 部署完成 ==="
echo "默认管理员账号：17610788168"
echo "默认管理员密码：administrator"
echo "请及时修改默认密码！"
echo ""
echo "访问地址：http://8.138.207.21"