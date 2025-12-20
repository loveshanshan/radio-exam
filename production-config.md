# 业余无线电考试系统生产环境配置

## 服务器信息
- 云服务器IP: 8.138.207.21
- 访问根目录: http://8.138.207.21/radio

## 端口配置
- 前端开发服务器: 3001
- 后端API服务器: 5001
- Nginx代理端口: 80

## 项目路径
- 项目代码路径: /opt/radio-exam
- 前端构建输出: /opt/radio-exam/frontend/dist
- 后端服务: /opt/radio-exam/backend/app.py
- 数据存储: /opt/radio-exam/backend/data/

## 系统服务
- 后端服务: radio-exam-backend (systemd)
- Web服务: nginx
- Python虚拟环境: /opt/radio-exam/venv

## 默认认证信息
- 管理员账号: 17610788168 / administrator
- 用户默认密码: wxd666a