---
alwaysApply: false
version: 2.0.0
lastUpdated: 2026-09-03
description: Trae 工具套件索引与快速入门指南
---

# Trae Rules & Skills 工具套件

> **版本**: 2.0.0 | **最后更新**: 2026-09-03
>
> 本目录包含 AI 编程助手的完整规则（Rules）和技能（Skills）配置，已针对 **ai-eval-web** 项目（React + TypeScript 前端）深度定制。

## 🚀 5 分钟快速入门

### 第 1 步：了解架构（1 分钟）

```
.trae - 副本/
├── rules/                    # 规则层（约束 AI 行为）
│   ├── README.md             # ← 你在这里
│   ├── common/               # 通用规则（4 个，可直接复用）
│   └── project/              # 项目特定规则（2 个，需定制）
└── skills/                   # 技能层（扩展 AI 能力）
    ├── SKILL_REGISTRY.md     # 技能注册表（必读！）
    └── [10 个技能目录]       # 按需触发
```

**核心原则**：
- **Rules** = "不能做什么"（约束边界）
- **Skills** = "能做什么"（能力扩展）

### 第 2 步：选择规则模式（1 分钟）

| 你的场景 | 必读规则 | 按需读 |
|---------|---------|--------|
| **每次写代码** | `01-coding-standards` | — |
| **开发新功能前** | `04-dev-workflow` (§1 零干预) | `02-architecture-patterns` |
| **修 Bug / 小改动** | `01-coding-standards`, `04-dev-workflow` (§9 卡点恢复) | — |
| **安全相关** | `03-code-quality` (§5 安全) | — |
| **新项目启动** | `templates/00-初始化问卷` | 全部 |

### 第 3 步：了解技能触发（2 分钟）

**必读**：[SKILL_REGISTRY.md](../skills/SKILL_REGISTRY.md)（技能注册表）

**常用技能速查**：

| 用户说 | 触发 Skill | 优先级 |
|--------|-----------|--------|
| "需求不清楚" / "一堆问题" | `qa-reset` | **P0** 最高 |
| "帮我写代码" / "Review" | `karpathy-guidelines` | **P0** 最高 |
| "设计一个页面" | `model-design` | P2 |
| "写设计文档" | `docs-design` | P2 |
| "优化 React 性能" | `vercel-react-best-practices` | P2 |
| "审查 UI" | `web-design-guidelines` | P3 |
| "找技能 / 装技能" | `find-skills` | P1 |
| "分析项目" | `project-analysis` | P1 |

### 第 4 步：开始使用（1 分钟）

**正常流程**：
1. 用户提出需求
2. AI 自动匹配对应 Rule + Skill
3. 按 Rule 约束执行，按 Skill 工作流输出

**手动触发**：
- 输入 `/qa-reset` → 强制触发需求润色
- 输入"用 Karpathy 准则重构" → 触发编码准则

### 第 5 步：遇到问题？（30 秒）

→ 跳到 [FAQ](#faq常见问题)

---

## 📁 目录结构

### Rules 层

```
rules/
├── README.md                          # 本文件：索引与快速入门
├── common/                            # 通用基础规则（React + TS 项目通用）
│   ├── 01-coding-standards.md         # 编码规范 (v1.0.0)
│   ├── 02-architecture-patterns.md    # 架构设计 (v1.1.0)
│   ├── 03-code-quality.md             # 代码质量 (v1.0.0)
│   └── 04-dev-workflow.md             # 开发工作流 (v1.0.0)
└── project/                           # 项目定制规则（ai-eval-web 专用）
    ├── 00-project-overview.md         # 项目概述 (v2.0.0)
    └── 01-project-specific.md         # 项目特定规则 (v2.0.0)
```

### Skills 层

```
skills/
├── SKILL_REGISTRY.md                  # 技能注册表 (v1.0.0) ⭐ 必读
├── qa-reset/                          # 需求润色 (v1.1.0)
├── karpathy-guidelines/                # 编码准则 (v1.0.0)
├── find-skills/                       # 技能发现 (v1.0.0)
├── project-analysis/                  # 项目分析器 (v2.0.0)
├── docs-design/                       # 设计文档生成 (v1.1.0)
├── model-design/                      # HTML 原型设计 (v1.1.0)
├── frontend-design/                   # 前端设计 (v1.1.0)
├── ui-ux-pro-max/                     # UI/UX 设计系统 (v1.1.0)
├── vercel-react-best-practices/       # React 最佳实践 (v1.0.0)
└── web-design-guidelines/             # Web 设计审计 (v1.0.0)
```

---

## 📋 规则速查表

### Common Rules（通用）

| 编号 | 规则名 | 版本 | 核心内容 | 适用范围 |
|------|--------|------|---------|---------|
| common-01 | 编码规范 | v1.0.0 | TS/React 命名、TSDoc、类型提示、JSX | 所有 React+TS 项目 |
| common-02 | 架构设计 | **v1.1.0** | 分层架构、组件/Hook/Service/Store、新模块定位指南 | React+TS 项目 |
| common-03 | 代码质量 | v1.0.0 | 审查清单、Vitest/Playwright、性能、安全 | 所有前端项目 |
| common-04 | 开发工作流 | v1.0.0 | 零干预流程、目录规范、Git 提交 | 所有前端项目 |

### Project Rules（项目定制）

| 编号 | 规则名 | 版本 | 核心内容 | 适用范围 |
|------|--------|------|---------|---------|
| project-00 | 项目概述 | **v2.0.0** | 技术栈、16个功能模块、19个Service、6个Store | ai-eval-web |
| project-01 | 项目特定规则 | **v2.0.0** | 17个领域前缀、18个页面目录、6大模块详细规则 | ai-eval-web |

---

## 🧩 技能速查表

| 优先级 | 技能名 | 版本 | 定位 | 状态 |
|--------|--------|------|------|------|
| **P0** | qa-reset | v1.1.0 | 需求润色与交互模式识别 | ✅ 活跃 |
| **P0** | karpathy-guidelines | v1.0.0 | 编码准则（简洁/精准/目标驱动） | ✅ 活跃 |
| P1 | find-skills | v1.0.0 | 技能发现与安装 | ✅ 活跃 |
| P1 | project-analysis | **v2.0.0** | 项目分析器（已清理死代码） | ✅ 活跃 |
| P2 | docs-design | v1.1.0 | 项目级设计文档（内嵌原型） | ✅ 活跃 |
| P2 | model-design | v1.1.0 | 独立 HTML 原型 | ✅ 活跃 |
| P2 | vercel-react-best-practices | v1.0.0 | React 最佳实践与性能优化 | ✅ 活跃 |
| P3 | frontend-design | v1.1.0 | 设计哲学 + 创意方向 | ✅ 活跃 |
| P3 | ui-ux-pro-max | v1.1.0 | 设计系统规则库（基础设施） | ✅ 活跃 |
| P3 | web-design-guidelines | v1.0.0 | Web 设计审计（依赖外部URL） | ✅ 活跃 |

> 完整依赖关系图 → [SKILL_REGISTRY.md](../skills/SKILL_REGISTRY.md#依赖关系图)

---

## 🔍 快速查找

### 常见问题定位

| 问题 | → 解决方案 |
|------|-----------|
| TS/React 命名怎么写？ | → [01-coding-standards.md §1](./common/01-coding-standards.md#1-命名规范) |
| 组件/Hook TSDoc 怎么写？ | → [01-coding-standards.md §3](./common/01-coding-standards.md#3-tsdoc-注释) |
| 代码放哪个模块？ | → [01-project-specific.md §2](./project/01-project-specific.md#2-模块结构) |
| feature-based 架构怎么分？ | → [02-architecture-patterns.md §1](./common/02-architecture-patterns.md#1-分层架构) |
| core/ 目录放什么？ | → [02-architecture-patterns.md §1.3](./common/02-architecture-patterns.md#13-core-目录定位) |
| 何时用全局 Store？ | → [02-architecture-patterns.md §1.4](./common/02-architecture-patterns.md#14-何时使用全局-store) |
| 新模块（Bug/笔记/图例）放哪？ | → [02-architecture-patterns.md §7](./common/02-architecture-patterns.md#7-新模块架构定位指南) ⭐ NEW |
| 请求 traceId 怎么打？ | → [02-architecture-patterns.md §10](./common/02-architecture-patterns.md#10-日志与监控) |
| 错误怎么抛？ | → [02-architecture-patterns.md §8](./common/02-architecture-patterns.md#8-错误处理架构) |
| Bug 管理状态机？ | → [01-project-specific.md §3.13](./project/01-project-specific.md#313-m11-bug-管理前端规则) ⭐ NEW |
| 笔记 V2 怎么做？ | → [01-project-specific.md §3.12](./project/01-project-specific.md#312-m10-智能笔记-v2-前端规则) ⭐ NEW |
| 参考图例 v3.0 怎么做？ | → [01-project-specific.md §3.14](./project/01-project-specific.md#314-m12-参考图例-v30-前端规则) ⭐ NEW |
| 代码审查查什么？ | → [03-code-quality.md §2](./common/03-code-quality.md#2-代码审查清单) |
| Vitest 测试怎么写？ | → [03-code-quality.md §3.4](./common/03-code-quality.md#34-单元测试要求) |
| Playwright E2E 怎么写？ | → [03-code-quality.md §3.5](./common/03-code-quality.md#35-e2e-测试要求playwright) |
| XSS/CSRF/Token 怎么防？ | → [03-code-quality.md §5](./common/03-code-quality.md#5-安全规范) |
| Git 怎么提交？ | → [04-dev-workflow.md §3](./common/04-dev-workflow.md#3-git-提交规范) |
| 卡住了怎么办？ | → [04-dev-workflow.md §9](./common/04-dev-workflow.md#9-卡点检测与恢复机制) |
| 需求不清楚怎么办？ | → [qa-reset Quick Reference](../skills/qa-reset/SKILL.md#quick-reference快速查找) ⭐ NEW |
| 设计 UI 用哪个 Skill？ | → [SKILL_REGISTRY.md 触发冲突解决规则](../skills/SKILL_REGISTRY.md#触发冲突解决规则) ⭐ NEW |

---

## 🔄 版本历史

→ 完整变更日志：[CHANGELOG.md](./CHANGELOG.md)

### v2.0.0 (2026-09-03) — 大规模同步更新

**Rules 层**：
- ✅ `00-project-overview.md` v1.0 → v2.0.0（新增 5 个功能模块、19 个 Service、6 个 Store）
- ✅ `01-project-specific.md` v1.0 → v2.0.0（新增 17 个领域前缀、6 大模块详细规则）
- ✅ `02-architecture-patterns.md` v1.0 → v1.1.0（新增 §7 新模块架构定位指南）

**Skills 层**：
- ✅ 新增 `SKILL_REGISTRY.md`（技能注册表 + 依赖关系图）
- ✅ 4 个 Skill 添加依赖声明（frontend-design/ui-ux-pro-max/model-design/docs-design）
- ✅ `qa-reset` v1.0 → v1.1.0（新增 Quick Reference）
- ✅ `project-analysis` v1.0 → v2.0.0（清理 7 个死代码脚本）
- ✅ `ui-ux-pro-max` v1.0 → v1.1.0（明确基础设施角色）

**工程化**：
- ✅ 新增版本管理机制（frontmatter version 字段）
- ✅ 新增 CHANGELOG.md
- ✅ README 全面重写（快速入门 + 速查表 + FAQ）

---

## FAQ 常见问题

### Q1: Rules 和 Skills 有什么区别？

| 维度 | Rules | Skills |
|------|-------|--------|
| **本质** | 约束（不能做什么） | 能力（能做什么） |
| **触发方式** | 自动加载（alwaysApply） | 按需触发（用户意图匹配） |
| **数量** | 少而精（6 个） | 多而专（10 个） |
| **修改频率** | 低（稳定后少改） | 中（持续迭代） |
| **类比** | 交通法规 | 驾驶技能 |

### Q2: 如何为项目添加新 Rule？

1. 判断是**通用规则**还是**项目特定规则**
2. 通用规则 → 放在 `rules/common/`，编号递增（如 `05-xxx.md`）
3. 项目特定规则 → 放在 `rules/project/`，编号递增（如 `02-xxx.md`）
4. 在 frontmatter 添加 `version` 和 `lastUpdated`
5. 更新本 README 的速查表
6. 更新 `CHANGELOG.md`

### Q3: 如何为项目添加新 Skill？

1. 在 `skills/` 下创建新目录（kebab-case 命名）
2. 创建 `SKILL.md`（frontmatter 含 name/version/description）
3. 在 `SKILL_REGISTRY.md` 中注册（添加一行 + 更新依赖图）
4. 如果依赖其他 Skill，在 frontmatter 添加 `depends_on`
5. 更新 `CHANGELOG.md`

### Q4: frontend-design 和 ui-ux-pro-max 该用哪个？

→ 详见 [SKILL_REGISTRY.md 触发冲突解决规则](../skills/SKILL_REGISTRY.md#触发冲突解决规则)

**简版**：
- 需要**创意方向/品牌感** → `frontend-design`
- 需要**具体 Token 值**（颜色代码/字体名）→ `ui-ux-pro-max`
- 两者可**联合使用**

### Q5: Rules 过时了怎么办？

本项目已在 **2026-09-03** 完成大规模同步更新（v2.0.0），所有 Rule 已与最新代码对齐。

后续维护：
- 代码有大变动时 → 同步更新 `rules/project/` 
- 发现 Rule 不合理 → 提出 Issue，团队评审后修改
- 历史版本通过 Git 追溯

### Q6: 可以把这些 Rules/Skills 复制到其他项目吗？

**可以！** 迁移方法：

1. **`common/` 目录** → 直接复制（React+TS 项目通用）
2. **`project/` 目录** → 替换为新项目的规则（详见下方"迁移指南"）
3. **`skills/` 目录** → 按需选择（大部分 Skill 是通用的）
4. **调整技术栈默认值**（如不用 Zustand → 改 Store 选型说明）

→ 详细步骤见下方 [迁移指南](#迁移到其他项目)

### Q7: project-analysis 的 Python 脚本去哪了？

**已于 v2.0.0 清理**。原因：
- SKILL.md 声明"首选内置工具，非必要不调用 scripts/*.py"
- 7 个脚本无测试覆盖，与 Trae/Copilot 不兼容
- 保留 `references/` 和 `templates/`（知识资产）

Git 历史中仍可找到旧版本。

---

## 迁移到其他项目

### 一句话总结

**`common/` 直接复制，`project/` 替换，`skills/` 按需选择。**

### 详细步骤

#### 第 1 步：复制通用 Rules

```bash
cp -r .trae/rules/common/ <新项目>/.trae/rules/
```

> 如新项目用 Vue，需替换 React 特定内容（JSX → Template，Hooks → Composables）

#### 第 2 步：替换项目 Rules

复制 `project/` 后修改：

**`00-project-overview.md`**：
- [ ] 项目名称、目标、技术栈
- [ ] 功能列表、关键约束

**`01-project-specific.md`**：
- [ ] 领域前缀（§1.1）
- [ ] 模块结构（§2）
- [ ] 领域特定规则（§3）

#### 第 3 步：选择 Skills

```bash
# 推荐必选
cp -r .trae/skills/qa-reset/ <新项目>/.trae/skills/
cp -r .trae/skills/karpathy-guidelines/ <新项目>/.trae/skills/
cp -r .trae/skills/SKILL_REGISTRY.md <新项目>/.trae/skills/

# 按需选择
cp -r .trae/skills/model-design/ <新项目>/.trae/skills/  # 需要原型
cp -r .trae/skills/docs-design/ <新项目>/.trae/skills/   # 需要文档
cp -r .trae/skills/ui-ux-pro-max/ <新项目>/.trae/skills/  # 需要设计系统
```

#### 第 4 步：调整技术栈

| 默认值 | 如需替换 |
|--------|---------|
| React + Hooks | Vue + Composables / Svelte |
| TypeScript | JavaScript（不推荐） |
| Zustand | Pinia / Redux / MobX |
| Vite | Webpack / esbuild |
| Ant Design | Element Plus / Shadcn |
| Vitest + Playwright | Jest + Cypress |

#### 第 5 步：验证

- [ ] README 中链接可访问
- [ ] 团队成员知晓新规则
- [ ] 测试一次完整开发流程

---

## 贡献指南

### 如何报告问题？

1. 确认问题类型（Rule 过时 / Skill 缺失 / 文档错误）
2. 在 `plan/03-问题记录.md` 中记录
3. 或直接提 Issue（如有 GitHub 仓库）

### 如何提交修改？

1. Fork / 创建分支
2. 修改 Rule/Skill（遵循版本管理规范）
3. 更新 `CHANGELOG.md`
4. 更新 README 速查表（如有新增/删除）
5. 提交 PR，附上变更说明

### 版本管理规范

- 采用**语义化版本**：`MAJOR.MINOR.PATCH`
  - **MAJOR**：不兼容的重大变更（如删除核心 Rule）
  - **MINOR**：向后兼容的新功能（如新增 Skill）
  - **PATCH**：Bug 修复、文档改进
- 每次**修改必须更新** frontmatter 中的 `version` 和 `lastUpdated`
- **重大变更**必须在 `CHANGELOG.md` 中记录

---

## 与后端项目的关系

本项目（ai-eval-web）是 AI 测评系统的前端，对应后端为 `ai-eval-server`：

- **Rules 层**：前端用 React/TS 版，后端用 Python 版，**不共享**
- **Skills 层**：部分通用（如 karpathy-guidelines），部分前端专用
- **协作约定**：接口契约定义在 [project/00-project-overview.md](./project/00-project-overview.md) 末尾

---

*Trae Tools v2.0.0 — 2026-09-03*
*最后更新：2026-09-03 by Claude Code Review*
