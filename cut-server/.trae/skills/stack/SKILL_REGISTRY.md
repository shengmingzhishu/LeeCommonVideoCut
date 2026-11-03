# Python 技术栈技能注册表

> 最后更新：2026-09-07 | 版本：2.0.0
> Python 技术栈层技能，适用于所有 Python 后端项目。

## 快速查找表

| Skill 名 | 触发关键词 | 优先级 | 依赖 | 定位 |
|----------|-----------|--------|------|------|
| **fastapi-python** | FastAPI、API 开发、路由 | **P1** | 无 | FastAPI 最佳实践 |
| **coding-skill** | 写 Python、脚本、工具函数 | **P2** | 无 | 通用 Python 编码 |
| **python-testing** | 写测试、pytest、覆盖率 | **P2** | 无 | Python 测试 |
| **code-review** | 代码审查、Review | **P2** | karpathy-guidelines | Python 代码审查 |
| **python-scaffold** | 项目脚手架、初始化结构 | **P3** | 无 | 完整项目脚手架 |
| **python-project-bootstrap** | 轻量项目初始化 | **P3** | 无 | 最小项目结构 |
| **python-code-standards-validator** | 代码检查、PEP8、规范验证 | **P3** | 无 | 代码规范自动检查 |
| **db-migration** (新) | 数据库迁移、Alembic、表结构变更 | **P2** | 无 | 数据库迁移管理 |

## 触发冲突解决

| 用户说 | 优先 Skill | 原因 |
|--------|-----------|------|
| "写 FastAPI 接口" | `fastapi-python` | 有 FastAPI 框架上下文 |
| "写通用 Python 脚本" | `coding-skill` | 无框架上下文 |
| "审查代码" | `code-review` | 审计场景 |
| "检查代码规范" | `python-code-standards-validator` | 自动化检查场景 |
| "写测试" | `python-testing` | 测试场景 |
| "数据库表结构变更" | `db-migration` | 迁移场景 |

## 与共享层技能的配合

Python 栈技能与共享层技能配合使用：

```
qa-reset（共享）→ request-analysis（项目）→ fastapi-python（栈）→ python-testing（栈）→ code-review（栈）
```

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 2.0.0 | 2026-09-07 | 从旧版迁移，新增 db-migration |
| 1.0.0 | 2026-09-03 | 初始版本 |
