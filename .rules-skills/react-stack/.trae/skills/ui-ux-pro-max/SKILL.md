---
name: ui-ux-pro-max
version: 1.1.0
lastUpdated: 2026-09-03
description: "UI/UX Pro Max 专业设计智能。含 50+ 风格、97 配色、57 字体搭配、99 UX 规则、25 图表类型，跨 9 技术栈(html-tailwind/react/nextjs/vue/svelte/shadcn 等)。8 大类按优先级：可访问性(CRITICAL)/触摸交互(CRITICAL)/性能(HIGH)/布局响应(HIGH)/字体配色(MEDIUM)/动画(MEDIUM)/风格选择(MEDIUM)/图表(LOW)。4 步工作流：分析需求→生成 Design System(MASTER.md + 页面 Overrides)→分域精细搜索→技术栈指南。含交付前 Checklist（视觉/交互/深浅色/布局/可访问性）。"
role: design-system  # 核心角色：设计系统规则库（被其他 Skill 依赖）
consumed_by:
  - model-design  # 原型设计的 Design System 来源
  - docs-design   # 设计文档的 Design System 来源
  - frontend-design  # 可选：当需要具体 Token 值时引用
---

# UI/UX Pro Max - Design Intelligence

> **v1.1 更新 (2026-09-03)**：添加角色定位声明、被依赖关系说明。

## 核心定位：设计系统规则库

**本 Skill 是"基础设施级"Skill** —— 提供具体的设计 Token 值（颜色、字体、间距、效果），被其他 Skill 消费：

- `model-design` 和 `docs-design` **强制依赖**本 Skill 作为 Design System 来源
- `frontend-design` **可选依赖**本 Skill（当需要从"设计哲学"落地到"具体Token"时）

**本 Skill 通常不被直接触发**，而是作为其他 Skill 的底层支撑。但当用户明确要求"给我一套配色方案"/"推荐字体搭配"时可直接使用。

Comprehensive design guide for web and mobile applications. Contains 50+ styles, 97 color palettes, 57 font pairings, 99 UX guidelines, and 25 chart types across 9 technology stacks. Searchable database with priority-based recommendations.

## When to Apply

Reference these guidelines when:
- Designing new UI components or pages
- Choosing color palettes and typography
- Reviewing code for UX issues
- Building landing pages or dashboards
- Implementing accessibility requirements

## Rule Categories by Priority

| Priority | Category | Impact | Domain |
|---|---|---|---|
| 1 | Accessibility | CRITICAL | ux |
| 2 | Touch & Interaction | CRITICAL | ux |
| 3 | Performance | HIGH | ux |
| 4 | Layout & Responsive | HIGH | ux |
| 5 | Typography & Color | MEDIUM | typography, color |
| 6 | Animation | MEDIUM | ux |
| 7 | Style Selection | MEDIUM | style, product |
| 8 | Charts & Data | LOW | chart |

## Quick Reference

### 1. Accessibility (CRITICAL)
- **color-contrast** — Minimum 4.5:1 ratio for normal text
- **focus-states** — Visible focus rings on interactive elements
- **alt-text** — Descriptive alt text for meaningful images
- **aria-labels** — aria-label for icon-only buttons
- **keyboard-nav** — Tab order matches visual order
- **form-labels** — Use label with for attribute

### 2. Touch & Interaction (CRITICAL)
- **touch-target-size** — Minimum 44x44px touch targets
- **hover-vs-tap** — Use click/tap for primary interactions
- **loading-buttons** — Disable button during async operations
- **error-feedback** — Clear error messages near problem
- **cursor-pointer** — Add cursor-pointer to clickable elements

### 3. Performance (HIGH)
- **image-optimization** — Use WebP, srcset, lazy loading
- **reduced-motion** — Check prefers-reduced-motion
- **content-jumping** — Reserve space for async content

### 4. Layout & Responsive (HIGH)
- **viewport-meta** — width=device-width initial-scale=1
- **readable-font-size** — Minimum 16px body text on mobile
- **horizontal-scroll** — Ensure content fits viewport width
- **z-index-management** — Define z-index scale (10, 20, 30, 50)

### 5. Typography & Color (MEDIUM)
- **line-height** — Use 1.5-1.75 for body text
- **line-length** — Limit to 65-75 characters per line
- **font-pairing** — Match heading/body font personalities

### 6. Animation (MEDIUM)
- **duration-timing** — Use 150-300ms for micro-interactions
- **transform-performance** — Use transform/opacity, not width/height
- **loading-states** — Skeleton screens or spinners

### 7. Style Selection (MEDIUM)
- **style-match** — Match style to product type
- **consistency** — Use same style across all pages
- **no-emoji-icons** — Use SVG icons, not emojis

### 8. Charts & Data (LOW)
- **chart-type** — Match chart type to data type
- **color-guidance** — Use accessible color palettes
- **data-table** — Provide table alternative for accessibility

## Workflow

When user requests UI/UX work (design, build, create, implement, review, fix, improve), follow this workflow:

### Step 1: Analyze User Requirements

Extract key information from user request:
- **Product type**: SaaS, e-commerce, portfolio, dashboard, landing page, etc.
- **Style keywords**: minimal, playful, professional, elegant, dark mode, etc.
- **Industry**: healthcare, fintech, gaming, education, etc.
- **Stack**: React, Vue, Next.js, or default to html-tailwind

### Step 2: Generate Design System (REQUIRED)

Match design to product type and industry:

**Color Palette Selection**:
- SaaS/Dashboard: Neutral base (Zinc/Slate) + 1 accent (Blue/Emerald/Teal/Rose)
- E-commerce: Warm neutrals + accent (Amber/WarmRed)
- Healthcare: Cool blue base + mint accents
- Fintech: Deep navy + gold/emerald accents
- Portfolio/Agency: Bold accent, high contrast, experimental typography
- Landing: Hero-optimized, higher visual weight

**Typography Scale**:
- Headline: `text-4xl md:text-6xl font-bold tracking-tight`
- H2: `text-2xl md:text-3xl font-bold tracking-tight`
- H3: `text-xl font-semibold`
- Body: `text-base leading-relaxed`
- Caption: `text-sm text-gray-500`

**Spacing & Layout**:
- 8px grid baseline
- Container: `max-w-6xl mx-auto px-4`
- Section gap: `py-16 md:py-24`
- Card gap: `gap-4 md:gap-6`

**Effects**:
- Shadow: `shadow-sm hover:shadow-md transition-shadow`
- Radius: `rounded-xl` for cards, `rounded-lg` for buttons
- Transitions: `transition-all duration-200 ease-out`

### Step 3: Supplement with Domain-Specific Details

**Style Library**:
- **Minimal/Professional**: White bg, gray typography, 1 accent, generous whitespace, no decoration
- **Playful/Vibrant**: Gradient accents, rounded shapes, soft shadows, illustration-friendly, 2 accent colors
- **Elegant/Luxury**: Serif headings, ample whitespace, thin borders, gold/champagne accents
- **Dark Mode**: Zinc-900 base, tinted white text (not pure #fff), subtle borders (white/5-10)
- **Glassmorphism**: `backdrop-blur-lg bg-white/80 border border-white/20 shadow-xl`
- **Brutalist**: Hard borders, no shadows, high contrast, bold typography, monospace numbers
- **Editorial/Magazine**: Serif display + sans body, asymmetric layouts, pull quotes, large leading
- **Retro/Futuristic**: Neon glow accents (use sparingly!), cyberpunk color, monospaced + bold display
- **Bento Grid**: Asymmetric tile layout, Apple Control Center style, varied spans, 1px borders
- **Organic/Natural**: Hand-drawn feel, rounded shapes, warm earth tones, micro textures

**Anti-Patterns**:
- ❌ Inter + Purple gradient (AI tell)
- ❌ 3 equal columns cards (banned)
- ❌ Emojis as icons (banned)
- ❌ Centered text hero over dark image
- ❌ Generic "John Doe" / "Acme Inc" names
- ❌ `h-screen` instead of `min-h-[100dvh]` (iOS jump)
- ❌ Unsplash links (broken) → use picsum.photos/seed/xxx

### Step 4: Stack Guidelines (Default: html-tailwind)

**Available Stacks**: html-tailwind, react, nextjs, vue, svelte, swiftui, react-native, flutter, shadcn, jetpack-compose

**React/Next.js specific rules**:
- Client components: `'use client'` only where needed (interactivity/motion)
- Server components for all static layout sections
- Global state → only when deep prop drilling would occur
- Image component: `next/image` with proper alt + sizes

## Professional UI Rules

### Icons & Visual Elements

| Rule | Do | Don't |
|---|---|---|
| No emoji icons | Use SVG icons (Heroicons/Lucide/Simple Icons) | Use 🎨🚀⚙️ as UI icons |
| Stable hover states | Use color/opacity transitions on hover | Use scale transforms that shift layout |
| Correct brand logos | Research official SVG from Simple Icons | Guess or use incorrect logo paths |
| Consistent icon sizing | Use fixed viewBox (24x24) with w-6 h-6 | Mix different icon sizes randomly |

### Interaction & Cursor

| Rule | Do | Don't |
|---|---|---|
| Cursor pointer | Add cursor-pointer to all clickable/hoverable cards | Leave default cursor on interactive elements |
| Hover feedback | Provide visual feedback (color, shadow, border) | No indication element is interactive |
| Smooth transitions | Use `transition-colors duration-200` | Instant state changes or >500ms |

### Light/Dark Mode Contrast

| Rule | Do | Don't |
|---|---|---|
| Glass card light mode | Use `bg-white/80` or higher opacity | Use `bg-white/10` (too transparent) |
| Text contrast light | Use `slate-900` for text | Use `slate-400` for body text |
| Muted text light | Use `slate-600` minimum | gray-400 or lighter |
| Border visibility | Use `border-gray-200` in light mode | Use `border-white/10` (invisible in light) |

### Layout & Spacing

| Rule | Do | Don't |
|---|---|---|
| Floating navbar | Add `top-4 left-4 right-4` spacing | Stick navbar to `top-0 left-0 right-0` |
| Content padding | Account for fixed navbar height | Let content hide behind fixed elements |
| Consistent max-width | Use same `max-w-6xl` or `max-w-7xl` | Mix different container widths randomly |

## Pre-Delivery Checklist

### Visual Quality
- [ ] No emojis used as icons (use SVG instead)
- [ ] All icons from consistent icon set (Heroicons/Lucide)
- [ ] Brand logos are correct (verified from Simple Icons)
- [ ] Hover states don't cause layout shift
- [ ] Use theme colors directly (bg-primary) not var() wrapper

### Interaction
- [ ] All clickable elements have cursor-pointer
- [ ] Hover states provide clear visual feedback
- [ ] Transitions are smooth (150-300ms)
- [ ] Focus states visible for keyboard navigation

### Light/Dark Mode
- [ ] Light mode text has sufficient contrast (4.5:1 minimum)
- [ ] Glass/transparent elements visible in light mode
- [ ] Borders visible in both modes
- [ ] Test both modes before delivery

### Layout
- [ ] Floating elements have proper spacing from edges
- [ ] No content hidden behind fixed navbars
- [ ] Responsive at 375px, 768px, 1024px, 1440px
- [ ] No horizontal scroll on mobile

### Accessibility
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is not the only indicator
- [ ] prefers-reduced-motion respected
