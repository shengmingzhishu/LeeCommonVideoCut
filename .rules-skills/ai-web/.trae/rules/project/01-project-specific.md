---
alwaysApply: true
version: 2.0.0
lastUpdated: 2026-09-03
---
# 项目特定规则

> 本文档定义 ai-web 项目特有的命名约定、模块结构和领域规则。
>
> **v2.0 更新 (2026-09-03)**：同步最新代码结构，新增 Bug/笔记V2/参考图例/用户管理/用例调试模块规则；移除已废弃的 historyService 引用；更新目录结构树。

## 1. 命名约定

### 1.1 领域前缀

| 领域 | 前缀（组件/Hook/Service/Store） | 示例 |
|------|--------------------------------|------|
| 评测 | `Eval` / `useEval` / `evalService` / `caseService` | `EvalListPage`, `useEvalList`, `caseService` |
| 计划 | `Plan` / `usePlan` / `planService` | `PlanListPage`, `planService` |
| 任务 | `Task` / `useTask` / `taskService` / `useTaskStore` | `TaskDetailPage`, `useTaskPolling`, `taskService` |
| MCP 工具 | `Mcp` / `useMcp` / `mcpService` | `McpToolList`, `useMcpTools`, `mcpService` |
| 用户认证 | `Auth` / `User` / `useAuth` / `authService` / `useAuthStore` | `LoginPage`, `useAuth`, `useUserStore` |
| 用户管理 | `User` / `userService` | `UserManagePage`, `userService` |
| 文件/媒体 | `File` / `Media` / `fileService` / `mediaService` | `FileImportModal`, `useFileUpload`, `mediaService` |
| 历史记录 | `History` / `Record` / `caseService` | `HistoryListPage`, `useHistoryList`, `caseService.getCaseHistory` |
| 报告 | `Report` / `useReport` / `reportService` | `ReportViewPage`, `useReportData`, `reportService` |
| 被测系统 | `Target` / `Provider` / `useTarget` / `targetService` | `TargetConfigPage`, `useTargetList`, `targetService` |
| Bug 管理 | `Bug` / `useBug` / `bugService` | `BugDashboardPage`, `BugListPage`, `bugService` |
| 笔记 | `Note` / `useNote` / `noteService` | `NoteTreePage`, `NoteEditPage`, `noteService` |
| 参考图例 | `RefGallery` / `RefImage` / `refGalleryService` / `useRefGalleryStore` | `RefGalleryPage`, `refGalleryService` |
| 检索 | `Retrieval` / `retrievalService` | `retrievalService.search` |
| Dashboard | `Dashboard` / `dashboardService` | `DashboardPage`, `dashboardService` |
| 提示词预设 | `PromptPreset` / `promptPresetService` | `promptPresetService` |

> **注意**：历史记录相关功能统一使用 `caseService`（如 `getCaseHistory`、`getCaseTrend`），不再使用已废弃的 `historyService`。

页面组件以 `Page` 结尾（`EvalListPage`），基础组件以业务名词命名（`EvalList`、`TaskProgress`），Hook 以 `use` 开头，Service 以 `Service` 结尾，Store 以 `useXxxStore` 命名（Zustand 惯例）。

### 1.2 评测相关命名

- 评测套件：`evalSuite`（变量）/ `EvalSuite`（类型）/ `EvalSuiteList`（组件）
- 评测用例：`evalCase` / `EvalCase` / `EvalCaseForm`
- 评测结果：`evalResult` / `EvalResult` / `EvalResultChart`
- 评测方向：`evalDirection`（如 `text_qa` / `sql_correctness` / `rag_scoring`）
- 测试方式：`evalMethod`（如 `ai_model` / `rag_scoring`）
- 任务：`task` / `Task` / `TaskItem`
- 被测系统/供应商：`target` / `provider` / `TargetSystem`

### 1.3 评测方向与测试方式类型定义

> 前端不硬编码枚举值，优先从后端配置接口动态获取。以下为基础类型定义，用于 TS 类型约束。

```typescript
// types/eval.types.ts

/** 评测方向。 */
type EvalDirection = 'text_qa' | 'sql_correctness' | 'rag_scoring' | (string & {});

/** 测试方式。 */
type EvalMethod = 'ai_model' | 'rag_scoring' | (string & {});

/** 任务状态。 */
type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

/** 评测方向配置（从后端动态获取）。 */
interface EvalDirectionConfig {
  /** 方向标识，如 text_qa。 */
  code: EvalDirection;
  /** 方向名称，如"文本问答评测"。 */
  name: string;
  /** 该方向支持的测试方式。 */
  supportedMethods: EvalMethod[];
  /** 该方向特有的字段配置（用于动态表单渲染）。 */
  fields?: EvalFieldConfig[];
}

/** 评测方向字段配置（驱动动态表单）。 */
interface EvalFieldConfig {
  /** 字段名。 */
  name: string;
  /** 字段标签。 */
  label: string;
  /** 字段类型。 */
  type: 'input' | 'textarea' | 'select' | 'number' | 'switch';
  /** 是否必填。 */
  required: boolean;
  /** 选项（type 为 select 时使用）。 */
  options?: Array<{ label: string; value: string }>;
  /** 默认值。 */
  defaultValue?: unknown;
}
```

### 1.4 错误类命名

```
AppError                              # 项目根错误
├── ApiError                          # API 请求错误（HTTP 状态码、业务错误码）
│   ├── NetworkError                  # 网络错误（断网、超时、CORS）
│   ├── UnauthorizedError             # 401 未认证（跳登录页）
│   ├── ForbiddenError                # 403 无权限
│   ├── NotFoundError                 # 404 资源不存在
│   └── BusinessError                 # 业务错误（HTTP 200 但 code != 0）
├── ValidationError                   # 前端数据校验错误（表单校验、类型守卫失败）
└── RuntimeError                      # 运行时错误（由 React Error Boundary 捕获）
```

错误类实现示例：

```typescript
// utils/errors.ts

/** 项目根错误。 */
export class AppError extends Error {
  constructor(message: string, public readonly context?: Record<string, unknown>) {
    super(message);
    this.name = this.constructor.name;
  }
}

/** API 请求错误。 */
export class ApiError extends AppError {
  constructor(
    message: string,
    public readonly statusCode: number,
    public readonly businessCode?: number,
    public readonly traceId?: string,
    context?: Record<string, unknown>,
  ) {
    super(message, { ...context, statusCode, businessCode, traceId });
  }
}

export class UnauthorizedError extends ApiError { /* ... */ }
export class BusinessError extends ApiError { /* ... */ }
```

## 2. 模块结构

> 各层职责定义见 `common/02-architecture-patterns.md` §1（分层架构）、§1.3（core/ 定位）、§1.4（何时用全局 Store）。

```
src/
├── main.tsx                         # 应用入口（ReactDOM.render + 全局 Provider）
├── App.tsx                          # 根组件（路由配置、全局布局、ErrorBoundary）
├── router/                          # 路由配置
│   ├── index.tsx                    # 路由表（懒加载 + 路由守卫）
│   └── routes.ts                    # 路由元信息（菜单、权限、标题）
├── pages/                           # 页面层（按 feature 组织）
│   ├── login/                       # 登录页
│   │   └── LoginPage/
│   ├── case/                        # 评测管理
│   │   ├── EvalListPage/            # 评测套件列表
│   │   ├── EvalDetailPage/          # 评测套件详情
│   │   ├── EvalCaseFormPage/        # 评测用例新建/编辑
│   │   ├── EvalSuiteManagePage/     # 测试集管理
│   │   └── CaseDebugPage/           # 用例调试（v0.11 新增）
│   ├── plan/                        # 计划管理（v0.10 新增）
│   │   ├── PlanListPage/
│   │   └── PlanDetailPage/
│   ├── task/                        # 任务管理
│   │   ├── TaskListPage/            # 任务列表
│   │   ├── TaskCreatePage/          # 创建任务
│   │   └── TaskDetailPage/          # 任务详情（实时进度）
│   ├── history/                     # 历史记录
│   │   ├── HistoryListPage/         # 历史列表
│   │   ├── HistoryDetailPage/       # 历史详情
│   │   └── HistoryComparePage/      # 结果对比
│   ├── report/                      # 报告
│   │   ├── ReportListPage/          # 报告列表
│   │   └── ReportViewPage/          # 报告查看（可视化）
│   ├── config/                      # 系统配置
│   │   ├── TargetConfigPage/        # 被测系统配置
│   │   └── PromptPresetPage/        # 提示词预设管理
│   ├── dashboard/                   # Dashboard 首页
│   │   └── DashboardPage/
│   ├── debug/                       # 用例调试（v0.11 新增）
│   │   └── DebugPage/
│   ├── bug/                         # Bug 管理（M11）
│   │   ├── BugDashboardPage/        # Bug 工作台（个人统计）
│   │   ├── BugListPage/             # Bug 列表
│   │   ├── BugReportPage/           # Bug 提报
│   │   └── BugSystemManagePage/     # Bug 系统管理
│   ├── noteV2/                      # 智能笔记 V2（M10）
│   │   ├── NoteTreePage/            # 笔记树
│   │   └── NoteEditPage/            # 笔记编辑（Markdown）
│   ├── refgallery/                  # 参考图例（M12 v3.0）
│   │   ├── RefGalleryPage/          # 图例画廊
│   │   ├── RefImageEditPage/        # 图例编辑
│   │   └── RefImagePickerModal/     # 图例选择器（弹窗）
│   ├── system/                      # 系统管理
│   │   └── UserManagePage/          # 用户管理（管理员）
│   ├── profile/                     # 个人中心
│   │   └── ProfilePage/
│   └── error/                       # 错误页
│       └── ErrorPage/
├── components/                      # 全局可复用组件
│   ├── basic/                       # 基础组件（对 antd 的二次封装）
│   │   ├── ErrorBoundary/           # 错误边界
│   │   ├── PageContainer/           # 页面容器（统一标题、面包屑）
│   │   ├── DataTable/               # 数据表格（封装 antd Table）
│   │   ├── FormInput/               # 表单输入（动态表单渲染）
│   │   ├── SearchBar/               # 搜索栏
│   │   ├── StatusTag/               # 状态标签（任务状态等）
│   │   └── ConfirmButton/           # 带二次确认的按钮
│   └── business/                    # 业务通用组件（跨 feature 复用）
│       ├── UserMenu/                # 用户菜单（头像、登出）
│       ├── SideMenu/                # 侧边栏菜单（权限驱动）
│       ├── EvalDirectionSelector/   # 评测方向选择器
│       ├── TargetSystemSelector/    # 被测系统选择器
│       ├── HistoryRecordModal/      # 历史记录弹窗（走 caseService）
│       └── ReferenceImagePickerModal/  # 旧参考图库选择器（渐进式迁移中）
├── hooks/                           # 全局可复用 Hook
│   ├── useAuth.ts                   # 认证状态与登录/登出
│   ├── usePermission.ts             # 权限校验
│   ├── usePagination.ts             # 分页逻辑
│   ├── useRequest.ts                # 通用请求 Hook（loading/error/data）
│   ├── usePolling.ts                # 轮询 Hook（任务状态轮询）
│   └── useDebounce.ts               # 防抖 Hook
├── services/                        # API 服务封装（按业务领域）
│   ├── request.ts                   # axios 实例 + 拦截器（Token、错误、traceId）
│   ├── authService.ts               # 认证接口（登录、登出、刷新 Token）
│   ├── userService.ts               # 用户管理（CRUD、角色分配）
│   ├── caseService.ts               # 评测套件/用例 CRUD + 历史记录查询
│   ├── planService.ts               # 计划管理 CRUD
│   ├── taskService.ts               # 任务创建、查询、取消、重试
│   ├── reportService.ts             # 报告查询、导出
│   ├── fileService.ts               # 文件上传、导入
│   ├── mediaService.ts              # 媒体文件管理
│   ├── targetService.ts             # 被测系统配置 CRUD、连接测试
│   ├── configService.ts             # 后端动态配置（评测方向、字段配置）
│   ├── bugService.ts                # Bug 管理（CRUD、状态机、评论、通知）
│   ├── noteService.ts               # 智能笔记（树形、Markdown、自动保存）
│   ├── refGalleryService.ts         # 参考图例 v3.0（画廊、编辑、关联）
│   ├── referenceImageService.ts     # 旧参考图库（渐进式迁移中）
│   ├── retrievalService.ts          # 上下文检索（替代已废弃 contextService）
│   ├── metricsService.ts            # 指标数据
│   ├── promptPresetService.ts       # 提示词预设管理
│   └── dashboardService.ts          # Dashboard 统计数据
├── store/                           # 全局状态（Zustand）
│   ├── useAuthStore.ts              # 认证状态（token、refreshToken、登录态）
│   ├── useUserStore.ts              # 用户信息（profile、权限）
│   ├── useAppStore.ts               # 应用全局状态（侧边栏、主题、语言）
│   ├── useConfigStore.ts            # 后端动态配置缓存（评测方向、字段配置）
│   ├── useReferenceImageStore.ts    # 旧参考图库状态（渐进式迁移中）
│   └── useRefGalleryStore.ts        # 参考图例 v3.0 状态
├── core/                            # 核心业务组件（定位见 02 §1.3）
│   ├── EvalResultChart/             # 评测结果图表（ECharts）
│   ├── ScoreRadar/                  # 评分雷达图
│   ├── TaskProgress/                # 任务进度可视化
│   ├── ReportRenderer/              # 报告渲染器
│   ├── ResultCompare/               # 结果对比组件
│   └── TrendChart/                  # 趋势分析图
├── types/                           # 全局类型定义
│   ├── index.ts                     # 统一导出
│   ├── api.types.ts                 # API 通用响应类型（ApiResponse、分页）
│   ├── eval.types.ts                # 评测相关类型（套件、用例、方向、配置）
│   ├── task.types.ts                # 任务相关类型
│   ├── user.types.ts                # 用户与权限类型
│   ├── report.types.ts              # 报告类型
│   ├── file.types.ts                # 文件导入类型
│   ├── target.types.ts              # 被测系统类型
│   ├── config.types.ts              # 配置相关类型
│   ├── bug.types.ts                 # Bug 相关类型（M11）
│   ├── dashboard.types.ts           # Dashboard 类型
│   ├── promptPreset.types.ts        # 提示词预设类型
│   ├── refGallery.types.ts          # 参考图例 v3.0 类型（M12）
│   ├── referenceImage.types.ts      # 旧参考图库类型
│   └── ragas.types.ts               # RAG 评估类型
├── utils/                           # 工具函数（纯函数）
│   ├── logger.ts                    # 日志工具（见 02 §6.1）
│   ├── request.ts                   # 请求辅助（traceId 生成、取消请求）
│   ├── date.ts                      # 日期格式化（dayjs 封装）
│   ├── format.ts                    # 通用格式化（数字、金额、文件大小）
│   ├── validate.ts                  # 校验工具（邮箱、手机、密码强度）
│   ├── storage.ts                   # 存储工具（localStorage/sessionStorage 封装）
│   ├── download.ts                  # 文件下载工具
│   └── errors.ts                    # 错误类定义（见 §1.4）
├── constants/                       # 常量与枚举映射
│   ├── app.ts                       # 应用常量（应用名、版本）
│   ├── task.ts                      # 任务状态映射（状态→颜色、文案、图标）
│   ├── eval.ts                      # 评测方向/方式映射
│   └── permission.ts                # 权限码定义
├── config/                          # 配置
│   ├── env.ts                       # 环境变量读取（见 02 §5.2）
│   ├── api.ts                       # API 路径配置
│   ├── router.tsx                   # 路由与菜单配置（权限驱动）
│   └── theme.ts                     # 主题配置（antd ConfigProvider）
└── assets/                          # 静态资源
    ├── images/
    ├── icons/
    └── styles/                      # 全局样式
        ├── variables.scss           # SCSS 变量（颜色、间距、字体）
        ├── mixins.scss              # SCSS 混入
        ├── reset.scss               # 样式重置
        └── global.scss              # 全局样式
```

## 3. 领域特定规则

### 3.1 评测展示

- 评测方向、测试方式、字段配置**从后端动态获取**，前端通过 `configService.getEvalDirections()` 拉取并缓存到 `useConfigStore`
- 不同评测方向的用例表单**通过 `EvalFieldConfig` 动态渲染**，禁止为每个方向硬编码表单
- 评测方向扩展时（后端新增方向），前端无需改代码，自动渲染新方向的表单和列表
- 评测用例列表展示按方向过滤，支持方向切换 Tab
- 用例详情展示按方向差异化渲染（如 SQL 方向展示 SQL 代码块，RAG 方向展示检索片段）

### 3.2 任务状态管理

- 任务列表支持状态筛选（pending/running/completed/failed/cancelled），状态用 `StatusTag` 组件统一展示（颜色、图标）
- **任务详情页必须轮询任务状态**（`usePolling` Hook），running 状态下每 5s 轮询一次，终态停止轮询
- 任务进度按用例粒度展示（已完成/总数），用进度条 + 用例状态列表
- 任务取消、重试需二次确认（`ConfirmButton`），操作后立即刷新列表
- 任务创建后跳转任务详情页，让用户实时看到进度
- **轮询必须在组件卸载时取消**（`useEffect` 清理），避免内存泄漏和无效请求

### 3.3 历史记录与复测

- 历史记录功能统一使用 **`caseService`**（`getCaseHistory`、`getCaseTrend`），不使用已废弃的 `historyService`
- 历史记录列表支持按时间、方向、状态、关键词筛选，支持分页
- 历史详情展示完整链路：输入、模型输出、评分明细、耗时、traceId
- **复测操作**：列表支持多选 + 一键复测按钮，复测创建新任务并跳转任务详情
- **结果对比**：选择同一用例的多次执行结果，并排展示差异（输入相同则折叠，输出与评分差异高亮）
- **趋势分析**：按用例或套件维度，展示评分随时间的变化趋势（折线图）

### 3.4 报告可视化

- 报告页以可视化为主：雷达图（多维度评分）、柱状图（用例级评分）、折线图（趋势）
- 图表组件统一封装在 `core/` 目录（`EvalResultChart`、`ScoreRadar`、`TrendChart`），基于 ECharts 按需引入
- 报告数据量大时，图表懒加载（`React.lazy`），避免首屏卡顿
- 报告导出：前端生成 PDF（html2canvas + jsPDF）或调用后端导出接口，按需选择
- 报告页支持打印样式优化（`@media print`）

### 3.5 文件导入

- 支持 Excel（.xlsx）、JSON、CSV 三种格式，前端校验扩展名和大小（默认 10MB）
- 上传后**先预览解析结果**（前 N 条），用户确认字段映射后再正式导入
- 字段映射：源文件列 → 系统字段，支持自动匹配（按列名）+ 手动调整
- 导入结果反馈：成功条数、失败条数、失败原因明细（可下载失败列表）
- 大文件上传支持进度条（`onUploadProgress`），分片上传按需
- 导入的目标测试集由用户选择，导入后刷新对应测试集的用例列表

### 3.6 用户认证

- 登录页调用 `authService.login(username, password)`，成功后后端返回 `token` + `refreshToken`
- **Token 存储**：`token` 存内存（`useAuthStore`），`refreshToken` 存 sessionStorage（Zustand persist + partialize）
- 请求拦截器统一注入 `Authorization: Bearer <token>`
- 响应拦截器捕获 401：尝试用 `refreshToken` 刷新，失败则清空 Store 并跳转登录页
- **路由守卫**：未登录访问受保护路由，重定向到 `/login` 并记录 `redirect` 参数
- **权限路由**：根据 `useUserStore` 中的权限码，动态生成路由表和菜单（`config/router.tsx`）
- 登出时**必须清空所有 Store**（`useAuthStore`、`useUserStore`、`useConfigStore`）和 sessionStorage
- **重要**：前端权限控制仅作体验优化，前端不承担最终权限校验职责，安全以服务端校验为准

### 3.7 文件上传安全

- 前端校验：扩展名白名单（.xlsx/.json/.csv）+ MIME 类型 + 文件大小（默认 10MB）
- 文件名展示前 sanitize（去除路径分隔符），防止显示异常
- 前端文件类型校验仅作体验优化，不作为安全依赖，最终以服务端校验为准
- 大文件支持分片上传（按需，超过 50MB 启用）

### 3.8 被测系统配置

- 被测系统类型（LLM/RAG/MCP）**从后端动态获取**，前端按类型渲染差异化配置表单
- 配置表单通过 `EvalFieldConfig` 类似的动态字段配置驱动，禁止为每种类型硬编码表单
- 新增被测系统类型时（后端扩展），前端无需改代码，自动渲染新类型的配置表单
- 配置保存前提供"连接测试"按钮，调用后端测试接口验证配置有效性
- 敏感字段（API Key、Secret）前端展示为掩码，编辑时清空重填，不回显原值

### 3.9 评测方向与测试方式配置

- 评测方向和测试方式通过后端配置组合，前端不硬编码
- 前端通过 `configService` 拉取配置，缓存到 `useConfigStore`，应用启动时一次性加载
- 配置数据结构示例（与后端对齐）：

```typescript
// types/eval.types.ts

/** 评测方向配置项。 */
interface EvalDirectionConfig {
  /** 方向标识。 */
  code: EvalDirection;
  /** 方向名称。 */
  name: string;
  /** 该方向支持的测试方式。 */
  supportedMethods: EvalMethod[];
  /** 该方向用例的字段配置（驱动动态表单）。 */
  caseFields: EvalFieldConfig[];
  /** 该方向结果展示配置（驱动结果渲染）。 */
  resultFields?: EvalFieldConfig[];
}

/** 评测方向配置集合（从后端获取）。 */
type EvalDirectionConfigs = Record<EvalDirection, EvalDirectionConfig>;
```

- 创建评测用例时，根据选择的方向动态渲染表单字段
- 查看评测结果时，根据方向的结果展示配置动态渲染结果区域
- 评测方向扩展时，前端自动适配，无需修改代码

### 3.10 任务管理

- 大批量评测任务为异步执行，前端创建任务后立即获取任务 ID 并跳转任务详情页轮询进度
- 任务状态：pending / running / completed / failed / cancelled，前端用 `StatusTag` 统一展示
- 失败任务支持重试（前端调用重试接口，后端创建新任务）
- 任务进度按用例粒度更新，前端轮询展示进度条和用例状态列表
- 任务结果支持查看和导出，前端调用后端导出接口下载文件
- **复测支持**：任务可基于历史记录中的用例集合重新执行，前端复用任务创建流程

### 3.11 接口鉴权

- 用户登录通过用户名/密码验证，后端签发 JWT Token
- Token 在请求头中传递：`Authorization: Bearer <token>`
- 所有业务接口必须校验 Token（登录/注册接口除外），由 axios 请求拦截器统一注入
- 用户只能访问自己的测试数据和历史记录，前端不自行传 userId 过滤（由服务端从 Token 解析）
- Token 支持过期刷新机制：响应拦截器捕获 401，用 refreshToken 自动刷新

---

## 3.12 M10 智能笔记 V2 前端规则

### 笔记树组件
- 使用递归组件渲染树形结构
- 平铺数据通过 `parent_id` 组装成树（前端 `buildTree()` 函数）
- 节点类型区分：`folder`（分类）、`document`（文档）
- 拖拽使用 `@dnd-kit` 或 antd Tree 的 `draggable` 属性

### Markdown 编辑
- 支持实时预览（左右分栏或切换模式）
- 工具栏：标题/加粗/斜体/代码块/列表/链接/图片
- 自动保存使用 `useDebounce` Hook 防抖（300ms）

### 自动保存
- 仅更新 `content` 字段，不触发 `updated_at` 变更
- 保存状态指示器（保存中/已保存/保存失败）
- 乐观更新：先更新 UI，失败后回滚

### 软删除处理
- 前端过滤 `deleted_at != null` 的节点
- 删除操作使用 `Popconfirm` 二次确认
- 删除后立即从本地状态移除（乐观更新）
- 删除分类时级联删除所有子节点（前端递归过滤）

### 接口调用
| 操作 | 方法 | URL | 说明 |
|------|------|-----|------|
| 获取树 | GET | `/api/note/tree` | 返回平铺列表 |
| 新建节点 | POST | `/api/note/nodes` | type=folder/document |
| 更新标题 | PATCH | `/api/note/nodes/{id}` | title |
| 更新正文 | PATCH | `/api/note/nodes/{id}/content` | content（高频） |
| 删除节点 | DELETE | `/api/note/nodes/{id}` | 递归软删除 |
| 移动节点 | POST | `/api/note/nodes/{id}/move` | target_parent_id, sort_order |

---

## 3.13 M11 Bug 管理前端规则

### Bug 状态机展示
- 使用 `Tag` 组件映射 8 种状态：
  ```typescript
  const BUG_STATUS_MAP: Record<number, { color: string; label: string }> = {
    1: { color: 'orange', label: '待处理' },
    3: { color: 'blue', label: '修复中' },
    4: { color: 'cyan', label: '待验证' },
    5: { color: 'green', label: '验证通过' },
    6: { color: 'red', label: '重新打开' },
    7: { color: 'default', label: '已拒绝' },
    8: { color: 'default', label: '挂起' },
    9: { color: 'default', label: '已关闭' },
  };
  ```
- 状态流转按钮根据当前状态动态显示
- **禁止非法状态转换**（前端校验 + 后端兜底）

### Bug 严重程度展示
```typescript
const BUG_SEVERITY_MAP: Record<number, { color: string; label: string }> = {
  1: { color: 'red', label: 'P1 致命' },
  2: { color: 'orange', label: 'P2 严重' },
  3: { color: 'blue', label: 'P3 一般' },
  4: { color: 'default', label: 'P4 轻微' },
};
```

### 评论与附件
- 评论使用 `Timeline` 组件展示
- 附件支持图片预览（`antd Image` 组件）+ 文件下载
- 附件上传使用 `Upload` 组件，限制大小和类型
- 附件列表显示文件名、大小、上传时间、上传人

### 通知配置
- 邮件配置表单：SMTP 服务器、端口、发件人、收件人、密码
- 企微配置表单：Webhook URL、@人员列表
- 测试通知按钮调用 `POST /api/bug/notify/test`
- 配置保存调用 `PUT /api/bug/notify/config`

### 提醒日志
- 列表展示：触发时间、渠道、发送数量、成功/失败数
- 汇总统计：总发送次数、成功率、最近发送时间
- 手动触发：邮件/企微分别触发

### 个人首页统计
- 待处理 Bug 数量（红色高亮）
- 修复中/已解决等各状态数量
- 点击数字跳转到对应筛选条件的 Bug 列表

---

## 3.14 M12 参考图例 v3.0 前端规则

### 图例画廊
- 支持网格视图和列表视图切换
- 每张图例展示：缩略图、标题、标签、关联用例数、上传时间
- 支持按标签、分类、上传时间筛选
- 支持批量选择（用于批量操作）

### 图例编辑
- 支持上传新图片（jpg/png/gif/webp）
- 支持裁剪（集成裁剪组件）
- 支持添加标注（矩形/多边形标注）
- 元数据编辑：标题、描述、标签、分类

### 图例关联用例
- 在用例编辑页面通过 `RefImagePickerModal` 弹窗选择图例
- 支持多选关联
- 关联关系存储在后端

### 与旧参考图库的关系
- 旧参考图库（`referenceImageService` + `useReferenceImageStore`）仍在渐进式迁移中
- 新代码优先使用 `refGalleryService` + `useRefGalleryStore`
- 两者并存期间，通过组件引用逐步替换

---

## 3.15 Dashboard 前端规则

### 图表使用
- 使用 ECharts 渲染（按需引入）
- 雷达图：多维度评分展示（可选）
- 柱状图/饼图：用例/计划数量对比
- 图表响应式：监听窗口 `resize` 事件

### 数据刷新
- 页面加载时自动请求数据（`useEffect` + 空依赖）
- 支持手动刷新按钮
- 数据缓存 5 分钟
- 加载状态：Skeleton 骨架屏

### 统计卡片
```tsx
// 统计卡片结构
interface StatCard {
  title: string;        // 卡片标题
  value: number;        // 主数值
  unit?: string;        // 单位（如"个"）
  icon?: ReactNode;     // 图标
  color?: string;       // 主题色
  detail?: Record<string, number>;  // 明细（如按 type 细分）
}
```

---

## 3.16 上下文检索前端规则

### 检索服务
- **必须使用 `retrievalService`**，旧 `contextService` 已于 2026-09-03 移除
- 检索接口：`POST /api/retrieval/search`

### 检索结果展示
- 列表形式：每条结果展示内容摘要、来源文件、相似度分数
- 卡片形式（可选）：更详细的元信息展示
- 结果去重标识：显示 `(collection, file_id, seq_no)`

### 检索参数配置
```typescript
interface RetrievalParams {
  question: string;      // 检索问题
  top_k?: number;        // 返回数量（默认 30）
  collection?: string;   // Collection 名称
  enable_rerank?: boolean; // 是否 Rerank（默认 true）
}
```

---

## 3.17 用例调试前端规则（v0.11）

### 调试流程
1. 选择被测系统和模型配置
2. 输入测试内容（按评测方向差异化表单）
3. 点击"执行调试"
4. 实时查看输出和评分
5. 可保存配置为提示词预设

### 页面特点
- 单页面操作，无需创建完整用例
- 实时输出流式展示（SSE 或轮询）
- 支持多次快速迭代调试
- 配置可复用到正式用例创建
