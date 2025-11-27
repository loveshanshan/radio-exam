#!/bin/bash

# 部署时间限制功能脚本
# 适用于阿里云服务器

echo "开始部署时间限制功能..."

# 设置项目路径
PROJECT_PATH="/opt/radio-exam"

# 1. 备份当前文件
echo "备份当前文件..."
cd $PROJECT_PATH
cp backend/app.py backend/app.py.backup.$(date +%Y%m%d_%H%M%S)
cp -r frontend/src/components frontend/src/components.backup.$(date +%Y%m%d_%H%M%S)

# 2. 停止后端服务
echo "停止后端服务..."
sudo systemctl stop radio-exam

# 3. 更新后端代码
echo "更新后端代码..."
# 这里假设代码已经通过git同步到服务器
# 如果没有，可以手动复制文件

# 4. 安装新的依赖（如果有的话）
echo "检查并安装依赖..."
cd $PROJECT_PATH/backend
source venv/bin/activate
pip install -r requirements.txt

# 5. 重启后端服务
echo "重启后端服务..."
sudo systemctl start radio-exam
sudo systemctl enable radio-exam

# 6. 检查服务状态
echo "检查服务状态..."
sudo systemctl status radio-exam

# 7. 重新构建前端
echo "重新构建前端..."
cd $PROJECT_PATH/frontend
npm run build

# 8. 重启nginx
echo "重启nginx..."
sudo systemctl restart nginx
sudo systemctl status nginx

echo "部署完成！"
echo "请访问 http://your-domain.com 测试新功能"
echo "新功能包括："
echo "- 用户时间限制设置"
echo "- 密码修改功能"
echo "- 账号到期检查"
echo "- 管理员时间管理"