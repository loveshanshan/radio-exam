# 端口修改总结

## 已修改的配置文件

### 1. 前端配置
- **文件**: `frontend/vite.config.js`
- **修改内容**:
  - 开发服务器端口: 3000 → 3001
  - 代理目标: `http://localhost:5000` → `http://localhost:5001`

### 2. 后端配置  
- **文件**: `backend/app.py`
- **修改内容**:
  - 服务端口: 5000 → 5001
  - 控制台输出信息更新为新端口

### 3. 部署脚本
- **文件**: `p_build.sh`
- **修改内容**: API测试端口: 5000 → 5001

- **文件**: `rebuild.sh`  
- **修改内容**: API测试端口: 5000 → 5001

## 新增的部署配置文件

### 1. 生产环境配置
- **文件**: `production-config.md`
- **内容**: 服务器信息和端口配置说明

### 2. Nginx配置模板
- **文件**: `nginx-config.conf`
- **用途**: 云服务器Nginx反向代理配置
- **路径映射**: `/radio/` → `/opt/radio-exam/frontend/dist/`
- **API代理**: `/radio/api/` → `http://localhost:5001/api/`

### 3. Systemd服务配置
- **文件**: `radio-exam-backend.service`
- **用途**: 后端服务systemd配置
- **工作目录**: `/opt/radio-exam/backend`
- **虚拟环境**: `/opt/radio-exam/venv`

### 4. 部署脚本
- **文件**: `deploy.sh`
- **用途**: 云服务器一键部署脚本
- **功能**: 自动安装依赖、构建、配置服务

## 云服务器部署要求

### 系统服务配置
1. **Nginx配置**:
   ```bash
   sudo cp nginx-config.conf /etc/nginx/sites-available/radio-exam
   sudo ln -s /etc/nginx/sites-available/radio-exam /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

2. **后端服务配置**:
   ```bash
   sudo cp radio-exam-backend.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable radio-exam-backend
   sudo systemctl start radio-exam-backend
   ```

### 防火墙配置
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

### 端口映射
- 用户访问: `http://8.138.207.21/radio`
- Nginx监听: `80`
- 后端服务: `localhost:5001`
- 前端开发: `localhost:3001` (仅开发时使用)

### 验证命令
```bash
# 检查后端服务
curl http://localhost:5001/api/questions

# 检查Nginx代理
curl http://localhost/radio/api/questions

# 查看服务状态
sudo systemctl status radio-exam-backend
sudo systemctl status nginx
```

## 注意事项

1. **生产环境**: 前端通过Nginx提供静态文件，不需要运行开发服务器
2. **开发环境**: 前端运行在3001端口，后端运行在5001端口
3. **数据目录**: 确保`/opt/radio-exam/backend/data/`目录有写入权限
4. **日志查看**: `journalctl -u radio-exam-backend -f`