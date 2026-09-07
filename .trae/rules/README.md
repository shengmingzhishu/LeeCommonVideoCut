# 根级 Rules 索引

> **版本**: v1.0.0
> **最后更新**: 2026-09-04
> **定位**: 跨端协作规则层，不侵入子项目编码/架构/测试规则

---

## 目录结构

```
.trae/rules/
├── README.md                           # 本文件
├── common/
│   ├── 01-cross-end-conventions.md     # 跨端协作约定
│   ├── 02-unified-workflow.md          # 统一开发工作流
│   └── templates/
│       ├── 00-前后端联调checklist.md
│       └── 01-跨端接口变更模板.md
└── project/
    ├── 00-project-overview.md          # video-cut 项目总览
    └── 01-project-specific.md          # video-cut 项目特定规则
```

## 规则速查

| 规则文件 | alwaysApply | 关注点 |
|----------|-------------|--------|
| common/01-cross-end-conventions.md | true | 接口契约、字段映射、错误码、CORS、TraceId |
| common/02-unified-workflow.md | false | 跨端任务拆分、联调流程、Git 工作流 |
| project/00-project-overview.md | true | 项目身份、7步流程、技术栈、架构边界 |
| project/01-project-specific.md | true | 领域命名、步骤锁定、长任务、视频处理规则 |

## 与子项目规则的关系

| 层级 | 管什么 | 不管什么 |
|------|--------|----------|
| **根级 rules** | 跨端协作、项目总览、统一工作流 | Python/TS 编码规范、四层/feature-based 架构细节 |
| **cut-server rules** | Python 编码、四层架构、后端测试、数据库 | 跨端字段映射、前端组件 |
| **cut-web rules** | TS/React 编码、feature-based 架构、前端测试 | 跨端错误码定义、后端 API 实现细节 |

## 加载优先级

1. `AGENTS.md` — 父层编排指南（最高优先级）
2. `project/00-project-overview.md` — 项目身份
3. `project/01-project-specific.md` — 领域规则
4. `common/01-cross-end-conventions.md` — 跨端约定
5. `common/02-unified-workflow.md` — 工作流（按需加载）
6. 子项目 rules — 各端内部规则

## 迁移指南

如需将本规则体系迁移到新项目：
1. 复制 `common/` 目录（通用跨端约定，改端口/BaseURL 即可）
2. 重写 `project/00-project-overview.md`（新项目身份）
3. 重写 `project/01-project-specific.md`（新领域规则）
4. 子项目 rules 各自独立迁移
