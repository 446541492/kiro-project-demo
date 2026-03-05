# 语言规范 (Language Guidelines)

## 主要语言

项目的所有交流、文档和代码注释统一使用中文。

## 适用范围

### AI 助手回复
- 所有与用户的对话必须使用中文
- 技术解释和建议使用中文表达
- 错误信息和警告使用中文

### 文档
- 需求文档使用中文
- 设计文档使用中文
- 用户手册使用中文
- README 和项目说明使用中文
- API 文档使用中文

### 代码注释
- 函数和类的注释使用中文
- 复杂逻辑的行内注释使用中文
- TODO 和 FIXME 注释使用中文

### 代码命名
- 变量名、函数名、类名使用英文（遵循编程规范）
- 常量和配置项可以使用英文
- 用户界面相关的字符串使用中文

## 示例

### 好的做法 ✓

```typescript
// 用户登录组件
interface UserLoginProps {
  onSuccess: () => void;  // 登录成功回调
  onError: (error: string) => void;  // 登录失败回调
}

/**
 * 格式化价格显示
 * @param price - 原始价格
 * @param decimals - 小数位数
 * @returns 格式化后的价格字符串
 */
function formatPrice(price: number, decimals: number = 2): string {
  // 处理无效输入
  if (isNaN(price)) {
    return '--';
  }
  
  // 格式化为指定小数位
  return price.toFixed(decimals);
}
```

### 避免的做法 ✗

```typescript
// User login component (英文注释)
interface UserLoginProps {
  onSuccess: () => void;
  onError: (error: string) => void;
}

/**
 * Format price for display
 * @param price - raw price value
 * @returns formatted price string
 */
function formatPrice(price: number): string {
  return price.toFixed(2);
}
```

## 例外情况

以下情况可以使用英文：

- 第三方库和框架的标准术语（React, TypeScript, API 等）
- 技术专有名词（HTTP, WebSocket, JWT 等）
- 代码中的标识符（变量名、函数名、类名）
- Git 提交信息可以使用英文或中文
- 依赖包名称和配置文件

## 注意事项

- 保持专业和清晰的表达
- 避免使用网络俚语或过于口语化的表达
- 技术术语优先使用业界通用的中文翻译
- 如果某个技术概念没有合适的中文翻译，可以使用英文原文并在首次出现时加以说明

## 质量标准

- 语法正确，表达清晰
- 术语使用一致
- 注释简洁但信息完整
- 文档结构清晰，易于阅读
