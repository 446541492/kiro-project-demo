#!/bin/bash
# 一键启动前后端服务

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🚀 启动后端服务..."
cd "$PROJECT_ROOT/backend"
"$PROJECT_ROOT/.venv/bin/uvicorn" app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"

echo "🚀 启动前端服务..."
cd "$PROJECT_ROOT/frontend"
npx vite --host --port 5173 &
FRONTEND_PID=$!
echo "   前端 PID: $FRONTEND_PID"

echo ""
echo "✅ 服务已启动"
echo "   后端: http://localhost:8000"
echo "   前端: http://localhost:5173"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获退出信号，同时关闭前后端
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
