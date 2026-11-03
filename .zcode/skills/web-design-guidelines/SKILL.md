---
name: web-design-guidelines
description: "Vercel 官方 Web 界面设计指南审计工具。按 Vercel 工程团队标准审查 UI 代码的设计合规性、可访问性、UX 最佳实践。以 file:line 简洁格式输出问题与修复建议。设计、可访问性、UX 三维度全覆盖，支持指定文件路径或 glob 模式进行批量审查。"
---

# Web Interface Guidelines

> **适用性说明（ai-web 项目）**：
> 
> 本技能定位为 **UI 审计/审查工具**，与以下技能互补而非重叠：
> - `frontend-design`：**设计生成** - 从需求生成前端代码
> - `ui-ux-pro-max`：**设计系统** - 提供设计规范和组件库
> - **本技能**：**设计审查** - 审计已有代码的设计质量
>
> **建议使用场景**：
> - 代码 Review 时检查 UI 合规性
> - 可访问性（a11y）审计
> - UX 最佳实践检查
>
> **注意**：本技能主要输出问题列表和修复建议，不直接生成代码。

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Usage

When a user provides a file or pattern argument:

1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.

## Review Focus Areas

### Design Compliance
- Spacing scale consistency (8px baseline grid)
- Typography scale usage (not arbitrary font sizes)
- Color palette adherence to design tokens
- Component elevation (shadows) hierarchy
- Border radius scale consistency
- Icon usage & sizing consistency

### Accessibility (A11y)
- Color contrast ratios (4.5:1 minimum for body text)
- Focus states visible for keyboard users
- Alt text for meaningful images
- Semantic HTML structure (button, nav, main, etc.)
- ARIA labels for icon-only buttons
- Form labels associated with inputs
- Tab order matches visual order
- `prefers-reduced-motion` respect

### UX Best Practices
- Hover/active/pressed states for interactive elements
- Loading states (skeletons > spinners)
- Empty state design
- Error state messaging & positioning
- Touch targets ≥ 44x44px
- Cursor: pointer on clickable elements
- Button disabled state during async ops
- Content jumping prevention (space reservation)
