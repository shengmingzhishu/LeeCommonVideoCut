---
name: vercel-react-best-practices
description: "Vercel 官方 React/Next.js 最佳实践。57 条规则分 8 大类，按影响优先级排序：消除请求瀑布流(CRITICAL)/包体积优化(CRITICAL)/服务端性能(HIGH)/客户端数据获取(HIGH)/重渲染优化(MEDIUM)/渲染性能(MEDIUM)/JS 性能(LOW-MEDIUM)/高级模式(LOW)。适用：编写新组件、数据获取、Review 代码、优化性能。"
---

# Vercel React Best Practices

Comprehensive performance optimization guide for React and Next.js applications, maintained by Vercel. Contains 57 rules across 8 categories, prioritized by impact to guide automated refactoring and code generation.

## When to Apply

Reference these guidelines when:
- Writing new React components or Next.js pages
- Implementing data fetching (client or server-side)
- Reviewing code for performance issues
- Refactoring existing React/Next.js code
- Optimizing bundle size or load times

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|---|---|---|---|
| 1 | Eliminating Waterfalls | CRITICAL | `async-` |
| 2 | Bundle Size Optimization | CRITICAL | `bundle-` |
| 3 | Server-Side Performance | HIGH | `server-` |
| 4 | Client-Side Data Fetching | MEDIUM-HIGH | `client-` |
| 5 | Re-render Optimization | MEDIUM | `rerender-` |
| 6 | Rendering Performance | MEDIUM | `rendering-` |
| 7 | JavaScript Performance | LOW-MEDIUM | `js-` |
| 8 | Advanced Patterns | LOW | `advanced-` |

## Quick Reference

### 1. Eliminating Waterfalls (CRITICAL)

- **async-defer-await** — Move `await` into branches where actually used
- **async-parallel** — Use `Promise.all()` for independent operations
- **async-dependencies** — Use `better-all` for partial dependencies
- **async-api-routes** — Start promises early, await late in API routes
- **async-suspense-boundaries** — Use Suspense to stream content

### 2. Bundle Size Optimization (CRITICAL)

- **bundle-barrel-imports** — Import directly, avoid barrel files
- **bundle-dynamic-imports** — Use `next/dynamic` for heavy components
- **bundle-defer-third-party** — Load analytics/logging after hydration
- **bundle-conditional** — Load modules only when feature is activated
- **bundle-preload** — Preload on hover/focus for perceived speed

### 3. Server-Side Performance (HIGH)

- **server-auth-actions** — Authenticate server actions like API routes
- **server-cache-react** — Use `React.cache()` for per-request deduplication
- **server-cache-lru** — Use LRU cache for cross-request caching
- **server-dedup-props** — Avoid duplicate serialization in RSC props
- **server-serialization** — Minimize data passed to client components
- **server-parallel-fetching** — Restructure components to parallelize fetches
- **server-after-nonblocking** — Use `after()` for non-blocking operations

### 4. Client-Side Data Fetching (MEDIUM-HIGH)

- **client-swr-dedup** — Use SWR for automatic request deduplication
- **client-event-listeners** — Deduplicate global event listeners
- **client-passive-event-listeners** — Use passive listeners for scroll
- **client-localstorage-schema** — Version and minimize localStorage data

### 5. Re-render Optimization (MEDIUM)

- **rerender-defer-reads** — Don't subscribe to state only used in callbacks
- **rerender-memo** — Extract expensive work into memoized components
- **rerender-memo-with-default-value** — Hoist default non-primitive props
- **rerender-dependencies** — Use primitive dependencies in effects
- **rerender-derived-state** — Subscribe to derived booleans, not raw values
- **rerender-derived-state-no-effect** — Derive state during render, not effects
- **rerender-functional-setstate** — Use functional setState for stable callbacks
- **rerender-lazy-state-init** — Pass function to useState for expensive values
- **rerender-simple-expression-in-memo** — Avoid memo for simple primitives
- **rerender-move-effect-to-event** — Put interaction logic in event handlers
- **rerender-transitions** — Use `startTransition` for non-urgent updates
- **rerender-use-ref-transient-values** — Use refs for transient frequent values

### 6. Rendering Performance (MEDIUM)

- **rendering-animate-svg-wrapper** — Animate div wrapper, not SVG element
- **rendering-content-visibility** — Use `content-visibility` for long lists
- **rendering-hoist-jsx** — Extract static JSX outside components
- **rendering-svg-precision** — Reduce SVG coordinate precision
- **rendering-hydration-no-flicker** — Use inline script for client-only data
- **rendering-hydration-suppress-warning** — Suppress expected mismatches
- **rendering-activity** — Use Activity component for show/hide
- **rendering-conditional-render** — Use ternary, not `&&` for conditionals
- **rendering-usetransition-loading** — Prefer useTransition for loading state

### 7. JavaScript Performance (LOW-MEDIUM)

- **js-batch-dom-css** — Group CSS changes via classes or cssText
- **js-index-maps** — Build Map for repeated lookups
- **js-cache-property-access** — Cache object properties in loops
- **js-cache-function-results** — Cache function results in module-level Map
- **js-cache-storage** — Cache localStorage/sessionStorage reads
- **js-combine-iterations** — Combine multiple filter/map into one loop
- **js-length-check-first** — Check array length before expensive comparison
- **js-early-exit** — Return early from functions
- **js-hoist-regexp** — Hoist RegExp creation outside loops
- **js-min-max-loop** — Use loop for min/max instead of sort
- **js-set-map-lookups** — Use Set/Map for O(1) lookups
- **js-tosorted-immutable** — Use `toSorted()` for immutability

### 8. Advanced Patterns (LOW)

- **advanced-event-handler-refs** — Store event handlers in refs
- **advanced-init-once** — Initialize app once per app load
- **advanced-use-latest** — `useLatest` for stable callback refs

## How to Use

Read individual rule files for detailed explanations and code examples. Each rule file contains:
- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and references

---

## 适用性说明（ai-eval-web 项目）

> **重要**：本技能主要针对 **Next.js** 框架。本项目使用 **Vite + React 18 + SPA**，需注意以下适用性差异。

### ✅ 适用于本项目（Vite + React 18）的规则

| 类别 | 规则前缀 | 说明 |
|------|---------|------|
| **包体积优化 (CRITICAL)** | `bundle-*` | 全部适用：动态导入、条件加载、预加载 |
| **重渲染优化 (MEDIUM)** | `rerender-*` | 全部适用：memo、useMemo、useCallback、依赖优化 |
| **渲染性能 (MEDIUM)** | `rendering-*` | 大部分适用：content-visibility、JSX 提取、条件渲染 |
| **JS 性能 (LOW-MEDIUM)** | `js-*` | 全部适用：缓存、早期退出、循环优化 |
| **客户端数据获取** | `client-swr-dedup` | 部分适用：SWR 可用，但项目使用 axios + 自定义 Hook |

### ❌ 不适用于本项目（Next.js 专属）的规则

| 类别 | 规则前缀 | 原因 |
|------|---------|------|
| **消除请求瀑布流** | `async-*` | 大部分针对 Server Components / API Routes |
| **服务端性能 (HIGH)** | `server-*` | 全部针对 Next.js RSC / Server Actions / App Router |
| **高级模式 (LOW)** | `advanced-*` | 部分针对 Next.js 特有模式 |

### 📝 使用建议

1. **优先参考**：`bundle-*`、`rerender-*`、`js-*` 类规则
2. **谨慎参考**：`async-*`、`rendering-*` 中与 hydration 相关的规则
3. **忽略**：`server-*` 全部规则（本项目无服务端渲染）
4. **替代方案**：
   - 数据获取：使用 `axios` + 自定义 `useRequest` Hook（替代 SWR）
   - 路由懒加载：使用 `React.lazy()` + `Suspense`（替代 `next/dynamic`）
   - 代码分割：Vite 自动处理（无需手动配置）
