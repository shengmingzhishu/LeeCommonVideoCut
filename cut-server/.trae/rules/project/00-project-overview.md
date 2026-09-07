---
alwaysApply: true
version: 1.0.0
lastUpdated: 2026-09-04
description: video-cut 后端项目概述，包括项目目标、技术栈、7步流程、核心功能、关键约束。了解项目背景、制定技术方案、评估需求时使用此规则。
---
# 项目概述

> 本文档是 video-cut 后端（cut-server）项目的定制规则，仅适用于本项目。
> 接口契约权威文档: `cut-server/docs/04-接口契约.md`（v1.0.0）

## 项目名称

video-cut（后端 cut-server）

## 项目目标

构建本地化的漫剧/视频推广素材一键生产工具后端，支持 7 步流程自动生成 9:16 竖屏推广视频：
- 项目管理与历史版本管理
- 全局配置管理（AI/TTS/搜索引擎）
- 7 步流程：素材加载 → AI拆解+搜索 → 文案生成 → TTS音频+随机标记 → 虚拟预览标记保存 → ffmpeg裁切合并 → 合成+字幕导出
- 长任务管理（TTS/裁切/合成为异步任务）
- 生成历史保留与回滚

## 技术栈

| 类别 | 技术选型 | 说明 |
|------|---------|------|
| 编程语言 | Python 3.10+ | 遵循项目要求 |
| Web 框架 | FastAPI + Uvicorn | 异步高性能 API 服务，端口 8000 |
| 数据库 | SQLAlchemy 2.x + SQLite | 单文件零依赖，本地化部署 |
| ORM 模式 | 同步模式 | SQLAlchemy 2.x sync session |
| TTS | edge-tts（首选）+ pyttsx3（兜底） | 音频合成 |
| 视频处理 | ffmpeg + ffprobe | 系统级，PATH 可用 |
| AI 调用 | httpx | OpenAI 兼容协议（DeepSeek/火山云/OpenAI） |
| 搜索 | requests + beautifulsoup4 | Bing 搜索 |
| 日志 | loguru | 事务 ID 日志 |
| 测试 | pytest + pytest-asyncio + httpx | 单元测试与集成测试 |

## 项目范围

### 核心功能

1. **项目管理**
   - 项目 CRUD（创建/查询/更新/删除）
   - 项目复制、重置
   - 当前步骤状态管理（步骤锁定）

2. **全局配置管理**
   - AI 提供商配置（provider/apiKey/baseUrl/model）
   - TTS 引擎配置（engine/voice）
   - 搜索引擎配置（engine/apiKey）
   - 配置测试连接

3. **7 步流程**
   - Step1: 素材加载（扫描视频目录 + 读取介绍资料）
   - Step2: AI 拆解关键词（核心词/价值点/建议标题/搜索词）+ 搜索文章
   - Step3: AI 生成口播文案（4种风格：hot_review/objective/suspense/plot）
   - Step4: TTS 音频合成 + 随机标记视频片段（双线并行长任务）
   - Step5: 保存编辑后的标记（虚拟预览由前端实现，后端只存标记数据）
   - Step6: ffmpeg 裁切 + concat 合并（长任务）
   - Step7: 音视频合成 + 字幕烧录 → 最终 mp4（长任务）

4. **长任务管理**
   - 任务提交立即返回 taskId
   - 任务状态轮询（pending/running/completed/failed/cancelled/timeout）
   - 任务取消

5. **生成历史**
   - 每步骤每次生成保存历史版本
   - 历史查询与回滚

6. **文件交互**
   - 文件预览（视频流）
   - 文件下载
   - 目录浏览

### 非功能需求
- **本地化**: 零外部依赖（SQLite 单文件）
- **异步处理**: 长任务不阻塞 HTTP 响应
- **可追溯**: 事务 ID 贯穿日志
- **步骤锁定**: 禁止跳过未完成步骤
- **0 IO 预览**: Step5 后端只存标记数据，不触发 ffmpeg

## 关键约束

1. **步骤锁定**: 7 步流程有前置条件，不可跳过
2. **长任务异步**: TTS/裁切/合成通过 taskId 轮询，不阻塞
3. **0 IO 预览**: Step5 禁止 ffmpeg 操作
4. **配置驱动**: AI/TTS/搜索引擎运行时配置切换
5. **错误码统一**: `{ code, msg, data }`，HTTP 固定 200
6. **字段映射**: snake_case → camelCase（通过 to_camel 转换器）
7. **ffmpeg 系统级**: 不硬编码路径，从 PATH 获取
8. **敏感信息不记日志**: API Key 等脱敏处理

## 架构层级

项目采用四层架构（详见 `common/02-architecture-patterns.md`）：

- **Controller 层**：路由、参数校验、响应封装
- **Service 层**：单领域业务逻辑（项目管理、配置管理、Step 业务）
- **Manager 层**：跨领域编排（Step4 双线并行、外部系统适配、长任务调度）
- **Model 层**：数据模型（SQLAlchemy）、Pydantic Schema

## 数据模型

### 核心表（3 张）

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `vc_project` | 项目 | id(UUID), title, author, intro, video_dir, intro_dir, current_step, status, output_path |
| `vc_generation_history` | 生成历史 | id, project_id, step_num, version, result_type, result_data(JSON), status, duration_ms |
| `vc_config` | 全局配置 | key, value, updated_at |

### 步骤结果类型

`load | analyze | script | audio | markers | edit_markers | cut_video | final`

## 外部系统

| 系统 | 用途 | 配置方式 |
|------|------|---------|
| LLM | Step2 关键词拆解 + Step3 文案生成 | 运行时配置（aiProvider/aiApiKey/aiBaseUrl/aiModel） |
| 搜索引擎 | Step2 搜索文章 | Bing（默认）/ DuckDuckGo（兜底） |
| TTS | Step4 音频合成 | edge-tts（首选）/ pyttsx3（兜底） |
| ffmpeg | Step6 裁切 + Step7 合成 | 系统级 PATH |

## 与前端协作约定

- 前端服务: `cut-web`（React 18 + Vite，端口 5173）
- 接口契约: `cut-server/docs/04-接口契约.md`（v1.0.0，单一权威）
- 统一响应: `{ code: 0, msg: "ok", data: { ... } }`，HTTP 固定 200
- 错误码: 0=成功 / 40xxx=业务 / 50xxx=服务 / 60xxx=长任务
- Trace: 请求带 `X-Trace-Id` header
- 字段映射: 后端 snake_case ↔ 前端 camelCase
- CORS: 允许 `http://localhost:5173`
- 鉴权: 本期默认放行，预留 Bearer Token
