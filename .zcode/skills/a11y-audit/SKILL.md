---
name: a11y-audit
version: 1.0.0
description: 可访问性审计。WCAG 2.1 AA 合规检查、ARIA 验证、键盘导航测试。确保前端组件可访问。
---

# 可访问性审计技能

## 定位

系统化检查前端项目的可访问性合规情况，覆盖 WCAG 2.1 AA 标准。

## 审计工具

### 1. 自动化扫描

```bash
# axe-core CLI 扫描
npx @axe-devtools/cli http://localhost:5173

# Lighthouse 可访问性审计
npx lighthouse http://localhost:5173 --only-categories=accessibility

# Playwright + axe 集成
npx @axe-core/playwright
```

### 2. 手动检查

- 键盘导航测试（Tab / Shift+Tab / Enter / Esc / Arrow）
- 屏幕阅读器测试（NVDA / VoiceOver）
- 颜色对比度检查（DevTools Accessibility 面板）
- 缩放测试（200% 放大后布局不崩溃）

## 审计清单

### A. 可感知

- [ ] 所有 `<img>` 有 `alt` 属性（装饰性图片用 `alt=""`）
- [ ] 所有 `<button>` 有可读的文本或 `aria-label`
- [ ] 所有 `<a>` 链接文本有意义（非"点击这里"）
- [ ] 表单控件有关联的 `<label>`
- [ ] 颜色对比度 ≥ 4.5:1（正常文本）/ 3:1（大文本）
- [ ] 信息不仅依赖颜色传达（有图标或文字辅助）

### B. 可操作

- [ ] 所有交互元素可通过键盘操作
- [ ] Tab 顺序符合阅读顺序
- [ ] 无键盘陷阱（焦点可自由移出组件）
- [ ] 可见焦点指示器（`:focus-visible` 样式）
- [ ] 跳过导航链接（"跳到主内容"）
- [ ] 页面标题有意义

### C. 可理解

- [ ] `<html lang="zh-CN">` 已设置
- [ ] 表单错误提示清晰
- [ ] 输入有 placeholder 或 label 说明
- [ ] 组件行为可预测（一致的设计模式）

### D. 健壮

- [ ] HTML 语义化标签正确使用
- [ ] ARIA 属性正确（role、aria-label、aria-describedby）
- [ ] DOM 结构合理（无多余的嵌套 div）
- [ ] 动态内容有 `aria-live` 通知

## React/antd 专项检查

### 组件级检查

```tsx
// ✅ 正确：语义化标签
<button onClick={handleClick}>提交</button>

// ❌ 错误：用 div 模拟 button
<div onClick={handleClick} role="button">提交</div>
// 问题：缺少键盘事件、tabindex、焦点管理

// ✅ 正确：Modal 有 title 和关闭机制
<Modal title="编辑评测" open={open} onCancel={handleClose}>

// ❌ 错误：Modal 无 title
<Modal open={open}>
  <div>内容</div>
</Modal>
// 问题：屏幕阅读器无法识别 Modal 用途

// ✅ 正确：表单 label 关联
<Form.Item label="评测名称" name="title">
  <Input />
</Form.Item>

// ❌ 错误：无 label
<Form.Item name="title">
  <Input placeholder="名称" />
</Form.Item>
// 问题：屏幕阅读器无法获知输入框用途
```

### antd 组件可访问性规则

| 组件 | 必要属性 | 检查项 |
|------|---------|--------|
| Modal | `title` | 有标题、Esc 可关闭、焦点管理 |
| Drawer | `title` | 有标题、Esc 可关闭 |
| Table | `title`(列) | 列有标题、可被屏幕阅读器读取 |
| Form | `label` | 每个 Form.Item 有 label |
| Image | `alt` | 有替代文字 |
| Tooltip | 关联元素 | 关联目标有 `aria-describedby` |
| Tabs | `tabBar` | Tab 有文本、键盘可切换 |

## 审计报告模板

```markdown
## 可访问性审计报告 - [日期]

### 审计范围
- 页面: [页面列表]
- 工具: axe-core + Lighthouse + 手动检查

### 自动扫描结果
| 页面 | axe 问题数 | Lighthouse 得分 |
|------|-----------|----------------|
| /eval/list | 3 | 85 |
| /eval/detail | 1 | 92 |

### 问题清单

#### 问题 1 [Critical]
- **页面**: /eval/list
- **规则**: button-name
- **描述**: 按钮元素无可用名称
- **修复**: 添加 `aria-label` 或可见文本

#### 问题 2 [Serious]
- **页面**: /eval/list
- **规则**: color-contrast
- **描述**: 文本对比度 3.2:1，低于 4.5:1
- **修复**: 调整文本颜色或背景色

### 总结
- 通过率: 85%
- 需修复: 3 个 Critical，1 个 Serious
- Critical 问题需在当前迭代修复
```
