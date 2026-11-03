# AGENTS.md — LeeCommonVideoCut 项目指令（ZCode 自动加载）

> 本文件是 ZCode 工作区级指令入口，每次会话自动注入。
> 规则与技能体系：`.zcode/`（ZCode 用，本文件为准）与 `.trae/`（Trae 用）内容同源。
> 最后更新：2026-09-11

## 1. 项目概述

**LeeCommonVideoCut · 漫剧推广素材剪辑师 v4.0**（前后端分离重写版）：

| 目录 | 角色 | 技术栈 |
|------|------|--------|
| `cut-server/` | 后端 API 服务 | Python 3.10+ / FastAPI / SQLAlchemy 2 / PostgreSQL / Alembic |
| `cut-web/` | 前端 Web 应用 | React 18 / Vite / TypeScript / pnpm |
| `docs/openapi.yaml` | **API 契约唯一来源**（约 79 接口、18 个 Tag） | OpenAPI 3 |
| `docs/00-跨端协作约定.md` | 前后端联动**硬规则**（字段命名/响应格式/错误码/traceId/分页/异步任务） | — |
| `plan/` | 开发进度台账（00~08 共 9 个文件） | — |
| `AI漫剧剪辑师旧参考项目代码/` | 旧版参考实现（只读，不改动） | — |

## 2. 规则加载策略（按需读取，必读）

写代码前根据任务范围读取对应规则文件（`.zcode/rules/`）：

| 任务范围 | 必读规则 |
|----------|----------|
| 任何任务 | `shared/01-git-conventions.md`、`shared/07-dev-workflow.md` |
| cut-server 后端 | `shared/02-api-contract.md`、`shared/03-error-code-system.md`、`shared/04-logging-standards.md`、`shared/06-security-baseline.md` + `python-stack/01-coding-standards.md`、`python-stack/02-architecture-patterns.md`、`python-stack/03-code-quality.md` |
| cut-web 前端 | `shared/05-testing-strategy.md` + `react-stack/01-coding-standards.md`、`react-stack/02-architecture-patterns.md`、`react-stack/03-code-quality.md`、`react-stack/04-a11y-rules.md`、`react-stack/05-performance-budget.md` |
| 前后端联动 | `docs/00-跨端协作约定.md`（硬规则，冲突时以此为准）+ `shared/09-cross-end-workflow.md` |

后端四层架构：`controllers → services → managers → models`；禁止跨层调用。

## 3. 技能（Skills）

技能位于 `.zcode/skills/<name>/SKILL.md`（26 个），ZCode 会自动发现并按描述触发；也可显式要求使用。高频技能：

- **api-contract**：新增/修改接口时（维护 `docs/openapi.yaml`、生成 TS 类型）
- **db-migration**：表结构变更时（Alembic 迁移）
- **code-review / frontend-code-review**：提交前后端代码审查
- **python-testing / integration-testing**：单元测试与联调测试
- **qa-reset**：需求模糊时先结构化澄清
- **karpathy-guidelines**：写代码默认遵循（思考优先、简单优先、精准修改）
- **debugging / security-audit / cicd-automation**：按场景触发

## 4. 工作流硬约定

1. **进度台账**：完成一个任务后更新 `plan/01-开发进度.md`（状态与日期）；代码级变更记入 `plan/08-代码日志.md`。
2. **契约先行**：前后端联动任务先改 `docs/openapi.yaml`，后端实现与前端类型都从契约出发；接口变更同步更新契约文档。
3. **统一响应**：`{code, msg, data, traceId}`；错误码 `{DOMAIN}_{HTTP}_{SEQ}`；所有日志带 `trace_id`。
4. **验证后交付**：后端改动需通过 `pytest` + 服务可启动；前端改动需 `npm run build` 通过。不虚报完成状态。
5. **精准修改**：只改与任务相关的文件，不顺手重构；新文件遵循目标项目既有命名与分层。

## 5. 关键命令

```bash
# 后端（cut-server/）
pip install -e ".[dev]"        # 安装依赖
uvicorn app.main:app --reload --port 8000   # 启动（Swagger: /docs）
pytest                          # 测试
alembic upgrade head            # 数据库迁移

# 前端（cut-web/，骨架建立后）
pnpm install && pnpm dev        # 开发（localhost:5173）
pnpm build                      # 构建
```
