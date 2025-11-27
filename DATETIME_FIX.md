# DateTime错误修复指南

## 问题描述
```
AttributeError: type object 'datetime.datetime' has no attribute 'datetime'
```

## 错误原因
在 `generate_token` 函数中使用了错误的datetime语法：
```python
# ❌ 错误用法
'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
```

由于导入语句是 `from datetime import datetime`，所以应该直接使用 `datetime` 而不是 `datetime.datetime`。

## 修复内容

### 1. 修复导入语句
**修复前**:
```python
from datetime import datetime
```

**修复后**:
```python
from datetime import datetime, timedelta
```

### 2. 修复token生成函数
**修复前**:
```python
def generate_token(user_id, phone, is_admin):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'phone': phone,
        'is_admin': is_admin,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # ❌ 错误
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

**修复后**:
```python
def generate_token(user_id, phone, is_admin):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'phone': phone,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(days=7)  # ✅ 正确
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

## DateTime正确用法

### 导入方式1：导入具体类
```python
from datetime import datetime, timedelta

# 使用
now = datetime.utcnow()
future = now + timedelta(days=7)
```

### 导入方式2：导入整个模块
```python
import datetime

# 使用
now = datetime.datetime.utcnow()
future = now + datetime.timedelta(days=7)
```

### 推荐方式
推荐使用第一种方式，因为代码更简洁：
```python
from datetime import datetime, timedelta, timezone
```

## 测试修复

运行测试脚本验证修复：
```bash
cd d:\code\vscode\radio-exam
python test_datetime_fix.py
```

预期输出：
```
开始测试datetime修复...
测试datetime导入和使用...
✓ datetime.utcnow() 成功: 2024-01-01 12:00:00.000000
✓ timedelta 使用成功: 2024-01-08 12:00:00.000000
✓ 时间戳转换成功: 1704681600.0

测试JWT生成...
✓ JWT生成成功: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
✓ JWT解码成功: {'user_id': 'test_user', 'phone': '13800138000', 'is_admin': False, 'exp': 1704681600}

✅ 所有测试通过！datetime问题已修复。
```

## 启动后端服务

修复后，可以正常启动后端服务：

### Windows
```bash
cd d:\code\vscode\radio-exam
start_backend.bat
```

### Linux
```bash
cd /opt/radio-exam
./start_backend.sh
```

### 手动启动
```bash
cd backend
python app.py
```

## 常见DateTime错误

### 1. 混合导入方式
```python
# ❌ 错误
from datetime import datetime
import datetime
# 这会导致命名冲突

# ✅ 正确
from datetime import datetime, timedelta
# 或者
import datetime as dt
```

### 2. 错误的方法调用
```python
# ❌ 错误
datetime.datetime.utcnow()  # 如果已经导入了datetime类

# ✅ 正确
datetime.utcnow()  # 使用from datetime import datetime
```

### 3. 时区问题
```python
# 推荐使用UTC时间
datetime.utcnow()

# 如果需要本地时间
datetime.now()
```

## JWT Token最佳实践

### 1. 设置合理的过期时间
```python
# 短期token（7天）
'exp': datetime.utcnow() + timedelta(days=7)

# 长期token（30天）
'exp': datetime.utcnow() + timedelta(days=30)

# 自定义过期时间
'exp': datetime.utcnow() + timedelta(hours=24)
```

### 2. 包含必要信息
```python
payload = {
    'user_id': user_id,
    'phone': phone,
    'is_admin': is_admin,
    'iat': datetime.utcnow(),  # 签发时间
    'exp': datetime.utcnow() + timedelta(days=7)  # 过期时间
}
```

### 3. 安全密钥
```python
# 使用强密钥
SECRET_KEY = "your_very_long_and_secure_secret_key_here_2024"
```

## 如果问题仍然存在

1. **检查Python版本**：确保使用Python 3.7+
2. **检查依赖**：确保PyJWT已正确安装
3. **检查导入**：确保没有循环导入
4. **重启服务**：修改代码后需要重启服务

## 相关文件

- `backend/app.py` - 主要修复文件
- `test_datetime_fix.py` - 测试脚本
- `requirements.txt` - 依赖文件
- `start_backend.bat` - 启动脚本