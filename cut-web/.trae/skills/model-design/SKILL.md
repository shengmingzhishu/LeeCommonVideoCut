---
name: model-design
version: 1.1.0
lastUpdated: 2026-09-03
description: "HTML 原型设计与维护技能。深度集成 ui-ux-pro-max 设计系统，从需求到生成/迭代 HTML 原型文件。适用于页面设计、原型改动、UI 布局调整。"
depends_on:
  - ui-ux-pro-max  # 强制依赖：Design System 来源（配色/字体/间距/效果）
complementary_to:
  - docs-design  # docs-design 处理项目级文档（内嵌原型），model-design 处理独立原型文件
conflicts_with:
  - frontend-design  # 轻微冲突：两者都涉及页面设计，但产出形式不同（HTML vs React）
---

# Model Design — HTML 原型设计与维护

> **v1.1 更新 (2026-09-03)**：添加依赖声明、与 docs-design/frontend-design 的分工说明。

> **适用性说明（ai-eval-web 项目）**：
>
> **⚠️ 有限适用**：本项目使用 React + JSX/TSX，本技能主要生成纯 HTML 原型。
>
> **适用场景**：
> - 快速原型设计（与产品/设计师沟通前）
> - HTML 邮件模板
> - 静态文档页面
> - 不需要交互的展示性页面
>
> **不适用场景**：
> - React 组件开发（应使用 `frontend-design`）
> - 需要状态管理的交互页面
> - 需要路由跳转的多页面应用
>
> **建议**：仅在需要快速 HTML 原型时启用此技能，日常 React 开发使用 `frontend-design`。

## 核心定位

从**需求理解**到**设计系统生成**到**HTML 原型输出**到**迭代维护**的完整工作流。深度集成 `ui-ux-pro-max`，每次生成前自动提取配色/字体/风格/规则，确保输出一致且专业。

## 触发条件

- "设计一个页面/原型/UI"
- "模仿这个网站的设计"
- "改一下这个页面的布局"
- "加一个功能模块到页面里"
- "帮我画个原型"

## 五步工作流

### Step 1: 项目分析（内置）

1. **检测 HTML 文件**：扫描项目中的 `.html` 文件
2. **提取页面结构**：读取已有 HTML，理解布局、组件、样式
3. **识别设计风格**：配色、字体、间距、组件风格
4. **输出分析摘要**：页面清单 + 结构概要 + 设计风格总结

### Step 2: 需求理解

从用户输入中提取：
- **产品类型**：SaaS / 电商 / 作品集 / 仪表盘 / 落地页 / 个人主页 / 工具集
- **风格关键词**：极简 / 活泼 / 优雅 / 暗色 / 玻璃态 / Bento / 编辑风
- **行业**：医疗 / 金融 / 教育 / 游戏 / 通用
- **功能模块**：需要包含哪些功能区域
- **参考**：用户提供的 URL / 截图 / 描述

### Step 3: Design System 生成（必须，集成 ui-ux-pro-max）

**生成任何 HTML 之前，必须先执行此步骤。** 调用 `ui-ux-pro-max` 的工作流：

#### 3.1 确定 Design System

读取 `ui-ux-pro-max` SKILL.md，按其 Step 2 流程输出：

| 维度 | 从 ui-ux-pro-max 提取 | 输出 |
|------|----------------------|------|
| 配色 | 按产品类型选配色方案 | 主色 + 辅助色 + 中性色 + 背景色 |
| 字体 | 按风格选字体配对 | 标题字体 + 正文字体 |
| 间距 | 8px 网格基准 | 模块间距 + 组件间距 + 内边距 |
| 效果 | 阴影/圆角/过渡 | 卡片阴影 + 圆角 + 过渡时长 |

#### 3.2 选择风格

从 `ui-ux-pro-max` 风格库中选一个主风格：
- **Minimal/Professional**：白底 + 灰文字 + 1 主色 + 大留白
- **Dark Mode**：深底 + 微白文字 + 微边框 (white/5-10%)
- **Glassmorphism**：`backdrop-blur` + 半透明 + 模糊
- **Bento Grid**：不对称网格 + Apple 控制中心风格
- **Editorial/Magazine**：衬线标题 + 无衬线正文 + 不对称布局
- **Playful/Vibrant**：渐变 + 圆润 + 软阴影 + 2 主色
- **Elegant/Luxury**：衬线标题 + 大留白 + 细边框 + 金色点缀

#### 3.3 转化为 CSS 变量

将提取的 Design System 转为 `:root` 变量，直接用于 HTML：

```css
:root {
    /* === 从 ui-ux-pro-max 配色方案提取 === */
    --c-primary: #4f6df5;        /* 按产品类型选定 */
    --c-primary-light: #eef1fe;
    --c-text: #1a1a2e;
    --c-text-light: #6b7280;
    --c-text-muted: #9ca3af;
    --c-bg: #ffffff;
    --c-bg-soft: #f9fafb;
    --c-border: #e5e7eb;
    /* === 从 ui-ux-pro-max 间距系统提取 === */
    --sp-xs: 8px; --sp-sm: 16px; --sp-md: 24px; --sp-lg: 40px; --sp-xl: 80px;
    /* === 从 ui-ux-pro-max 字体配对提取 === */
    --font-heading: 'Inter', -apple-system, 'PingFang SC', sans-serif;
    --font-body: -apple-system, 'PingFang SC', 'Noto Sans CJK SC', sans-serif;
    --font-mono: 'SF Mono', 'Fira Code', Consolas, monospace;
    /* === 从 ui-ux-pro-max 效果系统提取 === */
    --r-sm: 6px; --r-md: 10px; --r-lg: 16px;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
    --shadow-lg: 0 8px 32px rgba(0,0,0,0.12);
    --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    /* === 响应式断点（来自 ui-ux-pro-max） === */
    --bp-mobile: 375px; --bp-tablet: 768px; --bp-desktop: 1024px; --bp-wide: 1440px;
}
/* === 暗色模式（来自 ui-ux-pro-max Dark Mode 规则） === */
@media (prefers-color-scheme: dark) {
    :root {
        --c-text: #f4f4f5; --c-text-light: #a1a1aa;
        --c-bg: #18181b; --c-bg-soft: #27272a; --c-border: #3f3f46;
    }
}
```

### Step 4: HTML 生成

#### 4.1 文件规范
- 单文件：HTML + 内联 CSS + 内联 JS，可直接浏览器打开
- 文件命名：`{页面名}.html`
- 存放位置：用户指定目录或项目根目录

#### 4.2 HTML 骨架
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{页面标题}</title>
    <style>/* Reset + :root 变量(Step 3) + 布局 + 组件 + 响应式 */</style>
</head>
<body>
    <!-- Header / Nav -->
    <!-- Main Content -->
    <!-- Footer -->
    <script>/* 交互逻辑 */</script>
</body>
</html>
```

#### 4.3 图标规范（来自 ui-ux-pro-max）
- **禁止用 emoji 当图标**：用 SVG（Heroicons / Lucide）
- SVG 统一 `viewBox="0 0 24 24"` + `w-6 h-6`
- 内联 SVG，不依赖外部文件

```html
<!-- ✅ 正确：内联 SVG -->
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
    <path d="m21 21-4.35-4.35"/><circle cx="11" cy="11" r="8"/>
</svg>
<!-- ❌ 错误：emoji 当图标 -->
<span>🔍</span>
```

#### 4.4 响应式断点（来自 ui-ux-pro-max）
```css
/* 移动优先 */
.container { padding: 0 16px; }
/* 平板 */
@media (min-width: 768px) { .container { padding: 0 24px; } }
/* 桌面 */
@media (min-width: 1024px) { .container { max-width: 960px; margin: 0 auto; } }
/* 宽屏 */
@media (min-width: 1440px) { .container { max-width: 1080px; } }
```

#### 4.5 动画规范（来自 ui-ux-pro-max）
- 微交互：150-300ms，`transition-all duration-200 ease-out`
- 只用 `transform` 和 `opacity`，不用 `width/height` 做动画
- 骨架屏或 spinner 用于加载状态
- `@media (prefers-reduced-motion: reduce)` 禁用动画

### Step 5: 迭代维护

- **修改指令**："把搜索框移到顶部"、"改配色为蓝色系"
- **流程**：读取已有 HTML → 理解当前 Design System → 定位修改 → 原地更新 → 重新过反模式检查
- **版本追踪**：HTML 注释记录变更

## 反模式检查（硬规则，来自 ui-ux-pro-max）

生成 HTML 前必须确认不违反：

- ❌ **禁止 emoji 当图标** → 用 SVG（Heroicons / Lucide）
- ❌ **禁止 Inter + 紫色渐变**（AI 告密者）
- ❌ **禁止 3 等宽列卡片布局**
- ❌ **禁止居中文配暗色背景图**
- ❌ **禁止 `h-screen`** → 用 `min-h-[100dvh]`（防 iOS 跳动）
- ❌ **禁止 Unsplash 链接**（会失效）→ 用 `picsum.photos/seed/xxx`
- ❌ **禁止 hover 导致布局偏移** → 用 color/shadow/border 变化

## 交付前检查清单（来自 ui-ux-pro-max）

生成 HTML 后逐项检查：

**视觉质量**
- [ ] 无 emoji 图标，全部用 SVG
- [ ] 图标来自同一套（Heroicons 或 Lucide）
- [ ] hover 不导致布局偏移

**交互**
- [ ] 所有可点击元素有 `cursor: pointer`
- [ ] hover 有清晰视觉反馈
- [ ] 过渡 150-300ms
- [ ] 键盘焦点状态可见

**明暗模式**
- [ ] 文字对比度 ≥ 4.5:1
- [ ] 玻璃/半透明元素在浅色模式可见
- [ ] 边框在明暗模式都可见

**布局**
- [ ] 响应式：375px / 768px / 1024px / 1440px
- [ ] 无移动端横向滚动
- [ ] 固定元素有边距（`top-4 left-4 right-4`）

**可访问性**
- [ ] 图片有 alt 文本
- [ ] 表单输入有 label
- [ ] 颜色不是唯一指示器
- [ ] `prefers-reduced-motion` 已处理

## 输出规范

- 用 `computer://` 链接让用户直接打开
- 涉及参考网站时，先抓取分析其设计风格再生成
- 生成后附 Design System 摘要（配色/风格/字体）
