---
alwaysApply: false
description: 跨端全生命周期工作流。需求→API契约→后端→前端→集成测试→发布的完整流程。涉及前后端联动开发时使用此规则。
---

# 跨端全生命周期工作流（共享层）

> 前后端联动的标准开发流程，确保两端进度同步、接口对齐、质量可控。

## 工作流 6：跨端功能开发流

```
┌──────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ qa-reset │──▶│ api-contract │──▶│ 后端实现  │──▶│ 前端实现  │──▶│ 集成测试  │──▶│  发布     │
│ (需求澄清)│   │ (契约定义)   │   │          │   │          │   │          │   │          │
└──────────┘   └──────────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
                                       │              │              │
                                       ▼              ▼              ▼
                                  后端工作流 1    前端工作流 1    integration-testing
                                  (server/       (web/
                                   WORKFLOW.md)   WORKFLOW.md)
```

### 阶段 1：需求澄清（qa-reset）

- 使用 `qa-reset` skill 结构化需求
- 明确功能点、验收标准、优先级
- 产出：结构化需求文档

### 阶段 2：API 契约定义（api-contract）

- 使用 `api-contract` skill 定义 OpenAPI
- 明确：接口 Path、Method、参数、响应、错误码
- 后端 PR 标注是否 breaking change
- 产出：`docs/openapi.yaml` + 接口变更记录

### 阶段 3：后端实现（并行）

- 后端按 `WORKFLOW.md` 工作流 1 执行
- 前端可同时使用 `api-mock` skill 生成 Mock 数据
- 后端完成 → 更新 OpenAPI → CI 通知前端
- 产出：可运行的后端接口 + 更新的 OpenAPI

### 阶段 4：前端实现（并行/串行）

- 前端拉取最新 OpenAPI → 生成 TS 类型
- 使用 Mock 数据开发（如后端未完成）
- 后端完成后关闭 Mock，直连后端
- 产出：可运行的前端页面/组件

### 阶段 5：集成测试（integration-testing）

- 使用 `integration-testing` skill 执行联调
- 联调检查清单：
  - [ ] Path/Method 对齐
  - [ ] 参数类型/必填项对齐
  - [ ] 响应字段对齐
  - [ ] 错误码对齐
  - [ ] 分页格式对齐
  - [ ] CORS 配置正确
- 产出：联调测试报告

### 阶段 6：发布

- PR 审查通过（前后端 code-review）
- 安全审计通过（security-audit）
- CI 全部通过
- 前后端同步发布

## 并行开发策略

```
时间线:
后端:  [API契约定义] ──→ [后端实现] ────────────→ [联调]
前端:  [等待契约] ────→ [Mock开发] → [前端实现] → [联调]
                                    ↑              ↑
                              契约就绪        前端完成
```

- 前端不等后端实现完成，使用 Mock 数据并行开发
- 契约定义后，两端可独立推进
- 联调阶段统一验证

## 质量门禁清单

### 后端 PR 必须通过

- [ ] ruff lint 无 error
- [ ] mypy type-check 无 error
- [ ] pytest unit test 通过（覆盖率 ≥ 80%）
- [ ] pytest integration test 通过
- [ ] pip-audit 无高危漏洞
- [ ] code-review skill 审查通过
- [ ] OpenAPI 契约验证通过
- [ ] 数据库迁移有回滚脚本（如涉及）

### 前端 PR 必须通过

- [ ] ESLint 无 error
- [ ] tsc --noEmit 无 error
- [ ] vitest unit test 通过（覆盖率 ≥ 80%）
- [ ] pnpm build 成功
- [ ] bundle size 在预算内
- [ ] pnpm audit 无高危漏洞
- [ ] frontend-code-review 审查通过
- [ ] a11y-audit 无 Critical 问题

### 联调阶段必须通过

- [ ] 联调检查清单全部通过
- [ ] 契约验证（OpenAPI schema 一致）
- [ ] E2E 测试关键路径通过
- [ ] 错误码定义前后端一致
- [ ] traceId 贯穿前后端日志
