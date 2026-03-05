#!/bin/bash
# 停止前后端服务

echo "🛑 停止后端服务..."
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "   后端已停止" || echo "   后端未运行"

echo "🛑 停止前端服务..."
pkill -f "vite" 2>/dev/null && echo "   前端已停止" || echo "   前端未运行"

echo "✅ 所有服务已停止"
