---
alwaysApply: false
description: 前端代码质量与审查规则，包括质量标准、代码审查清单、测试规范（Vitest + Playwright + 分类存放 + 时间戳输出）、性能规范、安全规范（XSS/CSRF/Token）、重构规则。进行代码审查、编写测试、性能优化、安全检查、代码重构时使用此规则。
---

# 代码质量与审查规则（通用）

> 本规范适用于所有 React + TypeScript 前端项目，可直接复制使用。

## 1. 代码质量标准

### 1.1 可读性

- 代码应该像散文一样清晰易读
- 组件函数体不超过 100 行，超过时考虑拆分子组件或抽取 Hook
- 嵌套层级不超过 4 层（JSX 嵌套也算），超过时考虑抽取子组件
- 单个文件不超过 400 行，超过时考虑拆分模块

### 1.2 可维护性

- 修改代码时，相关的测试必须同步更新
- 公共组件 Props 变更必须更新文档和类型定义
- 删除代码时确认没有其他地方依赖（用 IDE 的"查找引用"）
- 修复 Bug 时必须补充对应的回归测试

### 1.3 可测试性

- 组件通过 Props 注入依赖，避免硬编码（如直接 import Service，应通过 Props 传入或 Hook 注入）
- 副作用（API 调用、定时器、事件监听）与纯逻辑分离，纯逻辑部分必须可单元测试
- 避免在组件构造阶段（`useState` 初始化器、模块顶层）做复杂初始化或副作用
- 避免使用全局可变状态（除 Store 外）

## 2. 代码审查清单

### 2.1 必查项（P0 - 必须通过）

- [ ] 代码能正常构建（`pnpm build` 无错误），无 TypeScript 类型错误
- [ ] ESLint、Prettier 检查通过，无 warning
- [ ] 单元测试通过，覆盖率不降低
- [ ] 没有硬编码的密钥、Token、密码等敏感信息
- [ ] 没有 XSS 漏洞（`dangerouslySetInnerHTML`、未转义的用户输入）
- [ ] 异常处理正确，没有 `catch` 后静默吞掉（空 catch）
- [ ] 命名清晰，符合项目命名规范
- [ ] 没有重复代码（重复超过 3 行需要提取组件/函数）
- [ ] 所有 public 组件和函数有 TSDoc 注释（见编码规范 §5.2）
- [ ] 配置项有注释（见编码规范 §5.3）
- [ ] 没有使用 `any`、`// @ts-ignore`、`// @ts-nocheck`
- [ ] 没有在业务代码中直接使用 `console.*`

### 2.2 重要项（P1 - 尽量通过）

- [ ] 类型提示完整，Props 接口清晰
- [ ] 组件职责单一，没有"上帝组件"（一个组件干太多事）
- [ ] 没有过度设计
- [ ] 日志适当，包含 traceId，既不缺失也不冗余
- [ ] 性能考虑合理（避免不必要的重渲染、大列表未虚拟化等）
- [ ] 边界条件处理正确（空数据、加载中、错误态、超长文本）
- [ ] 分层正确（未跨层调用，组件不直接调 API）
- [ ] 列表渲染有稳定的 `key`
- [ ] 关键交互有 loading 反馈，防止重复提交

### 2.3 建议项（P2 - 可选优化）

- [ ] 代码风格一致性
- [ ] 注释清晰解释"为什么"
- [ ] 变量名可以更精准
- [ ] 可以进一步抽象复用（提取 Hook / 组件）
- [ ] 测试用例更全面
- [ ] 可访问性（a11y）：合理的 `aria-*`、键盘可操作、语义化标签

## 3. 测试规范

### 3.1 测试层级

| 层级 | 测试对象 | 工具 | 要求 |
|------|---------|------|------|
| 单元测试 | 纯函数 / 工具 / Hook | Vitest | 核心工具和 Hook 必须覆盖 |
| 组件测试 | 单个组件的渲染和交互 | Vitest + Testing Library | 业务组件必须覆盖 |
| 集成测试 | 多组件协作 / Page 级 | Vitest + Testing Library | 关键页面流程覆盖 |
| E2E 测试 | 完整业务流程（真实浏览器） | Playwright | 核心业务流程必须覆盖 |
| 视觉测试 | UI 视觉回归（可选） | Playwright 截图对比 | 关键页面可选 |

### 3.2 测试目录分类规范

测试文件**按分类存放**，每个分类对应一个子目录，避免所有测试堆在同一层级。测试文件与源码同目录（co-location）或集中存放，**项目内保持统一**。

**推荐：co-location（与源码同目录）**

```
src/
├── utils/
│   ├── date.ts
│   ├── date.test.ts               # 工具函数单测，与源码同目录
│   └── format.test.ts
├── hooks/
│   ├── useAuth.ts
│   └── useAuth.test.ts            # Hook 单测
└── components/
    └── business/
        └── UserAvatar/
            ├── UserAvatar.tsx
            └── UserAvatar.test.tsx   # 组件测试
```

**集中存放（备选方案）**：

```
tests/
├── unit/                          # 单元测试
│   ├── utils/
│   │   ├── date.test.ts
│   │   └── format.test.ts
│   ├── hooks/
│   │   └── useAuth.test.ts
│   └── services/
│       └── evalService.test.ts
├── component/                     # 组件测试
│   └── UserAvatar.test.tsx
├── integration/                   # 集成测试
│   └── eval-flow.test.tsx
└── e2e/                           # Playwright E2E 测试
    ├── auth.spec.ts
    ├── eval-list.spec.ts
    └── task-run.spec.ts
```

### 3.3 测试输出结果管理

**每个测试的输出结果按「日期+时间戳」文件夹独立存放**，避免不同次测试结果混淆。

```
tests/output/                              # 测试输出根目录
├── 20260813_103000/                       # 2026-08-13 10:30:00 的测试输出
│   ├── vitest-report.html                 # Vitest HTML 报告
│   ├── vitest-junit.xml                   # JUnit XML（CI 用）
│   ├── coverage/                          # 覆盖率报告
│   │   ├── index.html
│   │   └── ...
│   ├── playwright-report/                 # Playwright HTML 报告
│   │   └── index.html
│   ├── playwright-results/                # Playwright 测试产物（截图、视频、trace）
│   │   ├── auth-failed-payload.zip
│   │   └── video/
│   └── logs/                              # 测试期间的日志输出
│       └── test-run.log
├── 20260813_143000/                       # 同日不同时间的另一次测试
│   └── ...
└── ...
```

**实现方式：** 在 `vitest.config.ts` 和 `playwright.config.ts` 中通过环境变量注入时间戳目录，或在 `package.json` 的测试脚本中动态生成：

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import { format } from 'date-fns';

const timestamp = format(new Date(), 'yyyyMMdd_HHmmss');
const outputDir = `tests/output/${timestamp}`;

export default defineConfig({
  test: {
    coverage: {
      reporter: ['html', 'text', 'junit'],
      reportsDirectory: `${outputDir}/coverage`,
    },
    reporters: ['default', ['junit', { outputFile: `${outputDir}/vitest-junit.xml` }]],
  },
});
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';
import { format } from 'date-fns';

const timestamp = format(new Date(), 'yyyyMMdd_HHmmss');

export default defineConfig({
  reporter: [['html', { outputFolder: `tests/output/${timestamp}/playwright-report` }]],
  outputDir: `tests/output/${timestamp}/playwright-results`,
  use: {
    trace: 'on-first-retry',          // 首次重试时录制 trace
    screenshot: 'only-on-failure',    // 失败时截图
    video: 'retain-on-failure',       // 失败时保留视频
  },
});
```

### 3.4 单元测试要求

- 测试文件与源文件对应：`xxx.ts` → `xxx.test.ts`（co-location）或镜像目录结构
- 测试文件命名：`<module_name>.test.ts` / `<module_name>.spec.ts`
- 测试函数命名：`test('<场景>，<预期结果>', () => {})`
- 每个测试函数只验证一个场景
- 使用 `describe` 按模块组织，`it`/`test` 描述具体场景

**示例（工具函数测试）：**
```typescript
// src/utils/date.test.ts
import { describe, it, expect } from 'vitest';
import { formatDate } from './date';

describe('formatDate', () => {
  it('传入 ISO 字符串，应返回 YYYY-MM-DD 格式', () => {
    expect(formatDate('2026-08-13T10:30:00Z')).toBe('2026-08-13');
  });

  it('传入空字符串，应返回空字符串', () => {
    expect(formatDate('')).toBe('');
  });
});
```

**示例（Hook 测试）：**
```typescript
// src/hooks/useAuth.test.ts
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { useAuth } from './useAuth';

describe('useAuth', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('登录成功后，应更新用户状态并持久化 Token', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login('admin', 'password');
    });

    expect(result.current.user?.username).toBe('admin');
    expect(localStorage.getItem('token')).toBeTruthy();
  });
});
```

**示例（组件测试）：**
```typescript
// src/components/business/UserAvatar/UserAvatar.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { UserAvatar } from './UserAvatar';

describe('UserAvatar', () => {
  it('传入用户名，应显示首字母大写的头像', () => {
    render(<UserAvatar username="alice" />);
    expect(screen.getByText('A')).toBeInTheDocument();
  });

  it('未传入用户名，应显示默认占位', () => {
    render(<UserAvatar username="" />);
    expect(screen.getByText('U')).toBeInTheDocument();
  });
});
```

### 3.5 E2E 测试要求（Playwright）

> **Playwright 为本项目浏览器验证的唯一基础条件（必备，非可选）**：
> 1. 所有浏览器侧验证（页面渲染、交互行为、路由流转、视觉截图）必须通过 Playwright 脚本（`tests/e2e/`）执行
> 2. 日常任务开发**不启动浏览器**；E2E 测试统一在项目开发结束（INTEGRATION 阶段）集中编写并执行（见 `plan/06-功能测试.md` 12 个关键流程）
> 3. **禁止使用 browser_use 等临时浏览器自动化**替代 Playwright（耗时长、不可重复）
> 4. 单测（Vitest）与 E2E（Playwright）职责分离：单测覆盖纯逻辑/组件渲染，E2E 覆盖核心业务流程，E2E 不要求覆盖率

- 测试文件放在 `tests/e2e/` 目录，命名 `<feature>.spec.ts`
- 测试覆盖核心业务流程：登录、评测创建、任务执行、历史查询、报告查看
- 优先用 `data-testid` 或角色定位元素，避免用 CSS 选择器（脆弱）
- 每个测试独立，可重复执行（测试间不依赖共享状态）
- 运行方式：`pnpm test:e2e`（脚本见 `package.json`，输出按 `plan/06-功能测试.md` §1.4 时间戳归档）

```typescript
// tests/e2e/eval-list.spec.ts
import { test, expect } from '@playwright/test';

test.describe('评测列表', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="username"]', 'admin');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="login-btn"]');
    await page.waitForURL('/eval');
  });

  test('进入评测列表，应显示套件数据', async ({ page }) => {
    await expect(page.locator('[data-testid="eval-table"]')).toBeVisible();
    await expect(page.locator('text=评测套件').first()).toBeVisible();
  });

  test('点击新建按钮，应跳转到新建页面', async ({ page }) => {
    await page.click('[data-testid="create-eval-btn"]');
    await expect(page).toHaveURL(/\/eval\/create/);
  });
});
```

### 3.6 测试覆盖率

- 核心业务代码（utils、hooks、services）覆盖率 ≥ 80%
- 基础组件覆盖率 ≥ 90%
- 新增代码覆盖率必须 ≥ 80%
- 不追求 100% 覆盖率，但关键路径必须覆盖
- E2E 覆盖核心业务流程，不要求覆盖率

### 3.7 测试原则

- 测试应该快速、独立、可重复
- 使用 `beforeEach` / `afterEach` 共享测试数据和 setup/teardown
- 避免测试之间互相依赖
- Mock 外部依赖（API 请求、`localStorage`、定时器、`Date`）
- 测试数据应该具有代表性，覆盖边界情况（空数据、超长文本、特殊字符）
- 测试输出不互相覆盖，每次运行结果可追溯
- **测试行为而非实现**：不要断言组件内部 state 或私有方法，只断言可观察的输出

## 4. 性能规范

### 4.1 渲染性能

- 避免在 render 中做重计算，用 `useMemo` / `useCallback` 记忆化
- 大列表（> 100 项）使用虚拟滚动（`react-window` / `ahooks` 的 `useVirtualList`）
- 避免不必要的重渲染：`React.memo` 包装纯展示组件，Props 用 `useMemo` 稳定引用
- 避免 inline 函数和对象作为 Props（每次 render 都是新引用，破坏 `memo`）
- 复杂表单使用非受控或分片更新，避免每次按键触发全表单重渲染

### 4.2 网络性能

- 接口请求按需触发，避免在多个组件中重复请求同一接口（用缓存或状态提升）
- 列表分页加载，避免一次性请求全量数据
- 图片懒加载（`loading="lazy"`）和合理尺寸（不请求过大图）
- 防抖（`debounce`）和节流（`throttle`）高频触发的事件（搜索输入、滚动、resize）
- 使用请求取消（AbortController）避免竞态（快速切换页面时的旧请求覆盖新请求）

### 4.3 包体积

- 按路由懒加载（`React.lazy` + `Suspense`），首屏只加载必要代码
- 监控构建产物体积，单 chunk 超过 250KB 需警示
- 第三方库按需引入（`import { Button } from 'antd'` 而非 `import * from 'antd'`）
- 大型库（如 ECharts、moment）考虑替换为轻量替代（ECharts 按需引入、dayjs）
- Tree-shaking 友好：避免 `export default` 整个对象、避免副作用模块

### 4.4 首屏性能

- 关键 CSS 内联，非关键 CSS 异步加载
- 字体使用 `font-display: swap`，避免 FOIT
- 路由预加载（用户 hover 菜单时预加载目标页面）
- 接口预加载（关键接口在路由切换前发起）
- 生产环境必须开启 gzip/brotli 压缩

### 4.5 内存使用

- 及时清理副作用（`useEffect` 返回清理函数，取消订阅、清除定时器）
- 避免闭包持有大对象引用，导致内存泄漏
- 大数据集分页加载，不一次性全部加载到内存
- 切换页面时取消未完成的请求，避免内存堆积

## 5. 安全规范

> 涉及安全相关代码时必须遵守本节全部规则。

### 5.1 XSS 防护（跨站脚本攻击）

- **禁止使用 `dangerouslySetInnerHTML` 处理不可信内容**，如必须使用，先经 DOMPurify 清洗
- React 默认转义 JSX 插值内容，**不要绕过**（如拼接 HTML 字符串后插入）
- 用户输入展示前做转义（特别是富文本、URL、HTML 属性值）
- URL 跳转校验协议白名单（只允许 `http`/`https`，禁止 `javascript:`）

```typescript
// 正确：React 自动转义
<div>{userInput}</div>

// 正确：富文本先清洗
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(richText) }} />

// 错误：直接插入未清洗内容
<div dangerouslySetInnerHTML={{ __html: userInput }} />  // 禁止
```

### 5.2 CSRF 防护（跨站请求伪造）

- 状态变更接口（POST/PUT/DELETE）的 CSRF 防护以服务端校验为准，前端不自行实现校验逻辑
- 前端配合后端方案：若用 Token 模式，请求头携带 `X-CSRF-Token`
- 敏感操作（删除、支付）加二次确认（弹窗 / 验证码）

### 5.3 Token 与认证管理

- **Token 存储优先级**：内存（Store）> sessionStorage > localStorage > Cookie
- 推荐：Token 存内存 Store，刷新 Token 存 sessionStorage（关闭标签页即失效）
- **禁止把 Token 存 localStorage**（易受 XSS 攻击窃取），除非有明确风险接受
- Token 通过 axios 请求拦截器统一注入 `Authorization: Bearer <token>`
- Token 过期处理：响应拦截器捕获 401，自动刷新或跳转登录页
- 用户登出时**必须清除所有存储的 Token 和用户信息**

```typescript
// 推荐：Token 存内存，刷新 Token 存 sessionStorage
const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,                    // 内存，刷新页面后需用 refreshToken 重新换取
      refreshToken: null,             // 持久化到 sessionStorage
      // ...
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({ refreshToken: state.refreshToken }),
    },
  ),
);
```

### 5.4 敏感信息管理

- **禁止硬编码密钥**：API Key、第三方 SDK 密钥等不得写在前端代码（前端是公开的）
- 环境变量中的非敏感配置（API 地址、应用名）可用 `VITE_` 前缀，敏感信息走后端代理
- 日志中敏感信息必须脱敏（Token 只显示前 4 位 + `***`）
- `.env` 文件不提交到 Git（已在 `.gitignore` 中排除）

```typescript
// 正确：非敏感配置走环境变量
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// 错误：硬编码密钥
const API_KEY = 'sk-xxxxxxxxxxxx';  // 禁止：前端代码可被任何人查看

// 日志脱敏
logger.info('auth', `Token: ${token.slice(0, 4)}***`);
```

### 5.5 文件上传安全

- 校验扩展名白名单 + MIME 类型 + 文件大小（默认 10MB）
- 文件名必须 sanitize（去除路径分隔符、特殊字符），防止路径穿越
- 前端文件类型校验仅作体验优化，不作为安全依赖，最终以服务端校验为准
- 大文件上传支持分片、断点续传

### 5.6 路由与权限控制

- 路由守卫：未登录访问受保护路由，重定向到登录页并记录回跳地址
- 权限路由：根据用户角色动态渲染菜单和路由（前端控制）
- **重要**：前端权限控制只是体验优化，**所有权限校验必须在后端再做一次**（前端可被绕过）
- 菜单隐藏不等于接口权限，用户可能直接访问 URL 或调用 API

### 5.7 其他安全规则

- 依赖定期更新，修复已知漏洞（`pnpm audit`）
- 生产环境关闭 sourcemap 上传到公网（或加密 sourcemap）
- 生产环境关闭 React DevTools 提示
- 第三方 SDK 加载需校验完整性（SRI）
- 跨域请求配置 CORS 白名单，禁止 `Access-Control-Allow-Origin: *` 配合凭证

## 6. 重构规则

### 6.1 重构时机

- 三次重复：相同逻辑出现第三次时必须重构（提取组件 / Hook / 工具函数）
- 需求变化：现有结构无法优雅支撑新需求时
- Bug 修复：为修复 Bug 而导致代码混乱时
- 代码审查：审查中提出的结构性问题

### 6.2 重构原则

- 重构前确保有测试覆盖（无测试先补测试再重构）
- 小步重构，每步都可构建可验证（`pnpm build` + `pnpm test`）
- 重构不改变外部行为（组件 Props、Hook 返回值保持兼容）
- 重构后运行完整测试套件 + 手动验证关键流程

### 6.3 常见坏味道

- 重复 JSX → 提取组件
- 重复业务逻辑 → 提取 Hook
- 长组件（> 200 行）→ 拆分子组件 + Hook
- 多个组件共享状态逻辑 → 提取自定义 Hook
- Props 透传超过 2 层 → 考虑 Context 或状态提升
- 霰弹式修改（改一个需求要动多个文件）→ 调整职责边界
- 发散式变化（一个文件因不同需求反复修改）→ 拆分关注点
- 过度 Props（一个组件接收 10+ Props）→ 拆分组件或用组合模式
