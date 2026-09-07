---
alwaysApply: false
description: TypeScript/React 前端编码规范，包括命名约定、代码格式、类型提示、TSDoc 注释、导入规范。编写或审查前端代码时使用此规则。
---
# 编码规范（通用）

> 本规范适用于所有 TypeScript + React 前端项目，可直接复制到新项目使用。
> 项目特定的命名约定请在 `project/01-project-specific.md` 中补充。

## 1. 命名规范

### 1.1 通用原则

- 使用描述性名称，名称应清楚表达其用途
- 避免使用单字符变量（循环计数器 i, j, k 除外）
- 不使用语言关键字及全局对象属性名（如 `name`、`length`、`arguments`）
- 名称要简洁而完整，在清晰的前提下尽可能简短

### 1.2 命名约定速查表

| 类型 | 命名规范 | 示例 |
|------|---------|------|
| 文件（组件） | PascalCase.tsx | `UserService.tsx`, `EvalList.tsx` |
| 文件（非组件） | camelCase.ts / kebab-case.ts | `userService.ts`, `date-utils.ts` |
| 目录 | kebab-case | `user-service/`, `eval-list/` |
| 组件（函数组件） | PascalCase | `UserService`, `EvalList` |
| 钩子函数 | camelCase + use 前缀 | `useAuth`, `useEvalList` |
| 普通函数/方法 | camelCase | `parseData()`, `getUserInfo()` |
| 变量 | camelCase | `userName`, `totalCount` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| TypeScript 类型/接口 | PascalCase | `EvalCase`, `TaskStatus` |
| 类型别名 | PascalCase | `EvalDirection = 'text_qa' \| 'rag_scoring'` |
| 枚举 | PascalCase（类型）+ PascalCase（成员） | `enum TaskStatus { Pending, Running }` |
| 布尔变量 | is_/has_/can_/should_ 前缀 | `isValid`, `hasPermission` |
| 事件处理 | on/handle 前缀 | `onSubmit`, `handleSubmit` |
| 集合变量 | 复数形式 | `users`, `results`, `items` |
| CSS Modules 类名 | camelCase | `styles.container`, `styles.headerTitle` |

### 1.3 文件命名细则

- **组件文件**：使用 PascalCase（`EvalList.tsx`），与默认导出的组件名一致
- **非组件文件**（工具、服务、类型、配置）：使用 camelCase 或 kebab-case，**项目内保持统一**
- **类型定义文件**：`.types.ts` 后缀（如 `eval.types.ts`）或集中放在 `types/` 目录
- **测试文件**：与源文件同名加 `.test`/`.spec` 后缀（`userService.test.ts`）
- **样式文件**：与组件同名（`EvalList.module.scss` / `EvalList.module.css`）

## 2. 代码格式

### 2.1 缩进与行长度

- 使用 2 个空格缩进（前端惯例，与 Prettier 默认一致），不使用 Tab
- 每行最多 120 个字符
- 超过时合理换行，优先在逗号、运算符、JSX 属性后换行

### 2.2 空行

- 顶层函数、类、组件定义之间用 1 个空行
- 类内方法之间用 1 个空行
- 逻辑相关的代码块之间用 1 个空行分隔
- import 语句块与后续代码之间用 1 个空行

### 2.3 导入规范

**导入顺序（每组之间用 1 个空行分隔）：**
1. Node 内置模块 / 第三方库（React、antd、axios 等）
2. 项目内别名导入（`@/` 起头的绝对路径）
3. 相对路径导入（`./`、`../`）
4. 类型导入（使用 `import type`）

**规则：**
- 禁止使用通配符导入（`import * as Foo`），除特殊场景（如 CSS Modules：`import styles from './x.module.css'`）
- 同一组内按字母顺序排列（由 ESLint 自动排序）
- 避免循环导入
- **类型与值混用时优先使用 `import type` 显式分离**，便于构建工具做类型擦除

**示例：**
```typescript
// 1. 第三方库
import React, { useEffect, useState } from 'react';
import { Button, Form, Input } from 'antd';
import axios from 'axios';

// 2. 项目别名导入
import { useAuth } from '@/hooks/useAuth';
import { EvalService } from '@/services/evalService';

// 3. 相对路径导入
import { EvalList } from './components/EvalList';
import { formatDate } from './utils';

// 4. 类型导入
import type { EvalCase, TaskInfo } from './types';
```

### 2.4 JSX 规范

- 单标签必须自闭合：`<Input />`
- 多属性换行，闭合 `>` 单独一行
- 组件嵌套超过 3 层时考虑抽取子组件
- 列表渲染必须提供稳定的 `key`（优先使用业务 id，避免用数组下标）

```tsx
<EvalList
  data={cases}
  loading={loading}
  onRefresh={handleRefresh}
  onDelete={handleDelete}
/>
```

## 3. TSDoc 注释

### 3.1 模块注释

每个文件（组件、工具、服务）开头必须有注释，简要说明模块用途。

```typescript
/**
 * 评测用例管理服务。
 *
 * 封装评测用例的 CRUD、批量导入、查询等 API 调用。
 */
```

### 3.2 组件注释

```typescript
/**
 * 评测列表组件。
 *
 * 展示评测套件下的用例列表，支持分页、筛选、批量删除。
 *
 * @example
 * <EvalList suiteId="suite-001" onRefresh={handleRefresh} />
 */
export const EvalList: React.FC<EvalListProps> = ({ suiteId, onRefresh }) => {
  // ...
};
```

### 3.3 函数/方法注释

所有 public 函数和复杂逻辑必须有 TSDoc 注释，包含 `@param`、`@returns`、`@throws`。

```typescript
/**
 * 处理输入数据。
 *
 * @param data - 输入数据对象
 * @param validate - 是否进行数据校验，默认 true
 * @returns 处理后的数据对象
 * @throws {ValidationError} 数据校验失败时
 */
function processData(data: EvalCase, validate = true): ProcessedCase {
  // ...
}
```

## 4. 类型提示

- **强制开启 `strict: true`**，禁止使用 `any`，必须用 `unknown` + 类型守卫替代
- 所有公开函数、组件 Props、Hook 返回值必须有显式类型
- 复杂类型使用 `interface`（可扩展、可被实现），简单联合类型用 `type`
- 优先使用具体类型而非 `any`/`unknown`
- API 响应类型与后端 Schema 对齐，统一在 `types/` 目录维护

```typescript
// 接口：用于对象结构、可被扩展
interface EvalCase {
  id: string;
  title: string;
  direction: EvalDirection;
  status: TaskStatus;
}

// 类型别名：用于联合、交叉、工具类型
type EvalDirection = 'text_qa' | 'sql_correctness' | 'rag_scoring';
type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

// 枚举：用于有明确语义且需要运行时值的场景
enum LogLevel {
  Debug = 'debug',
  Info = 'info',
  Warn = 'warn',
  Error = 'error',
}

function processItems(items: EvalCase[]): Record<string, number> {
  // ...
}

function findItem(name: string): EvalCase | null {
  // ...
}
```

### 4.1 Props 类型规范

- 组件 Props 必须定义 `interface XxxProps`，并以 `Props` 结尾
- 事件回调命名：`onChange`、`onSubmit`、`onRefresh`，类型用 `React.ChangeEvent`、`() => void` 等
- 可选 Props 用 `?` 标注，并提供合理默认值

```typescript
interface EvalListProps {
  suiteId: string;
  loading?: boolean;
  onRefresh?: () => void;
  onDelete?: (caseId: string) => void;
}
```

## 5. 注释规范

### 5.1 注释原则

- 注释应该解释"为什么"，而不是"做什么"
- 避免注释与代码重复
- TODO/FIXME 注释必须包含负责人和日期

```typescript
// TODO: 优化大列表渲染性能，考虑虚拟滚动 - username - 2026-08-13
// FIXME: 分页参数边界条件处理不正确 - ticket #123
```

### 5.2 组件与函数注释（强制）

- **所有 public 组件和函数必须有 TSDoc 注释**，说明用途、参数、返回值和可能的异常
- **重要的 private 函数也应有注释**，说明其内部逻辑和设计意图
- 复杂逻辑段应有行内注释，解释设计原因

```typescript
/**
 * 构建评测上下文。
 *
 * 从服务端加载评测套件和用例配置，
 * 合并运行时参数生成不可变的上下文对象。
 *
 * @param suiteId - 评测套件 ID
 * @param caseIds - 指定执行的用例 ID 列表，为空则加载全部
 * @returns 评测上下文对象
 * @throws {EvalSuiteError} 套件不存在或配置无效时
 */
function buildEvalContext(suiteId: string, caseIds: string[]): EvalContext {
  // 只加载活跃状态的用例，避免历史废弃用例干扰结果
  const activeCases = filterActive(caseIds);
  // ...
}
```

### 5.3 配置文件注释（强制）

- **每个配置项必须有注释**，说明用途、取值范围、默认值含义
- **环境变量配置项**需注明对应的环境变量名和推荐值
- **分组配置**需有分组说明注释

```typescript
// 评测任务并发控制
export const EVAL_CONFIG = {
  // 最大并发评测任务数，默认 5（前端并发限制，避免阻塞浏览器）
  MAX_CONCURRENT_TASKS: Number(import.meta.env.VITE_MAX_CONCURRENT_TASKS ?? 5),
  // 单任务轮询超时秒数，默认 3600
  TASK_TIMEOUT: Number(import.meta.env.VITE_TASK_TIMEOUT ?? 3600),
};

// API 请求配置
export const API_CONFIG = {
  // 基础 URL，开发环境走 Vite 代理，生产环境走 Nginx 反代
  BASE_URL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  // 请求超时毫秒数，默认 30000
  TIMEOUT: 30000,
} as const;
```

## 6. 禁止事项

- 禁止使用魔数，使用常量替代
- 禁止硬编码配置（URL、密钥、环境相关参数），使用环境变量（`import.meta.env`）或配置文件
- 禁止在业务代码中使用 `console.log`，使用项目封装的日志工具（见 `02-architecture-patterns.md` §6）
- 禁止使用 `any`，必须用 `unknown` + 类型守卫或具体类型
- 禁止使用 `// @ts-ignore` / `// @ts-nocheck`，必须修复类型错误
- 禁止直接操作 DOM（`document.querySelector` 等），使用 React 受控组件和 ref
- 禁止在组件内直接修改 state（必须通过 setState / dispatch）
- 禁止修改已有公共组件 Props 签名（保持向后兼容，新增可选 Props 而非修改已有）
- 禁止提交无注释的配置项
- 禁止组件/函数缺少 TSDoc 注释（private 工具函数除外，但也建议添加）
- 禁止使用 `dangerouslySetInnerHTML` 处理不可信内容（见 `03-code-quality.md` §5 XSS 防护）

## 8. React/TypeScript 前端规范

> 本节为 ai-web 项目**特有**的前端编码规范，与后端规范并列。

### 8.1 组件设计原则

- **函数组件 + Hooks**：禁止使用 Class 组件
- **单一职责**：一个组件只做一件事，超过 200 行考虑拆分
- **Props 类型必须定义 interface/type**：
  ```tsx
  interface Props {
    title: string;
    onSubmit?: (data: FormData) => void;
    loading?: boolean;
  }
  
  const MyComponent: React.FC<Props> = ({ title, onSubmit, loading }) => { ... };
  ```
- **默认 Props 使用解构 + 默认值**：
  ```tsx
  const MyComponent = ({ title = '默认标题', loading = false }: Props) => { ... };
  ```

### 8.2 Hooks 使用规范

- **useEffect 必须明确依赖数组**：
  ```tsx
  // ✅ 正确：明确依赖
  useEffect(() => {
    fetchData(id);
  }, [id]); // 依赖数组
  
  // ❌ 错误：空依赖但使用了外部变量
  useEffect(() => {
    fetchData(id); // id 变化时不会重新执行
  }, []); // 缺少依赖
  ```
- **自定义 Hook 以 use 开头**：
  ```tsx
  // ✅ 正确
  const usePolling = (interval: number) => { ... };
  
  // ❌ 错误
  const polling = (interval: number) => { ... };
  ```
- **useState 惰性初始化**：初始值如果是复杂计算，使用函数形式
  ```tsx
  // ✅ 正确：惰性初始化
  const [data, setData] = useState(() => computeInitialValue());
  
  // ❌ 错误：每次渲染都执行
  const [data, setData] = useState(computeInitialValue());
  ```
- **禁止在循环/条件中调用 Hooks**：Hooks 必须在组件顶层调用

### 8.3 状态管理（Zustand）

- **全局状态才用 Store**，组件内部状态用 useState
- **Store 按 domain 拆分**：
  ```
  stores/
  ├── auth.store.ts      # 认证状态（token, user）
  ├── user.store.ts      # 用户信息
  ├── app.store.ts       # 应用配置（侧边栏、主题）
  └── config.store.ts    # 业务配置（评测方向、被测系统）
  ```
- **Action 使用普通函数**，不使用 async/await 在 Store 外
- **选择性订阅**：`useStore(s => s.xxx)` 避免不必要的重渲染
  ```tsx
  // ✅ 正确：仅订阅 token
  const token = useAuthStore(s => s.token);
  
  // ❌ 错误：订阅整个 Store，任何字段变化都触发重渲染
  const { token, user, isLoading } = useAuthStore();
  ```

### 8.4 样式规范（CSS Modules + Sass）

- **样式文件与组件同目录**：`xxx.module.scss`
- **类名使用 camelCase**：
  ```scss
  // ✅ 正确
  .container { }
  .headerTitle { }
  
  // ❌ 错误：kebab-case 在 JS 中需要字符串访问
  .container { }
  .header-title { } 
  ```
- **SCSS 变量统一在 `variables.scss` 定义**
- **禁止全局样式污染**（除 `global.scss`）
- **响应式使用 SCSS mixin**：
  ```scss
  @mixin respond-to($breakpoint) {
    @if $breakpoint == 'tablet' {
      @media (max-width: 768px) { @content; }
    }
  }
  ```

### 8.5 Ant Design 使用约定

- **优先使用 antd 组件**，避免重复造轮子
- **自定义主题使用 ConfigProvider + token**：
  ```tsx
  <ConfigProvider
    theme={{
      token: {
        colorPrimary: '#1677ff',
      },
    }}
  >
    <App />
  </ConfigProvider>
  ```
- **表单使用 Form.Item + name 规则校验**：
  ```tsx
  <Form form={form} onFinish={handleSubmit}>
    <Form.Item name="title" rules={[{ required: true, message: '请输入标题' }]}>
      <Input />
    </Form.Item>
  </Form>
  ```
- **表格使用 columns 配置**，统一分页：
  ```tsx
  const columns: ColumnsType<DataType> = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '操作', key: 'action', render: (_, record) => <a>操作</a> },
  ];
  
  <Table
    columns={columns}
    dataSource={data}
    rowKey="id"
    pagination={{ showSizeChanger: true, showTotal: (total) => `共 ${total} 条` }}
  />
  ```

### 8.6 路由规范（React Router v6）

- **路由懒加载**：
  ```tsx
  const EvalPage = lazy(() => import('@/pages/eval/EvalPage'));
  
  <Route path="/eval" element={<Suspense fallback={<Spin />}><EvalPage /></Suspense>} />
  ```
- **路由配置集中管理**：`config/router.tsx`
- **嵌套路由使用 Outlet**：
  ```tsx
  <Route path="/eval" element={<EvalLayout />}>
    <Route index element={<EvalList />} />
    <Route path=":id" element={<EvalDetail />} />
  </Route>
  ```

### 8.7 API 调用规范

- **按业务领域拆分 Service**：
  ```
  services/
  ├── auth.service.ts     # 认证相关 API
  ├── eval.service.ts     # 评测相关 API
  ├── task.service.ts     # 任务相关 API
  ├── bug.service.ts      # Bug 管理 API
  └── note.service.ts     # 笔记相关 API
  ```
- **Service 函数返回 Promise**，错误由拦截器统一处理
- **请求参数使用接口类型**：
  ```tsx
  interface LoginParams {
    username: string;
    password: string;
  }
  
  export const login = (params: LoginParams): Promise<LoginResult> => {
    return request.post('/api/auth/login', params);
  };
  ```

### 8.8 前端禁止事项（补充）

- 禁止使用 Class 组件
- 禁止在 useEffect 中缺少依赖数组
- 禁止在循环/条件中调用 Hooks
- 禁止直接修改 props（props 是只读的）
- 禁止在 render 中创建函数/对象（导致子组件不必要的重渲染）
- 禁止使用 `any` 类型（除非确实无法确定类型）
- 禁止使用 `!` 非空断言（优先使用可选链 `?.`）
- 禁止在 JSX 中写复杂逻辑（提取为函数或 useMemo）
