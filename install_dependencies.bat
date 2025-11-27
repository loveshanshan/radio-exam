@echo off
echo 安装项目依赖...

REM 检查是否存在虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装根目录依赖
echo 安装根目录依赖...
pip install -r requirements.txt

REM 安装后端依赖
echo 安装后端依赖...
cd backend
pip install -r requirements.txt
cd ..

echo 依赖安装完成！
echo.
echo 运行后端服务：
echo call venv\Scripts\activate.bat
echo cd backend
echo python app.py
echo.
pause