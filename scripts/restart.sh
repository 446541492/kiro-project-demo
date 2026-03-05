#!/bin/bash
# 重启前后端服务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔄 重启服务..."
echo ""

# 先停止
"$SCRIPT_DIR/stop.sh"

echo ""
sleep 1

# 再启动
"$SCRIPT_DIR/start.sh"
