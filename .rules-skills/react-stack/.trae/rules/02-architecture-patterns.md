---
alwaysApply: true
version: 1.1.0
lastUpdated: 2026-09-03
:description: 前端架构设计规则（v1.1），包括 feature-based 分层结构、组件分层、状态管理、API 层、路由、错误处理、配置管理、请求 traceId 日志规范、新模块架构定位指南。设计前端架构、划分模块、编写各层代码时使用此规则。
---

# 架构设计规则（通用）

> 本规范适用于采用 React + TypeScript 的前端项目，可直接复制使用。
> 项目特定的模块划分请在 `project/01-project-specific.md` 中定义。
>
> **v1.1 更新 (2026-09-03)**：新增 §7 新模块架构定位指南（Bug/笔记/参考图例/用户管理/用例调试）。

## 1. 分层架构

项目采用 **feature-based（按功能领域划分）+ 横向分层** 的混合架构。横向分层定义职责边界，feature-based 按业务领域聚合，避免按文件类型堆砌导致的"改一个功能跳 5 个目录"问题。

```
src/
├── pages/          # 页面层（路由入口、页面布局、数据编排）
├── components/     # 组件层
│   ├── basic/      # 基础 UI 组件（按钮、输入框、表格封装）
│   └── business/   # 业务组件（跨 feature 复用）
├── hooks/          # 自定义 Hook（业务逻辑复用）
├── services/       # API 服务层（HTTP 请求封装）
├── store/          # 全局状态管理（Zustand）
├── utils/          # 纯工具函数（无副作用）
├── types/          # TypeScript 类型定义
├── constants/      # 常量与枚举映射
└── config/         # 配置（环境变量、API 路径、主题）
```

### 1.1 各层职责

| 层 | 职责 | 示例 |
|---|------|------|
| **pages/** | 路由入口、页面布局、数据编排、权限控制 | `EvalListPage`、`TaskDetailPage` |
| **components/basic/** | 无业务逻辑的纯 UI 封装 | `DataTable`、`FormInput`、`StatusTag` |
| **components/business/** | 有业务逻辑的跨 feature 复用组件 | `UserMenu`、`SideMenu`、`HistoryRecordModal` |
| **hooks/** | 可复用的业务逻辑（状态 + 副作用） | `useAuth`、`usePagination`、`usePolling` |
| **services/** | API 调用封装（一个 Service 对应后端一个模块） | `caseService`、`taskService`、`bugService` |
| **store/** | 跨组件共享的全局状态（Zustand） | `useAuthStore`、`useUserStore`、`useConfigStore` |
| **utils/** | 纯函数工具（无副作用、无状态） | `formatDate`、`validateEmail`、`generateTraceId` |
| **types/** | 接口、类型别名、枚举 | `ApiResponse`、`EvalCase`、`TaskStatus` |
| **constants/** | 不变的值或映射表 | `TASK_STATUS_MAP`、`EVAL_DIRECTION_MAP` |
| **config/** | 环境变量读取、API 路径常量、主题配置 | `getApiBaseUrl`、`API_ENDPOINTS` |

### 1.2 数据流向

```
用户操作 → Page 组件 → Hook/Service → API 请求 → 后端
                ↓
           Store 更新 → 组件重渲染
```

**原则**：
- 页面组件（Page）是数据编排中心，负责调用 Hook/Service 获取数据并分发给子组件
- 子组件通过 props 接收数据，不直接调用 Service 或 Store（除非是业务组件）
- Service 只负责 HTTP 请求，不做业务逻辑判断（业务逻辑在 Hook 或 Page 中）
- Store 仅用于**真正跨组件共享**的状态（如登录态、用户信息），避免滥用

### 1.3 core/ 目录定位

对于**核心业务组件**（如评测结果可视化、报告渲染器），如果同时满足以下条件，可放在 `core/` 目录：

1. **复杂度高**：包含大量业务逻辑和状态管理（如图表渲染、数据转换）
2. **复用性强**：被多个 Page 或业务组件引用
3. **职责单一**：聚焦某一核心业务能力（如"评测结果展示"）

**示例**：
```
core/
├── EvalResultChart/     # 评测结果图表（ECharts 封装，被 Report/Task/History 引用）
├── ScoreRadar/          # 评分雷达图
├── TaskProgress/        # 任务进度可视化
├── ReportRenderer/      # 报告渲染器（PDF/HTML）
├── ResultCompare/       # 结果对比组件
└── TrendChart/          # 趋势分析图
```

**反例**（不应放 core/）：
- 纯 UI 封装（如 `DataTable`）→ 放 `components/basic/`
- 单页面专用组件（如 `EvalCaseForm`）→ 放 `pages/case/EvalCaseFormPage/`
- 简单业务组件（如 `StatusTag`）→ 放 `components/business/`

### 1.4 何时用全局 Store（Zustand）

**使用场景**：
- ✅ 登录态/Token（全局路由守卫需要）
- ✅ 用户信息/权限（多组件展示头像、菜单、权限按钮）
- ✅ 后端动态配置（评测方向、字段配置，多页面共用）
- ✅ 应用全局状态（侧边栏展开/收起、主题切换、语言）

**不使用场景**（用组件 state 或 props）：
- ❌ 表单数据（仅在当前表单组件内使用）
- ❌ 列表的筛选/排序状态（仅当前列表页使用）
- ❌ 弹窗的显示/隐藏状态（仅当前弹窗使用）
- ❌ 临时加载状态（loading/error，用 `useRequest` Hook 管理）

> **原则**：能用 props/state 解决的，不用 Store。Store 是"最后手段"，用于真正的全局共享状态。

## 2. 组件设计原则

### 2.1 组件分类与命名

| 类型 | 命名规则 | 存放位置 | 示例 |
|------|---------|---------|------|
| 页面组件 | `XxxPage` | `pages/feature/` | `EvalListPage`、`TaskDetailPage` |
| 业务组件 | `Xxx`（名词/动宾） | `components/business/` | `UserMenu`、`SideMenu`、`EvalDirectionSelector` |
| 基础组件 | `Xxx`（通用 UI） | `components/basic/` | `DataTable`、`FormInput`、`StatusTag` |
| 核心业务组件 | `Xxx`（核心能力） | `core/` | `EvalResultChart`、`ReportRenderer` |
| Hook | `useXxx` | `hooks/` | `useAuth`、`usePagination`、`usePolling` |

### 2.2 组件职责单一原则

每个组件只做一件事：

```tsx
// ✅ 好：职责单一——仅展示任务进度条
function TaskProgress({ progress, status }: { progress: number; status: TaskStatus }) {
  return <Progress percent={progress} status={status === 'failed' ? 'exception' : 'active'} />;
}

// ❌ 差：职责混杂——既展示进度又发请求又处理取消
function Task({ taskId }: { taskId: number }) {
  const [task, setTask] = useState<Task>();
  useEffect(() => { /* 轮询任务 */ }, [taskId]);
  const handleCancel = async () => { /* 取消任务 */ };
  return (
    <div>
      <Progress percent={task?.progress} />
      <Button onClick={handleCancel}>取消</Button>
    </div>
  );
}
```

### 2.3 容器组件 vs 展示组件

- **容器组件（Container/Smart Component）**：负责数据获取、状态管理、事件处理
- **展示组件（Presentational/Dumb Component）**：仅接收 props 渲染 UI，无副作用

```tsx
// 容器组件：负责数据获取
function EvalListContainer() {
  const { data, loading, error } = useEvalList(); // Hook 封装请求逻辑
  if (loading) return <Skeleton />;
  if (error) return <ErrorFallback error={error} />;
  return <EvalList data={data} />; // 展示组件
}

// 展示组件：仅渲染 UI
function EvalList({ data }: { data: EvalSuite[] }) {
  return <Table dataSource={data} columns={columns} />;
}
```

**实际项目中**：Page 组件充当容器角色，`components/basic/` 和 `components/business/` 中的组件尽量做成展示组件。

### 2.4 组件通信方式

| 场景 | 推荐方式 | 示例 |
|------|---------|------|
| 父 → 子 | Props | `<TaskDetail task={task} />` |
| 子 → 回调 | Props 回调函数 | `<ConfirmButton onConfirm={handleDelete} />` |
| 兄弟组件 | 提升状态到父组件 | 父组件管理筛选状态，传给列表+搜索栏 |
| 跨层级深嵌套 | Context / Zustand Store | 用户信息、主题、权限 |
| 跨 Feature | Zustand Store + 订阅 | 登录态变化 → 多个 Feature 响应 |

**禁止**：
- ❌ 使用 `ref` 操作子组件内部方法（除非是第三方库的 imperative handle）
- ❌ 直接修改 props（Props 是只读的）
- ❌ 在非必要场景使用 Context/Store（优先用 props）

## 3. Hooks 设计规范

### 3.1 自定义 Hook 命名与职责

- 必须以 `use` 开头（ESLint 规则强制）
- 一个 Hook 封装**一组相关的业务逻辑**
- 返回值结构统一：`{ data, loading, error }` + 操作方法

```typescript
// ✅ 好：职责清晰，返回值结构化
function useEvalList(params: EvalListParams) {
  const [data, setData] = useState<EvalSuite[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchList = useCallback(async () => {
    setLoading(true);
    try {
      const res = await caseService.getEvalSuites(params);
      setData(res.data.list);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => { fetchList(); }, [fetchList]);

  return { data, loading, error, refetch: fetchList };
}
```

### 3.2 通用请求 Hook（useRequest）

封装通用的请求逻辑（loading/error/data/refetch），避免每个组件重复写：

```typescript
// hooks/useRequest.ts
function useRequest<T>(serviceFn: () => Promise<ApiResponse<T>>, options?: { manual?: boolean }) {
  // 统一管理 loading、error、data、refetch
  // 支持 manual 模式（手动触发）
  // 自动处理错误日志
}
```

### 3.3 Hook 依赖数组规则

- **必须**在 `useEffect`/`useCallback`/`useMemo` 的依赖数组中声明所有外部变量
- **禁止**空依赖数组但内部使用了外部变量（会导致闭包陷阱）
- **推荐**使用 ESLint 的 `react-hooks/exhaustive-deps` 规则自动检查

```tsx
// ❌ 错误：userId 在依赖数组中缺失
useEffect(() => {
  caseService.getEvalSuites({ userId }).then(setData); // userId 可能是旧值
}, []); // 缺少 userId

// ✅ 正确：依赖完整
useEffect(() => {
  caseService.getEvalSuites({ userId }).then(setData);
}, [userId]); // 依赖完整
```

## 4. 服务层（Services）设计

### 4.1 Service 文件组织

- **按业务领域划分**，一个后端模块对应一个 Service 文件
- Service 文件放在 `services/` 目录（不在 pages/ 内部，便于跨 feature 复用）
- 每个 Service 导出一组**纯 API 调用函数**（无 UI 逻辑、无状态管理）

```typescript
// services/caseService.ts
/** 评测套件服务。 */
export const caseService = {
  /** 获取评测套件列表（分页）。 */
  getEvalSuites: (params: EvalListParams): Promise<ApiResponse<PaginatedData<EvalSuite>>> =>
    request.get('/eval/suites', { params }),

  /** 获取评测套件详情。 */
  getEvalSuiteDetail: (id: number): Promise<ApiResponse<EvalSuite>> =>
    request.get(`/eval/suites/${id}`),

  /** 创建评测套件。 */
  createEvalSuite: (data: CreateEvalSuiteDto): Promise<ApiResponse<EvalSuite>> =>
    request.post('/eval/suites', data),

  // ... 其他方法
};
```

### 4.2 Service 职责边界

**Service 只做**：
- ✅ HTTP 请求调用（GET/POST/PUT/DELETE）
- ✅ 请求参数组装和响应数据解构
- ✅ 请求/响应拦截（统一在 `request.ts` 的拦截器中）

**Service 不做**：
- ❌ 业务逻辑判断（如"是否允许删除"→ 放在 Hook 或 Page 中）
- ❌ 状态管理（不操作 Store）
- ❌ UI 交互（不弹确认框、不跳转路由）
- ❌ 数据缓存（缓存逻辑放在 Store 或 Hook 中）

### 4.3 错误处理策略

- Service 层**不捕获错误**，直接抛出（由调用方的 Hook/Page 统一处理）
- 或统一包装为 `ApiError`（在 `request.ts` 的响应拦截器中完成）

```typescript
// services/caseService.ts
deleteEvalSuite: async (id: number): Promise<void> => {
  // ✅ 直接返回，错误由拦截器统一处理
  return request.delete(`/eval/suites/${id}`);
},
```

```typescript
// hooks/useEvalList.ts
const handleDelete = async (id: number) => {
  try {
    await caseService.deleteEvalSuite(id); // 错误会抛出到这里
    message.success('删除成功');
    refetch(); // 刷新列表
  } catch (error) {
    // 统一错误处理（拦截器已弹 toast，这里可做额外处理）
    if (error instanceof ApiError && error.statusCode === 403) {
      message.error('无权删除');
    }
  }
};
```

## 5. 状态管理（Zustand）

### 5.1 Store 设计原则

- **按领域划分 Store**：一个业务域一个 Store（auth/user/config/app）
- **最小化 Store 数量**：不要为每个功能都建 Store，优先用组件 state + props
- **扁平化状态**：避免深层嵌套，便于更新
- **选择性持久化**：仅敏感数据（token）存 sessionStorage，其他默认内存

### 5.2 Store 示例

```typescript
// store/useAuthStore.ts
interface AuthState {
  token: string | null;
  refreshToken: string | null;
  isLoggedIn: boolean;
  // Actions
  setTokens: (token: string, refreshToken: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      isLoggedIn: false,
      setTokens: (token, refreshToken) =>
        set({ token, refreshToken, isLoggedIn: true }),
      clearAuth: () =>
        set({ token: null, refreshToken: null, isLoggedIn: false }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ refreshToken: state.refreshToken }), // 仅持久化 refreshToken
      storage: sessionStorageStorage, // refreshToken 存 sessionStorage
    },
  ),
);
```

### 5.3 Store 使用禁忌

- ❌ **禁止在 Store 中发 HTTP 请求**（请求逻辑放在 Service 中）
- ❌ **禁止在 Store 中操作 DOM**（DOM 操作在组件 Effect 中）
- ❌ **禁止循环依赖**（Store A 依赖 Store B，B 又依赖 A）
- ⚠️ **谨慎使用 subscribe**（仅在需要跨组件响应时使用，如监听 token 过期跳转登录）

## 6. 路由设计

### 6.1 路由配置

- 路由表集中定义在 `router/index.tsx`
- 使用 `React.lazy` 懒加载页面组件（减少首屏 bundle 大小）
- 受保护路由包裹 `ProtectedRoute` 组件（校验登录态和权限）

```typescript
// router/index.tsx
const routes: RouteObject[] = [
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute> {/* 校验登录态 + 权限 */}
        <MainLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Navigate to="/eval" replace /> },
      {
        path: 'eval',
        element: lazy(() => import('@/pages/case/EvalListPage')),
      },
      // ... 其他路由
    ],
  },
];
```

### 6.2 路由守卫

`ProtectedRoute` 组件职责：
1. 检查 `useAuthStore.isLoggedIn`，未登录则重定向到 `/login?redirect=<current_path>`
2. 检查 `useUserStore.hasPermission(route.permission)`，无权限则显示 403 页面
3. 显示加载状态（Token 刷新期间）

### 6.3 动态路由与菜单

- 菜单配置从后端获取（或前端配置文件），根据权限码过滤
- 路由元信息（`meta`）携带：标题、图标、权限码、是否缓存
- 面包屑根据路由匹配自动生成

## 7. 新模块架构定位指南

> **v1.1 新增 (2026-09-03)**：为 M10/M11/M12 及后续新增模块提供架构定位指导。

### 7.1 Bug 管理系统（M11）

| 架构层 | 放置位置 | 说明 |
|--------|---------|------|
| Pages | `pages/bug/BugDashboardPage`, `BugListPage`, `BugReportPage`, `BugSystemManagePage` | 4 个页面 |
| Components | `components/business/BugStatusTag`, `BugSeverityTag`, `BugCommentTimeline` | 跨页面复用的业务组件 |
| Services | `services/bugService.ts` | 统一 API 封装（CRUD/状态机/评论/通知） |
| Stores | 无独立 Store（使用组件 state + props） | Bug 数据不需要全局共享 |
| Types | `types/bug.types.ts` | Bug 相关类型定义 |
| Core | 无 | Bug 管理是独立功能，无需 core 组件 |

**关键决策**：
- Bug 状态机逻辑放在 `bugService.ts` 中（后端校验为主，前端仅做 UI 展示限制）
- 评论 Timeline 可复用为通用组件（未来笔记系统也可用）
- 通知配置独立页面，不与其他配置混在一起

### 7.2 智能笔记 V2（M10）

| 架构层 | 放置位置 | 说明 |
|--------|---------|------|
| Pages | `pages/noteV2/NoteTreePage`, `NoteEditPage` | 2 个页面（树形 + 编辑） |
| Components | `components/business/NoteTree`, `MarkdownEditor` | 树形组件 + Markdown 编辑器 |
| Services | `services/noteService.ts` | 笔记 CRUD + 内容保存 |
| Stores | 无独立 Store（使用组件 state + context） | 笔记数据局部分页即可 |
| Types | 复用现有类型或内联 | 笔记结构相对简单 |
| Core | 无 | 笔记是独立功能 |

**关键决策**：
- 树形数据在前端通过 `parent_id` 组装（`buildTree()` 函数放在 utils/）
- Markdown 编辑器选用轻量级库（如 `@uiw/react-md-editor` 或 `react-markdown` + 编辑模式）
- 自动保存通过 `useDebounce` Hook 实现（300ms 防抖）

### 7.3 参考图例 v3.0（M12）

| 架构层 | 放置位置 | 说明 |
|--------|---------|------|
| Pages | `pages/refgallery/RefGalleryPage`, `RefImageEditPage` + `RefImagePickerModal` | 2 个页面 + 1 个弹窗 |
| Components | `components/business/RefImageCard`, `RefImageGrid`, `RefImageUploader` | 图例卡片/网格/上传组件 |
| Services | `services/refGalleryService.ts` | 图例 CRUD + 关联用例 |
| Stores | `store/useRefGalleryStore.ts` | 图例选择状态（跨页面共享选择结果） |
| Types | `types/refGallery.types.ts` | 参考图例类型定义 |
| Core | 无 | 图例管理是独立功能 |

**关键决策**：
- 与旧参考图库（`referenceImageService` + `useReferenceImageStore`）并存，渐进式迁移
- 新代码优先使用 `refGalleryService` + `useRefGalleryStore`
- `RefImagePickerModal` 作为弹窗组件，可被用例编辑页面引用

### 7.4 用户管理

| 架构层 | 放置位置 | 说明 |
|--------|---------|------|
| Pages | `pages/system/UserManagePage` | 1 个页面（管理员功能） |
| Components | 复用 `components/basic/DataTable`, `FormInput` 等 | 无需特殊业务组件 |
| Services | `services/userService.ts` | 用户 CRUD + 角色分配 |
| Stores | 无（使用 `useUserStore` 获取当前用户信息） | 用户列表不需要全局状态 |
| Types | `types/user.types.ts` | 已有用户类型定义 |
| Core | 无 | 用户管理是简单 CRUD |

**关键决策**：
- 用户管理是管理员功能，需权限控制（`permission: 'user:manage'`）
- 复用通用 `DataTable` 组件，无需自定义
- 密码修改/重置需二次确认

### 7.5 用例调试（v0.11）

| 架构层 | 放置位置 | 说明 |
|--------|---------|------|
| Pages | `pages/debug/DebugPage` 或 `pages/case/CaseDebugPage` | 1 个页面 |
| Components | 复用现有评测相关组件 | 表单、结果展示等 |
| Services | 复用 `caseService.debugExec()` 或新增 `debugService.ts` | 调试执行接口 |
| Stores | 无 | 调试状态局部即可 |
| Types | 复用 `types/eval.types.ts` | 复用现有类型 |
| Core | 可能复用 `core/EvalResultChart` | 结果展示 |

**关键决策**：
- 用例调试是评测流程的延伸，可放在 `pages/case/` 下
- 调试执行可能需要 SSE（Server-Sent Events）支持流式输出
- 配置可保存为提示词预设（复用 `promptPresetService`）

### 7.6 Dashboard 首页

| 架构层 | 放置位置 | 说明 |
|--------|---------|------|
| Pages | `pages/dashboard/DashboardPage` | 1 个页面 |
| Components | `components/business/StatCard` | 统计卡片组件 |
| Services | `services/dashboardService.ts` | 统计数据查询 |
| Stores | 无（使用组件 state + `useQuery` 缓存） | 数据缓存 5 分钟 |
| Types | `types/dashboard.types.ts` | Dashboard 类型定义 |
| Core | 可能复用 ECharts 组件 | 图表展示 |

**关键决策**：
- Dashboard 是数据展示页，重点在图表和统计卡片
- 所有用户（含管理员）仅查看本人数据，不显示全局统计
- 数据缓存 5 分钟，避免频繁请求

---

## 8. 错误处理架构

### 8.1 错误分类与处理链路

```
用户操作 → Service → HTTP 请求
                  ↓
            响应拦截器（request.ts）
                  ↓
    ┌─────────────┼─────────────┐
    ↓             ↓             ↓
  网络错误      4xx 错误      5xx 错误/业务错误
    ↓             ↓             ↓
 NetworkError  UnauthorizedError  BusinessError
    ↓             ↓             ↓
  断网提示     刷新Token/跳登录   提示业务错误信息
```

### 8.2 错误边界（Error Boundary）

- 使用 `react-error-boundary` 或自建 `ErrorBoundary` 组件
- 包裹整个应用（`App.tsx` 级别）和每个懒加载页面
- 错误降级：展示错误信息 + 重试按钮

```tsx
// App.tsx
<ErrorBoundary fallback={<ErrorPage onRetry={() => window.location.reload()} />}>
  <RouterProvider router={router} />
</ErrorBoundary>
```

### 8.3 全局未捕获异常

```typescript
// main.tsx
window.addEventListener('unhandledrejection', (event) => {
  logger.error('Unhandled promise rejection:', event.reason);
  // 可选：上报到 Sentry
});

window.addEventListener('error', (event) => {
  logger.error('Uncaught error:', event.error);
});
```

## 9. 配置管理

### 9.1 环境变量

- 使用 Vite 的 `import.meta.env` 读取环境变量
- 环境变量定义在 `.env` / `.env.development` / `.env.production` 中
- 敏感配置（API Key）不提交到 Git，通过环境变量注入

```typescript
// config/env.ts
export const env = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || '/api',
  APP_NAME: import.meta.env.VITE_APP_NAME || 'AI 测评系统',
  SENTRY_DSN: import.meta.env.VITE_SENTRY_DSN, // 可选
};
```

### 9.2 API 路径配置

- API 路径集中定义在 `config/api.ts`，Service 层引用常量而非硬编码 URL
- 支持环境变量前缀（开发环境 `/api` 代理，生产环境可能不同）

```typescript
// config/api.ts
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
  },
  EVAL: {
    SUITES: '/eval/suites',
    CASES: '/eval/cases',
  },
  // ...
} as const;
```

## 10. 日志与监控

### 10.1 日志规范

- 使用统一的 `logger` 工具（基于 `console` 封装，支持级别控制）
- 生产环境关闭 `debug` 级别日志
- 所有 API 请求/响应记录 `traceId`（便于前后端联查）

```typescript
// utils/logger.ts
const logger = {
  info: (...args: any[]) => console.log('[INFO]', ...args),
  warn: (...args: any[]) => console.warn('[WARN]', ...args),
  error: (...args: any[]) => console.error('[ERROR]', ...args),
  debug: (...args: any[]) => {
    if (import.meta.env.DEV) console.log('[DEBUG]', ...args);
  },
};
```

### 10.2 性能监控（可选）

- 首屏加载时间（FCP、LCP）
- 路由切换耗时
- API 请求耗时（P50/P95/P99）
- 可集成 Web Vitals + 上报到监控系统

## 11. 安全规范

### 11.1 XSS 防护

- React 默认转义 JSX 中的动态内容（防 XSS）
- **危险操作**：`dangerouslySetInnerHTML` 必须对内容 sanitize（使用 `DOMPurify`）
- 用户输入展示前转义（虽然 React 自动处理，但拼接字符串时需注意）

### 11.2 CSRF 防护

- 使用 `SameSite` Cookie 属性（后端配置）
- 或后端返回 CSRF Token，前端在请求头中携带

### 11.3 敏感数据处理

- Token / RefreshToken **禁止**存 localStorage（用内存 Store + sessionStorage）
- 日志中**禁止**打印 Token、密码、API Key 等敏感信息
- 错误上报到监控系统时，脱敏处理（移除 Token、用户隐私）

## 12. 代码分割与性能优化

### 12.1 路由级代码分割

- 所有页面组件使用 `React.lazy()` 动态导入
- 配合 `<Suspense>` 展示加载骨架屏

```typescript
const EvalListPage = lazy(() => import('@/pages/case/EvalListPage'));

// Router 中使用
<Suspense fallback={<PageSkeleton />}>
  <EvalListPage />
</Suspense>
```

### 12.2 第三方库按需引入

- ECharts：按需注册组件（`echarts/core` + 按需引入图表类型）
- Ant Design：按需引入组件（`babel-plugin-import` 或 unplugin-auto-import）
- Dayjs：按需引入插件（`dayjs/plugin/relativeTime`）

### 12.3 Bundle 优化目标

- 首屏 JS ≤ 250KB（gzip 后）
- 单个路由 chunk ≤ 100KB（gzip 后）
- 图片资源使用 WebP 格式，懒加载

## 13. 测试策略

### 13.1 单元测试

- **测试范围**：utils/、hooks/、services/（纯逻辑，无 UI）
- **不测**：组件渲染细节（UI 变化快，维护成本高，价值低）
- **工具**：Vitest + @testing-library/react（如需测 Hook）
- **覆盖率目标**：核心逻辑 ≥ 80%，整体 ≥ 60%

```typescript
// tests/unit/utils/date.test.ts
describe('formatDate', () => {
  it('should format date to YYYY-MM-DD', () => {
    expect(formatDate(new Date('2024-01-15'))).toBe('2024-01-15');
  });
});
```

### 13.2 E2E 测试

- **测试范围**：核心用户流程（登录 → 创建用例 → 执行任务 → 查看报告）
- **工具**：Playwright
- **运行环境**：CI/CD 中 Headless 模式，本地调试用 headed 模式
- **关键流程必须覆盖**：