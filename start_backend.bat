@echo off
echo 启动后端服务...

REM 检查虚拟环境
if not exist "venv" (
    echo 虚拟环境不存在，请先运行 install_dependencies.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 进入后端目录
cd backend

REM 检查依赖
echo 检查依赖...
python -c "import jwt" 2>nul
if errorlevel 1 (
    echo 安装缺失的依赖...
    pip install -r requirements.txt
)

REM 启动应用
echo 启动应用...
python app.py

pause