@echo off
echo 启动业余无线电考试系统...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

REM 启动后端
echo 启动后端服务器...
cd backend
start /b python app.py

REM 等待后端启动
timeout /t 3 /nobreak

REM 安装前端依赖（如果尚未安装）
echo 检查前端依赖...
cd ..\frontend
if not exist "node_modules" (
    echo 安装前端依赖...
    npm install
)

REM 启动前端
echo 启动前端开发服务器...
npm run dev

echo 系统启动完成！
echo 请访问: http://localhost:3000
pause