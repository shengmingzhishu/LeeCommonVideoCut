# video-cut 项目特定规则

> alwaysApply: true
> 版本: v1.0.0
> 最后更新: 2026-09-04

---

## 1. 领域命名约定

### 1.1 领域前缀

| 前缀 | 含义 | 示例 |
|------|------|------|
| `VC` | video-cut 项目全局 | `VCCutError`, `VCProjectConfig` |
| `Project` | 项目管理 | `ProjectController`, `ProjectService` |
| `Step` | 步骤流程 | `Step1Controller`, `Step4Manager` |
| `Marker` | 视频标记 | `VideoMarker`, `MarkerTimeline` |
| `Audio` | 音频相关 | `AudioTTSManager`, `AudioTTSError` |
| `Cut` | 裁切合并 | `CutVideoManager`, `CutError` |
| `Compose` | 合成导出 | `ComposeManager`, `ComposeError` |
| `History` | 生成历史 | `HistoryController`, `HistoryService` |
| `Task` | 长任务 | `TaskStatus`, `TaskNotFoundError` |
| `Config` | 全局配置 | `ConfigService`, `ConfigKey` |

### 1.2 命名铁律

- 后端类名: `{Domain}{Layer}{Name}`（如 `Step4AudioManager`）
- 后端异常: `{Domain}Error`（如 `StepLockError`, `AudioTTSError`, `FfmpegError`）
- 前端组件: `{Feature}Panel` / `{Feature}Modal` / `{Feature}Timeline`
- 前端 Hook: `use{Feature}{Action}`（如 `useStep4Audio`, `useTaskPoll`）
- 前端 Service: `{feature}Service`（如 `projectService`, `step4Service`）
- 前端 Store: `use{Feature}Store`（如 `useProjectStore`, `useConfigStore`）

## 2. 步骤锁定规则

### 2.1 步骤状态机

```
Step1 → Step2 → Step3 → Step4 → Step5 → Step6 → Step7
```

每个步骤有前置条件：
- Step2 需 Step1 完成（素材已加载）
- Step3 需 Step2 完成（关键词已拆解）
- Step4 需 Step3 完成（文案已生成/确认）
- Step5 需 Step4 完成（音频+标记已生成）
- Step6 需 Step5 完成（标记已编辑/确认）
- Step7 需 Step6 完成（视频已裁切合并）

### 2.2 步骤跳转规则

- 禁止跳过未完成的步骤
- 允许回退到已完成步骤重新执行（会清除后续步骤的历史）
- `currentStep` 字段记录当前可执行步骤

### 2.3 异常体系

根异常: `VideoCutServerError`

```
VideoCutServerError
├── StepLockError          # 步骤锁定冲突
├── ProjectNotFoundError   # 项目不存在
├── MaterialNotFoundError  # 素材不存在
├── AudioTTSError          # TTS 合成失败
├── FfmpegError            # ffmpeg 执行失败
├── LLMError               # LLM 调用失败
├── SearchError            # 搜索引擎异常
├── FileOperationError     # 文件操作失败
├── TaskNotFoundError      # 任务不存在
└── ConfigError            # 配置缺失/无效
```

## 3. 长任务管理

### 3.1 长任务类型

| 步骤 | 任务类型 | 预期耗时 | 可取消 |
|------|---------|---------|--------|
| Step4 | TTS 音频合成 | 10-60 秒 | 是 |
| Step4 | 随机标记 | 1-5 秒 | 否 |
| Step6 | ffmpeg 裁切+合并 | 10-120 秒 | 是 |
| Step7 | ffmpeg 合成+字幕 | 10-60 秒 | 是 |

### 3.2 任务状态

```
pending → running → completed | failed | cancelled | timeout
```

### 3.3 任务管理铁律

1. 长任务提交后立即返回 `taskId`，不阻塞 HTTP 响应
2. 前端通过 `GET /api/task/{id}` 轮询（间隔 1-2 秒）
3. 前端页卸载时必须取消轮询
4. 任务失败后提供「重试」入口
5. 任务超时阈值: 300 秒（可配置）

## 4. 虚拟预览规则（Step5 铁律）

### 4.1 0 IO 原则

Step5 虚拟预览阶段**禁止触发任何 ffmpeg IO 操作**。

- 预览通过 `<video>.currentTime` 模拟串播
- 标记片段的裁切/合并只在 Step6 执行
- 前端只保存编辑后的标记列表，不生成中间文件

### 4.2 实现约束

- `<video>` 元素跨源: 确保 `videoDir` 中的文件可被浏览器直接访问（通过后端 file preview 接口）
- `seeked` 事件节流: 连续 seek 时做 debounce，避免频繁触发
- 媒体资源回收: 切换项目或步骤时，释放 `<video>` src
- `MarkerTimeline` 组件定位: 复杂度高 + 复用性强 + 职责单一 → 放入 `core/MarkerTimeline/`

## 5. 数据库约定

### 5.1 表命名

- 单数 + `vc_` 前缀（如 `vc_project`, `vc_config`）
- 不使用复数（如 `vc_projects` ❌）

### 5.2 字段命名

- snake_case
- 主键: `id`（UUID 字符串）
- 时间戳: `created_at`, `updated_at`
- JSON 字段: 使用 TEXT 存储 JSON 字符串

### 5.3 迁移

- 使用 SQLite 手工 SQL 或 alembic
- 每次表结构变更必须在后端 plan 目录记录迁移脚本

## 6. 视频处理约定

### 6.1 ffmpeg 调用

- 所有 ffmpeg 命令通过后端 Manager 层调用
- 禁止前端直接调用 ffmpeg
- ffmpeg 路径必须从系统 PATH 获取，不硬编码

### 6.2 输出格式

- 最终导出: MP4 (H.264 + AAC)
- 视频尺寸: 9:16 竖屏（如 1080x1920）
- 字幕: SRT 格式，通过 ffmpeg burn-in 烧录

### 6.3 临时文件

- 中间产物存放在项目 `output_path` 下的 `.tmp/` 目录
- 任务完成后清理临时文件
- 异常中断后下次启动时检查并清理残留临时文件

## 7. 配置管理

### 7.1 配置项

| Key | 说明 | 默认值 |
|-----|------|--------|
| `ai_provider` | AI 提供商 | deepseek |
| `ai_api_key` | AI API Key | — |
| `ai_base_url` | AI Base URL | — |
| `ai_model` | AI 模型名 | deepseek-chat |
| `tts_engine` | TTS 引擎 | edge-tts |
| `tts_voice` | TTS 语音 | zh-CN-XiaoxiaoNeural |
| `search_engine` | 搜索引擎 | bing |
| `bing_api_key` | Bing API Key | — |

### 7.2 配置铁律

- 敏感信息（API Key）不记日志
- 配置变更后需要调用 `POST /api/config/test-connection` 验证
- 配置缺失时返回明确错误，不使用默认值静默运行
