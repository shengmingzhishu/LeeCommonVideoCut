---
alwaysApply: false
description: 可访问性（a11y）规则，包括 WCAG 2.1 AA 合规、ARIA 规范、键盘导航。涉及前端组件开发、UI 实现时使用此规则。
---

# 可访问性规则（React 技术栈层）

> 前端项目必须遵守 WCAG 2.1 AA 级合规要求。

## 1. WCAG 2.1 AA 核心原则

### 1.1 可感知（Perceivable）

- 所有非文本内容提供替代文字（`alt` 属性）
- 视频/音频提供字幕或文字版
- 颜色不仅是传达信息的唯一手段
- 文本与背景对比度 ≥ 4.5:1（正常文本），≥ 3:1（大文本）

### 1.2 可操作（Operable）

- 所有功能可通过键盘操作
- 无键盘陷阱（焦点可自由移入移出）
- 跳过导航链接（"跳到主内容"链接）
- 页面标题描述清晰

### 1.3 可理解（Understandable）

- 语言声明：`<html lang="zh-CN">`
- 输入错误提供明确提示
- 组件 label 与控件关联

### 1.4 健壮（Robust）

- HTML 语义化标签优先
- ARIA 属性正确使用
- 兼容辅助技术

## 2. React/antd 实现规则

### 2.1 语义化 HTML

```tsx
// 正确
<nav aria-label="主导航">...</nav>
<main>...</main>
<article>...</article>
<button onClick={...}>...</button>

// 错误
<div onClick={...} role="button">...</div>  // 禁止用 div 模拟 button
```

### 2.2 antd 组件可访问性

- Form.Item 必须设置 `label`，不使用 `noLabel` 除非有视觉替代
- Table 列必须设置 `title`（列标题）
- Modal 必须设置 `title` 和 `aria-modal`
- Image 必须设置 `alt` 属性
- Tooltip 必须关联目标元素

### 2.3 键盘导航

| 组件 | 键盘支持 |
|------|---------|
| Modal | Esc 关闭，Tab 在 Modal 内循环 |
| Dropdown | 上下箭头导航，Enter 选择，Esc 关闭 |
| Table | 上下箭头切换行 |
| Tab | 左右箭头切换 Tab |
| Drawer | Esc 关闭 |

### 2.4 焦点管理

- 路由切换时焦点移到页面顶部或主内容区
- Modal 打开时焦点移到 Modal 内第一个可聚焦元素
- Modal 关闭时焦点返回触发元素
- 禁止 `outline: none`（除非有替代的 focus 样式）

## 3. 对比度要求

| 文本类型 | 最小对比度 |
|---------|-----------|
| 正常文本（< 18px） | 4.5:1 |
| 大文本（≥ 18px 或 14px+bold） | 3:1 |
| 界面组件边界 | 3:1 |
| 非文本内容 | 3:1 |

使用工具：`@axe-devtools/cli` 或浏览器 DevTools 的 Accessibility 面板检查。

## 4. 测试要求

- E2E 测试中包含键盘导航测试
- CI 中运行 axe-core 自动扫描
- 严重 a11y 问题与功能 bug 同等优先级
