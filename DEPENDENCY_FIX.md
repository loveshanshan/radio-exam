# 依赖问题解决方案

## 问题描述
运行后端时出现 `ModuleNotFoundError: No module named 'jwt'` 错误。

## 解决方案

### 方法1：使用安装脚本（推荐）

#### Windows系统
```bash
# 运行安装脚本
install_dependencies.bat

# 启动后端
start_backend.bat
```

#### Linux系统
```bash
# 给脚本执行权限
chmod +x install_dependencies.sh start_backend.sh

# 运行安装脚本
./install_dependencies.sh

# 启动后端
./start_backend.sh
```

### 方法2：手动安装

#### 1. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate.bat

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 2. 安装依赖
```bash
# 安装根目录依赖
pip install -r requirements.txt

# 安装后端依赖
cd backend
pip install -r requirements.txt
cd ..
```

#### 3. 启动应用
```bash
cd backend
python app.py
```

### 方法3：直接安装缺失的模块
```bash
# 激活虚拟环境后
pip install PyJWT==2.8.0
```

## 依赖文件说明

### 根目录 requirements.txt
```
blinker==1.9.0
click==8.3.0
colorama==0.4.6
Flask==3.1.2
flask-cors==6.0.1
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.3
Werkzeug==3.1.3
PyJWT==2.8.0
```

### backend/requirements.txt
```
flask==3.1.2
flask-cors==6.0.1
PyJWT==2.8.0
```

## 常见问题

### Q: 为什么会有两个requirements.txt文件？
A: 根目录的包含所有项目依赖，backend目录的只包含后端运行所需的核心依赖。

### Q: 虚拟环境有什么用？
A: 虚拟环境可以隔离项目依赖，避免与系统Python环境冲突。

### Q: 如何检查依赖是否安装成功？
A: 运行以下命令：
```bash
python -c "import jwt; print('JWT模块安装成功')"
```

### Q: 如果还有其他模块缺失怎么办？
A: 查看错误信息，使用 `pip install 模块名` 安装对应的模块。

## 开发环境设置

### Windows开发环境
1. 安装Python 3.8+
2. 运行 `install_dependencies.bat`
3. 使用 `start_backend.bat` 启动后端

### Linux开发环境
1. 安装Python 3.8+和pip
2. 运行 `chmod +x *.sh && ./install_dependencies.sh`
3. 使用 `./start_backend.sh` 启动后端

### 生产环境部署
参考 `DEPLOY_TIME_FEATURES.md` 中的部署说明。