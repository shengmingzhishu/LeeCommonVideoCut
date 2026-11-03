---
name: frontend-design
version: 1.1.0
lastUpdated: 2026-09-03
description: "Anthropic 官方前端设计 Skill。反 AI 通用美学，生成有个性、有品牌视觉识别度的生产级前端界面。强调字体、配色、动效、空间构图，拒绝 Inter 字体、紫色渐变等俗套 AI 设计模式。适用于组件/页面/应用设计任务。"
depends_on:
  - ui-ux-pro-max  # 当需要具体 Token 值（配色/字体/间距）时引用
conflicts_with:
  - ui-ux-pro-max  # 仅在设计哲学层面重叠（前者=创意方向，后者=规则库）
complementary_to:
  - model-design  # model-design 处理独立 HTML 原型，frontend-design 处理 React 组件设计
---

# Frontend Design

> **v1.1 更新 (2026-09-03)**：添加依赖声明、与 ui-ux-pro-max 的分工说明、触发优先级规则。

## 定位与分工

**本 Skill 的核心价值 = 设计哲学 + 创意方向**，而非具体的 CSS 变量值。

### 与 ui-ux-pro-max 的分工

| 维度 | frontend-design（本 Skill） | ui-ux-pro-max |
|------|---------------------------|---------------|
| **核心输出** | 设计理念、品牌识别度、视觉个性 | 具体Token值（颜色代码、字体名、间距px） |
| **回答的问题** | "这个产品应该看起来什么样？" | "具体用什么颜色/字体/间距？" |
| **适用场景** | 需要独特视觉风格、品牌差异化 | 需要具体CSS变量、Design System |
| **不做什么** | 不提供具体的 hex 色值、font-family 名 | 不提供创意方向指导 |

### 何时联合使用

1. 用户要求"设计一个有品牌感的页面" → 先用 **frontend-design** 确定设计方向（极简/活泼/暗色等），再引用 **ui-ux-pro-max** 获取具体 Token 值
2. 用户仅要求"给我一套蓝色系配色方案" → 直接用 **ui-ux-pro-max**，无需 frontend-design
3. 用户要求"帮我设计一个不像 AI 生成的页面" → 用 **frontend-design**（这是它的核心强项）

## 触发优先级

当用户说"设计前端/UI"时：
- 有明确产出物（原型文件/文档）→ 优先 `model-design` 或 `docs-design`
- 无明确产出物，强调"品牌感/个性/不像AI" → 用 **frontend-design**
- 强调"具体配色/字体/规范" → 用 **ui-ux-pro-max`

Approach this as the design lead at a small studio known for giving every client a visual identity that could not be mistaken for anyone else's. This client has already rejected proposals that felt templated or AI-generic — they're looking for something bold, distinctive, and thoughtfully considered.

## Ground it in the subject

If the brief does not pin down what the product or subject is, pin it yourself before designing: name one concrete subject, its audience, and the page's single job, and state your choice. If there's a real client context, use that; otherwise invent a plausible one.

## Design principles

**For web designs, the hero is a thesis.** Open with the most characteristic thing in the subject's world, in whatever form makes sense for it: a headline, an image, an animation, a live demo, an interactive widget. Whatever you choose must feel inevitable given the subject.

**Typography carries the personality of the page.** Pair the display and body faces deliberately, not the same families you would reach for on any other project, and set a clear type scale with intention. Let headlines breathe and let body copy have a comfortable rhythm.

**Structure is information.** Structural devices, numbering, eyebrows, dividers, labels, should encode something true about the content, not decorate it. Many generic designs use numbered markers (01 / 02) just because; here numbers, sections, and layout choices should reflect actual relationships in the material.

**Leverage motion deliberately.** Think about where and if animation can serve the subject: a page-load sequence, a scroll-triggered reveal, hover micro-interactions, ambient atmosphere. An orchestrated motion plan beats random bounce-in animations by orders of magnitude.

**Match complexity to the vision.** Maximalist directions need elaborate execution; minimal directions need precision in spacing, type, and detail. Elegance is executing the chosen vision well, not simply choosing "minimal" or "maximal."

**Consider written content carefully.** Often a design brief may not contain real content, and it's up to you to come up with copy. Copy can make a design feel as templated as the design itself. See the section below for more guidance on writing in design.

## Process: brainstorm, explore, plan, critique, build, critique again

Work in two passes. First, **brainstorm a short design plan** based on the human's design brief: create a compact token system with color, type, layout, and signature.
- **Color:** describe the palette as 4–6 named colors with hex codes, including background, foreground, accent, and neutral tones.
- **Type:** specify font families for headings and body, plus sizes/weights for key scales.
- **Layout:** define grid structure, max widths, and how sections relate.
- **Signature:** identify one memorable device unique to this skill's output style (e.g., irregular grids, oversized typography, kinetic backgrounds).

Then review that plan against the brief before building: if any part of it reads like the generic default you would produce for any similar page, revise until the direction feels specific and earned.

When writing the code, be careful of structuring your CSS selector specificities. It's easy to generate CSS classes that cancel each other out (especially with a type-based selector like .section and another class), so keep selectors straightforward and consistent.

Try to do a lot of this planning and iteration in your thinking, and only show ideas to the user when you have higher confidence it'll delight them.

## Restraint and self-critique

**Spend your boldness in one place.** Let the signature element be the one memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Not taking enough risks is better than taking too many unrelated ones.

## More on writing in design

Words appear in a design for one reason: to make it easier to understand, and therefore easier to use. They are design material, not decoration. Bring the same intentionality to copy that you would bring to kerning.

**Write from the end user's side of the screen.** Name things by what people control and recognize, never by how the system is built. A person manages notifications, not webhook config. Describe what some feature enables rather than listing technical capabilities.

**Use active voice as default.** A control should say exactly what happens when it's used: "Save changes," not "Submit." An action keeps the same name through the whole flow, so the button that says "Publish draft" doesn't later become "Update" mid-process unless there's a good reason.

**Treat failure and emptiness as moments for direction, not mood.** Explain what went wrong and how to fix it, in the interface's voice rather than a person's. Errors don't apologize, and they are never very cute either.

**Keep the register conversational and tuned:** plain verbs, sentence case, no filler, with tone matched to the brand and the audience. Let each element do exactly one job. A label labels, an example demonstrates, a CTA invites action.
