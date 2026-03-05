# U5 业务逻辑模型 - 前端认证与个人中心

## 1. 登录流程

```
[LoginPage]
  用户输入用户名和密码
    |
    v
  表单验证（前端校验）
    -> 失败: 显示字段错误提示
    |
    v
  检查是否需要滑块验证码（失败次数 >= 3）
    -> 需要: 显示 SliderCaptcha 组件
    -> 用户完成滑块验证 -> 获取 captcha_token
    |
    v
  调用 authStore.login({ username, password, captcha_token })
    |
    v
  响应处理:
    -> requires_2fa == true:
      - 显示 2FA 验证码输入框
      - 用户输入 6 位验证码
      - 调用 authStore.verify2FA(code)
      - 成功: 跳转首页
      - 失败: 显示错误，可重试
    -> requires_2fa == false:
      - 登录成功，自动跳转首页
    -> 错误:
      - 显示错误信息
      - 递增失败计数
```

## 2. 注册流程

```
[RegisterPage]
  用户填写注册表单
    |
    v
  表单验证:
    - 用户名: 3-50 字符，字母数字下划线
    - 密码: 8+ 字符，大小写 + 数字 + 特殊字符
    - 确认密码: 与密码一致
    - 邮箱: 可选，格式验证
    - 手机: 可选，格式验证
    -> 失败: 显示字段错误提示
    |
    v
  显示 SliderCaptcha 组件
    -> 用户完成滑块验证
    |
    v
  调用 authStore.register({ username, password, email, phone })
    |
    v
  响应处理:
    -> 成功: 自动登录，跳转首页
    -> 错误: 显示错误信息（如用户名已存在）
```

## 3. 个人中心

```
[ProfilePage]
  加载用户信息 (authStore.user)
    |
    v
  展示功能列表:
    - 用户信息（用户名、邮箱、手机、注册时间）
    - 修改密码
    - 两步验证设置（已启用/未启用）
    - 登录设备管理
    - 主题切换
    - 退出登录

[修改密码]
  用户输入当前密码和新密码
    -> 表单验证
    -> 调用 PUT /api/auth/password
    -> 成功: 提示修改成功
    -> 失败: 显示错误信息

[退出登录]
  调用 authStore.logout()
    -> 清除状态
    -> 跳转登录页
```

## 4. 两步验证设置

```
[TwoFactorSetupPage]
  检查 2FA 状态 (user.is_2fa_enabled)
    |
    v
  未启用:
    - 显示"启用两步验证"按钮
    - 点击 -> 调用 POST /api/auth/2fa/enable
    - 显示二维码和密钥
    - 用户扫码后输入验证码确认
    - 调用 POST /api/auth/2fa/verify 确认启用
    - 显示恢复码列表，提示用户保存
    |
  已启用:
    - 显示"禁用两步验证"按钮
    - 点击 -> 弹出验证码输入框
    - 用户输入当前验证码
    - 调用 POST /api/auth/2fa/disable
    - 成功: 更新状态
```

## 5. 滑块验证码

```
[SliderCaptcha]
  生成随机拼图位置
    |
    v
  显示背景图 + 拼图块
    |
    v
  用户拖动滑块
    -> 记录拖动轨迹
    -> 释放时计算偏移量
    |
    v
  前端验证:
    - 偏移量误差 < 5px
    - 拖动时间 > 300ms（防机器人）
    - 轨迹非直线（有自然抖动）
    |
    v
  验证通过: 生成 captcha_token -> 回调 onSuccess
  验证失败: 重新生成拼图 -> 回调 onFail
```

## 6. 设备管理

```
[设备列表]
  调用 GET /api/auth/devices
    -> 显示设备列表（设备名、IP、最后登录时间）
    -> 当前设备标记
```
