---
name: project-analysis
description: 本地项目智能分析器。自动检测并分析当前项目目录，生成包含技术栈、架构、依赖关系、质量评分和最佳实践建议的多维分析报告。适用于代码审查、项目优化、文档生成等场景。当用户说"分析项目"、"生成项目文档"、"分析当前目录"、"评估项目质量"等时触发。
agent_created: true
---

# Local Project Analyzer - VS Code Copilot版

## 技能概述

分析当前项目的目录结构和代码，智能识别技术栈、架构模式、依赖关系，并生成包含质量评分、最佳实践建议的多维度分析报告。

此版本面向 VS Code Copilot Agent 运行场景：
- 默认分析整个项目（项目根目录）
- 优先使用 Copilot 内置工具完成扫描与统计
- 在耗时场景中，将原先脚本逻辑内化为执行约束，减少对外部 Python 脚本的强依赖
- 最终必须生成可留存的 Markdown 分析文档

## 适用场景

- 代码审查和项目评估
- 新项目快速了解
- 项目文档生成
- 架构分析和技术栈识别
- 代码质量评估
- 最佳实践建议

## 触发条件

用户以下意图时触发此技能：
- 分析项目、分析当前项目
- 生成项目文档、生成设计文档
- 分析当前目录、评估项目质量
- 这个项目用的是什么技术栈

## VS Code Copilot 执行约束

1. 默认范围
- 未指定目录时，分析整个项目根目录。
- 仅在用户明确要求时，缩小到 focus_dir。

2. 工具优先级
- 首选：list_dir、file_search、grep_search、read_file、semantic_search。
- 可选：execution_subagent 仅用于必要的单次统计或测试命令，不作为主路径。
- 非必要不调用本技能目录下 scripts/*.py。

3. 大项目降级策略
- 小型项目（<500 文件）：deep。
- 中型项目（500-2000 文件）：standard。
- 大型项目（>2000 文件）：quick（保留核心结论 + 风险项）。

4. 忽略目录
- node_modules、.git、.idea、.vscode、dist、build、target、__pycache__、venv、.venv、env、logs。

5. 输出硬约束
- 每次执行都必须产出 1 个 Markdown 主报告文件。
- 默认输出目录为项目根目录下 文档。
- 默认文件名：项目分析-{YYYYMMDD-HHmmss}.md。
- 若用户指定输出路径，遵从用户；若路径无效，回退到 文档 目录并继续输出。

## 分析流程（内化版）

### 1. 环境感知与初始化

- 检测项目根目录：优先识别 package.json、pom.xml、requirements.txt、pyproject.toml、Cargo.toml、go.mod、composer.json、Gemfile、.git。
- 统计项目规模：文件数、主要语言分布、核心目录。
- 自动选择分析深度：quick / standard / deep。

### 2. 技术栈识别

- 扫描配置文件：
  - Node.js：package.json
  - Python：requirements.txt、pyproject.toml
  - Java：pom.xml、build.gradle
  - Rust：Cargo.toml
  - Go：go.mod
- 结合代码特征识别框架：
  - 前端：React、Vue、Angular、Next.js
  - Python：Flask、Django、FastAPI
  - Java：Spring Boot
- 识别工具链：构建工具、测试框架、Lint/Format 工具。

### 3. 架构分析

- 生成目录结构摘要（不要求全量树，优先核心模块）。
- 识别架构模式：MVC、Monorepo、Micro-Frontend、分层架构等。
- 评估模块边界、职责清晰度、耦合风险。
- 输出代码组织评分（0-5）。

### 4. 依赖分析

- 解析直接依赖与 dev 依赖。
- 识别高风险依赖（过旧版本、体积大、与技术栈冲突）。
- 如可行，输出简化 Mermaid 依赖图代码块（可选，不强制图片渲染）。

### 5. 代码质量评估

按以下维度评分（每项 0-5）：
- 文档完整性：README、安装说明、使用说明、注释情况。
- 测试完整性：测试文件分布、测试框架、冒烟/单测存在性。
- 代码规范：命名、结构、风格一致性。
- 安全性：硬编码密钥、潜在注入风险、敏感信息暴露。
- 可维护性：超长文件/函数、重复代码、模块内聚度。

综合评分：给出总分、等级（A/A-/B/B-/C/D）与依据。

### 6. 最佳实践建议

- 生成技术栈专属建议（React/Vue/Python/Java 等）。
- 生成通用建议（文档、测试、安全、性能、规范）。
- 按优先级输出：高 / 中 / 低。
- 每条建议包含：问题、影响、建议动作、预估收益。

## 主报告输出模板（必须落地）

主报告至少包含以下章节：
- 执行摘要
- 项目概况（规模、目录、语言）
- 技术栈识别结果
- 架构分析
- 依赖与风险
- 质量评分卡
- 高优先级改进清单
- 设计文档留存段（架构决策与后续演进建议）

建议附录：
- 关键文件索引
- 统计口径说明
- 若有，Mermaid 依赖图代码块

## 参数约定

可选参数：
- focus_dir: 指定分析子目录
- include_tests: 是否包含测试代码（默认 true）
- analysis_depth: quick | standard | deep
- output_dir: 输出目录（默认 文档）
- overwrite: 是否覆盖同名文件（默认 false，推荐时间戳）

智能推断：
- 未指定 analysis_depth 时按项目规模自动选择。
- 未指定 output_dir 时默认使用 文档。
- 未指定 focus_dir 时默认分析整个项目。

## 错误处理

- 项目路径不存在：提示并请求更正。
- 无法识别项目类型：降级为通用分析并继续输出主报告。
- Token 或时间受限：降级为 quick 模式，但仍必须输出主报告。
- 依赖解析失败：标记失败原因并继续其他章节。

## 完成标准

满足以下条件才视为完成：
- 完成全项目或用户指定范围分析。
- 给出技术栈、架构、依赖、质量评分与建议。
- 在项目根目录 文档 下生成 Markdown 主报告文件。
- 报告可直接作为后续设计文档留存使用。
