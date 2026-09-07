---
alwaysApply: true
version: 1.0.0
lastUpdated: 2026-09-04
---
# 项目特定规则

> 本文档定义 video-cut 前端（cut-web）项目特有的命名约定、模块结构和领域规则。
> 接口以 `cut-server/docs/04-接口契约.md` 为权威，前端 TypeScript 类型必须与契约附录 A 字段映射严格对齐。

## 1. 命名约定

### 1.1 领域前缀

| 领域 | 前缀（组件/Hook/Service/Store） | 示例 |
|------|--------------------------------|------|
| 项目 | `Project` / `useProject` / `projectService` / `useProjectStore` | `ProjectListPage`, `projectService` |
| 步骤 | `Step` / `useStep` / `step{N}Service` | `Step5Panel`, `useStep4Audio`, `step4Service` |
| 标记 | `Marker` / `useMarker` / `markerService` | `MarkerTimeline`, `useMarkerEdit` |
| 音频 | `Audio` / `useAudio` | `AudioPlayer`, `useAudioPreview` |
| 裁切 | `Cut` / `useCut` | `CutProgress`, `useCutTask` |
| 合成 | `Compose` / `useCompose` | `ComposeProgress`, `useComposeTask` |
| 任务 | `Task` / `useTask` / `taskService` / `useTaskStore` | `TaskStatusTag`, `useTaskPoll`, `taskService` |
| 配置 | `Config` / `useConfig` / `configService` / `useConfigStore` | `ConfigPage`, `configService` |
| 历史 | `History` / `useHistory` / `historyService` | `HistoryPage`, `historyService` |

页面组件以 `Page` 或 `Panel` 结尾，基础组件以业务名词命名，Hook 以 `use` 开头，Service 以 `Service` 结尾，Store 以 `useXxxStore` 命名。

### 1.2 video-cut 相关命名

- 项目: `project` / `Project` / `ProjectCard`
- 步骤: `step` / `Step` / `Step{N}Panel`
- 标记: `videoMarker` / `VideoMarker` / `MarkerTimeline`
- 音频: `audio` / `Audio` / `AudioPlayer`
- 裁切: `cut` / `Cut` / `CutProgress`
- 合成: `compose` / `Compose` / `ComposeProgress`
- 任务: `task` / `Task` / `TaskStatusTag`

### 1.3 步骤与任务状态类型

```typescript
// types/step.types.ts

/** 步骤编号。 */
type StepNum = 1 | 2 | 3 | 4 | 5 | 6 | 7;

/** 任务状态。 */
type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'timeout';

/** 步骤结果类型。 */
type StepResultType = 'load' | 'analyze' | 'script' | 'audio' | 'markers' | 'edit_markers' | 'cut_video' | 'final';

/** 文案风格。 */
type ScriptStyle = 'hot_review' | 'objective' | 'suspense' | 'plot';
```

### 1.4 错误类命名

```
AppError                              # 项目根错误
├── ApiError                          # API 请求错误
│   ├── NetworkError                  # 网络错误（断网、超时、CORS）
│   ├── BusinessError                 # 业务错误（code=40xxx）
│   ├── ServiceError                  # 服务异常（code=50xxx）
│   └── TaskError                     # 长任务失败（code=60xxx）
├── ValidationError                   # 前端数据校验错误
└── RuntimeError                      # 运行时错误（Error Boundary 捕获）
```

## 2. 模块结构

> 各层职责定义见 `common/02-architecture-patterns.md` §1（分层架构）、§1.3（core/ 定位）、§1.4（何时用全局 Store）。

```
src/
├── main.tsx                         # 应用入口
├── App.tsx                          # 根组件（路由 + 全局布局 + ErrorBoundary）
├── router/                          # 路由配置
│   ├── index.tsx                    # 路由表（懒加载）
│   └── routes.ts                    # 路由元信息
├── pages/                           # 页面层（按 step 组织）
│   ├── project-list/                # 项目列表页
│   │   └── ProjectListPage/
│   ├── step1/                       # Step1 输入信息
│   │   └── Step1Panel/
│   ├── step2/                       # Step2 AI拆解+搜索
│   │   └── Step2Panel/
│   ├── step3/                       # Step3 口播文案
│   │   └── Step3Panel/
│   ├── step4/                       # Step4 双线并行
│   │   └── Step4Panel/
│   ├── step5/                       # Step5 虚拟预览（核心）
│   │   └── Step5Panel/
│   ├── step6/                       # Step6 裁切合并
│   │   └── Step6Panel/
│   ├── step7/                       # Step7 合成导出
│   │   └── Step7Panel/
│   ├── complete/                    # 完成页
│   │   └── CompletePage/
│   ├── config/                      # 全局配置
│   │   └── ConfigPage/
│   ├── history/                     # 生成历史
│   │   └── HistoryPage/
│   └── error/                       # 错误页
│       └── ErrorPage/
├── components/                      # 全局可复用组件
│   ├── basic/                       # 基础组件
│   │   ├── ErrorBoundary/
│   │   ├── PageContainer/
│   │   ├── StatusTag/               # 状态标签
│   │   ├── StepProgress/            # 步骤进度条
│   │   ├── ConfirmButton/           # 带二次确认的按钮
│   │   └── DirBrowser/              # 目录浏览器
│   └── business/                    # 业务通用组件
│       ├── ProjectCard/             # 项目卡片
│       ├── ScriptStyleSelector/     # 文案风格选择器
│       ├── AudioPlayer/             # 音频播放器
│       └── TaskProgress/            # 任务进度
├── hooks/                           # 全局可复用 Hook
│   ├── useRequest.ts                # 通用请求 Hook
│   ├── useTaskPoll.ts               # 长任务轮询 Hook
│   ├── useDebounce.ts               # 防抖 Hook
│   └── useVideoSeek.ts              # 视频 seek 控制 Hook（Step5）
├── services/                        # API 服务封装
│   ├── request.ts                   # axios 实例 + 拦截器
│   ├── projectService.ts
│   ├── configService.ts
│   ├── step1Service.ts
│   ├── step2Service.ts
│   ├── step3Service.ts
│   ├── step4Service.ts
│   ├── step5Service.ts
│   ├── step6Service.ts
│   ├── step7Service.ts
│   ├── taskService.ts
│   ├── historyService.ts
│   └── fileService.ts
├── store/                           # 全局状态（Zustand）
│   ├── useProjectStore.ts           # 项目状态
│   ├── useConfigStore.ts             # 配置缓存
│   ├── useStepStore.ts              # 步骤状态
│   └── useTaskStore.ts              # 任务状态
├── core/                            # 核心业务组件
│   ├── request.ts                   # 统一请求封装（traceId/错误处理/to_camel）
│   └── MarkerTimeline/              # 时间轴标记编辑组件（Step5 核心）
├── types/                           # 全局类型定义
│   ├── index.ts
│   ├── api.types.ts                 # API 通用响应类型
│   ├── project.types.ts             # 项目类型
│   ├── step.types.ts                # 步骤类型
│   ├── marker.types.ts              # 标记类型
│   ├── task.types.ts                # 任务类型
│   ├── config.types.ts              # 配置类型
│   └── history.types.ts             # 历史类型
├── utils/                           # 工具函数
│   ├── logger.ts                    # 日志工具
│   ├── format.ts                    # 格式化（时间、文件大小）
│   ├── download.ts                  # 文件下载
│   └── errors.ts                    # 错误类定义
├── constants/                       # 常量与枚举映射
│   ├── app.ts                       # 应用常量
│   ├── step.ts                      # 步骤状态映射
│   └── task.ts                      # 任务状态映射
├── config/                          # 配置
│   ├── env.ts                       # 环境变量
│   ├── api.ts                       # API 路径
│   └── theme.ts                     # 主题配置（深色科技风）
└── assets/                          # 静态资源
    ├── images/
    └── styles/
        ├── variables.scss
        └── global.scss
```

## 3. 领域特定规则

### 3.1 步骤流程管理

- 7 步流程按顺序执行，不可跳过未完成步骤
- 步骤进度通过 `useStepStore` 管理当前步骤数据
- 每步完成后调用下一步骤接口
- 允许回退到已完成步骤（会清除后续步骤历史）
- 步骤进度条（`StepProgress` 组件）展示 1~7 步状态

### 3.2 长任务轮询

- 长任务（Step4 TTS/标记、Step6 裁切、Step7 合成）通过 `useTaskPoll` Hook 轮询
- 轮询间隔: 1-2 秒
- **页卸载时必须取消轮询**（useEffect 清理），避免 setState on unmounted
- 任务状态用 `StatusTag` 组件统一展示
- 任务失败/超时后提供「重试」按钮
- 任务可取消（`ConfirmButton` 二次确认）

### 3.3 项目管理

- 项目列表以卡片形式展示
- 卡片显示: 缩略图、标题、作者、当前步骤进度、更新时间
- 创建项目后跳转到 Step1
- 复制项目后刷新列表
- 删除项目使用 `Popconfirm` 二次确认

### 3.4 全局配置

- 配置页展示 AI/TTS/搜索引擎配置表单
- 敏感字段（API Key）展示为掩码，编辑时清空重填
- 保存前提供「测试连接」按钮
- 配置变更后刷新 `useConfigStore`

---

## 4. video-cut 专属规则

### 4.1 虚拟预览实现规范（Step5 铁律）

**0 IO 原则**: Step5 虚拟预览阶段禁止触发任何 ffmpeg/文件 IO 操作。

- 预览通过 `<video>.currentTime` 模拟串播，按标记片段顺序 seek
- 标记片段的裁切/合并只在 Step6 执行
- 前端只保存编辑后的标记列表，不生成中间文件

**实现约束**:
- `<video>` 元素跨源: 确保视频文件可通过后端 file preview 接口访问
- `seeked` 事件节流: 连续 seek 时做 debounce（200ms），避免频繁触发
- 媒体资源回收: 切换项目或步骤时，释放 `<video>` src（`video.src = ''`）
- 串播逻辑: 标记片段播放结束（`timeupdate` 接近 end）→ 自动 seek 到下一片段 start

**MarkerTimeline 组件定位**:
- 复杂度高 + 复用性强 + 职责单一 → 放入 `core/MarkerTimeline/`
- 数据结构与接口契约 `VideoMarker` 对齐
- 支持标记增删改、拖拽调整起止点
- 支持时长匹配检查（标记总时长 vs 音频时长）

### 4.2 长任务轮询 Hook 规范（useTaskPoll）

```typescript
interface UseTaskPollOptions {
  taskId: string | null;
  interval?: number;        // 默认 1500ms
  onSuccess?: (result: TaskResult) => void;
  onError?: (error: TaskError) => void;
  enabled?: boolean;        // 可条件启停
}
```

**铁律**:
- 页卸载时必须取消轮询（`useEffect` 清理 `AbortController`）
- 任务终态（completed/failed/cancelled/timeout）后自动停止轮询
- 组件卸载后不调用 `setState`（避免 React 警告）
- 轮询失败时自动重试 3 次，之后停止并报错

### 4.3 标记编辑组件规范（MarkerTimeline）

**数据结构**（与接口契约 `VideoMarker` 对齐）:
```typescript
interface VideoMarker {
  id: string;
  start: number;           // 秒
  end: number;             // 秒
  videoFile: string;       // 视频文件路径
  remark?: string;         // 备注
  duration: number;        // 持续时长（end - start）
}
```

**交互**:
- 时间轴拖拽调整 start/end
- 右键菜单: 删除标记、添加标记、编辑备注
- 随机重标按钮（调用后端重新随机生成）
- 时长匹配检查: 标记总时长 vs 音频时长，不匹配时警告

### 4.4 前后端字段对齐铁律

1. 前端 TypeScript 类型必须与 `cut-server/docs/04-接口契约.md` 附录 A 字段映射严格对齐
2. 后端修改字段名时，必须同步更新契约文档附录 A
3. 前端发现字段不匹配时，以契约文档为准，不自行 mock
4. 字段命名: 前端 camelCase ↔ 后端 snake_case
5. 禁止前端绕过接口契约直接构造数据

### 4.5 前后端联调规范

1. 启动顺序: 先后端（8000）→ 再前端（5173）
2. 健康检查: `GET /api/health` 验证后端可用
3. CORS 检查: 前端控制台无 CORS 报错
4. Vite proxy: `/api` → `http://localhost:8000`
5. TraceId 联查: 前端生成 → 后端日志贯穿 → 响应头回传

### 4.6 视频与音频资源管理规范

> video-cut 是视频工具，`<video>` / `<audio>` 元素使用频率极高，**与普通 Web 项目最大的区别**。
> 资源管理不当会导致：内存泄漏、播放卡顿、Range 请求失败、跨页面残留、卸载崩溃。

#### 4.6.1 必带属性

| 元素 | 必带属性 | 原因 |
|------|---------|------|
| `<video>` | `preload="metadata"` | 不全量加载，节省带宽；海报图预加载即可 |
| `<video>` | `playsInline` | iOS Safari 不全屏 |
| `<video>` | `crossOrigin="anonymous"` | 与后端 `/api/file/preview` 配合，支持 Canvas 截图 |
| `<audio>` | `preload="metadata"` | 同 video |
| `<audio>` | `controls` | 调试期保留（生产可隐藏） |

**禁止**：
- ❌ `preload="auto"`（除非是首屏必播的极短视频）
- ❌ 多个页面共用同一 `<video>` 元素的 `src`（必须每个页面独立创建）
- ❌ `<video autoplay>` 在用户未交互前（违反浏览器自动播放策略）

#### 4.6.2 资源生命周期管理

**组件卸载时必须清理**：

```tsx
function VideoPreview({ src, onTimeUpdate }: VideoPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    // 加载新源
    video.src = src;
    video.load();

    return () => {
      // ⭐ 关键：组件卸载时彻底清理
      video.pause();
      video.removeAttribute('src');
      video.load();  // 触发 abort + 清空缓冲
    };
  }, [src]);

  return <video ref={videoRef} controls preload="metadata" />;
}
```

**跨页面复用场景**（如 Step4 → Step5 复用同一视频源）：

```tsx
// 切页前先 pause 旧页面的视频
useEffect(() => {
  return () => {
    const video = document.querySelector('video');
    video?.pause();
  };
}, []);
```

#### 4.6.3 HTTP Range 请求

- **必须**：后端 `/api/file/preview` 与 `/api/file/download` 都支持 HTTP Range（视频 seek 必需）
- **前端 axios 配置**：
  ```typescript
  // services/fileService.ts
  export const fileService = {
    getPreviewUrl: (path: string): string => {
      // 直接返回 URL，让 <video src> 触发 Range 请求
      // 不要用 axios.get 加载（不支持 Range）
      return `/api/file/preview?path=${encodeURIComponent(path)}`;
    },
  };
  ```
- **禁止**：用 `axios.get(..., { responseType: 'blob' })` 加载视频（一次性下载，无法 seek）
- **例外**：下载完整文件用 `/api/file/download` + `responseType: 'blob'`

#### 4.6.4 多视频并发限制

- **同屏最多展示 3 个 `<video>`**（浏览器解码器限制，过多会卡顿）
- Step4 音频 + 视频标记线：1 个 `<audio>` + 1 个 `<video>`（合规）
- Step5 多素材预览：使用 `<video>` + 切换 `src` 而非同时挂载多个

#### 4.6.5 视频时长格式化

```typescript
// utils/format.ts
export function formatVideoDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return h > 0
    ? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
    : `${m}:${String(s).padStart(2, '0')}`;
}
```

#### 4.6.6 错误处理

| 错误 | 触发条件 | 前端处理 |
|------|---------|---------|
| `MEDIA_ERR_NETWORK` | 网络中断 | 弹 toast "网络中断，请检查后端服务" |
| `MEDIA_ERR_DECODE` | 视频编码不被浏览器支持 | 弹 toast "视频编码不支持，建议转码为 H.264" |
| `MEDIA_ERR_SRC_NOT_SUPPORTED` | 后端拒绝（路径越权 / 文件不存在） | 弹 toast 显示后端 `msg` 字段 |
| `loadedmetadata` 超时 | 后端 Range 响应异常 | 重试 1 次，仍失败则提示用户 |

```tsx
<video
  ref={videoRef}
  onError={(e) => {
    const err = videoRef.current?.error;
    switch (err?.code) {
      case 1: message.error('网络中断'); break;
      case 2: message.error('视频解码失败'); break;
      case 3: // 我们的"解码失败"也归这里
      case 4: message.error('视频加载失败：' + err?.message); break;
    }
  }}
  onLoadedMetadata={() => {
    const duration = videoRef.current?.duration;
    // 通知父组件时长
  }}
/>
```

#### 4.6.7 海报图与预览

- **必带** `poster` 属性，`<video poster="...">` 在加载期间显示
- 海报图由后端 `/api/file/preview?path=...&poster=true` 返回（首帧截图）
- **禁止**：用 `video.currentTime=0` 模拟海报（闪烁 + 触发网络请求）

#### 4.6.8 性能优化清单

- [ ] `<video>` 元素加 `preload="metadata"`，不全量加载
- [ ] 不在 JSX 中直接 `<source>` 切换（用 ref + 状态切换 `src`）
- [ ] 长视频（> 5min）启用 `Range` 请求的 axios 配置
- [ ] 组件卸载必清理（pause + removeAttribute + load）
- [ ] 同屏 `<video>` 不超过 3 个
- [ ] 错误处理覆盖 4 种 `MEDIA_ERR_*` 状态码
- [ ] 海报图通过 `poster` 属性设置

---

## 5. video-cut core 组件清单

> **判断标准**（来自 `02-architecture-patterns.md §1.3`）：
> 同时满足 **(1) 复杂度高** + **(2) 复用性强** + **(3) 职责单一** 三个条件才进 `src/core/`，否则放 `components/business/`。
>
> 下表是 video-cut **计划中的** 核心组件清单（先定后实现，避免无脑造 `core/`）。

| # | 组件 | 复杂度 | 复用性 | 职责 | 是否进 `core/` | 落地位置 | 关联 Step |
|---|------|--------|--------|------|---------------|---------|----------|
| 1 | `VideoPreviewPlayer` | 中 | **高** | `<video>` 封装：属性默认值 + 清理 + 错误处理 + Range URL | **是** | `src/core/VideoPreviewPlayer/` | Step4/5/6 |
| 2 | `LongTaskProgress` | 中 | **高** | 长任务进度条 + 状态轮询 + 取消按钮 + 终态展示 | **是** | `src/core/LongTaskProgress/` | Step4/6/7 |
| 3 | `TtsAudioPlayer` | 中 | 中 | TTS 试听播放器（播放 + 拖动 + 语速切换） | **否** | `src/components/business/TtsAudioPlayer/` | Step4 |
| 4 | `MarkerTimeline` | **高** | 中 | 时间轴 + 标记编辑（起止/删除/拖拽/添加）+ 时长匹配检查 | **否** | `src/components/business/MarkerTimeline/` | Step5 |
| 5 | `ScriptEditor` | 中 | 低 | 口播文案编辑器（折叠大纲 + 字数/时长预估） | **否** | `src/components/business/ScriptEditor/` | Step3 |
| 6 | `KeywordTagCloud` | 低 | 低 | 关键词标签云（4 个分类标签） | **否** | `src/components/business/KeywordTagCloud/` | Step2 |
| 7 | `ArticleList` | 中 | 低 | 搜索文章采纳/弃用列表 | **否** | `src/components/business/ArticleList/` | Step2 |
| 8 | `ProjectCard` | 低 | 中 | 项目卡片（封面 + 标题 + 进度 + 操作） | **否** | `src/components/business/ProjectCard/` | 项目列表 |
| 9 | `LogStream` | 中 | 中 | 实时日志流（折叠展开 + 自动滚动到底部） | **否** | `src/components/business/LogStream/` | Step6/7 |
| 10 | `StepNavBar` | 中 | **高** | 7 步步骤条 + 锁定态 + 跳转 | **是** | `src/core/StepNavBar/` | 全局（项目详情） |
| 11 | `HistoryCompareViewer` | 中 | 低 | 历史版本对比查看器（左右双栏 + 高亮差异） | **否** | `src/components/business/HistoryCompareViewer/` | 历史详情 |
| 12 | `VideoDurationTag` | 低 | 高 | 视频时长格式化展示（mm:ss） | **否** | `src/components/basic/VideoDurationTag/` | 多处 |

### 5.1 进 `core/` 的 3 个组件详解

#### 5.1.1 `core/VideoPreviewPlayer/`

**为什么进 core**：
- 复杂度中：跨页面属性管理（preload / crossOrigin / onError）+ 资源清理 + Range URL 拼接
- 复用性高：被 Step4（音频 + 视频双线预览）、Step5（虚拟预览）、Step6（裁切前确认）、Step7（成品预览）4 处引用
- 职责单一：只做"播放视频"，不做时间轴编辑、不做标记管理

**目录结构**：
```
src/core/VideoPreviewPlayer/
├── index.tsx                    # 主组件（默认导出）
├── types.ts                     # VideoPreviewPlayerProps
├── useVideoLifecycle.ts         # 资源生命周期 hook（核心）
├── useVideoErrorHandler.ts      # 错误处理 hook
├── formatDuration.ts            # 时长格式化（也可放 utils/）
└── README.md                    # 组件说明 + 4 个调用示例
```

**Props 接口**：
```typescript
interface VideoPreviewPlayerProps {
  src: string;                              // 视频 URL（已拼接 /api/file/preview）
  poster?: string;                          // 海报图 URL
  autoPlay?: boolean;                       // 默认 false
  onLoadedMetadata?: (duration: number) => void;
  onTimeUpdate?: (currentTime: number) => void;
  onEnded?: () => void;
  onError?: (code: number, message: string) => void;
  className?: string;
  style?: React.CSSProperties;
}
```

#### 5.1.2 `core/LongTaskProgress/`

**为什么进 core**：
- 复杂度中：状态机（pending/running/success/failed/cancelled）+ 轮询 + 取消 + 错误展示 + 重试
- 复用性高：Step4 音频（type=audio）、Step6 裁切（type=cut）、Step7 合成（type=compose）3 个长任务共用
- 职责单一：只做"展示任务进度"，不发起任务

**目录结构**：
```
src/core/LongTaskProgress/
├── index.tsx
├── types.ts                   # TaskType, TaskStatus
├── useTaskPolling.ts          # 轮询 hook（按 §6 规范实现）
├── statusMap.ts               # 状态→颜色/图标/文案映射
└── README.md
```

#### 5.1.3 `core/StepNavBar/`

**为什么进 core**：
- 复杂度中：7 步状态联动（currentStep + 历史记录 → 步骤条 + 锁定态）
- 复用性高：项目详情页 + 完成页 + 多个 Step 内部都需要
- 职责单一：只做"步骤导航"，不做 Step 内部业务

### 5.2 反例（不应进 `core/`）

| 候选 | 为什么不进 | 正确位置 |
|------|-----------|---------|
| `DataTable` | 纯 UI 封装 | `components/basic/` |
| `StatusTag` | 简单映射 | `components/basic/` |
| `ConfirmButton` | 简单弹窗 | `components/basic/` |
| `EvalCaseForm` | 单页面专用 | `pages/case/EvalCaseFormPage/`（注：video-cut 无此场景） |
| `UserMenu` | 简单业务组件 | `components/business/` |

### 5.3 维护规则

- `core/` 下新增组件必须满足三条件（复杂度 + 复用性 + 职责单一）
- `core/` 下组件**禁止** import `pages/` 任何文件
- `core/` 下组件**禁止**依赖 antd 之外的 UI 库（如需新 UI 库，必须先讨论）
- `core/` 下组件必须配套 `README.md`（说明：何时用、Props、3 个调用示例）

---

## 6. 7 步流程前端映射

> video-cut 业务核心是 7 步向导，本节把每一步对应到前端的页面/组件/Service 入口，**作为新功能开发时的索引**。

| Step | 页面 | 核心组件 | Service 入口 | 长任务 | 关键约束 |
|------|------|---------|-------------|--------|---------|
| 0 项目列表 | `pages/project/ProjectListPage` | `ProjectCard` | `projectService.getList` | — | 支持搜索/筛选/复制/删除 |
| 1 输入信息 | `pages/step/Step1Page` | `FormInput` (动态) | `step1Service.load` | — | 校验 videoDir 至少 1 个视频 |
| 2 拆解 + 搜索 | `pages/step/Step2Page` | `KeywordTagCloud`, `ArticleList` | `step2Service.analyze` | — | 步骤锁定（Step1 未完成不可进） |
| 3 口播文案 | `pages/step/Step3Page` | `ScriptEditor` | `step3Service.generate`, `step3Service.save` | — | 重新计算 estDurationSec |
| 4 双线并行 | `pages/step/Step4Page` | `VideoPreviewPlayer`, `TtsAudioPlayer`, `LongTaskProgress` | `step4Service.audio`, `step4Service.markers`, `step4Service.status`, `step4Service.cancel` | ✅ 音频 | 音频 + 标记并发执行 |
| 5 虚拟预览 | `pages/step/Step5Page` | `MarkerTimeline`, `VideoPreviewPlayer` | `step5Service.save`, `step5Service.remark` | — | **0 IO 预览**（仅 `<video>.currentTime` seek） |
| 6 裁切合并 | `pages/step/Step6Page` | `LongTaskProgress`, `LogStream` | `step6Service.cut`, `step6Service.cancel` | ✅ 裁切 | 进度条 + 实时日志 |
| 7 合成 + 字幕 | `pages/step/Step7Page` | `LongTaskProgress` | `step7Service.compose`, `step7Service.cancel` | ✅ 合成 | 字幕烧录 + 导出 mp4 |
| 8 完成页 | `pages/step/DonePage` | `StepNavBar`, `ProjectCard` | `projectService.getDetail` | — | 成品预览 + 导出 |
| 全局 | `pages/project/ProjectDetailPage` | `StepNavBar` | `projectService.getDetail` | — | 7 步进度总览 |

### 6.1 步骤锁定规则

- 前端从 `projectService.getDetail` 拿 `stepResults: StepResultSummary[]`
- 每步状态为 `success` 才算"完成"
- Step5 不产生 success 记录（无后端 IO），其"完成"由 Step6 触发前的存在性隐式确认
- 锁定展示：当前步骤之前的 step 有缺失 success 记录 → 当前 step 按钮置灰

### 6.2 长任务统一入口

所有长任务（Step4 音频 / Step6 裁切 / Step7 合成）统一走：

```typescript
// services/taskService.ts（统一长任务查询）
export const taskService = {
  getStatus: (taskId: string) => request.get(`/api/task/${taskId}`),
  listByProject: (projectId: string) => request.get(`/api/task/list?project_id=${projectId}`),
};
```

前端组件统一用 `useTaskPolling(taskId, { interval: 5000 })` hook（见 `01-project-specific.md` 后续 §7 计划）。

### 6.3 7 步流程的 Service 命名约定

| Service | 路径前缀 | 职责 |
|---------|---------|------|
| `projectService` | `/api/projects` | 项目 CRUD + 复制 + 重置 |
| `step1Service` | `/api/step1` | 素材扫描 + 知识库加载 |
| `step2Service` | `/api/step2` | AI 拆解 + 搜索 |
| `step3Service` | `/api/step3` | 文案生成 + 编辑保存 |
| `step4Service` | `/api/step4` | 音频合成 + 视频标记 |
| `step5Service` | `/api/step5` | 标记编辑保存 + 重新标记 |
| `step6Service` | `/api/step6` | 裁切 + 合并 |
| `step7Service` | `/api/step7` | 合成 + 字幕 |
| `taskService` | `/api/task` | 长任务统一查询 |
| `historyService` | `/api/history` | 生成历史 + 回滚 |
| `fileService` | `/api/file` | 文件预览 / 下载 |
| `configService` | `/api/config` | 全局配置 |
