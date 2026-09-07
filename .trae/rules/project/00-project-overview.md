# video-cut 项目总览

> alwaysApply: true
> 版本: v1.0.0
> 最后更新: 2026-09-04

---

## 1. 项目身份

| 项 | 值 |
|----|-----|
| 项目名 | LeeCommonVideoCut（video-cut） |
| 定位 | 面向漫剧/视频推广素材的一键式本地化生产工具 |
| 目标用户 | 无剪辑经验的漫剧推广从业者 |
| 核心价值 | 7 步流程自动生成 9:16 竖屏推广视频；虚拟预览（0 IO）避免反复切片；多次生成保留历史版本 |
| 部署方式 | 本地化（Windows 10/11） |

## 2. 7 步流程

```
Step1 输入项目信息 → Step2 AI拆解+搜索 → Step3 生成口播文案
  → Step4 音频生成+视频标记（并行）
  → Step5 虚拟预览+编辑标记（0 IO）
  → Step6 ffmpeg 裁切合并 → Step7 音视频合成+字幕 → 导出 mp4
```

| 步骤 | 输入 | 输出 | 关键技术 |
|------|------|------|---------|
| Step1 | 项目标题/作者/简介/视频目录/介绍资料目录 | 素材清单（视频文件列表 + 介绍文本） | os.walk 文件扫描 |
| Step2 | 素材清单 | 关键词拆解（核心词/价值点/建议标题/搜索词）+ 搜索结果 | LLM + Web Search |
| Step3 | 关键词+搜索结果 | 口播长文（4种风格：hot_review/objective/suspense/plot） | LLM 生成 |
| Step4 | 口播文案+视频目录 | TTS 音频文件 + 随机标记片段列表 | edge-tts + 随机算法 |
| Step5 | 音频+标记片段 | 编辑后的标记片段（用户可增删改标记） | `<video>.currentTime` 0 IO 预览 |
| Step6 | 编辑后的标记 | 裁切+合并后的视频片段 | ffmpeg cut + concat |
| Step7 | 合并视频+音频+字幕 | 最终 mp4 成品 | ffmpeg compose + subtitle burn |

## 3. 技术栈

### 3.1 后端（cut-server）

| 类别 | 选型 |
|------|------|
| 语言 | Python 3.10+ |
| Web 框架 | FastAPI（异步） |
| ASGI | uvicorn[standard] |
| 数据库 | SQLite（单文件零依赖） |
| ORM | SQLAlchemy 2.x（同步模式） |
| TTS | edge-tts（首选）+ pyttsx3（兜底） |
| 视频处理 | ffmpeg + ffprobe（系统级） |
| AI | httpx（OpenAI 兼容协议，支持 DeepSeek/火山云/OpenAI） |
| 搜索 | requests + beautifulsoup4（Bing） |
| 日志 | loguru |
| 测试 | pytest + pytest-asyncio + httpx |

### 3.2 前端（cut-web）

| 类别 | 选型 |
|------|------|
| 语言 | TypeScript 5+（strict） |
| UI 框架 | React 18（函数组件 + Hooks） |
| 构建 | Vite |
| UI 组件库 | Ant Design 5.x（深色科技风） |
| 路由 | React Router v6 |
| 状态管理 | Zustand |
| 样式 | CSS Modules + SCSS |
| 请求 | axios + 自封装 core/request.ts |
| 表单 | React Hook Form + Zod |
| 测试 | Vitest + Playwright |

## 4. 架构边界

### 4.1 后端四层架构

```
Controller → Service → Manager → Model
```
- Controller: 请求路由、参数校验、响应组装
- Service: 单领域业务逻辑
- Manager: 跨服务编排、复杂流程、外部系统对接
- Model: 数据模型（SQLAlchemy）
- core/: 纯算法/策略实现（裁切计算、字幕生成等），由 Manager 调用

### 4.2 前端 feature-based 架构

```
Pages → Components{basic, business} → Hooks → Services → Store → Utils/Types
```
- Pages: 按页面组织（项目列表 + Step1~7 + 配置 + 历史）
- Components: basic（通用 UI）、business（业务组件）
- Hooks: 数据逻辑复用（useRequest, usePolling, useTaskPoll）
- Services: API 调用层
- Store: 全局状态（项目列表、当前步骤、配置）
- core/: 复杂度高+复用性强+职责单一的组件（如 MarkerTimeline）

## 5. 数据模型

### 5.1 核心表（3 张）

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `vc_project` | 项目 | id(UUID), title, author, intro, video_dir, intro_dir, current_step, status, output_path |
| `vc_generation_history` | 生成历史 | id, project_id, step_num, version, result_type, result_data(JSON), status, duration_ms |
| `vc_config` | 全局配置 | key, value, updated_at |

### 5.2 步骤结果类型

`load | analyze | script | audio | markers | edit_markers | cut_video | final`

## 6. 外部系统

| 系统 | 用途 | 配置方式 |
|------|------|---------|
| LLM | Step2 关键词拆解 + Step3 文案生成 | 运行时配置（aiProvider/aiApiKey/aiBaseUrl/aiModel） |
| 搜索引擎 | Step2 搜索文章 | Bing（默认）/ DuckDuckGo（兜底） |
| TTS | Step4 音频合成 | edge-tts（首选）/ pyttsx3（兜底） |
| ffmpeg | Step6 裁切 + Step7 合成 | 系统级 PATH |

## 7. 接口契约

**权威文档**: `cut-server/docs/04-接口契约.md`（v1.0.0）

- Base URL: `http://localhost:8000/api`
- 统一响应: `{ code, msg, data }`，HTTP 固定 200
- 错误码: 0=成功 / 40xxx=业务 / 50xxx=服务 / 60xxx=长任务
- 字段映射: 后端 snake_case ↔ 前端 camelCase

前后端任何接口变更，必须先改契约文档。详见 `common/01-cross-end-conventions.md`。

## 8. 历史参考

`AI漫剧剪辑师旧参考项目代码/` 是旧版单文件 HTML + Python 实现，仅作为需求与算法思路参考。**禁止直接复用其代码**。

## 9. 协作约定

- 前端端口: 5173，后端端口: 8000
- 启动顺序: 先后端后前端
- Vite proxy: `/api` → `http://localhost:8000`
- CORS: 后端限定 `http://localhost:5173`
- 本期无强制鉴权，预留 Bearer Token
