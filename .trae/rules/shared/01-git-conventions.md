---
alwaysApply: false
description: Git 提交规范、分支策略、版本管理。创建 Git 提交、管理分支、发布版本时使用此规则。
---

# Git 规范（共享层）

> 适用于所有项目，前后端通用。

## 1. 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

## 2. Type 类型

| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档变更 |
| style | 代码格式调整（不影响功能） |
| refactor | 重构（不新增功能，不修 Bug） |
| perf | 性能优化 |
| test | 测试相关 |
| chore | 构建/工具/依赖等辅助变更 |
| build | 构建系统或外部依赖变更 |
| ci | CI 配置变更 |

## 3. 示例

```
feat(eval): 支持RAG评分评测方向

- 新增 RAG 评测管理器
- 扩展评测方向配置
- 支持文件导入测试集

Closes #123
```

## 4. 提交原则

- 每次提交只做一件事
- 提交信息用中文或英文均可，但项目内保持一致
- 不提交无法运行/无法构建的代码
- 不提交大文件和临时文件
- 不提交 `.env`、`dist/`、`node_modules/`、测试输出等文件

## 5. 分支策略

### 5.1 分支类型

| 分支 | 命名 | 用途 |
|------|------|------|
| 主分支 | `main` / `master` | 稳定可用的代码 |
| 开发分支 | `develop` | 集成分支（可选） |
| 功能分支 | `feature/<功能描述>` | 新功能开发 |
| 修复分支 | `fix/<问题描述>` | Bug 修复 |
| 发布分支 | `release/<版本号>` | 发布准备 |
| 热修复分支 | `hotfix/<问题描述>` | 线上紧急修复 |

### 5.2 功能开发流程

```
main → feature/xxx → 开发 → PR → 审查 → 合并到 main
```

### 5.3 分支命名示例

```
feature/rag-eval-support
feature/eval-list-page
fix/login-timeout
hotfix/prod-db-connection
release/v1.0.0
```

## 6. 版本管理

### 6.1 版本号格式

遵循语义化版本（Semantic Versioning）：

```
MAJOR.MINOR.PATCH
```

- **MAJOR**：不兼容的 API 变更
- **MINOR**：向下兼容的功能性新增
- **PATCH**：向下兼容的问题修正

### 6.2 示例

- `1.0.0` - 首个正式版本
- `1.0.1` - 修复 Bug
- `1.1.0` - 新增功能
- `2.0.0` - 重大变更，不兼容旧版
