#!/bin/bash

echo "启动业余无线电考试系统..."

# 启动后端
echo "启动后端服务..."
./start_backend.sh &

# 等待后端启动
sleep 3

# 启动前端
echo "启动前端服务..."
cd frontend
npm run dev

echo "系统启动完成！"
echo "后端地址：http://localhost:5000"
echo "前端地址：http://localhost:3000"