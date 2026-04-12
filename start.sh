#!/bin/bash

# MiniMax Vision Frontend 启动脚本

echo "=================================="
echo "MiniMax Vision Frontend"
echo "=================================="

# 设置 API Key (如果环境变量未设置)
if [ -z "$MINIMAX_API_KEY" ]; then
    echo "请设置 MINIMAX_API_KEY 环境变量:"
    echo "export MINIMAX_API_KEY=your_api_key"
    echo ""
    echo "或者在运行前设置:"
    echo "MINIMAX_API_KEY=your_key $0"
    exit 1
fi

echo "MINIMAX_API_KEY: ${MINIMAX_API_KEY:0:10}..."

# 启动后端
echo ""
echo "启动后端服务 (port 5000)..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "启动前端开发服务器 (port 5173)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=================================="
echo "服务已启动:"
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:5000"
echo "=================================="
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待信号
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
