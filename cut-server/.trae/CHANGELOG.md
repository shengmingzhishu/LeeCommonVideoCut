# cut-server · Changelog

> 记录 cut-server Trae Rules & Skills 工具套件的所有重要变更。
> 与 docs/02-项目上下文.md §关键决策记录 配合使用。

## [Unreleased] — 整改期

### Added（新增）

- ✅ `skills/SKILL_REGISTRY.md` v1.0.0（技能注册表 + 依赖图 + 触发冲突解决）
- ✅ `docs/00-跨端协作约定.md`（在仓库根 docs/ 下，跨端协作铁律）
- ✅ 待办：SKILL frontmatter 标准化（`inputs` / `outputs` / `dependencies` / `status` 字段）

### Changed（变更）

- 📝 `skills/WORKFLOW.md` 维持原状，下一次同步将工作流 3/4/5 重写为 video-cut 场景

### Deprecated（废弃预告）

- ⚠️ `eval-direction-extension`、`eval-case-design`、`target-system-integration`、`pymupdf-pdf` 4 个 skill 在 video-cut 场景下不适用，下次大版本将归档

---

## [0.1.0] - 2026-09-03 — 初始化 video-cut 主题

> cut-server 起源规则来自 ai-eval-server（仓库根 `.trae/rules/server/`）。本版本针对 video-cut 项目做了一轮主题切换与定制。

### Added

**问卷与上下文**：
- ✅ `docs/01-项目初始化问卷.md` — 基于 PRD v1.2 填写完成
- ✅ `docs/02-项目上下文.md` — 待 AI 启动后生成
- ✅ `docs/04-接口契约.md` v1.0.0 — 7 步流程 + 项目 + 配置 + 文件 + 长任务

**工作流**：
- ✅ `skills/WORKFLOW.md` v1.0.0 — 5 套标准工作流（新功能开发 / Bug 修复 / 评测方向扩展 / 被测系统接入 / 用例设计）
- ✅ 18 个 skill 文件从 ai-eval-server 模板继承

### Notes

- ⚠️ `rules/project/00-project-overview.md` 仍标注为"ai-eval-server"（沿用模板），待主题切换整改
- ⚠️ `rules/project/01-project-specific.md` 命名约定/异常体系/模块结构仍为评测领域，待重写

---

## 版本号说明

采用**语义化版本**（Semantic Versioning）：

| 类型 | 格式 | 示例 | 触发条件 |
|------|------|------|---------|
| **Major** | `X.0.0` | 1.0.0 | 不兼容的重大变更（如删除核心 Rule/Skill） |
| **Minor** | `x.Y.0` | 0.2.0 | 向后兼容的新功能（如新增 Skill/章节） |
| **Patch** | `x.y.Z` | 0.1.1 | Bug 修复、文档改进、小调整 |

## 当前各文件版本总览

**Rules 层**：

| 文件 | 当前版本 | 最后更新 |
|------|---------|---------|
| README.md | 1.0.0 | 2026-09-03 |
| common/01-coding-standards.md | 1.0.0 | — |
| common/02-architecture-patterns.md | 1.0.0 | — |
| common/03-code-quality.md | 1.0.0 | — |
| common/04-dev-workflow.md | 1.0.0 | — |
| project/00-project-overview.md | 0.1.0（待重写） | 2026-09-03 |
| project/01-project-specific.md | 0.1.0（待重写） | 2026-09-03 |

**Skills 层**：

| 文件 | 当前版本 | 最后更新 |
|------|---------|---------|
| WORKFLOW.md | 1.0.0 | 2026-09-03 |
| SKILL_REGISTRY.md | 1.0.0 | 2026-09-03 |

---

*Changelog 维护者：Claude Code Review*
*生成时间：2026-09-03*
