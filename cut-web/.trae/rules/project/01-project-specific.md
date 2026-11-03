---
alwaysApply: true
version: 2.0.0
lastUpdated: 2026-09-08
description: cut-web 项目特定规则（v2.0）。组件设计、虚拟预览器、权限路由、与后端的硬约束。
---

# cut-web 项目特定规则

> 本文档是 cut-web 的项目级硬约束，补充共享层规则的不足。
> 与共享层 + React 栈层规则**叠加生效**（冲突时以本文档为准）。

## 1. 视觉规范（强制沿用旧版）

### 1.1 CSS 变量（保留旧版）

```css
/* src/shared/styles/variables.css */
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --surface-2: #21252f;
  --surface-3: #2a2f3d;
  --border: #2d3142;
  --border-light: #3a3f52;
  --text: #e4e7ec;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;
  --primary: #7c3aed;
  --primary-hover: #8b5cf6;
  --primary-dim: #6d28d9;
  --accent: #D85A30;
  --accent-hover: #e96a3f;
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #3b82f6;
  --radius-card: 12px;
  --radius-btn: 8px;
  --radius-input: 8px;
  --shadow: 0 4px 20px rgba(0,0,0,0.3);
  --shadow-lg: 0 8px 40px rgba(0,0,0,0.4);
  --transition: 0.2s ease;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC',
               'Microsoft YaHei', sans-serif;
}
```

## 2. 旧版 UI 复刻硬清单

### 2.1 全局组件
- [ ] Header（Logo + 标题 + 连接状态 + 配置按钮）
- [ ] 步骤导航条（7 步，当前高亮，未完成置灰）
- [ ] 面板布局（标题 + 提示 + 内容区 + 操作按钮组）
- [ ] 浮动状态栏（右下角执行中提示）
- [ ] 登录卡片（深色，居中）
- [ ] Toast/Notification

### 2.2 业务组件
- [ ] 项目卡片（封面 emoji + 标题 + 作者 + 操作菜单）
- [ ] Step1 表单
- [ ] Step2 关键词卡片
- [ ] Step3 编辑器 + 大纲折叠
- [ ] Step4 音频播放器 + 视频标记可视化
- [ ] Step5 **虚拟串播预览器**（见 §3）
- [ ] Step6 裁切确认
- [ ] Step7 合成进度 + 下载

## 3. 虚拟串播预览器（核心创新·强制复刻）

> 用 `<video>` 的 `currentTime` 切换实现 0 IO 预览。

```typescript
const playVirtual = (marks: VideoMark[], audio: HTMLAudioElement) => {
  const video = videoRef.current;
  let i = 0;
  const playNext = () => {
    if (i >= marks.length) { audio.pause(); return; }
    const mark = marks[i];
    video.currentTime = mark.start;
    video.play();
    setTimeout(() => {
      video.pause();
      i++;
      playNext();
    }, (mark.end - mark.start) * 1000);
  };
  audio.play();
  playNext();
};
```

### 3.1 交互清单

- [ ] 播放/暂停
- [ ] 时间轴拖动 seek
- [ ] 片段标记可视化（点击跳转）
- [ ] 片段增删/拖拽/编辑
- [ ] 标记总时长 vs 音频时长
- [ ] 时长不匹配提示（差 ≥2s 高亮）
- [ ] 倍速切换（0.5x / 1x / 1.5x / 2x）

### 3.2 性能

- 预览启动延迟 < 200ms
- 拖拽帧率 ≥ 30fps
- 时间轴 `requestAnimationFrame`

## 4. 权限路由守卫

```typescript
const routes = [
  { path: '/login', element: <Login /> },
  { path: '/', element: <RequireAuth><Layout /></RequireAuth>, children: [
    { path: 'projects', element: <Projects /> },
    { path: 'admin', element: <RequireAdmin><AdminLayout /></RequireAdmin>, children: [
      { path: 'users', element: <UserAdmin /> },
      { path: 'memberships', element: <MembershipAdmin /> },
      { path: 'configs', element: <ConfigAdmin /> },
    ]},
  ]},
];
```

**守卫层级**：
- `<RequireAuth>`：未登录跳 `/login`
- `<RequireAdmin>`：非管理员跳 `/403`
- 资源所有权检查在组件内调后端校验

## 5. 与后端的硬约束

| 项 | 规则 |
|----|------|
| 字段命名 | 后端 snake_case 通过 codegen 转 camelCase |
| 时间格式 | 后端 ISO 8601，前端 dayjs |
| 数字 | 价格用 `string`，避免浮点 |
| 错误响应 | 拦截器解析 `code` + `msg`，业务错误 toast |
| HTTP 401 | 拦截器自动跳 `/login` 并清 token |
| HTTP 402 | 弹"配额不足"模态框，引导联系管理员升级 |
| HTTP 403 | 跳 `/403` |
| HTTP 422 | 表单字段错误高亮 |
| 分页 | `{page, pageSize, total, items}` |
| 长任务 | `useTaskPolling(taskId)` 自动轮询 |

## 6. 组件设计原则

- 单一职责
- Props 类型化（所有 Props 必须有 TS 接口）
- 可访问性：按钮 `<button>`，图标按钮 `aria-label`
- feature 级别 `ErrorBoundary` 包裹
- 每个异步组件必须有 `loading` / `error` / `empty` 三态

## 7. 状态管理（Zustand）

```typescript
interface AuthStore {
  token: string | null;
  user: User | null;
  isAdmin: boolean;
  membershipTier: 'free' | 'pro' | 'enterprise';
  setAuth: (token, user) => void;
  clear: () => void;
}
```

**禁止**把列表数据存 Store（用 `useApi` 自定义 hook）。

## 8. 管理员页面规范

- 表格用 AntD `<Table>`，必须含搜索栏 + 分页
- 改会员等级用弹窗 + 二次确认
- 操作成功后必须刷数据 + toast
- 审计日志列表按时间倒序

## 9. 性能纪律

- 首屏 chunk ≤ 250KB（gzip 前）
- 路由切换 < 500ms
- 列表 >100 行启用虚拟滚动
- 图片 `loading="lazy"`
- 字体使用系统字体

## 10. 可访问性（A11y）

- 按钮 `<button>`，图标按钮 `aria-label`
- 表单 `<label htmlFor>`，错误 `aria-describedby`
- 颜色对比度 ≥ 4.5:1（WCAG AA）
- 键盘可操作：Tab/Shift+Tab/Enter/Esc
- focus 可见（`outline: 2px solid var(--primary)`）

## 11. 旧项目交互复刻硬清单

- [ ] 步骤锁定（前步未完成后步置灰）
- [ ] 任意步骤"返回上一步"
- [ ] 每步"重新执行"按钮
- [ ] 每步进度独立 loading
- [ ] 浮动状态栏显示当前步骤
- [ ] 项目列表分页
- [ ] 项目封面 emoji 可选
- [ ] 删除项目二次确认
- [ ] 复制项目功能
- [ ] 配置弹窗（用户级）
- [ ] 配置"测试连接"按钮
- [ ] 健康检查指示器（Header ●已连接/未连接）

## 12. 测试纪律

- 组件单测：覆盖关键 props 与渲染分支
- Hook 单测
- E2E：Playwright 覆盖登录 → 7 步完整流程 → 导出
- 管理员流程 E2E 单独覆盖

## 13. 不允许的反模式

| 反模式 | 正确做法 |
|--------|---------|
| 在组件内 `useEffect` 发请求 | 用 `useApi` hook |
| 直接 `import axios` | 用 `src/shared/api/client.ts` |
| 用 CSS-in-JS 写复杂样式 | 用 CSS Modules |
| 用 `localStorage` 存 token | 用内存 Zustand |
| 手动维护路由权限 | 用 `<RequireAdmin>` 包裹 |
| 硬编码接口地址 | 用 `VITE_API_BASE_URL` |
| 用 `any` 类型 | 必须有明确 TS 类型 |
| 直接复制旧版 HTML 字符串 | 重写为 React 组件 |

## 14. 已知技术债务与决策记录

| 议题 | 决策 | 原因 |
|------|------|------|
| 状态管理 | Zustand | 轻量 |
| 组件库 | Ant Design 5 | 企业级表单/表格 |
| HTTP | axios | 拦截器生态 |
| 类型生成 | openapi-typescript | 零运行时 |
| 测试 | Vitest | 与 Vite 集成 |
| E2E | Playwright | 多浏览器 |

## 15. 阶段交付纪律

每个开发阶段结束必须：
1. `pnpm lint` 无 error
2. `pnpm tsc --noEmit` 无 error
3. `pnpm test` 覆盖率 ≥ 80%
4. `pnpm build` 成功，首屏 chunk ≤ 250KB
5. 更新 `plan/01-开发进度.md` + `plan/08-代码日志.md`
6. `CHANGELOG.md` 记录变更

---

_由 AI 起草，待用户确认定稿_