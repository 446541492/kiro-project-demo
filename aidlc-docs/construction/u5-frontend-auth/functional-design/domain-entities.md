# U5 领域实体 - 前端认证与个人中心

## 1. 表单数据模型

### LoginFormData（登录表单）
| 字段 | 类型 | 验证规则 | 说明 |
|------|------|---------|------|
| username | string | 必填, 3-50 字符 | 用户名 |
| password | string | 必填, 8-128 字符 | 密码 |
| captcha_token | string | 3 次失败后必填 | 滑块验证码 Token |

### RegisterFormData（注册表单）
| 字段 | 类型 | 验证规则 | 说明 |
|------|------|---------|------|
| username | string | 必填, 3-50 字符, 字母数字下划线 | 用户名 |
| password | string | 必填, 8+ 字符, 大小写+数字+特殊字符 | 密码 |
| confirmPassword | string | 必填, 与 password 一致 | 确认密码 |
| email | string | 可选, 邮箱格式 | 邮箱 |
| phone | string | 可选, 手机号格式 | 手机号 |

### ChangePasswordFormData（修改密码表单）
| 字段 | 类型 | 验证规则 | 说明 |
|------|------|---------|------|
| old_password | string | 必填 | 当前密码 |
| new_password | string | 必填, 8+ 字符, 大小写+数字+特殊字符 | 新密码 |
| confirm_password | string | 必填, 与 new_password 一致 | 确认新密码 |

## 2. 组件 Props

### SliderCaptchaProps
| 属性 | 类型 | 说明 |
|------|------|------|
| onSuccess | (token: string) => void | 验证成功回调 |
| onFail | () => void | 验证失败回调 |

### TwoFactorSetupData
| 字段 | 类型 | 说明 |
|------|------|------|
| qr_code | string | Base64 二维码图片 |
| secret | string | TOTP 密钥 |
| recovery_codes | string[] | 恢复码列表 |
