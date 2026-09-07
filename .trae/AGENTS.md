# AGENTS.md — 父层 AI 编排指南

> **版本**: v1.0.0
> **最后更新**: 2026-09-04
> **适用对象**: 在仓库根目录打开的 AI Agent（父层对话框）

---

## 0. 项目身份

| 项 | 值 |
|----|-----|
| 项目名 | LeeCommonVideoCut（简称 video-cut） |
| 定位 | 面向漫剧/视频推广素材的一键式本地化生产工具 |
| 核心流程 | 7 步：输入信息 → AI拆解搜索 → 生成文案 → 音频+标记（并行） → 虚拟预览 → ffmpeg裁切 → 合成导出 |
| 架构 | 前后端分离 monorepo |

## 1. 仓库结构

```
LeeCommonVideoCut/
├── .trae/                    # ← 你在这里：根级 AI 编排层
│   ├── AGENTS.md             # 本文件
│   ├── rules/                # 跨端协作规则（不与子项目冲突）
│   ├── skills/               # 统一技能注册表 + 工作流编排
│   └── docs/                 # 项目级管理文档
├── cut-server/               # 后端：Python + FastAPI
│   └── .trae/                # 后端独立 rules + skills
├── cut-web/                  # 前端：React + TypeScript + Vite
│   └── .trae/                # 前端独立 rules + skills
├── AI漫剧剪辑师旧参考项目代码/   # 历史参考（只读，禁止复用代码）
└── docs/                     # 仓库级文档（评估报告等）
```

## 2. 规则层级与冲突解决

```
根 .trae/rules/         ← 跨端协作、项目总览、统一工作流（父层关注）
├── cut-server/.trae/rules/  ← Python 编码规范、四层架构、后端测试（子层关注）
└── cut-web/.trae/rules/     ← TS/React 编码规范、feature-based 架构、前端测试（子层关注）
```

**铁律**：
1. 根级规则只管「跨端协作 + 项目级管理」，不侵入子项目的编码/架构/测试规则
2. 子项目规则只管「本端内部实现」，不定义跨端约定
3. 当根级与子级出现矛盾时，**根级跨端规则优先**（接口契约、字段映射、错误码）
4. 编码规范、架构模式、测试策略由子项目自主决定，根级不覆盖

## 3. 任务路由策略

当用户提出开发需求时，按以下策略路由：

| 需求特征 | 路由到 | 使用的规则/技能 |
|----------|--------|----------------|
| 纯后端 API 开发 | `cut-server/` | cut-server rules + fastapi-python/coding-skill/python-testing/code-review |
| 纯前端 UI 开发 | `cut-web/` | cut-web rules + frontend-design/vercel-react-best-practices |
| 接口变更（新增/修改 API） | **两端联动** | 根级 01-cross-end-conventions + 子项目编码技能 |
| 跨端 Bug（前后端字段不匹配） | **两端联动** | 根级 01-cross-end-conventions + 接口契约对照 |
| 项目级需求（新功能规划） | 根级 | qa-reset → request-analysis → task-spliter → 子项目技能 |
| 前后端联调 | 根级 | 根级 02-unified-workflow + 联调 checklist |

## 4. 接口契约权威性

**接口契约文档**：`cut-server/docs/04-接口契约.md`（v1.0.0）

这是前后端 API 的**唯一权威来源**。任何接口变更必须：
1. 先改契约文档
2. 后端按契约实现/修改
3. 前端按契约生成/对齐 TypeScript 类型
4. 在 PR 描述中引用契约版本号

**核心约定**：
- Base URL: `http://localhost:8000/api`
- 统一响应: `{ code: 0, msg: "ok", data: { ... } }`，HTTP 固定 200
- Trace: 所有请求带 `X-Trace-Id` header
- 错误码: 0=成功 / 40xxx=业务错误 / 50xxx=服务异常 / 60xxx=长任务失败
- 字段映射: 后端 snake_case ↔ 前端 camelCase（通过 `to_camel` 转换器）

## 5. 技能编排矩阵

### 5.1 系统内置技能（根级可用）

| Skill | 用途 | 何时使用 |
|-------|------|---------|
| `doc-writing-guide` | 文档写作 | 写 PRD、需求文档、研究报告 |
| `research-guide` | 竞品调研 | 技术选型、竞品分析 |
| `dynamic-ui` | 内联可视化 | 架构图、流程图、数据对比 |
| `html-report` | HTML 报告 | 研究报告、仪表盘 |
| `xlsx` | 电子表格 | 数据表、进度表 |
| `skill-creator` | 创建技能 | 需要新建自定义 skill 时 |

### 5.2 插件技能（按需调用）

| Plugin:Skill | 用途 |
|--------------|------|
| `github:github` | Git 工作流、PR 管理 |
| `github:yeet` | 发布变更到 GitHub |
| `frontend-design:frontend-design` | 前端设计品质提升 |
| `web-app-development:uicraft` | Web UI 开发 |
| `rapid-prototype-craft:prototype-craft` | 高保真原型 |
| `chrome-devtools:chrome-devtools` | 浏览器调试 |
| `chrome-devtools:chrome-performance` | 性能分析 |

### 5.3 后端技能（cut-server/.trae/skills/）

| Skill | 用途 | 状态 |
|-------|------|------|
| `qa-reset` | 需求润色与结构化 | 活跃 |
| `request-analysis` | 需求分析 | 活跃 |
| `task-spliter` | 任务拆分 | 活跃 |
| `fastapi-python` | FastAPI 开发 | 活跃 |
| `coding-skill` | 编码实现（Controller/Service/Manager） | 活跃 |
| `python-testing` | Python 测试 | 活跃 |
| `code-review` | 代码审查 | 活跃 |
| `design-doc-code-completion` | 设计文档与代码补全 | 活跃 |
| `karpathy-guidelines` | 编码准则 | 活跃 |
| `project-analysis` | 项目分析 | 活跃 |
| `python-code-standards-validator` | Python 规范验证 | 活跃 |
| `python-project-bootstrap` | 项目脚手架 | 按需 |
| `python-scaffold` | 完整脚手架 | 按需 |
| `find-skills` | 技能发现 | 按需 |
| `eval-direction-extension` | ⛔ 评测方向扩展（待替换） | 废弃 |
| `eval-case-design` | ⛔ 评测用例设计（待替换） | 废弃 |
| `target-system-integration` | ⛔ 目标系统接入（待替换） | 废弃 |
| `pymupdf-pdf` | ⛔ PDF 解析（与项目无关） | 废弃 |

### 5.4 前端技能（cut-web/.trae/skills/）

| Skill | 用途 | 状态 |
|-------|------|------|
| `qa-reset` | 需求润色与结构化 | 活跃 |
| `karpathy-guidelines` | 编码准则 | 活跃 |
| `find-skills` | 技能发现 | 按需 |
| `project-analysis` | 项目分析 | 活跃 |
| `docs-design` | 设计文档 | 活跃 |
| `model-design` | HTML 原型 | 按需 |
| `frontend-design` | 前端设计 | 活跃 |
| `ui-ux-pro-max` | UI/UX 设计系统 | 活跃 |
| `vercel-react-best-practices` | React 最佳实践 | 活跃 |
| `web-design-guidelines` | Web 设计审计 | ⚠️ 依赖外部 URL |

### 5.5 技能冲突解决规则

1. **需求澄清优先**: 当需求不明确时，先用 `qa-reset` 润色，再进入开发
2. **后端任务路由到后端技能**: 前端技能不处理后端代码
3. **前端任务路由到前端技能**: 后端技能不处理前端代码
4. **系统内置技能 > 子项目技能**: 当 `doc-writing-guide` 与 `docs-design` 同时可触发时，按产出类型选择（报告→doc-writing-guide，项目设计文档→docs-design）
5. **具体 > 抽象**: 有明确产出物的技能优先

## 6. 7 步流程与接口映射

| 步骤 | 后端接口 | 前端页面 | 关键技术 |
|------|---------|---------|---------|
| Step1 输入信息 | POST /api/step1/load | Step1 面板 | 素材目录扫描 |
| Step2 AI拆解+搜索 | POST /api/step2/analyze | Step2 面板 | LLM + Web Search |
| Step3 生成文案 | POST /api/step3/generate | Step3 面板 | LLM 4种风格 |
| Step4 音频+标记（并行） | POST /api/step4/audio + markers | Step4 面板 | edge-tts + 随机标记 |
| Step5 虚拟预览 | PUT /api/step5/save | Step5 面板 | `<video>.currentTime` 0 IO |
| Step6 裁切合并 | POST /api/step6/cut | Step6 面板 | ffmpeg 裁切 + concat |
| Step7 合成导出 | POST /api/step7/compose | Step7 面板 | ffmpeg 合成 + 字幕烧录 |

## 7. 开发环境

| 项 | 后端 | 前端 |
|----|------|------|
| 端口 | 8000 | 5173 |
| 语言 | Python 3.10+ | TypeScript 5+ |
| 框架 | FastAPI + Uvicorn | React 18 + Vite |
| 数据库 | SQLite | — |
| 视频处理 | ffmpeg + ffprobe | — |
| TTS | edge-tts | — |
| UI 库 | — | Ant Design 5 |
| 状态管理 | — | Zustand |
| 测试 | pytest | Vitest + Playwright |

**启动顺序**: 先启动后端（8000）→ 再启动前端（5173）→ 前端通过 Vite proxy 代理到后端

## 8. 进度追踪

项目进度文档：`.trae/docs/03-开发进度.md`

每次完成一个功能点后，更新进度文档中的状态：
- `pending` → `designing` → `developing` → `testing` → `done`

## 9. 禁止事项

1. 禁止直接复用 `AI漫剧剪辑师旧参考项目代码/` 中的代码
2. 禁止在不更新接口契约的情况下修改 API
3. 禁止前端在后端未实现时 mock 不一致的数据结构
4. 禁止后端在前端未对齐时擅自改字段名
5. 禁止跳过 code-review 直接合并代码
6. 禁止在 Step5 编辑阶段触发任何 ffmpeg IO 操作（虚拟预览 0 IO 铁律）
