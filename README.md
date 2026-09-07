# LeeCommonVideoCut

> **video-cut · 视频剪辑工具（前后端分离）**
> 面向漫剧 / 视频推广素材的一键式本地化生产工具

## 一句话简介

> AI 拆解关键词 → 搜索文章 → 生成口播文案 → TTS 合成音频 → 标记视频片段 → 虚拟串播预览 → 确认后裁切 → 合成最终成品。
> 7 步流程，0 素材浪费，所有版本可回滚。

## 快速跳转表

> **新人第一站**：从右侧"我要做什么"挑一行，跳过去。

| 我要做什么 | 跳到哪 |
| --- | --- |
| 了解 video-cut 整体规则评估与整改 | [docs/cut-rules-and-skills-analysis.md](./docs/cut-rules-and-skills-analysis.md) |
| 了解前后端协作契约（接口、字段、错误码） | [docs/00-跨端协作约定.md](./docs/00-跨端协作约定.md) |
| 看权威的接口契约文档 | [cut-server/docs/04-接口契约.md](./cut-server/docs/04-接口契约.md) |
| 改后端代码 | [cut-server/.trae/rules/README.md](./cut-server/.trae/rules/README.md) |
| 改前端代码 | [cut-web/.trae/rules/README.md](./cut-web/.trae/rules/README.md) |
| 看后端 skill 工作流 | [cut-server/.trae/skills/WORKFLOW.md](./cut-server/.trae/skills/WORKFLOW.md) |
| 看前端 skill 注册表 | [cut-web/.trae/skills/SKILL_REGISTRY.md](./cut-web/.trae/skills/SKILL_REGISTRY.md) |
| 看后端变更历史 | [cut-server/.trae/CHANGELOG.md](./cut-server/.trae/CHANGELOG.md) |
| 看前端变更历史 | [cut-web/.trae/CHANGELOG.md](./cut-web/.trae/CHANGELOG.md) |
| 启动后端 | [cut-server/README.md](./cut-server/README.md)（待补） |
| 启动前端 | [cut-web/README.md](./cut-web/README.md)（待补） |
| 看后端初始化问卷 | [cut-server/docs/01-项目初始化问卷.md](./cut-server/docs/01-项目初始化问卷.md) |
| 看前端初始化问卷 | [cut-web/docs/01-项目初始化问卷.md](./cut-web/docs/01-项目初始化问卷.md) |

## 项目结构

```
LeeCommonVideoCut/
├── docs/                          # 跨端总文档（接口协作、评估、整改）
│   ├── 00-跨端协作约定.md            ⭐ 前后端字段/错误码/traceId 硬规则
│   └── cut-rules-and-skills-analysis.md  # 当前规则体系评估与整改建议
├── .trae/                          # 根级 AI 编排层（上一代 ai-eval 模板，备用）
├── cut-server/                     # 后端：Python + FastAPI
│   ├── .trae/
│   │   ├── rules/                 # ⭐ 后端规则（看这里）
│   │   ├── skills/                # ⭐ 后端技能
│   │   │   └── WORKFLOW.md        # 5 套工作流矩阵
│   │   └── CHANGELOG.md
│   └── docs/
│       ├── 01-项目初始化问卷.md     ⭐ 后端启动问卷
│       └── 04-接口契约.md          ⭐ 权威接口契约
├── cut-web/                        # 前端：React + TypeScript + Vite
│   ├── .trae/
│   │   ├── rules/                 # ⭐ 前端规则（看这里）
│   │   ├── skills/                # ⭐ 前端技能
│   │   │   └── SKILL_REGISTRY.md  # 技能注册表 + 触发冲突解决
│   │   └── CHANGELOG.md
│   └── docs/
│       └── 01-项目初始化问卷.md     ⭐ 前端启动问卷
└── AI漫剧剪辑师旧参考项目代码/          # 历史参考（只读，不在开发范围）
```

## 子项目

- **后端** [`cut-server/`](./cut-server/)：Python 3.10+ / FastAPI / SQLAlchemy / ffmpeg
  - 四层架构：Controller → Service → Manager → Model
  - 异步任务、SQLite、edge-tts、本地 ffmpeg
- **前端** [`cut-web/`](./cut-web/)：React 18 / TypeScript / Vite / Ant Design / Zustand
  - feature-based 架构
  - 7 步向导 + 虚拟串播预览

## 业务概览

7 步流程：

```
Step1 输入项目信息 → Step2 AI 拆解 + 搜索 → Step3 生成口播文案
  → Step4 音频生成 + 视频标记（并行）
  → Step5 虚拟预览 + 编辑标记（0 IO）
  → Step6 ffmpeg 裁切合并 → Step7 音视频合成 + 字幕 → 导出 mp4
```

## AI 协作入口

- **跨端协作**：[docs/00-跨端协作约定.md](./docs/00-跨端协作约定.md)
- **项目身份**：[.trae/rules/project/00-project-overview.md](./.trae/rules/project/00-project-overview.md)
- **项目特定规则**：[.trae/rules/project/01-project-specific.md](./.trae/rules/project/01-project-specific.md)

## 历史参考

`AI漫剧剪辑师旧参考项目代码/` 是单文件 HTML + Python 后端的旧实现，仅作为需求与算法思路参考保留，**禁止直接复用其代码**。

## 启动方式（待补）

后端、前端各自的启动步骤会在两个子项目的 README 中维护。

---

_文档版本：v1.1（2026-09-03 整改首版）_
