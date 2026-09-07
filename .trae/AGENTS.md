# AGENTS.md — 全局协调规则

> 本文件是 LeeCommonSkills 三层架构的根级入口，AI 在任何项目工作时首先读取此文件。
> 最后更新：2026-09-07 | 版本：2.0.0

## 1. 架构总览

LeeCommonSkills 采用**三层分离架构**：

```
第一层：共享层 (.trae/)              → 前后端通用的 rules 和 skills
第二层：技术栈层 (.rules-skills/*/stack/)      → Python 专项 / React 专项
第三层：项目层 (.rules-skills/ai-*/)       → 项目定制 rules 和 skills
```

## 2. 三层定位

| 层 | 位置 | 内容 | 修改频率 |
|----|------|------|---------|
| 共享层 | `.trae/rules/shared/` + `.trae/skills/shared/` | Git 规范、API 契约、日志、测试策略、安全基线、开发工作流、CI/CD + 5 个共享技能 | 低 |
| Python 栈 | `.rules-skills/python-stack/.trae/` | Python 编码规范、四层架构、Python 代码质量 + 7 个 Python 技能 | 中 |
| React 栈 | `.rules-skills/react-stack/.trae/` | TS/React 编码规范、feature-based 架构、前端代码质量、a11y、性能预算 + 5 个 React 技能 | 中 |
| 后端项目 | `.rules-skills/ai-server/.trae/` | ai-server 项目概述、特定规则 + 8 个项目技能 | 高 |
| 前端项目 | `.rules-skills/ai-web/.trae/` | ai-web 项目概述、特定规则 | 高 |

## 3. AI 工作指引

### 3.1 判断当前项目

AI 在开始工作前，先判断当前在哪个项目：

- 如果在 `ai-server` 目录 → 加载共享层 + Python 栈层 + 后端项目层
- 如果在 `ai-web` 目录 → 加载共享层 + React 栈层 + 前端项目层
- 如果在 LeeCommonSkills 仓库 → 全部可见，用于维护模板

### 3.2 跨端任务协调

当任务涉及前后端联动（如新增 API 接口）时：

1. **先定义 API 契约**（参考 `.trae/rules/shared/02-api-contract.md`）
2. **后端实现** → 遵守 Python 栈规则 + 后端项目规则
3. **前端实现** → 遵守 React 栈规则 + 前端项目规则
4. **联调测试** → 参考 `.trae/rules/shared/05-testing-strategy.md` §3

### 3.3 规则与技能边界

- **Rules** = 约束（"必须做什么"/"不能做什么"）→ AI 必须遵守
- **Skills** = 能力（"怎么做"/"用什么工具"）→ AI 按需触发

| 场景 | 用 Rules | 用 Skills |
|------|---------|----------|
| 命名怎么写 | 编码规范 rule | — |
| 代码怎么审查 | 审查清单 rule | code-review skill |
| 怎么写测试 | 测试策略 rule | python-testing / vitest skill |
| API 怎么定义 | API 契约 rule | api-contract skill |
| 安全检查标准 | 安全基线 rule | security-audit skill |

## 4. 共享规则索引

| 编号 | 规则 | 说明 |
|------|------|------|
| shared-01 | [Git 规范](./rules/shared/01-git-conventions.md) | 提交、分支、版本管理 |
| shared-02 | [API 契约](./rules/shared/02-api-contract.md) | OpenAPI、类型同步、breaking change |
| shared-03 | [错误码体系](./rules/shared/03-error-code-system.md) | 错误码段位、响应格式、traceId |
| shared-04 | [日志规范](./rules/shared/04-logging-standards.md) | 日志级别、JSON 格式、脱敏 |
| shared-05 | [测试策略](./rules/shared/05-testing-strategy.md) | 测试分层、覆盖率、联调 |
| shared-06 | [安全基线](./rules/shared/06-security-baseline.md) | 输入校验、密钥、XSS/CSRF |
| shared-07 | [开发工作流](./rules/shared/07-dev-workflow.md) | 零干预流程、plan 目录、卡点恢复 |
| shared-08 | [CI/CD 流水线](./rules/shared/08-cicd-pipeline.md) | CI 触发、构建、部署、回滚 |

## 5. 技术栈层规则索引

### Python 栈

| 编号 | 规则 | 说明 |
|------|------|------|
| python-01 | 编码规范 | Python 命名、格式、注释、类型提示 |
| python-02 | 架构设计 | 四层架构、core/、错误处理、事务ID |
| python-03 | 代码质量 | 审查清单、测试、安全、重构 |

### React 栈

| 编号 | 规则 | 说明 |
|------|------|------|
| react-01 | 编码规范 | TS/React 命名、格式、TSDoc |
| react-02 | 架构设计 | feature-based、目录、数据流 |
| react-03 | 代码质量 | 审查清单、测试、性能、重构 |
| react-04 | 可访问性 | WCAG 2.1 AA、ARIA、键盘导航 |
| react-05 | 性能预算 | Core Web Vitals、bundle 限制 |

## 6. 同步机制

LeeCommonSkills 是模板仓库，通过 `scripts/sync-to-project.ps1` 分发到各目标项目：

```powershell
# 同步到后端项目
./scripts/sync-to-project.ps1 -Target server

# 同步到前端项目
./scripts/sync-to-project.ps1 -Target web

# 预览差异（不实际复制）
./scripts/sync-to-project.ps1 -Target all -DryRun
```

同步规则：
- `shared/` + `stack/` 层：从模板覆盖到目标项目
- `project/` 层：**不被覆盖**，保持项目本地定制
- `AGENTS.md` 和 `SKILL_REGISTRY.md`：自动生成合并版本

## 7. 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 2.0.0 | 2026-09-07 | 三层架构重构，提取共享层，新增 10 个 rules + 9 个 skills |
| 1.0.0 | 2026-09-03 | 初始版本，前后端独立维护 |
