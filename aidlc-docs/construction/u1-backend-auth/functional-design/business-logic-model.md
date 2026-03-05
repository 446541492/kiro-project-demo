# U1 业务逻辑模型 - 后端认证模块

## 1. 注册流程

```
输入: username, password, email?, phone?
  |
  v
[验证输入格式]
  - username: 3-50 字符，字母/数字/下划线
  - password: 满足密码策略
  - email: 合法邮箱格式（如提供）
  - phone: 11 位手机号（如提供）
  - email 和 phone 至少填一个
  |
  v
[检查唯一性]
  - username 是否已存在 -> 是: 返回错误 "用户名已被注册"
  - email 是否已存在 -> 是: 返回错误 "邮箱已被注册"
  - phone 是否已存在 -> 是: 返回错误 "手机号已被注册"
  |
  v
[创建用户]
  - 使用 bcrypt 加密密码（cost factor = 12）
  - is_active = True
  - is_2fa_enabled = False
  - failed_login_count = 0
  |
  v
[创建默认自选组合]
  - 调用 PortfolioService.create_default_portfolio(user_id)
  - 组合名称: "我的自选"
  - is_default = True
  |
  v
[生成 Token]
  - 生成 Access Token（有效期 15 分钟）
  - 生成 Refresh Token（有效期 7 天）
  |
  v
[记录设备信息]
  - 解析 User-Agent 获取设备名称
  - 记录 device_id、ip_address
  |
  v
输出: { access_token, refresh_token, user }
```

## 2. 登录流程

```
输入: username, password, device_id?, captcha_token?
  |
  v
[查找用户]
  - 按 username 查找
  - 未找到 -> 返回错误 "用户名或密码错误"
  |
  v
[检查账户状态]
  - is_active == False -> 返回错误 "账户已被禁用"
  - locked_until > 当前时间 -> 返回错误 "账户已锁定，请X分钟后重试"
  - locked_until <= 当前时间 -> 重置锁定状态
  |
  v
[检查是否需要验证码]
  - failed_login_count >= 3 -> 验证 captcha_token
    - captcha_token 无效 -> 返回错误 "请完成验证码验证"
  |
  v
[验证密码]
  - bcrypt 验证密码
  - 验证失败:
    - failed_login_count += 1
    - failed_login_count >= 5:
      - locked_until = 当前时间 + 15 分钟
      - 返回错误 "连续登录失败过多，账户已锁定 15 分钟"
    - failed_login_count >= 3:
      - 返回错误 "用户名或密码错误，请完成验证码验证"
    - 否则:
      - 返回错误 "用户名或密码错误"
  |
  v
[密码验证成功]
  - 重置 failed_login_count = 0
  - 清除 locked_until
  |
  v
[检查 2FA 状态]
  - is_2fa_enabled == True:
    - 返回 { requires_2fa: true, temp_token: "..." }
    - temp_token 有效期 5 分钟，仅用于 2FA 验证
  - is_2fa_enabled == False:
    - 继续生成正式 Token
  |
  v
[生成 Token]
  - 生成 Access Token（有效期 15 分钟）
  - 生成 Refresh Token（有效期 7 天）
  |
  v
[记录设备信息]
  - 检查 device_id 是否已存在
  - 已存在: 更新 last_login_at
  - 不存在: 创建新设备记录
  |
  v
输出: { access_token, refresh_token, user }
```

## 3. 2FA 验证流程（登录第二步）

```
输入: temp_token, totp_code
  |
  v
[验证 temp_token]
  - 解码 temp_token
  - 检查是否过期（5 分钟）
  - 提取 user_id
  |
  v
[验证 TOTP 码]
  - 获取用户的 totp_secret
  - 使用 PyOTP 验证 totp_code
  - 允许前后 1 个时间窗口的偏差（30 秒窗口）
  |
  v
[TOTP 验证失败]
  - 检查是否为恢复码
  - 查找用户未使用的恢复码
  - 匹配成功:
    - 标记恢复码为已使用（is_used = True, used_at = 当前时间）
    - 继续生成 Token
  - 匹配失败:
    - 返回错误 "验证码错误"
  |
  v
[生成正式 Token]
  - 生成 Access Token
  - 生成 Refresh Token
  |
  v
输出: { access_token, refresh_token, user }
```

## 4. Token 刷新流程

```
输入: refresh_token
  |
  v
[验证 Refresh Token]
  - 解码 Token
  - 检查是否过期
  - 提取 user_id
  - Token 无效/过期 -> 返回 401 错误
  |
  v
[检查用户状态]
  - 查找用户
  - is_active == False -> 返回 401 错误
  |
  v
[生成新 Token]
  - 生成新的 Access Token（有效期 15 分钟）
  - Refresh Token 保持不变（除非即将过期）
  - 如果 Refresh Token 剩余有效期 < 1 天，同时刷新 Refresh Token
  |
  v
输出: { access_token, refresh_token? }
```

## 5. 启用 2FA 流程

```
输入: 当前用户（已认证）
  |
  v
[检查 2FA 状态]
  - is_2fa_enabled == True -> 返回错误 "2FA 已启用"
  |
  v
[生成 TOTP 密钥]
  - 使用 PyOTP 生成随机密钥（base32 编码）
  - 临时保存密钥（不写入数据库）
  |
  v
[生成二维码]
  - 格式: otpauth://totp/StocksAssist:{username}?secret={secret}&issuer=StocksAssist
  - 生成二维码图片（Base64 PNG）
  |
  v
输出: { secret, qr_code_base64, provisioning_uri }
  |
  v
[等待用户验证]
  - 用户扫码后输入验证码
  |
  v
输入: totp_code, secret
  |
  v
[验证首次 TOTP 码]
  - 使用提供的 secret 验证 totp_code
  - 验证失败 -> 返回错误 "验证码错误，请重试"
  |
  v
[保存 2FA 设置]
  - totp_secret = secret（加密存储）
  - is_2fa_enabled = True
  |
  v
[生成恢复码]
  - 生成 8 个随机恢复码（8 位字母数字）
  - 加密存储到 RecoveryCode 表
  |
  v
输出: { recovery_codes: [...] }
```

## 6. 禁用 2FA 流程

```
输入: 当前用户, totp_code
  |
  v
[检查 2FA 状态]
  - is_2fa_enabled == False -> 返回错误 "2FA 未启用"
  |
  v
[验证 TOTP 码]
  - 验证当前验证码
  - 验证失败 -> 返回错误 "验证码错误"
  |
  v
[禁用 2FA]
  - is_2fa_enabled = False
  - totp_secret = None
  - 删除所有恢复码
  |
  v
输出: { message: "2FA 已禁用" }
```

## 7. 修改密码流程

```
输入: 当前用户, old_password, new_password
  |
  v
[验证旧密码]
  - bcrypt 验证 old_password
  - 验证失败 -> 返回错误 "当前密码错误"
  |
  v
[验证新密码]
  - 检查密码策略（最少 8 位，大小写+数字+特殊字符）
  - 新密码不能与旧密码相同
  |
  v
[更新密码]
  - 使用 bcrypt 加密新密码
  - 更新 password_hash
  - 更新 updated_at
  |
  v
输出: { message: "密码修改成功" }
```

## 8. 设备记录逻辑

```
[登录时记录设备]
  - 从请求头获取 User-Agent
  - 解析设备名称（浏览器 + 操作系统）
  - 从请求获取 IP 地址
  - 从请求头或 Cookie 获取 device_id
    - 如果没有 device_id，生成新的 UUID
  |
  v
[查找设备记录]
  - 按 user_id + device_id 查找
  - 已存在: 更新 last_login_at, ip_address, device_name
  - 不存在: 创建新记录
  |
  v
[获取设备列表]
  - 按 user_id 查询所有设备
  - 按 last_login_at 降序排列
  - 返回设备列表
```
