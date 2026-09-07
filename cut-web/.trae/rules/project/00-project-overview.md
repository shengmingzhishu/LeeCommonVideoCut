---
alwaysApply: true
version: 1.0.0
lastUpdated: 2026-09-04
description: video-cut 前端项目概述，包括项目目标、技术栈、7步流程页面、核心功能、关键约束。了解项目背景、制定技术方案、评估需求时使用此规则。
---
# 项目概述

> 本文档是 video-cut 前端（cut-web）项目的定制规则，仅适用于本项目。
> 接口契约权威文档: `cut-server/docs/04-接口契约.md`（v1.0.0）

## 项目名称

video-cut（前端 cut-web）

## 项目目标

为 video-cut 视频剪辑工具提供 Web 前端界面，支持：
- 项目卡片式管理（创建、复制、删除、进度恢复）
- 7 步引导式创作流程
- Step5 虚拟串播预览（`<video>.currentTime` 模拟，0 IO）
- 标记编辑（增删改、拖拽、时长匹配检查）
- 长任务进度展示与轮询
- 全局配置管理（AI/TTS/搜索引擎）
- 生成历史查看与回滚

## 技术栈

| 类别 | 技术选型 | 说明 |
|------|---------|------|
| 编程语言 | TypeScript 5+ | strict 模式 |
| UI 框架 | React 18 | 函数组件 + Hooks |
| 构建工具 | Vite | 极速冷启动 + HMR |
| UI 组件库 | Ant Design 5.x | 深色科技风主题 |
| 路由 | React Router v6 | 声明式路由 + 懒加载 |
| 状态管理 | Zustand | 轻量全局状态 |
| HTTP 客户端 | axios | 自封装 core/request.ts |
| 样式方案 | CSS Modules + SCSS | 局部作用域 |
| 表单 | React Hook Form + Zod | 表单验证 |
| 代码规范 | ESLint + Prettier | 统一代码风格 |
| 单元测试 | Vitest + @testing-library/react | Vite 原生单测 |
| E2E 测试 | Playwright | 跨浏览器端到端测试 |

## 项目范围

### 核心功能

1. **项目列表页（首页）**
   - 项目卡片展示（缩略图、标题、作者、进度、状态）
   - 创建新项目
   - 复制项目
   - 删除项目（二次确认）
   - 进入项目编辑流程

2. **Step1 输入信息面板**
   - 项目标题、作者、简介输入
   - 视频目录选择（目录浏览）
   - 介绍资料目录选择
   - 素材加载与预览

3. **Step2 AI拆解+搜索面板**
   - AI 拆解结果展示（核心词、价值点、建议标题、搜索词）
   - 搜索结果列表
   - 关键词编辑

4. **Step3 口播文案面板**
   - 4 种风格选择（hot_review/objective/suspense/plot）
   - 文案生成
   - 文案编辑（富文本或 Markdown）
   - 确认进入下一步

5. **Step4 双线并行面板**
   - TTS 音频生成进度（长任务轮询）
   - 随机标记生成进度
   - 音频预览播放
   - 标记片段列表预览

6. **Step5 虚拟预览面板（核心创新）**
   - `<video>.currentTime` 串播模拟（0 IO）
   - 标记编辑（增删改、拖拽调整起止点）
   - 时长匹配检查
   - 随机重标按钮
   - 确认进入裁切

7. **Step6 裁切合并面板**
   - 裁切进度（长任务轮询）
   - 裁切结果预览
   - 取消按钮

8. **Step7 合成导出面板**
   - 合成进度（长任务轮询）
   - 字幕预览
   - 最终 mp4 预览与下载

9. **完成页**
   - 成品视频预览
   - 下载按钮
   - 返回项目列表

10. **全局配置面板**
    - AI 提供商配置（provider/apiKey/baseUrl/model）
    - TTS 引擎配置（engine/voice）
    - 搜索引擎配置（engine/apiKey）
    - 测试连接按钮

11. **生成历史查看**
    - 按步骤维度查看历史版本
    - 版本对比
    - 回滚操作

### 非功能需求
- **性能**: 首屏加载 < 3s，路由切换 < 500ms
- **0 IO 预览**: Step5 禁止触发 ffmpeg IO
- **轮询安全**: 页卸载时取消所有轮询
- **深色科技风**: Ant Design 5 主题定制
- **响应式**: 适配主流 PC 分辨率（≥ 1280×720）

## 关键约束

1. **接口契约对齐**: 前端 TypeScript 类型必须与接口契约附录 A 字段映射严格一致
2. **0 IO 预览铁律**: Step5 编辑阶段禁止触发任何 ffmpeg/文件 IO 操作
3. **轮询安全**: 长任务轮询在页卸载时必须取消（避免 setState on unmounted）
4. **字段映射**: 前端 camelCase ↔ 后端 snake_case（通过 to_camel 转换）
5. **统一响应**: `{ code, msg, data }`，HTTP 固定 200
6. **TraceId**: 每个请求带 `X-Trace-Id` header
7. **错误处理**: 40xxx 显示 msg / 50xxx 显示重试 / 60xxx 显示任务失败+重试
8. **步骤锁定**: 不可跳过未完成步骤
9. **构建产物**: 路由懒加载，首屏 chunk ≤ 250KB

## 服务层清单

| Service 文件 | 职责领域 |
|-------------|---------|
| `request.ts` | axios 实例 + 拦截器（traceId/错误处理） |
| `projectService.ts` | 项目 CRUD + 复制 + 重置 |
| `configService.ts` | 全局配置 + 测试连接 |
| `step1Service.ts` | Step1 素材加载 |
| `step2Service.ts` | Step2 AI拆解+搜索 |
| `step3Service.ts` | Step3 文案生成 |
| `step4Service.ts` | Step4 TTS+标记 |
| `step5Service.ts` | Step5 标记保存 |
| `step6Service.ts` | Step6 裁切合并 |
| `step7Service.ts` | Step7 合成导出 |
| `taskService.ts` | 长任务查询/取消 |
| `historyService.ts` | 生成历史查询/回滚 |
| `fileService.ts` | 文件预览/下载/目录浏览 |

## Store 清单

| Store 文件 | 职责 |
|-----------|------|
| `useProjectStore.ts` | 当前项目信息（id/title/author/intro/currentStep/status） |
| `useConfigStore.ts` | 全局配置缓存 |
| `useStepStore.ts` | 当前步骤状态（各步骤数据/进度） |
| `useTaskStore.ts` | 长任务状态（taskId/status/progress） |

## 架构层级

项目采用 feature-based + 横向分层架构（详见 `common/02-architecture-patterns.md`）：

- **Pages 层**: 路由入口、页面布局、数据编排
- **Components 层**: 可复用 UI 组件（basic + business）
- **Hooks 层**: 自定义 Hook（useRequest, usePolling, useTaskPoll）
- **Services 层**: API 调用封装
- **Store 层**: 全局状态（Zustand）
- **Utils/Types 层**: 工具函数、类型定义
- **core/ 目录**: 核心业务组件（MarkerTimeline, Request 封装）

## 页面目录结构

```
src/pages/
├── project-list/     # 项目列表页（首页）
├── step1/            # Step1 输入信息
├── step2/            # Step2 AI拆解+搜索
├── step3/            # Step3 口播文案
├── step4/            # Step4 双线并行
├── step5/            # Step5 虚拟预览（核心）
├── step6/            # Step6 裁切合并
├── step7/            # Step7 合成导出
├── complete/         # 完成页
├── config/           # 全局配置
├── history/          # 生成历史
└── error/            # 错误页
```

## 与后端协作约定

- 后端服务: `cut-server`（FastAPI，端口 8000）
- 接口契约: `cut-server/docs/04-接口契约.md`（v1.0.0，单一权威）
- 统一响应: `{ code: 0, msg: "ok", data: { ... } }`，HTTP 固定 200
- 错误码: 0=成功 / 40xxx=业务 / 50xxx=服务 / 60xxx=长任务
- Trace: 请求带 `X-Trace-Id` header
- 字段映射: 前端 camelCase ↔ 后端 snake_case
- 跨域: 开发环境 Vite proxy（`/api` → `http://localhost:8000`）
- 鉴权: 本期默认放行，预留 Bearer Token
- Base URL: `http://localhost:8000/api`（环境变量 `VITE_API_BASE_URL`）
