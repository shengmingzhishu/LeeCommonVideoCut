---
alwaysApply: true
version: 1.0.0
lastUpdated: 2026-09-03
description: cut-web 前端技能工作流编排。按任务类型选择合适的工作流，按顺序执行各步骤。
---

# cut-web · Skills 工作流编排指南

> 与 `SKILL_REGISTRY.md` 配合使用：
> - `SKILL_REGISTRY.md` 关注"每个 Skill 是什么、何时用"
> - 本文件关注"按任务类型组合多个 Skill"

## 工作流总览

```
┌────────────────────────────────────────────────────────────────────────┐
│                         技能工作流矩阵                                   │
├─────────────┬─────────────┬─────────────┬─────────────┬────────────────┤
│             │  需求澄清   │  分析设计   │  编码实现   │  验证交付      │
├─────────────┼─────────────┼─────────────┼─────────────┼────────────────┤
│ 新功能开发  │  qa-reset   │ request-    │ frontend-   │ vercel-react-  │
│ (新页面)    │             │ analysis    │ design +    │ best-practices │
│             │             │ → task-     │ docs-design │ + playwright   │
│             │             │ spliter     │             │ e2e-7-step     │
├─────────────┼─────────────┼─────────────┼─────────────┼────────────────┤
│ 新组件/UI   │     —       │ model-      │ frontend-   │ vercel-react-  │
│ (非页面)    │             │ design      │ design      │ best-practices │
├─────────────┼─────────────┼─────────────┼─────────────┼────────────────┤
│ Bug 修复    │     —       │     —       │ karpathy-   │ vercel-react-  │
│             │             │             │ guidelines  │ best-practices │
│             │             │             │             │ + playwright   │
├─────────────┼─────────────┼─────────────┼─────────────┼────────────────┤
│ 7 步流程    │     —       │ virtual-    │ marker-     │ task-poll +    │
│ Step5 实现  │             │ preview     │ timeline    │ playwright     │
├─────────────┼─────────────┼─────────────┼─────────────┼────────────────┤
│ 设计稿评估  │     —       │ web-design- │     —       │     —          │
│ / UI 审查   │             │ guidelines  │             │                │
├─────────────┼─────────────┼─────────────┼─────────────┼────────────────┤
│ 重构        │     —       │     —       │ karpathy-   │ vercel-react-  │
│             │             │             │ guidelines  │ best-practices │
└─────────────┴─────────────┴─────────────┴─────────────┴────────────────┘
```

## 工作流 1：新页面开发流

**适用场景**：新增完整页面（如新增一个 Settings 页、个人中心页等）

```
┌──────────┐    ┌──────────────────┐    ┌─────────────┐    ┌──────────┐
│ qa-reset  │──▶│ request-analysis │──▶│ task-spliter│──▶│ docs-    │
│ (需求澄清) │    │ (需求分析+方案)  │    │ (任务拆分)  │    │ design + │
└──────────┘    └──────────────────┘    └─────────────┘    │ frontend-│
                                                            │ design   │
                                                            └────┬─────┘
                                                                 │
                                ┌─────────────┐    ┌────────────▼────────┐
                                │ vercel-     │◀───│ playwright-         │
                                │ react-best- │    │ e2e-7-step          │
                                │ practices   │    │ (新增 E2E 用例)     │
                                └─────────────┘    └─────────────────────┘
```

**执行要点**：

1. **qa-reset**：如果需求表述不清，先用此 skill 结构化需求
2. **request-analysis**：产出 `docs/需求分析-${名称}.md`（页面布局 + 状态管理 + Service 依赖 + 路由）
3. **task-spliter**：产出 `docs/任务拆分-${名称}.md`
4. **docs-design / frontend-design**：根据是否有现成设计稿选择
   - 有 Figma / Sketch 设计稿 → `docs-design`（生成内嵌原型的设计文档）
   - 无设计稿，仅需风格方向 → `frontend-design`（Anthropic 风格指南）
5. **karpathy-guidelines + vercel-react-best-practices**：编码实现，遵循 React 最佳实践
6. **playwright-e2e-7-step**：编写页面级 E2E 用例

---

## 工作流 2：非页面组件开发流

**适用场景**：新增一个可复用组件（如 `MarkerCard`、`TaskProgressBadge`）

```
┌──────────────┐    ┌─────────────┐    ┌──────────┐
│ model-design │──▶│ frontend-   │──▶│ vercel-  │
│ (可选原型)    │    │ design      │    │ react-   │
│              │    │ (风格)      │    │ best-    │
└──────────────┘    └─────────────┘    │ practices│
                                       └──────────┘
```

**执行要点**：

1. **model-design**（可选）：用 HTML 原型快速验证布局
2. **frontend-design**：确认视觉风格（暗色科技风 / 简约白 / 品牌色）
3. **karpathy-guidelines + vercel-react-best-practices**：编码 + 性能优化
4. 组件必须通过 Storybook 或至少一个使用页面验证

---

## 工作流 3：Bug 修复流

**适用场景**：修复已知缺陷、回归问题

```
┌──────────────┐    ┌─────────────┐    ┌──────────┐
│ karpathy-    │──▶│ vercel-     │──▶│playwright│
│ guidelines   │    │ react-best- │    │ e2e-7-   │
│ (定位+修复)   │    │ practices   │    │ step     │
└──────────────┘    └─────────────┘    └──────────┘
```

**执行要点**：

1. **karpathy-guidelines**：按"思考优先、简单优先、精准修改、目标驱动"四原则定位并修复
2. **vercel-react-best-practices**：检查是否引入反模式（无效重渲、内存泄漏、过度 useEffect）
3. **playwright-e2e-7-step**：补一个回归用例，避免重复踩坑
4. 简化规则：不需要 qa-reset（Bug 已有明确描述），不需要 task-spliter（修复范围通常清晰）

---

## 工作流 4：7 步流程核心实现流

**适用场景**：实现 video-cut 的 7 步流程中的某一步（特别是 Step4/5/6/7 这种涉及视频/音频/ffmpeg 的步骤）

```
┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│ virtual-     │──▶│ marker-      │──▶│ task-poll + │
│ preview      │    │ timeline     │    │ playwright- │
│ (Step5 规范) │    │ (标记组件)   │    │ e2e-7-step  │
└──────────────┘    └──────────────┘    └─────────────┘
```

**执行要点**：

1. **virtual-preview**：读取 `01-project-specific.md §4.5 视频与音频资源管理规范`（必须遵守 0 IO 预览原则）
2. **marker-timeline**：实现时间轴组件（按 §1.3 三条件判定是否进 `core/`）
3. **task-poll**：Step4 音频 / Step6 裁切 / Step7 合成都用此 skill
4. **playwright-e2e-7-step**：7 步完整链路 E2E 测试

**Step5 是 video-cut 的核心创新点**，单独走这条工作流。

---

## 工作流 5：UI 设计审查流

**适用场景**：审查现有 UI 设计是否符合规范、是否需要改进

```
┌──────────────────┐    ┌─────────────┐
│ web-design-      │──▶│ frontend-   │
│ guidelines       │    │ design      │
│ (设计审计)        │    │ (改进建议)  │
└──────────────────┘    └─────────────┘
```

**执行要点**：

1. **web-design-guidelines**：按 checklist 逐项检查（对比度、可达性、信息密度、视觉层级）
2. **frontend-design**：给出风格改进建议
3. 输出问题清单 + 改进方案（不动代码）

---

## 工作流 6：重构流

**适用场景**：代码质量改进（提取组件、提取 Hook、消除重复）

```
┌──────────────┐    ┌─────────────┐    ┌──────────┐
│ karpathy-    │──▶│ vercel-     │──▶│playwright│
│ guidelines   │    │ react-best- │    │ e2e-7-   │
│              │    │ practices   │    │ step     │
└──────────────┘    └─────────────┘    └──────────┘
```

**执行要点**：

1. 先确认重构必要（重复 ≥ 3 次 / 组件 > 300 行 / 函数 > 50 行）
2. **karpathy-guidelines**：保持外部行为不变，仅优化内部结构
3. **vercel-react-best-practices**：检查重构后是否引入新反模式
4. **playwright-e2e-7-step**：跑一遍 E2E 确认无回归

---

## 快速选择指南

| 你的任务是... | 使用工作流 |
|---------------|-----------|
| "新增一个 XXX 页面" | **工作流 1**：新页面开发流 |
| "做一个 XXX 组件" | **工作流 2**：非页面组件开发流 |
| "这个 Bug 怎么修" | **工作流 3**：Bug 修复流 |
| "实现 Step4/5/6/7" | **工作流 4**：7 步流程核心实现流 |
| "审查 UI 设计" | **工作流 5**：UI 设计审查流 |
| "这段代码太烂了重构下" | **工作流 6**：重构流 |
| "需求不太清楚，帮我梳理" | 先用 **qa-reset**，再进入对应工作流 |

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 1.0.0 | 2026-09-03 | 初始版本，定义 6 套标准工作流 |
