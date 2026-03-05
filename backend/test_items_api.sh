#!/bin/bash
# 登录获取 token
echo "=== 登录 ==="
LOGIN_RESP=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')
echo "$LOGIN_RESP" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESP"

TOKEN=$(echo "$LOGIN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "登录失败，无法获取 token"
  exit 1
fi

echo ""
echo "=== 获取组合列表 ==="
PORTFOLIOS=$(curl -s http://localhost:8000/api/portfolios \
  -H "Authorization: Bearer $TOKEN")
echo "$PORTFOLIOS" | python3 -m json.tool 2>/dev/null || echo "$PORTFOLIOS"

# 取第一个组合的 ID
PID=$(echo "$PORTFOLIOS" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data[0]['id'] if data else '')" 2>/dev/null)

if [ -z "$PID" ]; then
  echo "没有组合"
  exit 1
fi

echo ""
echo "=== 获取组合 $PID 的标的列表 ==="
ITEMS=$(curl -s "http://localhost:8000/api/portfolios/$PID/items" \
  -H "Authorization: Bearer $TOKEN")
echo "$ITEMS" | python3 -m json.tool 2>/dev/null || echo "$ITEMS"
