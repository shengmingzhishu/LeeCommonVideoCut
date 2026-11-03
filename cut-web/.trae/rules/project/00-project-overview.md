---
alwaysApply: true
version: 2.0.0
lastUpdated: 2026-09-08
description: cut-web 项目概述（v2.0 重写）。基于旧漫剧剪辑工具 `static/index.html` 重写为 React 前端，UI/交互 100% 复刻，新增登录注册 + 个人中心 + 会员中心 + 管理员后台。
---

# cut-web 项目概述

> 本文档是 cut-web（漫剧剪辑师前端）的定制规则，仅适用于本项目。
> v2.0 重写原因：v1.0 误加股票/关注功能，已删除重写。

## 项目名称

**cut-web** — 漫剧推广素材剪辑师前端（前后端分离 · React）

## 项目目标

为 cut-server 提供 Web 前端界面，UI/交互 100% 复刻旧版 `AI漫剧剪辑师旧参考项目代码/static/index.html`，并补齐：

- 用户注册/登录/个人中心
- 7 步向导（与旧版视觉一致）
- 虚拟串播预览器（保留核心交互）
- 会员中心
- 管理员后台
- 沿用旧版深色主题

**本前端无股票、关注、社交功能**。

## 技术栈

| 类别 | 技术选型 | 说明 |
|------|---------|------|
| 编程语言 | TypeScript 5+ | strict 模式 |
| UI 框架 | React 18 | 函数组件 + Hooks |
| 构建工具 | Vite 5 | |
| UI 组件库 | Ant Design 5 | 旧版 CSS 变量作 token 覆盖 |
| 路由 | React Router v6 | 声明式 + 懒加载 |
| 状态管理 | Zustand | 轻量全局状态 |
| HTTP 客户端 | axios + 拦截器 | 注入 traceId、token |
| 样式 | CSS Modules + Sass | 沿用旧版 CSS 变量 |
| 包管理 | pnpm 9+ | |
| 代码规范 | ESLint + Prettier + tsc | strict |
| 单元测试 | Vitest + @testing-library/react | |
| E2E 测试 | Playwright | |

## 项目范围

### A. 核心页面（旧 `static/index.html` · 100% 复刻）

| 旧版页面 | 新版路由 | 复刻要点 |
|---------|---------|---------|
| 登录页 | `/login` | 深色卡片、表单校验 |
| 项目列表页 | `/projects` | 卡片网格 + 封面 emoji + 新建/编辑/删除弹窗 |
| Step1~7 面板 | `/creations/:id/step[1-7]` | 沿用旧版交互 |
| Step5 虚拟预览 | `/creations/:id/preview` | **核心创新·强制复刻** |
| 配置弹窗 | 全局 Modal | API Key、TTS 引擎等 |

### B. 新增页面（v4.0 重写新增）

| 路由 | 功能 | 说明 |
|------|------|------|
| `/register` | 注册 | 表单 + 密码强度 |
| `/profile` | 个人中心 | 头像、昵称、简介 |
| `/profile/password` | 修改密码 | |
| `/profile/membership` | 会员中心 | 当前等级、配额使用 |
| `/admin/users` | 管理员-用户管理 | 列表、改密码、改会员、停用 |
| `/admin/memberships` | 管理员-会员分配 | 开/续/停 |
| `/admin/configs` | 管理员-全局配置 | |
| `/admin/audit-logs` | 管理员-操作审计 | |
| `/403` | 无权限页 | |
| `/404` | 404 页 | |

### 显式排除（NOT in scope）

- ❌ 股票行情 / 自选股 / K 线
- ❌ 关注 / 粉丝 / 动态流
- ❌ 公开用户主页 / 评论 / 点赞
- ❌ 邮件订阅 / 消息推送

## 项目目录结构（feature-based）

```
cut-web/src/
├── app/
│   ├── App.tsx
│   ├── router.tsx             # 路由 + 守卫
│   └── providers/             # 全局 Provider
├── features/                  # 业务功能模块
│   ├── auth/                  # 登录/注册
│   ├── profile/               # 个人中心
│   ├── membership/            # 会员中心
│   ├── projects/
│   ├── episodes/
│   ├── creations/
│   │   ├── step1/ ~ step7/
│   │   └── preview/           # 虚拟预览器子模块
│   ├── tasks/                 # 任务轮询
│   ├── files/
│   ├── configs/               # 配置弹窗
│   └── admin/                 # 管理员后台
├── shared/
│   ├── components/            # 基础组件
│   ├── hooks/                 # useAuth / useTask / useApi
│   ├── api/
│   │   ├── client.ts          # axios + 拦截器
│   │   └── types/             # 从 openapi.yaml 生成
│   ├── store/                 # Zustand stores
│   ├── styles/                # 全局 CSS 变量（沿用旧版）
│   └── utils/
└── pages/                     # 路由入口（薄壳）
```

## 关键约束

1. **API 类型由契约生成**：禁止手写接口类型
2. **字段命名 camelCase**：后端 snake_case 通过 codegen 转
3. **视觉 1:1**：旧版 CSS 变量作 AntD token 覆盖基础
4. **路由懒加载**：所有 feature 路由 `React.lazy()`
5. **管理员路由守卫**：`<RequireAdmin>` 包裹，非管理员跳 `/403`
6. **Token 安全**：accessToken 内存态，refreshToken v4.0 暂用 sessionStorage
7. **traceId 传递**：所有 axios 请求注入 `X-Trace-Id`
8. **虚拟预览器保留**：Step5 复用旧版 `currentTime` 切换逻辑
9. **可访问性**：键盘导航、ARIA 属性、focus 管理

## 视觉规范（沿用旧版）

```css
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --surface-2: #21252f;
  --primary: #7c3aed;
  --accent: #D85A30;
  --text: #e4e7ec;
  --text-secondary: #9ca3af;
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --radius-card: 12px;
  --radius-btn: 8px;
  --shadow: 0 4px 20px rgba(0,0,0,0.3);
}
```

字体：`-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif`

## Ant Design 主题 Token 覆盖

```typescript
export const antdTheme = {
  token: {
    colorPrimary: '#7c3aed',
    colorBgBase: '#0f1117',
    colorTextBase: '#e4e7ec',
    borderRadius: 8,
  },
  components: {
    Button: { colorPrimary: '#7c3aed' },
    Layout: { headerBg: '#1a1d27', bodyBg: '#0f1117' },
  },
};
```

## 与后端协作约定

- 后端服务：`cut-server`（FastAPI + PostgreSQL）
- 接口契约：后端 `docs/openapi.yaml` → 前端 `pnpm gen:api` 生成类型
- 鉴权：JWT Bearer Token，axios 拦截器自动注入
- 统一响应：`{code, msg, data, traceId}`
- 错误处理：业务错误 toast；HTTP 401 → 跳登录；HTTP 402 → 弹配额不足；HTTP 403 → 跳 `/403`
- 跨域：开发走 Vite proxy，生产走 Nginx 反代

## 启动与运行

```bash
pnpm install
pnpm gen:api     # 从 OpenAPI 生成 TS 类型
pnpm dev         # http://localhost:5173
pnpm build
```

## 环境变量

```
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=漫剧推广素材剪辑师
```

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 2.0.0 | 2026-09-08 | 重写。删除股票/关注/完整RBAC相关页面 |
| 1.0.0 | 2026-09-08 | 初版（已被 2.0 取代） |

---

_由 AI 起草，待用户确认定稿_