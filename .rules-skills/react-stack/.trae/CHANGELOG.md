# Changelog

> 记录 Trae Rules & Skills 工具套件的所有重要变更。

## [2.0.0] - 2026-09-03 — 大规模同步更新

### Added（新增）

**Rules 层**：
- ✅ `rules/project/00-project-overview.md` 新增 5 个功能模块描述（M12参考图例/用户管理/用例调试/Dashboard/上下文检索）
- ✅ `rules/project/00-project-overview.md` 新增完整服务层清单（19 个 Service）和 Store 清单（6 个）
- ✅ `rules/project/00-project-overview.md` 新增页面目录结构树（18 个页面目录）
- ✅ `rules/project/01-project-specific.md` 新增 17 个领域前缀（原 10 个）
- ✅ `rules/project/01-project-specific.md` 新增 §3.12~§3.16 五大模块详细规则（笔记V2/Bug管理/参考图例v3.0/Dashboard/上下文检索/用例调试）
- ✅ `rules/common/02-architecture-patterns.md` 新增 §7 新模块架构定位指南（6 个子章节）

**Skills 层**：
- ✅ 新增 `skills/SKILL_REGISTRY.md`（技能注册表 v1.0.0）
  - 10 个 Skill 快速查找表
  - 4 条触发冲突解决规则
  - ASCII 依赖关系图
  - 3 个使用示例
  - 维护指南
- ✅ `skills/qa-reset/SKILL.md` 新增 Quick Reference（30 行速查表）
  - 7 种交互模式速查
  - 模式组合速查
  - 5 大内容维度速查

**工程化**：
- ✅ 新增版本管理机制（frontmatter `version` + `lastUpdated` 字段）
- ✅ 新增 `rules/README.md` v2.0.0（快速入门 + 速查表 + FAQ + 贡献指南）
- ✅ 新增 `CHANGELOG.md`（本文件）

### Changed（变更）

**Rules 层**：
- 📝 `rules/project/00-project-overview.md` v1.0 → **v2.0.0**
  - 功能模块：11 → 16 个
  - Service 清单：11 → 19 个（+8 新增，移除 2 个废弃引用）
  - Store 清单：4 → 6 个
  - 页面目录：10 → 18 个
- 📝 `rules/project/01-project-specific.md` v1.0 → **v2.0.0**
  - 领域前缀：10 → 17 个
  - 目录结构树：全面同步最新代码
  - 新增 6 大模块详细规则（§3.12~§3.16, §3.17）
- 📝 `rules/common/02-architecture-patterns.md` v1.0 → **v1.1.0**
  - 新增 §7 新模块架构定位指南

**Skills 层**：
- 📝 `skills/frontend-design/SKILL.md` v1.0 → **v1.1.0**
  - 添加 `depends_on`/`conflicts_with`/`complementary_to` 声明
  - 新增"定位与分工"章节（与 ui-ux-pro-max 的分工表）
  - 新增触发优先级规则
- 📝 `skills/ui-ux-pro-max/SKILL.md` v1.0 → **v1.1.0**
  - 添加 `role: design-system`/`consumed_by` 声明
  - 新增"核心定位：设计系统规则库"章节
- 📝 `skills/model-design/SKILL.md` v1.0 → **v1.1.0**
  - 添加 `depends_on`/`complementary_to`/`conflicts_with` 声明
- 📝 `skills/docs-design/SKILL.md` v1.0 → **v1.1.0**
  - 添加 `depends_on`/`complementary_to` 声明
- 📝 `skills/qa-reset/SKILL.md` v1.0 → **v1.1.0**
  - 新增 Quick Reference（30 行速查表）
- 📝 `skills/project-analysis/SKILL.md` v1.0 → **v2.0.0**
  - 移除 7 个 Python 死代码脚本引用
  - 更新工具优先级说明

### Removed（移除）

**死代码清理**：
- 🗑️ `skills/project-analysis/scripts/analyzer.py`（项目主分析器）
- 🗑️ `skills/project-analysis/scripts/arch_analyzer.py`（架构分析器）
- 🗑️ `skills/project-analysis/scripts/best_practices.py`（最佳实践检查）
- 🗑️ `skills/project-analysis/scripts/dep_analyzer.py`（依赖分析器）
- 🗑️ `skills/project-analysis/scripts/output_manager.py`（输出管理器）
- 🗑️ `skills/project-analysis/scripts/quality_scorer.py`（质量评分器）
- 🗑️ `skills/project-analysis/scripts/tech_detector.py`（技术栈检测器）
- 🗑️ `skills/project-analysis/scripts/`（整个目录）

**废弃引用清理**：
- 🗑️ `rules/project/00-project-overview.md` 移除 `historyService`/`contextService` 引用
- 🗑️ `rules/project/01-project-specific.md` 移除 `historyService` 引用

### Fixed（修复）

- 🐛 修复 Rules 与实际代码不同步问题（最严重的问题，会导致 AI 生成废弃代码）
- 🐛 修复 Skills 间职责重叠导致的 AI 选择困难问题
- 🐛 修复缺少元数据管理导致维护困难的问题

### 安全提醒

- ⚠️ 本次更新移除了 `historyService.ts` 和 `contextService.ts` 的引用（这两个文件已于 2026-09-03 从代码库删除）
- ⚠️ `referenceImageService.ts` 仍在渐进式迁移中，暂未移除

---

## [1.0.0] - 初始版本

### Added

**Rules 层（6 个）**：
- ✅ `rules/common/01-coding-standards.md` — 编码规范
- ✅ `rules/common/02-architecture-patterns.md` — 架构设计
- ✅ `rules/common/03-code-quality.md` — 代码质量
- ✅ `rules/common/04-dev-workflow.md` — 开发工作流
- ✅ `rules/project/00-project-overview.md` — 项目概述
- ✅ `rules/project/01-project-specific.md` — 项目特定规则

**Skills 层（10 个）**：
- ✅ `skills/qa-reset/` — 需求润色
- ✅ `skills/karpathy-guidelines/` — 编码准则
- ✅ `skills/find-skills/` — 技能发现
- ✅ `skills/project-analysis/` — 项目分析器（含 7 个 Python 脚本）
- ✅ `skills/docs-design/` — 设计文档生成
- ✅ `skills/model-design/` — HTML 原型设计
- ✅ `skills/frontend-design/` — 前端设计
- ✅ `skills/ui-ux-pro-max/` — UI/UX 设计系统
- ✅ `skills/vercel-react-best-practices/` — React 最佳实践
- ✅ `skills/web-design-guidelines/` — Web 设计审计

**工程化**：
- ✅ `rules/README.md` — 规则索引（v1.0）

---

## 版本号说明

采用**语义化版本**（Semantic Versioning）：

| 类型 | 格式 | 示例 | 触发条件 |
|------|------|------|---------|
| **Major** | `X.0.0` | 2.0.0 | 不兼容的重大变更（如删除核心 Rule/Skill） |
| **Minor** | `x.Y.0` | 1.1.0 | 向后兼容的新功能（如新增 Skill/章节） |
| **Patch** | `x.y.Z` | 1.0.1 | Bug 修复、文档改进、小调整 |

### 当前各文件版本总览

**Rules 层**：
| 文件 | 当前版本 | 最后更新 |
|------|---------|---------|
| README.md | **2.0.0** | 2026-09-03 |
| common/01-coding-standards.md | 1.0.0 | — |
| common/02-architecture-patterns.md | **1.1.0** | 2026-09-03 |
| common/03-code-quality.md | 1.0.0 | — |
| common/04-dev-workflow.md | 1.0.0 | — |
| project/00-project-overview.md | **2.0.0** | 2026-09-03 |
| project/01-project-specific.md | **2.0.0** | 2026-09-03 |

**Skills 层**：
| 文件 | 当前版本 | 最后更新 |
|------|---------|---------|
| SKILL_REGISTRY.md | **1.0.0** | 2026-09-03 |
| qa-reset/SKILL.md | **1.1.0** | 2026-09-03 |
| karpathy-guidelines/SKILL.md | 1.0.0 | — |
| find-skills/SKILL.md | 1.0.0 | — |
| project-analysis/SKILL.md | **2.0.0** | 2026-09-03 |
| docs-design/SKILL.md | **1.1.0** | 2026-09-03 |
| model-design/SKILL.md | **1.1.0** | 2026-09-03 |
| frontend-design/SKILL.md | **1.1.0** | 2026-09-03 |
| ui-ux-pro-max/SKILL.md | **1.1.0** | 2026-09-03 |
| vercel-react-best-practices/SKILL.md | 1.0.0 | — |
| web-design-guidelines/SKILL.md | 1.0.0 | — |

---

*Changelog 维护者：Claude Code Review*
*生成时间：2026-09-03*
