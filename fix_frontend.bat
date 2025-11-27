@echo off
echo 修复前端构建问题...

REM 进入前端目录
cd frontend

REM 清理缓存和依赖
echo 清理缓存...
if exist "node_modules\.cache" rmdir /s /q "node_modules\.cache"
if exist "dist" rmdir /s /q "dist"

REM 重新安装依赖
echo 重新安装依赖...
npm install

REM 清理npm缓存
npm cache clean --force

echo 修复完成！
echo.
echo 现在可以运行：npm run dev
echo.
pause