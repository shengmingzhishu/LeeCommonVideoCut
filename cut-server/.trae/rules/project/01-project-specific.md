---
alwaysApply: true
version: 1.0.0
lastUpdated: 2026-09-04
---
# 项目特定规则

> 本文档定义 video-cut 后端（cut-server）项目特有的命名约定、模块结构和领域规则。
> 接口以 `docs/04-接口契约.md` 为权威，前后端任何修改必须先改契约。

## 1. 命名约定

### 1.1 领域前缀

| 领域 | 前缀（类/函数） | 示例 |
|------|-----------------|------|
| 项目管理 | `Project` / `project_` | `ProjectController`, `project_id` |
| 步骤流程 | `Step` / `step_` | `Step4AudioManager`, `step_num` |
| 视频标记 | `Marker` / `marker_` | `VideoMarker`, `marker_start` |
| 音频 | `Audio` / `audio_` | `AudioTTSManager`, `audio_path` |
| 裁切合并 | `Cut` / `cut_` | `CutVideoManager`, `cut_segments` |
| 合成导出 | `Compose` / `compose_` | `ComposeManager`, `compose_output` |
| 生成历史 | `History` / `history_` | `HistoryService`, `history_id` |
| 长任务 | `Task` / `task_` | `TaskStatus`, `task_id` |
| 全局配置 | `Config` / `config_` | `ConfigService`, `config_key` |
| 项目全局 | `VC` | `VideoCutServerError`, `VC_PROJECT` |

服务类以 `Service` 结尾，管理器类以 `Manager` 结尾，控制器类以 `Controller` 结尾。

### 1.2 video-cut 相关命名

- 项目: `project`（变量）/ `Project`（类型）/ `ProjectCard`（组件）
- 步骤: `step` / `Step` / `Step4Panel`
- 标记: `videoMarker` / `VideoMarker` / `MarkerTimeline`
- 音频: `audio` / `Audio` / `AudioTTSError`
- 裁切: `cut` / `Cut` / `CutVideoManager`
- 合成: `compose` / `Compose` / `ComposeManager`
- 任务: `task` / `Task` / `TaskStatus`
- 配置: `config` / `Config` / `ConfigService`

### 1.3 步骤枚举

```python
class StepNum(int, Enum):
    """7 步流程步骤编号。"""
    STEP1_LOAD = 1        # 素材加载
    STEP2_ANALYZE = 2     # AI拆解+搜索
    STEP3_GENERATE = 3    # 文案生成
    STEP4_AUDIO = 4       # TTS+标记（并行）
    STEP5_SAVE = 5        # 标记保存
    STEP6_CUT = 6         # 裁切合并
    STEP7_COMPOSE = 7     # 合成导出


class TaskType(str, Enum):
    """长任务类型。"""
    TTS_AUDIO = "tts_audio"
    RANDOM_MARKERS = "random_markers"
    CUT_VIDEO = "cut_video"
    COMPOSE_FINAL = "compose_final"


class TaskStatus(str, Enum):
    """任务状态。"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
```

### 1.4 异常类命名

```
VideoCutServerError                      # 项目根异常
├── StepLockError                        # 步骤锁定冲突
├── ProjectNotFoundError                 # 项目不存在
├── MaterialNotFoundError                # 素材不存在
├── AudioTTSError                        # TTS 合成失败
├── FfmpegError                          # ffmpeg 执行失败
│   ├── FfmpegCutError                   # 裁切失败
│   └── FfmpegComposeError               # 合成失败
├── LLMError                              # LLM 调用失败
├── SearchError                           # 搜索引擎异常
├── FileOperationError                    # 文件操作失败
├── TaskNotFoundError                     # 任务不存在
├── TaskCancelledError                    # 任务已取消
├── TaskTimeoutError                      # 任务超时
├── ConfigError                           # 配置缺失/无效
└── MarkerRangeError                      # 标记范围异常
```

## 2. 模块结构

> 各层职责定义见 `common/02-architecture-patterns.md` §1（分层架构）、§1.3（core/ 定位）、§1.4（何时用 Manager 层）。
> 接口以 `docs/04-接口契约.md` 为权威。

```
src/
├── main.py                              # 应用入口
├── config/                              # 配置模块
│   └── settings.py                      # 配置加载与管理
├── controllers/                         # 控制层
│   ├── __init__.py
│   ├── system_controller.py             # 健康检查
│   ├── project_controller.py            # 项目 CRUD
│   ├── config_controller.py             # 全局配置
│   ├── step1_controller.py              # Step1 素材加载
│   ├── step2_controller.py              # Step2 AI拆解+搜索
│   ├── step3_controller.py              # Step3 文案生成
│   ├── step4_controller.py              # Step4 TTS+标记
│   ├── step5_controller.py              # Step5 标记保存
│   ├── step6_controller.py              # Step6 裁切合并
│   ├── step7_controller.py              # Step7 合成导出
│   ├── task_controller.py               # 长任务管理
│   ├── history_controller.py            # 生成历史
│   └── file_controller.py               # 文件交互
├── services/                            # 服务层
│   ├── __init__.py
│   ├── project_service.py               # 项目管理
│   ├── config_service.py                # 配置管理
│   ├── step1_service.py                 # 素材加载
│   ├── step2_service.py                 # AI拆解+搜索
│   ├── step3_service.py                 # 文案生成
│   ├── step4_service.py                 # TTS+标记
│   ├── step5_service.py                 # 标记保存
│   ├── step6_service.py                 # 裁切合并
│   ├── step7_service.py                 # 合成导出
│   ├── task_service.py                  # 长任务管理
│   ├── history_service.py               # 生成历史
│   └── file_service.py                 # 文件交互
├── managers/                            # 管理层（跨领域编排）
│   ├── __init__.py
│   ├── step4_manager.py                 # Step4 双线并行编排（TTS+标记）
│   ├── step6_manager.py                 # Step6 裁切+合并编排
│   ├── step7_manager.py                 # Step7 合成+字幕编排
│   ├── llm_manager.py                   # LLM 适配器（DeepSeek/火山云/OpenAI）
│   ├── tts_manager.py                    # TTS 适配器（edge-tts/pyttsx3）
│   ├── search_manager.py                 # 搜索适配器（Bing/DuckDuckGo）
│   └── task_scheduler.py                # 长任务调度器
├── models/                              # 模型层
│   ├── __init__.py
│   ├── schemas/                         # Pydantic 数据模型
│   │   ├── project.py                   # 项目 Schema
│   │   ├── config.py                    # 配置 Schema
│   │   ├── step.py                       # 步骤 Schema（各步请求/响应）
│   │   ├── task.py                      # 任务 Schema
│   │   ├── history.py                   # 历史 Schema
│   │   └── file.py                      # 文件 Schema
│   └── entities/                        # ORM 实体模型
│       ├── vc_project.py               # 项目表
│       ├── vc_generation_history.py    # 生成历史表
│       └── vc_config.py                # 配置表
├── utils/                               # 工具集
│   ├── logs.py                          # loguru 日志配置
│   ├── trace.py                         # 事务 ID 生成
│   ├── camel.py                         # to_camel 转换器
│   └── env.py                           # 环境变量
└── core/                                # 核心业务组件（由 Manager 调用）
    ├── marker_randomizer.py             # 随机标记算法
    ├── cut_calculator.py               # 裁切片段计算
    ├── subtitle_generator.py            # 字幕 SRT 生成
    └── video_probe.py                   # ffprobe 视频信息获取
```

## 3. 领域特定规则

### 3.1 步骤执行

- 步骤执行必须校验前置条件（步骤锁定）
- 允许回退到已完成步骤重新执行（清除后续步骤历史）
- `currentStep` 字段记录当前可执行步骤
- 每步骤执行结果保存到 `vc_generation_history`

### 3.2 长任务管理

- Step4(TTS)、Step6(裁切)、Step7(合成) 为长任务
- 任务提交立即返回 taskId，不阻塞 HTTP 响应
- 任务状态: pending → running → completed | failed | cancelled | timeout
- 前端通过 GET /api/task/{id} 轮询（间隔 1-2 秒）
- 任务超时阈值: 300 秒（可配置）
- 任务支持取消（POST /api/step{N}/cancel）

### 3.3 TTS 音频合成

- edge-tts 为首选引擎，pyttsx3 为兜底
- TTS 引擎通过 TtsManager 适配器统一调用
- 音频输出到项目 output_path 下的 audio/ 目录
- 语音参数（voice/rate/volume）从配置读取

### 3.4 随机标记

- 随机标记算法在 core/marker_randomizer.py 实现
- 根据音频时长和视频总时长计算标记片段
- 标记片段包含: start, end, video_file, duration
- 标记结果保存到 vc_generation_history（result_type=markers）

### 3.5 虚拟预览（Step5）

- Step5 后端只保存编辑后的标记数据，不触发 ffmpeg
- 标记数据结构: `[{ start, end, video_file, remark }]`
- 禁止在 Step5 阶段调用 ffmpeg/ffprobe

### 3.6 ffmpeg 裁切合并（Step6）

- 使用 ffmpeg 裁切视频片段
- 使用 concat demuxer 合并片段
- 中间产物存放在 output_path/.tmp/ 目录
- 任务完成后清理临时文件
- 异常中断后下次启动检查并清理残留

### 3.7 合成导出（Step7）

- 音视频合成: ffmpeg 将音频与视频合并
- 字幕烧录: SRT 格式字幕通过 ffmpeg burn-in
- 输出格式: MP4 (H.264 + AAC)
- 视频尺寸: 9:16 竖屏（如 1080x1920）

### 3.8 配置管理

- 配置存储在 vc_config 表（key-value）
- 敏感信息（API Key）不记日志
- 配置变更后需调用 test-connection 验证
- 配置缺失时返回明确错误，不静默使用默认值

### 3.9 文件安全

- 文件路径参数必须经过校验，防止目录遍历攻击
- 文件预览/下载/目录浏览接口限制可访问的根目录
- 禁止访问项目 output_path 以外的路径（除非配置允许）
