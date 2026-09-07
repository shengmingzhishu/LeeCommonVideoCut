# 共享规则索引

> 最后更新：2026-09-07 | 版本：2.0.0
> 共享层规则适用于所有项目，前后端通用。

## 规则速查

| 编号 | 规则 | 分类 | 优先级 | 说明 |
|------|------|------|--------|------|
| shared-01 | [Git 规范](./shared/01-git-conventions.md) | 通用 | 必读 | 提交、分支、版本管理 |
| shared-02 | [API 契约](./shared/02-api-contract.md) | 通用 | 必读 | OpenAPI、类型同步、breaking change |
| shared-03 | [错误码体系](./shared/03-error-code-system.md) | 通用 | 必读 | 错误码段位、响应格式、traceId |
| shared-04 | [日志规范](./shared/04-logging-standards.md) | 通用 | 必读 | 日志级别、JSON 格式、脱敏 |
| shared-05 | [测试策略](./shared/05-testing-strategy.md) | 通用 | 必读 | 测试分层、覆盖率、联调 |
| shared-06 | [安全基线](./shared/06-security-baseline.md) | 通用 | 必读 | 输入校验、密钥、XSS/CSRF |
| shared-07 | [开发工作流](./shared/07-dev-workflow.md) | 通用 | 必读 | 零干预流程、plan 目录、卡点恢复 |
| shared-08 | [CI/CD 流水线](./shared/08-cicd-pipeline.md) | 通用 | 按需 | CI 触发、构建、部署、回滚 |

## 规则加载优先级

| 场景 | 必读规则 | 按需读规则 |
|------|---------|-----------|
| 每次开发 | shared-07(§5 卡点恢复) | — |
| 功能点开发前 | shared-07(§1 零干预 + §8 上下文) | shared-05(测试策略) |
| 涉及接口变更 | shared-02(API 契约) | shared-03(错误码) |
| 涉及安全/认证 | shared-06(安全基线) | — |
| 涉及日志/调试 | shared-04(日志规范) | — |
| 涉及 CI/CD | shared-08(CI/CD 流水线) | — |
| 新项目启动 | templates/00-初始化问卷 | 全部 |

## 模板文件

| 文件 | 说明 |
|------|------|
| [00-项目初始化问卷.md](./templates/00-项目初始化问卷.md) | 项目启动时用户唯一需填写的文件 |
| [01-新增模块checklist.md](./templates/01-新增模块checklist.md) | 四层架构各层检查清单 |
| [02-接口变更模板.md](./templates/02-接口变更模板.md) | API 变更标准文档模板 |
| [03-code-review-checklist.md](./templates/03-code-review-checklist.md) | 精简版代码审查清单 |

## 迁移到新项目

1. **共享层**：复制 `.trae/rules/shared/` 和 `.trae/rules/templates/` 到新项目
2. **技术栈层**：根据新项目技术栈选择 `.rules-skills/python-stack/` 或 `.rules-skills/react-stack/`
3. **项目层**：创建新项目的 `project/00-project-overview.md` 和 `project/01-project-specific.md`
4. 运行 `scripts/sync-to-project.ps1` 组合分发
