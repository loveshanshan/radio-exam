# 时间限制功能说明

## 新增功能

### 1. 用户时间限制管理
- **管理员功能**：可以为普通用户设置使用时间范围
- **开始时间**：用户账号生效时间
- **到期时间**：用户账号失效时间
- **实时检查**：用户登录和操作时自动检查时间限制

### 2. 密码修改功能
- **普通用户**：可以修改自己的密码
- **管理员**：可以重置普通用户的密码为默认密码（wxd666a）

### 3. 账号状态显示
- **剩余天数**：显示账号还有多少天到期
- **到期时间**：显示具体的到期日期
- **过期提醒**：账号到期时显示警告信息

## 使用说明

### 管理员操作

#### 1. 创建带时间限制的用户
1. 登录管理员账号
2. 进入"用户管理"页面
3. 点击"添加用户"
4. 填写手机号
5. 设置开始时间和到期时间
6. 点击确认创建

#### 2. 修改用户时间限制
1. 在用户列表中找到目标用户
2. 点击"设置时间"按钮
3. 修改开始时间和/或到期时间
4. 点击确认保存

#### 3. 重置用户密码
1. 在用户列表中找到目标用户
2. 点击"重置密码"按钮
3. 确认重置，密码将重置为 `wxd666a`

### 普通用户操作

#### 1. 修改密码
1. 登录系统
2. 进入"修改密码"标签页
3. 输入当前密码
4. 输入新密码并确认
5. 点击"修改密码"

#### 2. 查看账号状态
- 登录后，页面顶部会显示剩余天数和到期时间
- 如果账号已过期，会弹出提示信息

## API 接口

### 新增接口

#### 1. 修改密码
```
POST /api/auth/change-password
Content-Type: application/json
Authorization: Bearer <token>

{
  "old_password": "旧密码",
  "new_password": "新密码"
}
```

#### 2. 更新用户时间限制
```
POST /api/auth/update-user-time/<user_id>
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "start_time": "2024-01-01T00:00:00",
  "expire_time": "2024-02-05T23:59:59"
}
```

#### 3. 检查用户访问权限
```
GET /api/auth/user-access
Authorization: Bearer <token>

Response:
{
  "success": true,
  "access": true,
  "message": "访问正常",
  "days_left": 30,
  "expire_time": "2024-02-05T23:59:59"
}
```

### 修改的接口

#### 1. 用户登录
现在返回时间限制信息：
```json
{
  "success": true,
  "token": "jwt_token",
  "user": {
    "user_id": "user_001",
    "phone": "13800138000",
    "is_admin": false,
    "days_left": 30,
    "expire_time": "2024-02-05T23:59:59"
  }
}
```

#### 2. 添加用户
现在支持时间限制参数：
```json
POST /api/auth/register
{
  "phone": "13800138000",
  "start_time": "2024-01-01T00:00:00",
  "expire_time": "2024-02-05T23:59:59"
}
```

#### 3. 获取用户列表
现在返回时间限制和状态信息：
```json
{
  "users": [
    {
      "user_id": "user_001",
      "phone": "13800138000",
      "is_admin": false,
      "start_time": "2024-01-01T00:00:00",
      "expire_time": "2024-02-05T23:59:59",
      "access_status": "valid",
      "days_left": 30,
      "status": "active",
      "created_at": "2024-01-01T10:00:00"
    }
  ]
}
```

## 数据结构变化

### 用户数据结构
```json
{
  "user_id": "user_001",
  "phone": "13800138000",
  "password": "hashed_password",
  "is_admin": false,
  "created_at": "2024-01-01T10:00:00",
  "status": "active",
  "start_time": "2024-01-01T00:00:00",  // 新增
  "expire_time": "2024-02-05T23:59:59"  // 新增
}
```

## 部署说明

### 1. 后端部署
```bash
# 停止服务
sudo systemctl stop radio-exam

# 更新代码
cd /opt/radio-exam
git pull origin master

# 安装依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start radio-exam
```

### 2. 前端部署
```bash
cd /opt/radio-exam/frontend
npm run build
sudo systemctl restart nginx
```

### 3. 测试功能
运行测试脚本：
```bash
cd /opt/radio-exam
python test_time_features.py
```

## 注意事项

1. **时间格式**：使用 ISO 8601 格式（YYYY-MM-DDTHH:mm:ss）
2. **管理员权限**：管理员不受时间限制
3. **默认密码**：新用户和重置密码的默认密码都是 `wxd666a`
4. **过期检查**：所有需要认证的API都会检查用户时间限制
5. **兼容性**：现有用户如果没有设置时间限制，将正常使用

## 故障排除

### 1. 用户无法登录
- 检查用户状态是否为 'active'
- 检查是否在时间限制范围内
- 检查密码是否正确

### 2. 时间设置不生效
- 确认时间格式正确
- 检查开始时间是否早于到期时间
- 重新登录用户以刷新状态

### 3. 前端显示异常
- 检查浏览器控制台错误
- 确认API响应格式正确
- 重新构建前端代码