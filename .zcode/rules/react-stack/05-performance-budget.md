---
alwaysApply: false
description: 性能预算规则，包括 Core Web Vitals 门槛、bundle size 限制、懒加载策略。涉及前端性能优化、构建配置时使用此规则。
---

# 性能预算（React 技术栈层）

> 前端项目必须遵守性能预算，确保用户体验。

## 1. Core Web Vitals 门槛

| 指标 | 门槛 | 说明 |
|------|------|------|
| LCP（最大内容绘制） | ≤ 2.5s | 页面主要内容加载完成时间 |
| CLS（累积布局偏移） | ≤ 0.1 | 视觉稳定性 |
| INP（交互到下一次绘制） | ≤ 200ms | 交互响应速度 |
| FCP（首次内容绘制） | ≤ 1.8s | 首次渲染时间 |
| TTFB（首字节时间） | ≤ 800ms | 服务器响应速度 |

> 超过门槛的性能回归视为 P1 bug，必须在下一个迭代修复。

## 2. Bundle Size 限制

| 资源 | 限制 | 说明 |
|------|------|------|
| 初始 JS（gzip 后） | ≤ 200KB | 首屏加载的 JS |
| 初始 CSS（gzip 后） | ≤ 50KB | 首屏加载的 CSS |
| 单个 chunk（gzip 后） | ≤ 100KB | 按需加载的 chunk |
| 总资源（首屏） | ≤ 500KB | 所有首屏资源 |

### 2.1 Bundle 监控

- CI 中使用 `vite-bundle-visualizer` 生成包大小报告
- PR 检查中标注 bundle size 变化（增减百分比）
- 超过预算时 CI 报错

### 2.2 减小 Bundle 的策略

- 路由级懒加载（`React.lazy` + `Suspense`）
- 第三方库按需引入（如 `import { Button } from 'antd'`）
- 大型库使用替代品（如 `dayjs` 替代 `moment`）
- 图片懒加载（`loading="lazy"`）
- Tree shaking（确保 `sideEffects: false` 在 package.json）

## 3. 渲染性能

### 3.1 避免不必要重渲染

- 列表项使用 `React.memo` + 稳定 `key`
- Zustand 选择性订阅（`useStore(selector)`）
- 避免在 render 中创建新对象/函数
- 使用 `useCallback` / `useMemo` 包裹传递给子组件的回调

### 3.2 长列表优化

- 超过 100 条数据的列表使用虚拟滚动（`react-window` 或 `@tanstack/react-virtual`）
- 大表格使用分页或虚拟滚动

### 3.3 组件拆分

- 单个组件函数体 ≤ 100 行
- 嵌套 ≤ 4 层，超过时提取子组件
- 单文件 ≤ 400 行

## 4. 网络优化

- API 请求并行化（`Promise.all`）
- 请求去重（相同请求在 pending 状态时复用）
- 防抖/节流高频触发的事件（搜索、滚动、resize）
- 图片使用 WebP 格式 + CDN 压缩
- 启用 HTTP/2 或 HTTP/3

## 5. 性能测试

### 5.1 自动化性能测试

- E2E 测试中集成 Lighthouse CI
- 每次 PR 自动运行性能回归检测
- 性能数据记录到 `plan/06-功能测试.md`

### 5.2 性能监控

- 生产环境集成 Web Vitals 上报
- Sentry Performance 或自建性能监控
- 性能数据按页面路由分组统计
