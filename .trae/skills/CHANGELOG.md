# 变更记录

> 本文件记录根级 `.trae/skills/` 的版本演进

---

## v1.0.0 (2026-09-04)

### 新增
- 创建根级 `.trae/` 目录结构
- `AGENTS.md` — 父层 AI 编排指南
- `rules/README.md` — 根级规则索引
- `rules/common/01-cross-end-conventions.md` — 跨端协作约定（接口契约、字段映射、错误码、CORS、TraceId、长任务轮询）
- `rules/common/02-unified-workflow.md` — 统一开发工作流（跨端任务拆分、联调流程、Git 工作流、卡点恢复）
- `rules/common/templates/00-前后端联调checklist.md` — 联调检查清单
- `rules/common/templates/01-跨端接口变更模板.md` — 接口变更模板
- `rules/project/00-project-overview.md` — video-cut 项目总览（7步流程、技术栈、架构边界）
- `rules/project/01-project-specific.md` — video-cut 项目特定规则（领域命名、步骤锁定、长任务、虚拟预览、数据库、视频处理、配置管理）
- `skills/SKILL_REGISTRY.md` — 统一技能注册表（索引前后端+系统+插件所有技能）
- `skills/WORKFLOW.md` — 统一工作流编排（5 套跨端工作流）
- `skills/CHANGELOG.md` — 本文件
- `docs/01-项目初始化问卷.md` — 根级项目初始化问卷
- `docs/02-项目上下文.md` — 项目上下文
- `docs/03-开发进度.md` — 开发进度追踪

### 主题切换
- cut-server `rules/project/00-project-overview.md` 从 ai-eval-server 切换到 video-cut
- cut-server `rules/project/01-project-specific.md` 从 ai-eval-server 切换到 video-cut
- cut-web `rules/project/00-project-overview.md` 从 ai-eval-web 切换到 video-cut
- cut-web `rules/project/01-project-specific.md` 从 ai-eval-web 切换到 video-cut
