#!/bin/bash

echo "=== 业余无线电考试系统部署脚本 ==="
echo "服务器: 8.138.207.21"
echo "访问地址: http://8.138.207.21/radio"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用sudo运行此脚本"
    exit 1
fi

# 设置变量
PROJECT_DIR="/opt/radio-exam"
NGINX_SITE="/etc/nginx/sites-available/radio-exam"
NGINX_ENABLED="/etc/nginx/sites-enabled/radio-exam"
SYSTEMD_SERVICE="/etc/systemd/system/radio-exam-backend.service"

echo "1. 创建项目目录..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

echo "2. 克隆项目代码..."
if [ ! -d ".git" ]; then
    echo "请先手动克隆项目代码到 $PROJECT_DIR"
    echo "命令: git clone <your-repo-url> ."
    exit 1
fi

echo "3. 设置Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "4. 安装后端依赖..."
pip install -r backend/requirements.txt

echo "5. 安装前端依赖并构建..."
cd frontend
npm install -g pnpm
pnpm install
pnpm build

echo "6. 配置Nginx..."
cp nginx-config.conf $NGINX_SITE
ln -sf $NGINX_SITE $NGINX_ENABLED
rm -f /etc/nginx/sites-enabled/default

echo "7. 配置systemd服务..."
cp radio-exam-backend.service $SYSTEMD_SERVICE

echo "8. 设置权限..."
chown -R www-data:www-data $PROJECT_DIR
chmod +x $PROJECT_DIR/backend/data
chmod +x $PROJECT_DIR/frontend/dist

echo "9. 启动服务..."
systemctl daemon-reload
systemctl enable radio-exam-backend
systemctl start radio-exam-backend
systemctl restart nginx

echo "10. 验证部署..."
sleep 3

# 检查服务状态
if systemctl is-active --quiet radio-exam-backend; then
    echo "✓ 后端服务启动成功"
else
    echo "✗ 后端服务启动失败"
    systemctl status radio-exam-backend
fi

if systemctl is-active --quiet nginx; then
    echo "✓ Nginx服务启动成功"
else
    echo "✗ Nginx服务启动失败"
    systemctl status nginx
fi

# 测试API
if curl -s http://localhost:5001/api/questions > /dev/null; then
    echo "✓ 后端API响应正常"
else
    echo "✗ 后端API响应异常"
fi

# 测试Nginx代理
if curl -s http://localhost/radio/api/questions > /dev/null; then
    echo "✓ Nginx代理正常"
else
    echo "✗ Nginx代理异常"
fi

echo ""
echo "=== 部署完成 ==="
echo "访问地址: http://8.138.207.21/radio"
echo "默认管理员账号: 17610788168 / administrator"
echo "默认用户密码: wxd666a"
echo ""
echo "常用命令:"
echo "查看后端日志: journalctl -u radio-exam-backend -f"
echo "重启后端服务: systemctl restart radio-exam-backend"
echo "重启Nginx: systemctl restart nginx"