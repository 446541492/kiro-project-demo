# U1 非功能性设计 - 后端认证模块

## 1. 安全架构设计

### 1.1 密码安全

```
用户密码 -> bcrypt(password, salt, cost=12) -> password_hash
                                                    |
                                                    v
                                              存储到数据库
```

**实现要点**:
- 使用 `bcrypt` 库的 `hashpw()` 和 `checkpw()` 方法
- cost factor = 12（约 300ms 计算时间，安全性和性能的平衡）
- bcrypt 自动生成 salt，无需单独管理

### 1.2 JWT Token 架构

```
登录成功
  |
  v
生成 Access Token                    生成 Refresh Token
  - payload:                           - payload:
    user_id: int                         user_id: int
    username: str                        token_type: "refresh"
    token_type: "access"                 exp: 当前时间 + 7 天
    exp: 当前时间 + 15 分钟              iat: 当前时间
    iat: 当前时间
  |                                    |
  v                                    v
HS256 签名(JWT_SECRET_KEY)           HS256 签名(JWT_SECRET_KEY)
  |                                    |
  v                                    v
返回给前端                            返回给前端
  |                                    |
  v                                    v
存储在内存（Zustand）                 存储在 localStorage
每次请求携带 Authorization 头         Token 刷新时使用
```

**Token 刷新策略**:
```
前端请求 -> 401 响应（Access Token 过期）
  |
  v
前端自动使用 Refresh Token 请求 /api/auth/refresh
  |
  v
后端验证 Refresh Token
  - 有效: 生成新 Access Token，返回
  - Refresh Token 剩余 < 1 天: 同时返回新 Refresh Token
  - 无效/过期: 返回 401，前端跳转登录页
```

### 1.3 2FA 安全设计

```
TOTP 密钥生成
  |
  v
PyOTP.random_base32() -> 20 字节随机密钥
  |
  v
生成 provisioning URI
  otpauth://totp/StocksAssist:{username}?secret={secret}&issuer=StocksAssist
  |
  v
qrcode 库生成二维码 PNG -> Base64 编码 -> 返回前端
  |
  v
用户扫码后输入验证码 -> PyOTP.TOTP(secret).verify(code, valid_window=1)
  |
  v
验证通过 -> 保存 totp_secret 到数据库
```

### 1.4 请求频率限制设计

```
请求到达 -> 提取客户端 IP
  |
  v
检查内存计数器（字典: {ip: {count, reset_time}}）
  |
  v
count >= 10 且 当前时间 < reset_time
  -> 是: 返回 429 Too Many Requests
  -> 否: count += 1，继续处理请求
  |
  v
当前时间 >= reset_time -> 重置计数器（count=1, reset_time=当前时间+60秒）
```

**实现方式**: 使用 FastAPI 中间件 + 内存字典（适合单实例部署）

---

## 2. 错误处理设计

### 2.1 统一异常处理

```python
# 自定义异常类层次
AppException (基类)
  ├── AuthenticationError (401)    # 认证失败
  ├── AuthorizationError (403)     # 权限不足
  ├── ConflictError (409)          # 资源冲突
  ├── LockedError (423)            # 账户锁定
  ├── PreconditionError (428)      # 需要验证码
  └── RateLimitError (429)         # 频率限制
```

**异常处理中间件**:
```
请求处理过程中抛出异常
  |
  v
全局异常处理器捕获
  |
  v
AppException -> 返回对应 HTTP 状态码 + { detail, code }
ValidationError -> 返回 422 + 字段级错误信息
其他异常 -> 记录日志 + 返回 500 + { detail: "服务器内部错误" }
```

### 2.2 日志设计

```
日志级别:
  - DEBUG: 详细调试信息（仅开发环境）
  - INFO: 关键业务操作（注册、登录、2FA 操作）
  - WARNING: 异常但可恢复的情况（登录失败、Token 过期）
  - ERROR: 错误和异常

日志格式:
  [时间] [级别] [模块] [消息] [上下文]
  2026-03-05 10:30:00 INFO auth_service 用户登录成功 user_id=1

敏感信息过滤:
  - 密码: 不记录
  - Token: 仅记录前 8 位
  - TOTP 密钥: 不记录
  - 恢复码: 不记录
```

## 3. 数据库设计

### 3.1 连接管理

```
应用启动
  |
  v
创建 AsyncEngine (aiosqlite)
  |
  v
创建 AsyncSessionLocal (sessionmaker)
  |
  v
每个请求:
  get_db() 依赖注入 -> 创建 AsyncSession
    -> 请求处理
    -> 正常: commit
    -> 异常: rollback
    -> 最终: close session
```

### 3.2 数据库初始化

```
首次启动
  |
  v
检查 data/database.db 是否存在
  |
  v
不存在 -> 创建数据库文件
  -> 执行 Base.metadata.create_all() 创建所有表
  -> 插入初始测试数据（可选）
  |
  v
已存在 -> 直接使用
```

### 3.3 初始测试数据

```
测试用户:
  - username: admin
    email: admin@example.com
    phone: 13800000001
    password: Admin@123456
    is_2fa_enabled: false

  - username: testuser
    email: test@example.com
    phone: 13800000002
    password: Test@123456
    is_2fa_enabled: false

默认自选组合:
  - 每个用户创建 "我的自选" 默认组合
```

## 4. CORS 设计

```
CORS 中间件配置:
  - allow_origins: ["http://localhost:5173"]（前端开发地址）
  - allow_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
  - allow_headers: ["Authorization", "Content-Type"]
  - allow_credentials: true
  - max_age: 600（预检请求缓存 10 分钟）
```

## 5. 依赖注入设计

```
FastAPI Depends 链:

get_db() -> AsyncSession
  用于所有需要数据库访问的路由

get_current_user(token, db) -> User
  1. 从 Authorization 头提取 Token
  2. 解码 JWT Token
  3. 查询数据库获取用户
  4. 验证用户状态
  5. 返回 User 对象

get_current_active_user(user) -> User
  1. 调用 get_current_user
  2. 检查 is_active == True
  3. 返回活跃用户
```

## 6. 测试策略设计

### 6.1 测试架构

```
tests/
├── conftest.py          # 共享 fixtures
│   ├── test_db          # 内存 SQLite 测试数据库
│   ├── test_client      # httpx AsyncClient
│   ├── test_user        # 预创建的测试用户
│   └── auth_headers     # 带 Token 的请求头
├── test_auth.py         # 认证 API 测试
│   ├── test_register    # 注册测试（正常/重复/格式错误）
│   ├── test_login       # 登录测试（正常/错误密码/锁定）
│   ├── test_refresh     # Token 刷新测试
│   ├── test_logout      # 登出测试
│   └── test_me          # 获取用户信息测试
├── test_2fa.py          # 2FA 测试
│   ├── test_enable      # 启用 2FA 测试
│   ├── test_verify      # 验证 TOTP 测试
│   ├── test_disable     # 禁用 2FA 测试
│   └── test_recovery    # 恢复码测试
└── test_password.py     # 密码相关测试
    ├── test_change      # 修改密码测试
    └── test_validation  # 密码策略验证测试
```

### 6.2 测试数据库策略

```
每个测试函数:
  1. 创建内存 SQLite 数据库
  2. 创建所有表
  3. 插入测试数据（通过 fixture）
  4. 执行测试
  5. 自动清理（内存数据库随会话销毁）
```
