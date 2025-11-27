# 时间限制功能部署指南

## 快速部署步骤

### 1. 服务器端部署

```bash
# 进入项目目录
cd /opt/radio-exam

# 备份当前版本
cp backend/app.py backend/app.py.backup.$(date +%Y%m%d_%H%M%S)

# 停止后端服务
sudo systemctl stop radio-exam

# 更新代码（如果使用git）
git pull origin master

# 或者手动上传文件到服务器

# 安装依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start radio-exam
sudo systemctl status radio-exam
```

### 2. 前端部署

```bash
# 进入前端目录
cd /opt/radio-exam/frontend

# 重新构建
npm run build

# 重启nginx
sudo systemctl restart nginx
sudo systemctl status nginx
```

### 3. 验证部署

访问你的网站，检查以下功能：

1. **管理员登录**：17610788168 / administrator
2. **用户管理**：能否添加带时间限制的用户
3. **密码修改**：普通用户能否修改密码
4. **时间显示**：是否显示剩余天数和到期时间

## 新增文件说明

### 后端文件
- `backend/app.py` - 更新了用户认证和时间限制逻辑

### 前端文件
- `frontend/src/components/PasswordChangeComponent.vue` - 密码修改组件
- `frontend/src/components/UserManagementComponent.vue` - 更新了用户管理组件，支持时间设置
- `frontend/src/App.vue` - 更新了主应用，显示时间信息和密码修改入口

### 测试和部署文件
- `test_time_features.py` - 功能测试脚本
- `deploy-time-features.sh` - 自动部署脚本
- `TIME_FEATURES_README.md` - 详细功能说明

## 注意事项

1. **数据库兼容性**：现有用户数据完全兼容，新用户可以设置时间限制
2. **管理员权限**：管理员账号不受时间限制
3. **默认密码**：新用户和重置密码的默认密码都是 `wxd666a`
4. **时间格式**：使用标准ISO格式，支持精确到秒

## 回滚方案

如果部署出现问题，可以快速回滚：

```bash
# 停止服务
sudo systemctl stop radio-exam

# 恢复后端文件
cp backend/app.py.backup.20241127_HHMMSS backend/app.py

# 重启服务
sudo systemctl start radio-exam

# 恢复前端（如果需要）
cd frontend
git checkout HEAD~1 -- src/
npm run build
sudo systemctl restart nginx
```

## 测试新功能

运行测试脚本验证功能：

```bash
cd /opt/radio-exam
python test_time_features.py
```

该脚本会测试：
- 管理员登录
- 创建带时间限制的用户
- 用户时间限制检查
- 密码修改功能
- 时间更新功能

## 常见问题

### Q: 现有用户会受影响吗？
A: 不会。现有用户如果没有设置时间限制，将继续正常使用。

### Q: 如何设置永久有效的用户？
A: 创建用户时不设置到期时间，或者设置一个很远的未来时间。

### Q: 时间格式有什么要求？
A: 使用ISO 8601格式，如：2024-01-01T00:00:00

### Q: 管理员需要时间限制吗？
A: 不需要。管理员账号自动跳过时间限制检查。