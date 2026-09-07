---
alwaysApply: true
version: 1.0.0
lastUpdated: 2026-09-03
description: cut-server 后端技能注册表。技能查找、依赖关系、触发冲突解决、与 WORKFLOW.md 配合使用。
---

# cut-server · Skill Registry（技能注册表）

> 与 `WORKFLOW.md` 配合使用：
> - `WORKFLOW.md` 关注"按任务类型组合多个 Skill"
> - 本文件关注"每个 Skill 是什么、何时用、与其他 Skill 的依赖"

## 快速查找表

| Skill 名 | 触发关键词 | 优先级 | 依赖 | 状态 | 定位 |
|----------|-----------|--------|------|------|------|
| **qa-reset** | 需求不清、批量问题、/qa-reset | **P0** | 无 | ✅ 活跃 | 需求润色与交互模式识别 |
| **karpathy-guidelines** | 写代码、重构、Review | **P0** | 无 | ✅ 活跃 | 编码准则（简洁/精准/目标驱动） |
| **find-skills** | 找技能、装技能、缺少技能 | **P1** | 无 | ✅ 活跃 | 技能发现与安装 |
| **request-analysis** | 需求分析、新增/修改类需求 | **P1** | 无 | ✅ 活跃 | 产出 `.changes/需求分析-${name}.md` |
| **task-spliter** | 任务拆分、WBS | **P1** | request-analysis | ✅ 活跃 | 产出 `.changes/任务拆分-${name}.md` |
| **design-doc-code-completion** | 设计文档转代码 | **P1** | task-spliter | ✅ 活跃 | 按任务逐步实现 + 单测 |
| **python-testing** | 写单测、跑测试 | **P1** | 无 | ✅ 活跃 | pytest + coverage |
| **code-review** | Code Review、PR | **P1** | 无 | ✅ 活跃 | 静态检查 + 人工 review 清单 |
| **coding-skill** | 写后端业务代码 | **P2** | karpathy-guidelines | ✅ 活跃 | Controller/Service/Manager 三层规范 |
| **fastapi-python** | 写 FastAPI 接口 | **P2** | coding-skill | ✅ 活跃 | FastAPI 路由/参数/响应规范 |
| **python-code-standards-validator** | 编码规范检查 | **P2** | 无 | ✅ 活跃 | PEP8 + 命名 + 文档字符串校验 |
| **python-project-bootstrap** | 初始化新 Python 项目 | **P3** | 无 | ✅ 活跃 | 最小化脚手架（轻量） |
| **python-scaffold** | 完整脚手架 | **P3** | 无 | ✅ 活跃 | 完整脚手架（重） |
| **design-skill** | 设计文档 | P3 | 无 | ⚠️ 评估中 | 视频剪辑领域暂未深度用 |
| **docs-design** | 设计文档生成 | P3 | 无 | ⚠️ 评估中 | 与 design-skill 重复，待合并 |
| **project-analysis** | 分析项目、生成项目文档 | P3 | 无 | ✅ 活跃 | 项目结构分析 |

> **历史遗留**（已废弃，建议移除）：
> - `eval-direction-extension`、`eval-case-design`、`target-system-integration`：ai-eval-server 时代专用，video-cut 不需要
> - `pymupdf-pdf`：PDF 解析工具，与 video-cut 无关

## 触发冲突解决规则

### 规则 1：需求澄清 > 直接执行

| 用户说 | 优先 Skill | 原因 |
|--------|-----------|------|
| 需求模糊 / 一堆问题 / 不确定要什么 | `qa-reset` | 必须先澄清需求 |
| 需求清晰 / 单一任务 | 对应领域 Skill | 可直接执行 |

### 规则 2：分析 → 拆分 → 实现 → 测试

任何"新功能开发"任务，按以下顺序选择：

```
qa-reset (需求不清时)
  → request-analysis (需求分析)
    → task-spliter (任务拆分)
      → design-doc-code-completion (编码实现)
        → python-testing (单测)
          → code-review (审查)
```

### 规则 3：编码实现优先选最具体的 Skill

| 用户说 | 优先 Skill | 原因 |
|--------|-----------|------|
| "写一个 FastAPI 接口" | `fastapi-python` | 框架级专门 Skill |
| "实现一个 Service" | `coding-skill` | 层级别专门 Skill |
| "写通用业务代码" | `karpathy-guidelines` | 编码准则通用 Skill |
| "重构 / 改 Bug" | `karpathy-guidelines` + `python-testing` | 编码 + 回归 |

### 规则 4：审计 > 设计

| 用户说 | 优先 Skill | 原因 |
|--------|-----------|------|
| "审查 PR / 这段代码好不好" | `code-review` | 审计场景 |
| "帮我设计接口" | `request-analysis` | 创建场景 |

## 与 WORKFLOW.md 的对应关系

| 工作流（WORKFLOW.md） | 用到的 Skill 序列 |
|---------------------|------------------|
| 工作流 1：新功能开发流 | qa-reset → request-analysis → task-spliter → design-doc-code-completion → python-testing → code-review |
| 工作流 2：Bug 修复流 | coding-skill 或 fastapi-python → python-testing → code-review |
| 工作流 3：新增 Step 流 | design-skill → request-analysis → task-spliter → design-doc-code-completion → python-testing → code-review |
| 工作流 4：接入新 TTS / LLM | design-skill → coding-skill → python-testing → code-review |
| 工作流 5：模块设计流 | design-skill → design-doc-code-completion |

## 依赖关系图

```
                    ┌─────────────────┐
                    │   qa-reset      │  P0（独立，最高优先）
                    │ karpathy-guidelines │  P0（独立）
                    │   find-skills   │  P1（独立）
                    │   code-review   │  P1（独立）
                    │ python-testing  │  P1（独立）
                    │ python-code-    │  P2（独立）
                    │ standards-      │
                    │   validator     │
                    │   project-      │  P3（独立）
                    │   analysis      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ request-analysis│  P1
                    │  task-spliter   │  P1
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ design-doc-     │  P1
                    │ code-completion │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │ coding-skill │  │fastapi-     │  │ design-skill │
    │              │  │ python      │  │              │
    └─────────────┘  └─────────────┘  └─────────────┘
```

## 各 Skill 详细信息

### P0 - 核心技能

#### qa-reset
- **定位**：需求润色与交互模式识别
- **何时使用**：需求模糊、批量问题、需要澄清/纠偏/评估时
- **输出**：结构化需求、执行计划、风险评估

#### karpathy-guidelines
- **定位**：编码准则（Andrej Karpathy 风格）
- **何时使用**：写代码、重构、Code Review 时
- **输出**：高质量、可维护的代码

### P1 - 重要技能

#### request-analysis
- **定位**：需求分析（新增类 / 修改类）
- **何时使用**：拿到新需求后第一步
- **输出**：`.changes/需求分析-${name}.md`

#### task-spliter
- **定位**：任务拆分（WBS）
- **何时使用**：需求分析完成后
- **输出**：`.changes/任务拆分-${name}.md`

#### design-doc-code-completion
- **定位**：从设计文档直接产出代码
- **何时使用**：任务拆分完成后
- **输出**：每步的代码 + 单测

#### python-testing
- **定位**：pytest + coverage
- **何时使用**：编码完成后
- **输出**：测试结果 + 覆盖率

#### code-review
- **定位**：静态 + 清单 + 文档审查
- **何时使用**：PR 提交时 / 自检
- **输出**：`.changes/review/代码检查-${name}-${date}.md`

#### find-skills
- **定位**：技能发现与安装

#### project-analysis
- **定位**：项目结构分析（仅保留 references/，scripts/ 已清理）

### P2 - 常用技能

#### coding-skill
- **定位**：Controller / Service / Manager 三层编码规范
- **依赖**：karpathy-guidelines
- **何时使用**：写后端业务代码时
- **关键文件**：`REFERENCE/Controller规范.md`、`REFERENCE/业务层-业务逻辑spec.md`、`REFERENCE/应用层-接口定义spec.md`

#### fastapi-python
- **定位**：FastAPI 框架专门规范
- **依赖**：coding-skill
- **何时使用**：写 FastAPI 路由/参数/响应时

#### python-code-standards-validator
- **定位**：PEP8 + 命名 + 文档字符串校验
- **何时使用**：代码 commit 前自检

### P3 - 辅助技能

#### python-project-bootstrap
- **定位**：最小化项目脚手架
- **与 python-scaffold 区别**：bootstrap = 仅目录 + pyproject + .gitignore；scaffold = 完整模板代码
- **何时使用**：快速起步新项目

#### python-scaffold
- **定位**：完整 Python 项目脚手架
- **何时使用**：团队规范化项目

## 维护指南

### 新增 Skill
1. 在本文件"快速查找表"中添加一行
2. 在"依赖关系图"中添加节点和边
3. 在"各 Skill 详细信息"中添加描述
4. 在 `WORKFLOW.md` 的工作流矩阵中标注"何时用"
5. 更新版本号和日期
6. 在 `CHANGELOG.md` 追加变更记录

### 废弃 Skill
1. 在"快速查找表"中将状态改为 `🚫 已废弃`
2. 在"依赖关系图"中移除节点
3. 保留至少一个版本周期再删除文件

### 更新 Skill 依赖
1. 修改对应 Skill 的 SKILL.md frontmatter
2. 更新本文件"依赖关系图"
3. 更新"快速查找表"中的依赖列
4. 更新版本号

---

*Registry v1.0.0 — 2026-09-03*
