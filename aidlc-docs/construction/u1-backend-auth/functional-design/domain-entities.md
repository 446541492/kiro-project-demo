# U1 领域实体设计 - 后端认证模块

## 实体关系图

```
+------------------+       +------------------+
|      User        |       |     Device       |
+------------------+       +------------------+
| id: int (PK)    |<---+  | id: int (PK)    |
| username: str    |    |  | user_id: int (FK)|---+
| email: str?      |    |  | device_id: str   |
| phone: str?      |    |  | device_name: str |
| password_hash:str|    |  | ip_address: str  |
| is_active: bool  |    |  | last_login_at:dt |
| is_2fa_enabled:  |    |  | created_at: dt   |
|   bool           |    |  +------------------+
| totp_secret: str?|    |
| failed_login_    |    |  +------------------+
|   count: int     |    |  |  RecoveryCode   |
| locked_until: dt?|    |  +------------------+
| created_at: dt   |    +--| id: int (PK)    |
| updated_at: dt   |       | user_id: int(FK)|
+------------------+       | code: str       |
                            | is_used: bool   |
                            | used_at: dt?    |
                            | created_at: dt  |
                            +------------------+
```

---

## 实体详细定义

### 1. User（用户）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | 主键，自增 | 用户唯一标识 |
| username | String(50) | 唯一，非空 | 用户名，登录标识 |
| email | String(100) | 唯一，可空 | 邮箱地址 |
| phone | String(20) | 唯一，可空 | 手机号 |
| password_hash | String(128) | 非空 | bcrypt 加密后的密码哈希 |
| is_active | Boolean | 默认 True | 账户是否激活 |
| is_2fa_enabled | Boolean | 默认 False | 是否启用两步验证 |
| totp_secret | String(32) | 可空 | TOTP 密钥（加密存储） |
| failed_login_count | Integer | 默认 0 | 连续登录失败次数 |
| locked_until | DateTime | 可空 | 账户锁定截止时间 |
| created_at | DateTime | 非空，自动 | 创建时间 |
| updated_at | DateTime | 非空，自动 | 更新时间 |

**业务约束**:
- username 长度 3-50 字符，仅允许字母、数字、下划线
- email 和 phone 至少填写一个
- email 格式必须合法
- phone 格式支持中国大陆手机号（11 位数字）

### 2. Device（设备）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | 主键，自增 | 设备记录唯一标识 |
| user_id | Integer | 外键(users.id)，非空 | 关联用户 |
| device_id | String(64) | 非空 | 设备唯一标识（浏览器指纹） |
| device_name | String(100) | 非空 | 设备名称（User-Agent 解析） |
| ip_address | String(45) | 可空 | 登录 IP 地址 |
| last_login_at | DateTime | 非空 | 最后登录时间 |
| created_at | DateTime | 非空，自动 | 首次登录时间 |

**业务约束**:
- 同一用户的 device_id 唯一（联合唯一约束：user_id + device_id）
- 设备名称从 User-Agent 自动解析

### 3. RecoveryCode（恢复码）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | 主键，自增 | 恢复码唯一标识 |
| user_id | Integer | 外键(users.id)，非空 | 关联用户 |
| code | String(16) | 非空 | 恢复码（加密存储） |
| is_used | Boolean | 默认 False | 是否已使用 |
| used_at | DateTime | 可空 | 使用时间 |
| created_at | DateTime | 非空，自动 | 创建时间 |

**业务约束**:
- 每个用户最多 8 个有效恢复码
- 恢复码为 8 位随机字母数字组合
- 使用后标记为已用，不可重复使用
- 重新生成恢复码时，旧的全部失效
