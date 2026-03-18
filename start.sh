#!/bin/bash

echo "=================================="
echo "量化策略回测平台启动脚本"
echo "=================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js 16+"
    exit 1
fi

echo "正在启动后端服务..."
cd backend
pip3 install -q -r ../requirements.txt
python3 app.py &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID)"
echo ""

sleep 3

echo "正在启动前端服务..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "首次运行，正在安装前端依赖..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!
echo "前端服务已启动 (PID: $FRONTEND_PID)"
echo ""

echo "=================================="
echo "启动完成！"
echo "后端服务: http://localhost:5000"
echo "前端服务: http://localhost:5173"
echo "=================================="
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待进程结束
wait $BACKEND_PID $FRONTEND_PID
