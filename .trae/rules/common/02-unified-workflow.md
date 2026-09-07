# 统一开发工作流

> alwaysApply: false
> 版本: v1.0.0

---

## 1. 开发模式

### 1.1 轻量模式

适用: Bug 修复、配置调整、文案修改、样式微调

```
直接编码 → 测试 → code-review
```

### 1.2 完整模式

适用: 新功能、接口变更、架构调整、数据库变更

```
qa-reset → request-analysis → task-spliter → 编码 → 测试 → code-review
```

### 1.3 跨端模式

适用: 新增/修改 API、前后端联调、字段对齐

```
改契约文档 → 后端实现 → 前端对齐 → 联调验证 → code-review（两端各一次）
```

## 2. 跨端任务拆分

当一个需求涉及前后端时，按以下顺序拆分：

1. **契约先行**: 在 `04-接口契约.md` 中定义/修改接口
2. **后端先行**: 后端实现 API + 单元测试
3. **前端跟进**: 前端对齐类型 + 实现 UI + 单元测试
4. **联调验证**: 启动两端，按联调 checklist 验证
5. **代码审查**: 两端各自走 code-review

### 2.1 任务拆分模板

```
## 需求: [需求名称]

### 契约变更
- [ ] 修改 04-接口契约.md（方法/路径/Schema/错误码）

### 后端任务（cut-server）
- [ ] Controller 层
- [ ] Service 层
- [ ] Manager 层（如涉及跨域编排）
- [ ] Model 层（如涉及数据库变更）
- [ ] 单元测试
- [ ] code-review

### 前端任务（cut-web）
- [ ] TypeScript 类型对齐
- [ ] Service 层（API 调用）
- [ ] Hook 层（数据逻辑）
- [ ] Component 层（UI）
- [ ] Store 层（如涉及全局状态）
- [ ] 单元测试
- [ ] code-review

### 联调验证
- [ ] 启动后端（8000）
- [ ] 启动前端（5173）
- [ ] 按联调 checklist 逐项验证
```

## 3. 联调流程

### 3.1 启动顺序

1. 启动后端: `cd cut-server && python -m uvicorn app.main:app --reload --port 8000`
2. 启动前端: `cd cut-web && pnpm dev`
3. 验证健康检查: `GET http://localhost:8000/api/health`

### 3.2 联调 checklist

详见 `templates/00-前后端联调checklist.md`

### 3.3 常见问题排查

| 症状 | 排查方向 |
|------|---------|
| 前端请求 404 | 后端路由是否注册、Vite proxy 配置 |
| CORS 报错 | 后端 CORS 配置是否允许 5173 |
| 字段不匹配 | 对照接口契约附录 A 字段映射 |
| 长任务卡住 | 检查 ffmpeg/edge-tts 是否在 PATH |
| 步骤锁定 | 检查 `currentStep` 状态机 |

## 4. Git 工作流

### 4.1 分支策略

- `main`: 稳定分支
- `feat/xxx`: 功能分支
- `fix/xxx`: 修复分支

### 4.2 提交规范

```
<type>(<scope>): <subject>

<body>
```

type: `feat | fix | refactor | test | docs | chore`
scope: `server | web | root | api | step{N}`

示例:
```
feat(server): 实现 Step1 素材加载接口
fix(web): 修复 Step5 标记编辑时间轴溢出
docs(root): 更新接口契约 v1.1.0
```

### 4.3 PR 规范

PR 描述必须包含:
- 变更摘要
- 关联的契约版本
- 测试方式
- 截图（如涉及 UI 变更）

## 5. 卡点检测与恢复

### 5.1 卡点阈值

| 指标 | 阈值 | 动作 |
|------|------|------|
| 同文件修改次数 | ≥ 3 | 暂停，重新分析 |
| 同错误出现次数 | ≥ 2 | 暂停，换方案 |
| 对话轮次 | ≥ 5 | 暂停，拆分任务 |
| 修复后仍失败 | ≥ 2 | 回滚，重做 |

### 5.2 恢复策略

1. 检查 `03-开发进度.md` 中当前任务状态
2. 检查 `05-问题记录.md` 中是否有类似问题
3. 如果是跨端问题，对照接口契约检查
4. 如果是编码问题，走 code-review skill
5. 记录问题到 `05-问题记录.md`

## 6. 功能点状态机

```
pending → designing → developing → testing → done
```

- `pending`: 需求已拆分，等待设计
- `designing`: 正在分析/设计接口
- `developing`: 正在编码实现
- `testing`: 正在测试/联调
- `done`: 已完成 code-review 并合并
