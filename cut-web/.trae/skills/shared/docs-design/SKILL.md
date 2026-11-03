---
name: docs-design
description: "项目需求设计文档技能。深度集成 ui-ux-pro-max 设计系统。生成和维护 /docs 下的项目设计文档，集项目说明、功能描述、内嵌可交互原型、交互说明于一体。"
---

# Docs Design — 项目需求设计原型

## 核心定位

生成和维护**项目级设计文档**（位于 `/docs/`，按需求主题 + 尾部序号命名，迭代保留历史版本），一份文档涵盖：
- 项目整体说明（背景、目标、技术栈）
- 功能模块描述（每个功能的文字说明）
- 页面原型展示（内嵌可交互的 HTML 原型）
- 交互说明（操作流程、边界情况、状态流转）

**深度集成 `ui-ux-pro-max`**：每个内嵌原型在生成前自动提取配色/字体/风格/规则，确保所有原型风格统一且专业。

## 触发条件

- "写项目设计文档" / "设计文档" / "项目文档"
- "更新设计文档" / "文档加个功能"
- "生成项目原型" / "设计原型"
- "加个页面到文档" / "文档里加个模块"

## 文档规范

### 文件位置与命名（硬性规则）

> **核心原则：文件名 = 需求主题（中文）+ 尾部序号；每次迭代生成带新序号的文件，永不覆盖、永不删除旧文件。**

```
project-root/
└── docs/
    ├── 参考图库设计-v1.html      ← 首版
    ├── 参考图库设计-v2.html      ← 需求迭代 2（生成新文件，v1 保留）
    ├── 参考图库设计-v2.1.html    ← 需求迭代 3（尾部序号递增）
    ├── 用例执行详情设计-v1.html   ← 另一主题独立命名
    └── ...（一个主题一串版本文件，历史全部保留可追溯）
```

命名规则：
- 文件名格式：**`{主题}-v{序号}.html`**（如 `参考图库设计-v1.html`、`参考图库设计-v2.1.html`）
- **主题必须为中文**：主题词从用户需求中提取（如"参考图库"），文件名内不得出现英文单词或拼音命名（如 `project-design-v2.1.html`、`ref-image-v1.html` 均违规）
- **主题提取（要聪明）**：从用户需求文本中提取核心业务名词作为主题（如"参考图库"），去掉"增加""支持""管理""页面""设计文档"等动词与通用词；禁止使用 `project-design.html`、`design.html`、`未命名.html` 等通用名
- **尾部序号**：首版为 `-v1`，每次需求迭代序号递增（v1 → v2 → v2.1 → v2.2 → v3...），序号统一写在文件名**尾部**
- **永不覆盖**：迭代时基于旧文件生成带新序号的新文件，旧版本文件原样保留在 `docs/`，供追溯与回退
- **生成前必须扫描**：每次输出前扫描 `/docs/` 目录，识别同主题已有文件的最高序号，新文件序号 = 最高序号 + 1；同主题识别依据：文件名主题词一致，或 `<title>`/`<h1>` 主题一致（详见 Step 1）
- 新主题 → 新建 `{主题}-v1.html` 首个文件

### 文档结构（单 HTML 文件）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{项目名} · 设计文档</title>
    <style>
        /* === 文档全局样式 === */
        /* === 左侧导航栏 === */
        /* === 原型容器 === */
        /* === 各模块原型样式（.proto-{name} scope 隔离） === */
        /* === 暗色模式 === */
    </style>
</head>
<body>
    <!-- ====== 左侧导航栏（固定） ====== -->
    <aside id="doc-nav">
        <div class="nav-title">{项目名}</div>
        <a href="#overview">项目概述</a>
        <a href="#module-1">功能模块A</a>
        <a href="#module-2">功能模块B</a>
        <a href="#changelog">变更记录</a>
    </aside>

    <!-- ====== 主内容区 ====== -->
    <main id="doc-main">
        <!-- 项目概述 -->
        <section id="overview">...</section>

        <!-- 功能模块（每个含：描述 + 原型 + 交互说明） -->
        <section id="module-1">
            <h2>功能模块A</h2>
            <div class="feature-desc">...</div>
            <div class="prototype">
                <div class="proto-label">原型预览</div>
                <div class="proto-container">
                    <div class="proto-{module-name}"><!-- 内嵌原型 --></div>
                </div>
            </div>
            <div class="interaction-desc">...</div>
        </section>

        <!-- 变更记录 -->
        <section id="changelog">...</section>
    </main>
</body>
</html>
```

### 导航栏：左侧固定（确定方案）

```css
#doc-nav {
    position: fixed; top: 0; left: 0; width: 240px; height: 100vh;
    overflow-y: auto; padding: 24px 16px;
    background: var(--c-bg-soft); border-right: 1px solid var(--c-border);
}
#doc-main { margin-left: 240px; padding: 40px 48px; max-width: 960px; }
@media (max-width: 768px) {
    #doc-nav { display: none; }
    #doc-main { margin-left: 0; padding: 24px 16px; }
}
```

## 六步工作流

### Step 1: 项目分析（内置）

> **入口先做三件事：扫描 → 识别主题与最高序号 → 确定新文件名（含尾部序号），然后才动手写内容。**

1. **扫描 `/docs/` 目录**：列出所有 `.html` / `.md` 文件，记录每个文件的文件名与 `<title>`/`<h1>` 主题
2. **提取当前需求主题**：从用户需求文本中提取核心业务名词，得到主题词 X（如"参考图库"）
3. **找同主题已有文件**：按主题词 X 匹配现有文件（文件名或标题含 X）
   - 有匹配 → 解析出其中**最高序号**（如 `参考图库设计-v2.1.html` → `2.1`）
   - 无匹配 → 视为新主题
4. **确定新文件名**：
   - 新主题 → `X-v1.html`
   - 已有主题迭代 → `X-v{最高序号+1}.html`（如最高 `v2.1` → 新文件 `v2.2`；最高 `v2` → 新文件 `v3`）
   - **禁止**在旧文件上直接覆盖修改
   - 若无法判断主题归属：优先新建独立文件，不强行并入主题不符的旧文件
5. **分析项目结构**：读取 `package.json` / `src/` 等，理解技术栈和已有模块

### Step 2: 文档结构设计 + 风格选择

#### 2.1 规划模块清单
```
项目概述 → 功能模块A → 功能模块B → ... → 变更记录
```

#### 2.2 选择文档视觉风格（集成 ui-ux-pro-max）

读取 `ui-ux-pro-max` SKILL.md，按项目类型选择风格：

| 项目类型 | 推荐风格 | 配色方向 |
|---------|---------|---------|
| SaaS/工具 | Minimal/Professional | 中性灰 + 蓝主色 |
| 电商平台 | Warm Neutrals | 暖灰 + 琥珀色 |
| 数据仪表盘 | Dark Mode | 深底 + 微白文字 |
| 作品集/创意 | Editorial/Magazine | 衬线标题 + 不对称 |
| 个人主页 | Bento Grid 或 Minimal | 白底 + 1 主色 |

### Step 3: 功能描述编写

为每个模块编写文字描述：
```
- **模块名称**：xxx
- **核心价值**：解决什么问题
- **功能清单**：功能点A / 功能点B
- **依赖关系**：依赖模块X的xxx数据
- **不做范围**：明确不包含xxx
```

### Step 4: 原型嵌入生成（集成 ui-ux-pro-max）

#### 4.1 Design System 生成（必须，每个原型生成前执行）

读取 `ui-ux-pro-max` SKILL.md，提取并转化为 CSS 变量：

```css
:root {
    /* 从 ui-ux-pro-max 按项目类型选定 */
    --c-primary: #4f6df5;
    --c-primary-light: #eef1fe;
    --c-text: #1a1a2e; --c-text-light: #6b7280; --c-text-muted: #9ca3af;
    --c-bg: #ffffff; --c-bg-soft: #f9fafb; --c-border: #e5e7eb;
    /* 间距 8px 网格 */
    --sp-xs: 8px; --sp-sm: 16px; --sp-md: 24px; --sp-lg: 40px;
    /* 效果 */
    --r-sm: 6px; --r-md: 10px; --r-lg: 16px;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
    --transition: all 0.2s ease-out;
}
@media (prefers-color-scheme: dark) {
    :root {
        --c-text: #f4f4f5; --c-text-light: #a1a1aa;
        --c-bg: #18181b; --c-bg-soft: #27272a; --c-border: #3f3f46;
    }
}
```

#### 4.2 原型嵌入方式

**内联 HTML+CSS+JS**（原型直接嵌入文档，可实时交互）：

```html
<div class="prototype">
    <div class="proto-label">原型预览</div>
    <div class="proto-container">
        <div class="proto-eval-list">
            <!-- 原型 HTML -->
        </div>
    </div>
</div>
```

#### 4.3 样式隔离规范

```css
/* 每个模块的原型样式用 .proto-{module-name} 前缀隔离 */
.proto-eval-list .card { ... }
.proto-eval-list .btn { ... }
.proto-task-detail .header { ... }
```

```javascript
// 每个模块的原型 JS 用 IIFE 包裹
(function() {
    const root = document.querySelector('.proto-eval-list');
    if (!root) return;
    // 交互逻辑（限定在 root 内查询）
})();
```

#### 4.4 图标规范（来自 ui-ux-pro-max）
- **禁止 emoji 当图标** → 内联 SVG（Heroicons / Lucide）
- SVG 统一 `viewBox="0 0 24 24"`

#### 4.5 响应式断点（来自 ui-ux-pro-max）
- 375px / 768px / 1024px / 1440px
- 原型在文档中自适应宽度，移动端单列

#### 4.6 动画规范（来自 ui-ux-pro-max）
- 150-300ms 微交互，`transition-all duration-200 ease-out`
- 只用 `transform/opacity`，不用 `width/height`
- `@media (prefers-reduced-motion: reduce)` 禁用

### Step 5: 交互说明编写

为每个原型编写交互说明表格：

| 操作 | 触发方式 | 系统响应 | 边界情况 |
|------|---------|---------|---------|
| 搜索 | 输入关键词+回车 | 过滤匹配项 | 空输入恢复全部 |
| 删除 | 点击删除按钮 | 弹出确认框 | 不可逆操作需二次确认 |

补充：状态流转图（ASCII）、异常处理、键盘快捷键

### Step 6: 迭代维护（新版本 → 新文件，永不覆盖旧文件）

#### 6.1 新增功能（需求迭代）
1. **按 Step 1 确定新文件名**：`{主题}-v{最高序号+1}.html`
2. **复制基线**：将同主题最高序号（或内容最完整）的旧文件作为基线，复制为新文件名（如 `Copy-Item docs/参考图库设计-v2.1.html docs/参考图库设计-v2.2.html`），**旧文件保持原样不动**
3. 在新文件上继续维护：
   - 读取基线内容，理解当前 Design System（从 `:root` 变量读取）
   - 在 `</section>` 和 `</body>` 之间插入新 `<section>`
   - 新模块 CSS 追加到 `<style>` 末尾（用 `.proto-{name}` 隔离）
   - 新模块 JS 追加到 `<script>` 末尾（用 IIFE 包裹）
   - 更新左侧导航 + 变更记录（changelog 顶部新增一行，注明"基于 v{n} 复制"）
4. **验证旧文件未动**：确认旧版本文件内容与修改前一致

#### 6.2 修改功能
1. 定位到 `<section id="module-xxx">`
2. 修改描述/原型/交互说明
3. 保持 CSS scope 隔离不被破坏

#### 6.3 版本追踪
```html
<section id="changelog">
    <h2>变更记录</h2>
    <table>
        <tr><th>日期</th><th>版本</th><th>变更内容</th></tr>
        <tr><td>2026-08-23</td><td>v1.0</td><td>初始版本</td></tr>
    </table>
</section>
```

## 反模式检查（硬规则，来自 ui-ux-pro-max）

生成原型前必须确认不违反：
- ❌ 禁止 emoji 当图标 → 用 SVG
- ❌ 禁止 Inter + 紫色渐变
- ❌ 禁止 3 等宽列卡片
- ❌ 禁止 `h-screen` → 用 `min-h-[100dvh]`
- ❌ 禁止 hover 导致布局偏移

## 交付前检查清单（来自 ui-ux-pro-max）

每个原型生成后逐项检查：
- [ ] 无 emoji 图标，全部 SVG
- [ ] 可点击元素有 `cursor: pointer`
- [ ] 过渡 150-300ms
- [ ] 焦点状态可见
- [ ] 对比度 ≥ 4.5:1
- [ ] 响应式：375/768/1024/1440px
- [ ] `prefers-reduced-motion` 已处理
- [ ] CSS scope 隔离（模块间不污染）

## 与 model-design 的分工

| Skill | 定位 | 输出 |
|-------|------|------|
| `docs-design` | 项目级设计文档 | `/docs/{主题}-v{序号}.html`（中文主题 + 尾部序号，内嵌原型，迭代保留旧版） |
| `model-design` | 独立原型快速验证 | 单个 `.html`（不入文档） |

两者共享 `ui-ux-pro-max` 作为 Design System 来源，确保风格一致。

## 输出规范

- 用 `computer://` 链接让用户直接打开
- 新增模块时说明插入位置
- 原型必须可在浏览器中直接交互
- 变更记录必须更新
- 生成后附 Design System 摘要（风格/配色/字体）
