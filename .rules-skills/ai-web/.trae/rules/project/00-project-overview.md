---
alwaysApply: true
version: 2.0.0
lastUpdated: 2026-09-03
:description: ai-web 前端项目概述（v2.0），包括项目目标、技术栈、功能范围（登录/评测管理/计划管理/任务管理/历史记录/报告查看/文件导入/M10智能笔记/M11 Bug管理/M12参考图例/Dashboard/上下文检索/用户管理/用例调试）和关键约束。了解项目背景、制定技术方案、评估需求时使用此规则。
---
# 项目概述

> 本文档是 ai-web 项目的定制规则，仅适用于本项目。
>
> **v2.0 更新 (2026-09-03)**：同步最新代码状态，新增 M12 参考图例、用户管理、用例调试模块；移除已废弃的 historyService/contextService 引用；更新服务层清单。

## 项目名称

ai-web（AI 测评系统 Web 前端）

## 项目目标

为 AI 测评系统（ai-server）提供 Web 前端界面，支持：
- 用户登录与权限管理界面
- 评测套件与用例的可视化管理（创建、编辑、删除、查看）
- 评测计划的创建与管理
- 评测任务的创建、执行、进度查看与结果展示
- 多测试方向（文本问答、SQL 正确性、RAG 评分）的差异化展示
- 历史测试记录查询、复测、结果对比
- 多维度评测报告可视化（图表、雷达图、趋势分析）
- 测试数据多方式接入（文件导入、页面表单录入）
- 被测系统配置的可视化管理

## 技术栈

| 类别 | 技术选型 | 说明 |
|------|---------|------|
| 编程语言 | TypeScript 5+ | 强类型，配合 strict 模式 |
| UI 框架 | React 18 | 函数组件 + Hooks |
| 构建工具 | Vite 5 | 极速冷启动 + HMR |
| UI 组件库 | Ant Design 5 | 企业级后台组件 |
| 路由 | React Router v6 | 声明式路由 + 懒加载 |
| 状态管理 | Zustand | 轻量全局状态（用户、权限、应用配置） |
| HTTP 客户端 | axios | 拦截器统一处理 Token、错误、traceId |
| 样式方案 | CSS Modules + Sass | 局部作用域 + 全局变量 |
| 图表库 | ECharts（按需引入） | 评测结果可视化 |
| 包管理 | pnpm 9+ | 性能与磁盘占用优化 |
| 代码规范 | ESLint + Prettier + TypeScript strict | 统一代码风格 |
| 单元测试 | Vitest + @testing-library/react | Vite 原生单测 |
| E2E 测试 | Playwright | 跨浏览器端到端测试 |
| 错误监控 | Sentry（可选） | 生产环境错误上报 |

## 项目范围

### 核心功能

1. **用户认证界面**
   - 登录页（用户名/密码）
   - Token 管理（存储、自动刷新、过期跳转登录）
   - 路由守卫（未登录重定向、权限路由控制）
   - 用户信息展示与登出
   - M10 共享 Token 管理（管理员视角）

2. **评测管理界面**
   - 评测套件列表（分页、筛选、搜索）
   - 评测套件详情（用例列表、配置查看）
   - 评测用例创建/编辑表单（按方向差异化字段：text/image/video）
   - 测试集管理（创建、编辑、删除、批量操作）
   - Debug 调试执行（配置验证、保存配置、执行、停止）
   - 提示词预设管理（CRUD、变量替换）
   - 参考图片管理（上传、关联用例、批量删除）

3. **计划管理界面**（v0.10 新增）
   - 计划列表与详情
   - 用例分配到计划
   - 计划执行状态跟踪

4. **任务管理界面**
   - 任务列表（状态、进度、创建时间筛选）
   - 创建评测任务（选择套件、用例、被测系统）
   - 任务详情（实时进度、用例执行状态、日志查看）
   - 任务状态轮询（pending/running/completed/failed/cancelled）
   - 任务取消、重试

5. **历史记录与复测界面**
   - 历史记录列表（按时间、方向、状态筛选）
   - 历史详情（输入、输出、评分明细、对话记录）
   - 复测操作（勾选历史条目一键重新执行）
   - 多次结果对比（同一用例的不同执行结果对比）
   - 趋势分析图表

6. **评测报告界面**
   - 报告列表与查看
   - 多维度评分展示（雷达图、柱状图）
   - 用例级评分明细
   - 报告导出（PDF/Excel，按需）

7. **文件导入界面**
   - 文件上传（Excel/JSON/CSV、图片 jpg/png/gif/webp）
   - 导入预览与字段映射
   - 导入结果反馈（成功/失败条目明细）
   - 批量导入到指定测试集
   - Bug 附件上传与预览

8. **被测系统配置界面**
   - 被测系统列表（LLM 服务、RAG 系统、MCP 工具服务器）
   - 配置表单（按系统类型差异化字段）
   - 连接测试功能
   - 可用模型列表查询

9. **系统管理界面**
   - 用户管理（管理员视角：列表、编辑、删除、修改密码、角色分配）
   - 系统配置查看
   - 操作日志（按需）

★ 10. **M10 智能笔记界面**（V2 版本）
    - 笔记树形结构展示（平铺数据前端组装为树）
    - 分类文件夹 + 文档节点双类型
    - Markdown 编辑器（支持实时预览）
    - 自动保存（高频接口调用 + 防抖 300ms）
    - 拖拽排序（@dnd-kit 或 antd Tree draggable）
    - 递归软删除（前端过滤 deleted_at != null）
    - 删除操作二次确认（popconfirm）+ 乐观更新

★ 11. **M11 Bug 管理界面**
    - Bug 工作台（个人首页统计：待处理/修复中/已解决等）
    - Bug 列表（分页、筛选：状态/严重程度/责任人/系统/版本）
    - Bug 提报页（新建 Bug 表单）
    - Bug 系统管理（被测系统/版本管理 CRUD、连接测试）
    - Bug 全生命周期（8 种状态流转，StatusTag 展示）
    - Bug 详情（基本信息、状态变更历史、评论 Timeline）
    - Bug 评论系统（Timeline 组件、发表/删除）
    - Bug 附件管理（upload 组件、Image 预览、文件下载）
    - 批量操作（批量关闭、批量指派）
    - 通知配置（邮件 SMTP 配置、企微 Webhook 配置）
    - 测试通知发送（邮件/企微测试按钮）
    - 每日提醒列表（提醒日志查询、执行汇总）

★ 12. **M12 参考图例界面**（v3.0）
    - 参考图例画廊（网格/列表视图切换）
    - 参考图例编辑（上传、裁剪、标注、元数据编辑）
    - 参考图例选择器（弹窗形式，供用例编辑时关联）
    - 批量操作（批量上传、批量删除、批量关联用例）
    - 图例分类管理（标签、分组）

★ 13. **Dashboard 首页统计**
    - 用例总数 + 按 business_type 细分（text/image/video）
    - 计划总数 + 按 business_type 细分
    - 运行中计划数 + 按类型细分
    - 数据刷新（页面加载自动请求 + 手动刷新按钮）
    - 数据缓存 5 分钟（避免频繁请求）
    - ECharts 图表渲染（按需引入）

★ 14. **上下文检索界面**
    - Milvus 检索结果展示（列表/卡片形式）
    - Rerank 结果对比（开启/关闭对比）
    - 检索参数配置（top_k、collection、enable_rerank）
    - 结果去重展示（collection + file_id + seq_no 标识）

★ 15. **用例调试页面**（v0.11 新增）
    - 单个用例的快速调试执行
    - 配置验证与保存
    - 实时输出查看

### 非功能需求
- **性能**：首屏加载 < 3s，路由切换 < 500ms，列表渲染流畅（虚拟滚动）
- **可访问性**：键盘可操作、合理的 aria 标签、语义化 HTML
- **兼容性**：Chrome/Edge/Firefox 最新两个版本，分辨率 ≥ 1280×720
- **响应式**：适配主流 PC 分辨率（移动端适配按需）
- **可维护性**：组件化、配置驱动、与后端 API 解耦
- **安全性**：前端 XSS/CSRF 防护、Token 安全存储、权限双校验（前端+后端）

## 关键约束

1. **与后端 API 对齐**：前端类型定义必须与后端 OpenAPI Schema 保持一致，接口变更需同步更新
2. **配置驱动**：评测方向、测试方式、被测系统类型等通过后端配置动态渲染，前端不硬编码业务枚举
3. **权限双校验**：前端路由和菜单按权限控制仅作体验优化，前端不承担最终权限校验职责，安全以服务端校验为准
4. **Token 安全**：Token 存内存 Store，refreshToken 存 sessionStorage，禁止存 localStorage
5. **任务状态实时性**：长任务采用轮询（或 WebSocket，按需）更新进度，避免用户长时间等待无反馈
6. **数据隔离**：用户只能看到自己的测试数据，前端列表查询不带 userId（由服务端从 Token 解析用户身份），前端不自行绕过隔离
7. **构建产物优化**：路由懒加载、按需引入、Tree-shaking，首屏 chunk ≤ 250KB
8. **错误可追溯**：所有 API 请求携带 traceId，错误日志带 traceId 便于前后端联查
9. **M10 笔记性能**：笔记树使用虚拟滚动或懒加载，避免大量节点时卡顿
10. **M11 Bug 状态机**：前端必须严格遵循 8 种状态流转规则，禁止非法状态转换
11. **Dashboard 数据隔离**：所有用户（含管理员）仅查看本人数据，不显示全局统计
12. **检索接口版本**：使用 `/api/retrieval/search` 接口（retrievalService），旧 `/api/context/retrieve` 已废弃并移除
13. **废弃服务清理**：`historyService.ts` 和 `contextService.ts` 已于 2026-09-03 移除，相关功能分别迁移至 `caseService`（历史记录）和 `retrievalService`（上下文检索）

## 服务层清单（当前实际存在）

| Service 文件 | 职责领域 | 状态 |
|-------------|---------|------|
| `request.ts` | axios 实例 + 拦截器 | ✅ 活跃 |
| `authService.ts` | 认证（登录/登出/刷新Token） | ✅ 活跃 |
| `userService.ts` | 用户管理（CRUD/角色） | ✅ 活跃 |
| `caseService.ts` | 评测套件/用例 CRUD + 历史记录 | ✅ 活跃 |
| `planService.ts` | 计划管理 | ✅ 活跃 |
| `taskService.ts` | 任务创建/查询/取消/重试 | ✅ 活跃 |
| `reportService.ts` | 报告查询/导出 | ✅ 活跃 |
| `fileService.ts` / `mediaService.ts` | 文件上传/媒体管理 | ✅ 活跃 |
| `targetService.ts` | 被测系统配置 CRUD | ✅ 活跃 |
| `configService.ts` | 后端动态配置 | ✅ 活跃 |
| `bugService.ts` | Bug 管理（CRUD/状态机/评论/通知） | ✅ 活跃 (M11) |
| `noteService.ts` | 智能笔记（树形/Markdown/自动保存） | ✅ 活跃 (M10) |
| `refGalleryService.ts` | 参考图例 v3.0（画廊/编辑/关联） | ✅ 活跃 (M12) |
| `referenceImageService.ts` | 旧参考图库（渐进式迁移中） | ⚠️ 保留（仍被引用） |
| `retrievalService.ts` | 上下文检索（替代已废弃 contextService） | ✅ 活跃 |
| `metricsService.ts` | 指标数据 | ✅ 活跃 |
| `promptPresetService.ts` | 提示词预设管理 | ✅ 活跃 |
| `dashboardService.ts` | Dashboard 统计数据 | ✅ 活跃 |

## Store 清单（当前实际存在）

| Store 文件 | 职责 | 状态 |
|-----------|------|------|
| `useAuthStore.ts` | 认证状态（token/refreshToken/登录态） | ✅ 活跃 |
| `useUserStore.ts` | 用户信息（profile/权限） | ✅ 活跃 |
| `useAppStore.ts` | 应用全局状态（侧边栏/主题/语言） | ✅ 活跃 |
| `useConfigStore.ts` | 后端动态配置缓存 | ✅ 活跃 |
| `useReferenceImageStore.ts` | 旧参考图库状态 | ⚠️ 保留（渐进式迁移中） |
| `useRefGalleryStore.ts` | 参考图例 v3.0 状态 | ✅ 活跃 (M12) |

## 架构层级

项目采用 feature-based + 横向分层架构（详见 `common/02-architecture-patterns.md`）：

- **Pages 层**：路由入口、页面布局、数据编排
- **Components 层**：可复用 UI 组件（基础组件 + 业务组件）
- **Hooks 层**：自定义 Hook 封装业务逻辑
- **Services 层**：API 调用封装（按业务领域，共 19 个 Service）
- **Store 层**：全局状态管理（Zustand，共 6 个 Store）
- **Utils/Types 层**：工具函数、类型定义、常量、配置
- **core/ 目录**：核心业务组件（评测结果可视化、报告渲染器）

## 页面目录结构（当前实际）

```
src/pages/
├── login/           # 登录页
├── case/            # 评测管理（套件/用例/调试）
├── plan/            # 计划管理
├── task/            # 任务管理
├── history/         # 历史记录
├── report/          # 报告
├── config/          # 系统配置（被测系统/提示词预设等）
├── dashboard/       # Dashboard 首页
├── bug/             # Bug 管理（M11）
│   ├── BugDashboardPage/
│   ├── BugListPage/
│   ├── BugReportPage/
│   └── BugSystemManagePage/
├── noteV2/          # 智能笔记 V2（M10）
│   ├── NoteTreePage/
│   └── NoteEditPage/
├── refgallery/      # 参考图例（M12）
│   ├── RefGalleryPage/
│   ├── RefImageEditPage/
│   └── RefImagePickerModal/
├── debug/           # 用例调试（v0.11）
├── system/          # 系统管理（用户管理等）
└── profile/         # 个人中心
```

## 与后端协作约定

- 后端服务：`ai-server`（提供 RESTful API）
- API 文档：后端提供 OpenAPI/Swagger 文档，前端类型定义据此对齐
- 鉴权方式：JWT Bearer Token，请求头 `Authorization: Bearer <token>`
- 统一响应结构：`{ code: number, message: string, data: T, traceId: string }`
- 错误码：HTTP 状态码 + 业务 code，前端按 code 做差异化提示
- 跨域：开发环境走 Vite 代理（`/api` → 后端服务），生产环境走 Nginx 反代
