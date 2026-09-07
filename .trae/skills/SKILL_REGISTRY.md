# 统一技能注册表

> **版本**: v1.0.0
> **最后更新**: 2026-09-04
> **定位**: 索引前后端所有技能，编排跨端开发流程

---

## 快速查找

| 任务 | 推荐技能 | 来源 |
|------|---------|------|
| 需求不明确，需要润色 | `qa-reset` | 后端/前端共有 |
| 需求分析 | `request-analysis` | 后端 |
| 任务拆分 | `task-spliter` | 后端 |
| 后端 API 开发 | `fastapi-python` → `coding-skill` | 后端 |
| 后端测试 | `python-testing` | 后端 |
| 后端代码审查 | `code-review` | 后端 |
| 前端 UI 开发 | `frontend-design` → `vercel-react-best-practices` | 前端 |
| 前端设计系统 | `ui-ux-pro-max` | 前端 |
| 前端原型设计 | `model-design` | 前端 |
| 设计文档生成 | `docs-design` | 后端/前端共有 |
| 项目分析 | `project-analysis` | 后端/前端共有 |
| 编码准则 | `karpathy-guidelines` | 后端/前端共有 |
| 技能发现 | `find-skills` | 后端/前端共有 |
| 写 PRD/研究报告 | `doc-writing-guide` | 系统内置 |
| 竞品调研 | `research-guide` | 系统内置 |
| 可视化图表 | `dynamic-ui` | 系统内置 |
| HTML 报告 | `html-report` | 系统内置 |
| 电子表格 | `xlsx` | 系统内置 |
| 创建新技能 | `skill-creator` | 系统内置 |
| Git 工作流 | `github:github` | 插件 |
| 发布到 GitHub | `github:yeet` | 插件 |
| 浏览器调试 | `chrome-devtools:chrome-devtools` | 插件 |
| 性能分析 | `chrome-devtools:chrome-performance` | 插件 |
| 高保真原型 | `rapid-prototype-craft:prototype-craft` | 插件 |
| Web UI 开发 | `web-app-development:uicraft` | 插件 |

## 技能分类

### P0 — 核心常驻

| Skill | 来源 | 定位 |
|-------|------|------|
| `qa-reset` | 共有 | 需求润色与交互模式识别 |
| `karpathy-guidelines` | 共有 | 编码准则（简洁/精准/目标驱动） |
| `fastapi-python` | 后端 | FastAPI 后端开发 |
| `frontend-design` | 前端 | 前端设计品质 |

### P1 — 高频按需

| Skill | 来源 | 定位 |
|-------|------|------|
| `request-analysis` | 后端 | 需求分析（新增类/修改类） |
| `task-spliter` | 后端 | 任务拆分 |
| `coding-skill` | 后端 | 编码实现（Controller/Service/Manager） |
| `python-testing` | 后端 | Python 测试 |
| `code-review` | 后端 | 代码审查 |
| `project-analysis` | 共有 | 项目分析器 |
| `vercel-react-best-practices` | 前端 | React 最佳实践与性能优化 |
| `ui-ux-pro-max` | 前端 | 设计系统规则库 |
| `find-skills` | 共有 | 技能发现与安装 |

### P2 — 中频按需

| Skill | 来源 | 定位 |
|-------|------|------|
| `design-doc-code-completion` | 后端 | 设计文档与代码补全 |
| `python-code-standards-validator` | 后端 | Python 规范验证 |
| `docs-design` | 共有 | 项目级设计文档 |
| `model-design` | 前端 | 独立 HTML 原型 |

### P3 — 低频/特殊场景

| Skill | 来源 | 定位 |
|-------|------|------|
| `python-project-bootstrap` | 后端 | 项目脚手架（最小化） |
| `python-scaffold` | 后端 | 完整脚手架 |
| `web-design-guidelines` | 前端 | Web 设计审计（⚠️ 依赖外部 URL） |

### 系统内置技能

| Skill | 定位 | 触发场景 |
|-------|------|---------|
| `doc-writing-guide` | 文档写作 | PRD、需求文档、研究报告 |
| `research-guide` | 调研分析 | 竞品分析、技术选型 |
| `dynamic-ui` | 内联可视化 | 架构图、流程图、数据对比 |
| `html-report` | HTML 报告 | 研究报告、仪表盘、PRD |
| `xlsx` | 电子表格 | 数据表、进度表 |
| `skill-creator` | 创建技能 | 新建自定义 skill |

### 插件技能

| Plugin:Skill | 定位 | 触发场景 |
|--------------|------|---------|
| `github:github` | Git 工作流 | 仓库管理、PR/Issue |
| `github:yeet` | 发布变更 | 提交、推送、开 PR |
| `github:gh-address-comments` | PR 评论处理 | 处理 review 意见 |
| `github:gh-fix-ci` | CI 修复 | 修复 GitHub Actions 失败 |
| `frontend-design:frontend-design` | 前端设计 | 品牌感 UI |
| `web-app-development:uicraft` | Web UI | 营销页、portfolio |
| `rapid-prototype-craft:prototype-craft` | 高保真原型 | 从 PRD/截图生成原型 |
| `chrome-devtools:chrome-devtools` | 浏览器调试 | 页面问题复现 |
| `chrome-devtools:chrome-performance` | 性能分析 | Core Web Vitals |

## 废弃/待替换技能

| Skill | 来源 | 状态 | 建议 |
|-------|------|------|------|
| `eval-direction-extension` | 后端 | 废弃 | 替换为 `step-feature-extension`（新增 Step 流） |
| `eval-case-design` | 后端 | 废弃 | 替换为 `step-case-design` |
| `target-system-integration` | 后端 | 废弃 | 替换为 `tts-llm-integration`（接入新 TTS/LLM） |
| `pymupdf-pdf` | 后端 | 废弃 | 与 video-cut 无关，移除 |

## 触发冲突解决规则

1. **需求澄清 > 直接执行**: 需求不明确时先 `qa-reset`
2. **后端技能处理后端代码**: 前端技能不处理后端
3. **前端技能处理前端代码**: 后端技能不处理前端
4. **系统内置 > 子项目**: 报告→`doc-writing-guide`，项目设计文档→`docs-design`
5. **具体 > 抽象**: 有明确产出物的技能优先
6. **审计 > 设计**: `web-design-guidelines` > `frontend-design`（审计场景）
7. **性能 > 通用**: `chrome-performance` > `chrome-devtools`（性能场景）

## 依赖关系图

```
独立层:
  qa-reset, karpathy-guidelines, find-skills, project-analysis,
  vercel-react-best-practices, fastapi-python, python-testing,
  code-review, request-analysis, task-spliter

被依赖层:
  ui-ux-pro-max ← (frontend-design, docs-design, model-design)
  coding-skill ← (fastapi-python 规范参考)
  design-doc-code-completion ← (request-analysis, task-spliter)

编排层（根级 WORKFLOW.md）:
  qa-reset → request-analysis → task-spliter → [后端/前端技能] → [测试] → code-review
```
