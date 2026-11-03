# Skill Registry（统一技能注册表）

> 最后更新：2026-09-11 | 版本：2.1.0
> 本文件合并三层技能（共享层 + Python 栈层 + React 栈层），为 AI 提供全局技能索引。
> **ZCode 布局（2026-09-11 起）**：所有技能已拍平到 `.zcode/skills/<name>/SKILL.md`，ZCode 按目录自动发现；"所属层"仅作来源标注（Python 栈技能仅在 cut-server 任务使用，React 栈技能仅在 cut-web 任务使用）。原模板源仍在 `.rules-skills/*/stack/.trae/skills/`。

## 快速查找表

### 共享层技能（前后端通用）

| Skill 名 | 触发关键词 | 优先级 | 依赖 | 定位 |
|----------|-----------|--------|------|------|
| **qa-reset** | 需求不清、批量问题、/qa-reset | **P0** | 无 | 需求润色与交互模式识别 |
| **karpathy-guidelines** | 写代码、重构、Review | **P0** | 无 | 编码准则（简洁/精准/目标驱动） |
| **find-skills** | 找技能、装技能、缺少技能 | **P1** | 无 | 技能发现与安装 |
| **project-analysis** | 分析项目、生成项目文档 | **P1** | 无 | 项目分析器 |
| **docs-design** | 写设计文档、项目文档 | **P2** | 无 | 项目级设计文档 |
| **api-contract** (新) | 定义 API、OpenAPI、接口契约 | **P1** | 无 | API 契约定义与类型同步 |
| **integration-testing** (新) | 联调测试、契约测试、集成测试 | **P2** | api-contract | 前后端集成测试 |
| **cicd-automation** (新) | CI/CD、流水线、部署脚本 | **P2** | 无 | CI/CD 配置生成 |
| **debugging** (新) | 调试、排查问题、性能分析 | **P1** | 无 | 结构化调试流程 |
| **security-audit** (新) | 安全审计、漏洞扫描、依赖检查 | **P2** | 无 | 安全审计报告 |

### Python 栈技能（后端专用）

| Skill 名 | 触发关键词 | 优先级 | 依赖 | 定位 |
|----------|-----------|--------|------|------|
| **fastapi-python** | FastAPI、API 开发 | **P1** | 无 | FastAPI 最佳实践 |
| **coding-skill** | 写 Python、脚本、工具函数 | **P2** | 无 | 通用 Python 编码 |
| **python-testing** | 写测试、pytest、覆盖率 | **P2** | 无 | Python 测试 |
| **python-scaffold** | 项目脚手架、初始化结构 | **P3** | 无 | 完整项目脚手架 |
| **python-project-bootstrap** | 轻量项目初始化 | **P3** | 无 | 最小项目结构 |
| **python-code-standards-validator** | 代码检查、PEP8、规范验证 | **P3** | 无 | 代码规范自动检查 |
| **code-review** | 代码审查、Review | **P2** | 无 | Python 代码审查 |

### React 栈技能（前端专用）

| Skill 名 | 触发关键词 | 优先级 | 依赖 | 定位 |
|----------|-----------|--------|------|------|
| **frontend-design** | 前端设计、UI 设计、品牌感 | **P3** | ui-ux-pro-max（可选） | 设计哲学 + 创意方向 |
| **ui-ux-pro-max** | 配色方案、字体搭配、UX 规则 | — | 无 | 设计系统规则库 |
| **model-design** | 设计原型、HTML 页面 | **P2** | ui-ux-pro-max | 独立 HTML 原型 |
| **vercel-react-best-practices** | React 优化、性能调优 | **P2** | 无 | React 最佳实践 |
| **web-design-guidelines** | UI 审计、设计 Review | **P3** | 外部 URL | Web 设计审计规范 |
| **api-mock** (新) | Mock 数据、MSW、假接口 | **P3** | api-contract | 前端 API Mock |
| **frontend-code-review** (新) | 前端代码审查、组件审查 | **P2** | karpathy-guidelines | 前端代码审查 |
| **a11y-audit** (新) | 可访问性检查、WCAG、ARIA | **P3** | 无 | 可访问性审计 |

### 后端项目技能（ai-server 专用）

| Skill 名 | 触发关键词 | 优先级 | 依赖 | 定位 |
|----------|-----------|--------|------|------|
| **eval-case-design** | 评测用例、用例设计 | **P2** | 无 | 评测用例设计 |
| **eval-direction-extension** | 新增评测方向 | **P2** | 无 | 评测方向扩展 |
| **target-system-integration** | 接入模型/服务 | **P2** | 无 | 被测系统接入 |
| **request-analysis** | 需求分析 | **P2** | 无 | 需求分析 |
| **design-skill** | 设计文档、变更设计 | **P2** | 无 | 后端变更设计 |
| **design-doc-code-completion** | 按设计文档编码 | **P2** | 无 | 设计驱动编码 |
| **task-spliter** | 任务拆分 | **P2** | 无 | 任务拆分 |
| **pymupdf-pdf** | PDF 处理 | **P3** | 无 | PDF 解析 |

## 触发冲突解决规则

### 规则 1：具体 > 抽象

| 用户说 | 优先 Skill | 原因 |
|--------|-----------|------|
| "定义 API 接口" | `api-contract` | 有明确产出物（OpenAPI 定义） |
| "写设计文档" | `docs-design` | 有明确产出物（文档文件） |
| "设计一个页面" | `model-design` | 有明确产出物（HTML 文件） |

### 规则 2：审计 > 设计

| 用户说 | 优先 Skill |
|--------|-----------|
| "审查 UI 代码" | `web-design-guidelines` |
| "审查后端代码" | `code-review`（Python）/ `frontend-code-review`（React） |
| "安全审计" | `security-audit` |
| "可访问性检查" | `a11y-audit` |

### 规则 3：需求澄清 > 直接执行

| 用户说 | 优先 Skill |
|--------|-----------|
| 需求模糊/一堆问题 | `qa-reset` |
| 需求清晰/单一任务 | 对应领域 Skill |

## 依赖关系图

```
                    ┌─────────────────────────────────┐
                    │  独立技能（P0 最高优先）          │
                    │  qa-reset, karpathy-guidelines   │
                    │  find-skills, project-analysis   │
                    │  api-contract, debugging          │
                    │  cicd-automation, security-audit  │
                    │  docs-design, fastapi-python       │
                    │  coding-skill, python-testing      │
                    │  vercel-react-best-practices       │
                    └──────────────┬──────────────────┘
                                  │
                    ┌─────────────▼──────────────────┐
                    │  api-contract                    │
                    └──┬───────────────────────────┘
                       │
          ┌────────────▼───────────┐
          │ integration-testing     │
          │ api-mock                │
          └────────────────────────┘

                    ┌─────────────────────────────────┐
                    │  ui-ux-pro-max（基础设计系统）    │
                    └──────────────┬──────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │ docs-design  │    │ model-design │    │ frontend-  │
    │             │    │             │    │ design      │
    └─────────────┘    └─────────────┘    └─────────────┘
```

## 各 Skill 详细信息

### P0 - 核心技能

#### qa-reset
- **所属层**：共享
- **定位**：需求润色与交互模式识别
- **强项**：双层识别机制（7 种交互模式 × 5 大内容维度）
- **何时使用**：需求模糊、批量问题、需要澄清/纠偏/评估时

#### karpathy-guidelines
- **所属层**：共享
- **定位**：编码准则（Andrej Karpathy 风格）
- **强项**：4 条核心原则（思考优先、简单优先、精准修改、目标驱动）
- **何时使用**：写代码、重构、Code Review 时

### P1 - 重要技能

#### api-contract（新）
- **所属层**：共享
- **定位**：API 契约定义与类型同步
- **能力**：OpenAPI 定义生成/维护、TS 类型自动生成、mock 数据生成、契约验证
- **何时使用**：新增/修改 API 接口、前后端类型同步时

#### debugging（新）
- **所属层**：共享
- **定位**：结构化调试流程
- **能力**：日志分析、断点调试、性能 profiling、内存泄漏排查
- **何时使用**：遇到复杂问题需要系统化排查时

#### find-skills
- **所属层**：共享
- **定位**：技能发现与安装

#### project-analysis
- **所属层**：共享
- **定位**：项目分析器

#### fastapi-python
- **所属层**：Python 栈
- **定位**：FastAPI 最佳实践

### P2 - 常用技能

#### integration-testing（新）
- **所属层**：共享
- **定位**：前后端集成测试
- **能力**：联调测试、契约测试（Pact）、API 集成测试
- **依赖**：api-contract

#### cicd-automation（新）
- **所属层**：共享
- **定位**：CI/CD 配置生成
- **能力**：GitHub Actions 模板、部署脚本、环境配置

#### security-audit（新）
- **所属层**：共享
- **定位**：安全审计
- **能力**：依赖漏洞扫描、密钥泄露检查、OWASP Top 10 检查

#### docs-design
- **所属层**：共享
- **定位**：项目级设计文档

#### code-review
- **所属层**：Python 栈
- **定位**：Python 代码审查

#### frontend-code-review（新）
- **所属层**：React 栈
- **定位**：前端代码审查（组件/hooks/性能/a11y）
- **依赖**：karpathy-guidelines

#### model-design
- **所属层**：React 栈
- **定位**：独立 HTML 原型

#### vercel-react-best-practices
- **所属层**：React 栈
- **定位**：React 最佳实践与性能优化

### P3 - 辅助技能

#### api-mock（新）
- **所属层**：React 栈
- **定位**：前端 API Mock
- **能力**：MSW 配置、假数据生成
- **依赖**：api-contract

#### a11y-audit（新）
- **所属层**：React 栈
- **定位**：可访问性审计
- **能力**：WCAG 合规检查、ARIA 验证

#### frontend-design
- **所属层**：React 栈
- **定位**：设计哲学 + 创意方向

#### ui-ux-pro-max
- **所属层**：React 栈
- **定位**：设计系统规则库（基础设施级）

#### web-design-guidelines
- **所属层**：React 栈
- **定位**：Web 设计审计规范

#### python-scaffold / python-project-bootstrap / python-code-standards-validator
- **所属层**：Python 栈
- **定位**：项目脚手架 / 轻量初始化 / 代码规范检查

### 项目层技能

详见 `.rules-skills/ai-server/.trae/skills/` 下的技能定义。

## 维护指南

### 新增 Skill

1. 确定所属层（共享 / Python 栈 / React 栈 / 项目层）
2. 创建 SKILL.md 文件到对应目录
3. 在本文件"快速查找表"中添加一行
4. 在"依赖关系图"中添加节点和边
5. 更新版本号和日期

### 废弃 Skill

1. 在"快速查找表"中将状态改为"已废弃"
2. 记录废弃原因和替代方案
3. 不要立即删除文件（保留至少一个版本周期）

---
*Registry v2.0.0 — 2026-09-07*
