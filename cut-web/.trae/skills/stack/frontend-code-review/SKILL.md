---
name: frontend-code-review
version: 1.0.0
description: 前端代码审查。组件/hooks/性能/可访问性审查，产出结构化审查报告。PR 审查、代码质量检查时使用。
---

# 前端代码审查技能

## 定位

系统化审查前端代码（React/TypeScript），聚焦组件设计、Hook 使用、性能、可访问性。

## 审查维度

### 1. 正确性（P0）

- [ ] 组件逻辑正确，边界条件已处理
- [ ] useEffect 依赖数组完整且正确
- [ ] 异步操作有 loading/error 状态处理
- [ ] 表单校验规则完整（前端校验 + 后端校验）
- [ ] 路由权限守卫正确
- [ ] 错误边界（ErrorBoundary）已配置

### 2. 类型安全（P0）

- [ ] 无 `any` 类型（使用 `unknown` + 类型守卫替代）
- [ ] API 响应类型与后端 OpenAPI 一致
- [ ] Props 类型完整定义（`interface` + TSDoc）
- [ ] 枚举值与后端定义对齐
- [ ] `tsc --noEmit` 无错误

### 3. 组件设计（P1）

- [ ] 组件职责单一（单一关注点）
- [ ] 组件函数体 ≤ 100 行
- [ ] 嵌套 ≤ 4 层
- [ ] 单文件 ≤ 400 行
- [ ] Props 数量 ≤ 5 个（超过考虑使用配置对象）
- [ ] 组合优于继承
- [ ] 状态提升合理（不需要过度提升）

### 4. Hook 使用（P1）

- [ ] 自定义 Hook 以 `use` 开头
- [ ] Hook 不在条件/循环中调用
- [ ] useState 初始化惰性计算（`useState(() => initFn())`）
- [ ] useEffect 清理函数正确返回
- [ ] 自定义 Hook 有独立测试
- [ ] Hook 依赖数组无遗漏

### 5. 性能（P1）

- [ ] 列表项有稳定且唯一的 `key`
- [ ] 大列表使用虚拟滚动（> 100 条）
- [ ] 昂贵计算用 `useMemo` 缓存
- [ ] 回调函数用 `useCallback` 包裹（传给子组件时）
- [ ] 路由级懒加载（`React.lazy`）
- [ ] 图片懒加载（`loading="lazy"`）
- [ ] 无不必要的重渲染（`React.memo` + 选择性订阅）

### 6. 状态管理（P1）

- [ ] 全局状态使用 Zustand（非 Context 过度使用）
- [ ] Store 按领域拆分
- [ ] 选择性订阅（`useStore(selector)`）避免全局重渲染
- [ ] 派生状态用 selector 计算，不用 useEffect 同步
- [ ] 服务端状态与客户端状态分离

### 7. 可访问性（P2）

- [ ] 语义化 HTML 标签
- [ ] 所有图片有 `alt` 属性
- [ ] 表单 label 关联控件
- [ ] 键盘可操作（Tab/Esc/Enter/Arrow）
- [ ] 焦点管理正确（Modal 打开/关闭）
- [ ] 颜色对比度 ≥ 4.5:1
- [ ] 无 `outline: none`（或有替代 focus 样式）

### 8. 样式（P2）

- [ ] CSS Modules + Sass（无全局样式污染）
- [ ] 类名 camelCase
- [ ] 响应式设计（移动端适配）
- [ ] 主题变量使用 `variables.scss`
- [ ] antd 组件通过 ConfigProvider 定制主题

### 9. 安全（P0）

- [ ] 无 `dangerouslySetInnerHTML`（除非经 DOMPurify 清洗）
- [ ] 无 XSS 风险
- [ ] 敏感信息不在 localStorage 中明文存储
- [ ] Token 刷新机制安全
- [ ] 无密钥泄露（前端不应包含任何密钥）

## 审查报告模板

```markdown
## 代码审查报告 - [日期]

### 审查范围
- PR: #[number]
- 文件: [文件列表]

### 审查结果

| 维度 | 通过 | 问题数 | 说明 |
|------|------|--------|------|
| 正确性 | ✅ | 0 | — |
| 类型安全 | ✅ | 0 | — |
| 组件设计 | ⚠️ | 2 | 见下方问题 1-2 |
| 性能 | ⚠️ | 1 | 见下方问题 3 |
| 可访问性 | ✅ | 0 | — |

### 问题清单

#### 问题 1 [P1 - 组件设计]
- **文件**: `src/pages/eval/EvalListPage/index.tsx`
- **描述**: 组件函数体 150 行，超过 100 行限制
- **建议**: 提取 `EvalTable` 和 `EvalFilter` 子组件

#### 问题 2 [P2 - 组件设计]
- **文件**: `src/components/Basic/Button/index.tsx`
- **描述**: Props 数量 7 个，超过建议数量
- **建议**: 将 `size` 和 `variant` 合并为 `config` 对象

#### 问题 3 [P1 - 性能]
- **文件**: `src/pages/eval/EvalListPage/index.tsx`
- **描述**: 列表渲染未使用虚拟滚动（200+ 条数据）
- **建议**: 使用 `@tanstack/react-virtual`

### 总结
- **通过**: 7/9 维度
- **需修复**: 3 个问题（2 个 P1，1 个 P2）
- **结论**: 修复 P1 问题后可合并
```
