---
alwaysApply: false
description: 
---
# 项目规则索引

本目录包含项目的所有开发规则和规范，分为**通用规则**和**项目定制规则**两部分。

## 目录结构

```
.trae/rules/
├── README.md                # 本文件：规则索引与迁移指南
├── common/                  # 通用基础规则（可直接复制到其他 Python 项目）
│   ├── 01-coding-standards.md      # 编码规范（命名、格式、注释、类型提示）
│   ├── 02-architecture-patterns.md # 架构设计（四层架构、core/定位、错误处理、事务ID日志）
│   ├── 03-code-quality.md          # 代码质量（审查清单、测试规范、安全基线、重构规则）
│   ├── 04-dev-workflow.md          # 开发工作流（零干预流程、目录规范、项目上下文、卡点恢复、Git）
│   └── templates/                  # 模板文件
│       ├── 00-项目初始化问卷.md      # 项目启动时用户唯一需填写的文件
│       ├── 01-新增模块checklist.md   # 四层架构各层检查清单
│       ├── 02-接口变更模板.md        # API 变更标准文档模板
│       └── 03-code-review-checklist.md  # 精简版代码审查清单
└── project/                 # 项目定制规则（每个项目不同，需替换）
    ├── 00-project-overview.md      # 项目概述与目标
    └── 01-project-specific.md      # 项目特定命名、四层模块结构与领域规则
```

## 规则速查

| 编号 | 规则 | 分类 | 优先级 | 适用范围 |
|------|------|------|--------|---------|
| common-01 | 编码规范（含注释强制） | 通用 | 必读 | 所有 Python 项目 |
| common-02 | 架构设计（四层 + core/ + 事务ID日志） | 通用 | 必读 | 四层架构后端项目 |
| common-03 | 代码质量（审查 + 测试 + 安全基线 + 重构） | 通用 | 必读 | 所有项目 |
| common-04 | 开发工作流（零干预 + 目录 + 上下文 + 卡点恢复 + Git） | 通用 | 必读 | 所有项目 |
| project-00 | 项目概述 | 项目定制 | 必读 | 本项目 |
| project-01 | 项目特定规则 | 项目定制 | 必读 | 本项目 |

## 快速查找

- **命名怎么写？** → [01-coding-standards.md](./common/01-coding-standards.md#1-命名规范)
- **方法/配置注释怎么写？** → [01-coding-standards.md](./common/01-coding-standards.md#5-注释规范)
- **代码放哪个模块？** → [project/01-project-specific.md](./project/01-project-specific.md#2-模块结构)
- **四层架构怎么分？** → [02-architecture-patterns.md](./common/02-architecture-patterns.md#1-分层架构)
- **core/ 目录放什么？** → [02-architecture-patterns.md](./common/02-architecture-patterns.md#13-core-目录定位)
- **何时用 Manager 层？** → [02-architecture-patterns.md](./common/02-architecture-patterns.md#14-何时使用-manager-层)
- **事务ID日志怎么打？** → [02-architecture-patterns.md](./common/02-architecture-patterns.md#62-事务-idtransaction-id)
- **错误怎么抛？** → [02-architecture-patterns.md](./common/02-architecture-patterns.md#4-错误处理规范)
- **代码审查查什么？** → [03-code-quality.md](./common/03-code-quality.md#2-代码审查清单)
- **测试怎么写？测试输出放哪？** → [03-code-quality.md](./common/03-code-quality.md#3-测试规范)
- **安全基线怎么遵守？** → [03-code-quality.md](./common/03-code-quality.md#5-安全规范)
- **docs/plan/test 目录怎么管？** → [04-dev-workflow.md](./common/04-dev-workflow.md#2-项目目录规范)
- **零干预开发流程怎么运作？** → [04-dev-workflow.md](./common/04-dev-workflow.md#1-零干预开发流程)
- **项目上下文文件怎么生成？** → [04-dev-workflow.md](./common/04-dev-workflow.md#8-项目上下文文件规范)
- **初始化问卷怎么填？** → [templates/00-项目初始化问卷.md](./common/templates/00-项目初始化问卷.md)
- **反复修复不通过怎么办？** → [04-dev-workflow.md](./common/04-dev-workflow.md#9-卡点检测与恢复机制)
- **Git 怎么提交？** → [04-dev-workflow.md](./common/04-dev-workflow.md#3-git-提交规范)
- **本项目命名前缀？** → [project/01-project-specific.md](./project/01-project-specific.md#1-命名约定)
- **评测方向/方式怎么配？** → [project/01-project-specific.md](./project/01-project-specific.md#38-评测方向与测试方式配置)

## 规则加载优先级

> 4 个规则文件按场景加载，无需每次全部精读。

| 场景 | 必读规则 | 按需读规则 |
|------|---------|-----------|
| **每次开发** | 01-coding-standards, 04(§9 卡点恢复) | — |
| **功能点开发前** | 04(§1 零干预 + §8 上下文) | 02-architecture-patterns, 03-code-quality |
| **涉及安全/认证/文件** | 03(§5 安全规范) | — |
| **新项目启动** | templates/00-初始化问卷 | 全部 |
| **轻量修复**（bug 修复/重构/格式化） | 01-coding-standards, 04(§9 卡点恢复) | 跳过 plan 文件更新（仅更新代码日志） |

---

## 迁移到其他项目的方法

### 一句话总结

**`common/` 目录直接复制，`project/` 目录内容替换成新项目的。**

### 详细步骤

#### 第 1 步：复制通用规则

把整个 `common/` 目录复制到新项目的 `.trae/rules/` 下。
这部分完全通用，不需要修改。

#### 第 2 步：复制并修改项目定制规则

复制 `project/` 目录到新项目，然后修改以下内容：

**文件 1：`project/00-project-overview.md`**
- [ ] 项目名称 → 新项目名
- [ ] 项目目标 → 新项目的业务目标
- [ ] 技术栈表格 → 新项目实际使用的技术
- [ ] 核心功能列表 → 新项目的功能范围
- [ ] 关键约束 → 新项目的约束条件

**文件 2：`project/01-project-specific.md`**
- [ ] 「1.1 领域前缀」→ 替换为新项目的业务领域前缀
- [ ] 「1.3 异常类命名」→ 替换为新项目的异常体系
- [ ] 「2. 模块结构」→ 按新项目实际目录结构调整
- [ ] 「3. 领域特定规则」→ 补充新项目的业务规则

#### 第 3 步：可选优化

- 如果新项目不使用四层架构，可以删除或替换 `common/02-architecture-patterns.md`
- 如果项目有特殊的安全/合规要求，在 `project/` 下新增文件补充
- 如果团队有自己的 Git 流程，修改 `common/04-dev-workflow.md` 中的相关部分

### 迁移检查清单

- [ ] `common/` 目录已完整复制
- [ ] `project/00-project-overview.md` 已替换为新项目信息
- [ ] `project/01-project-specific.md` 已替换为新项目规则
- [ ] README 中的项目特定链接可正常访问
- [ ] 团队成员知晓并同意新规则

---

## 规则维护

- 规则不是一成不变的，发现不合理之处可以提出修改
- 修改规则需要团队评审通过
- **通用规则修改**：考虑是否需要同步到其他项目
- **项目定制规则修改**：仅影响当前项目
- 历史版本通过 Git 追溯
