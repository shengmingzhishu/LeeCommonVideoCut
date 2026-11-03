---
alwaysApply: false
description: API 契约治理规则，包括 OpenAPI 定义、前后端类型同步、breaking change 管控。涉及接口定义、接口变更、前后端联调时使用此规则。
---

# API 契约规则（共享层）

> 前后端独立项目必须遵守此契约规则，确保接口对齐。

## 1. 契约优先原则

- **先定义契约，再写实现**：任何新接口或接口变更，先更新 OpenAPI 定义，再编码
- **单一数据源**：后端 OpenAPI/Swagger 文件是 API 契约的唯一数据源
- **前端类型由契约生成**：前端 TS 类型必须从 OpenAPI 自动生成，禁止手写接口类型

## 2. OpenAPI 定义规范

### 2.1 文件位置

- 后端：FastAPI 自动生成 `/docs/openapi.json`，同时在代码仓库维护 `docs/openapi.yaml` 作为设计稿
- 前端：从后端 `/docs/openapi.json` 拉取并生成 TS 类型

### 2.2 命名规范

- Path：`/api/{domain}/{action}`，如 `/api/eval/suites`、`/api/task/run`
- Method：RESTful 语义（GET 查询、POST 创建、PUT 更新、DELETE 删除）
- 字段名：后端 snake_case（Python 风格），前端通过 codegen 转为 camelCase

### 2.3 必填字段

每个接口必须定义：
- `summary`：一句话描述
- `description`：详细说明
- `tags`：按领域分组
- `parameters`：路径参数 + 查询参数，含类型和校验规则
- `requestBody`：请求体 Schema（如有）
- `responses`：所有可能的状态码和响应体 Schema
- `x-error-codes`：自定义错误码列表（扩展字段）

## 3. 前后端类型同步

### 3.1 同步流程

```
后端更新 OpenAPI → CI 生成 openapi.json → 前端拉取 → codegen 生成 TS 类型 → 前端使用
```

### 3.2 Codegen 工具

- 使用 `openapi-typescript` 或 `orval` 从 OpenAPI 生成 TS 类型和 API 客户端
- 生成的文件放在 `src/types/api/` 目录，禁止手动修改
- 前端 Service 层直接引用生成的类型

### 3.3 同步触发时机

- 后端 PR 合并到 main → CI 自动触发前端类型同步
- 前端开发时如需提前对齐 → 手动运行 `pnpm run sync-api` 拉取最新契约

## 4. Breaking Change 管控

### 4.1 Breaking Change 判定

| 变更类型 | Breaking? | 说明 |
|---------|-----------|------|
| 新增接口 | 否 | 纯增量 |
| 新增可选字段 | 否 | 向下兼容 |
| 删除接口 | **是** | 必须版本升级 |
| 删除字段 | **是** | 必须版本升级 |
| 修改字段类型 | **是** | 必须版本升级 |
| 字段从可选改为必填 | **是** | 必须版本升级 |
| 字段从必填改为可选 | 否 | 向下兼容 |
| 新增枚举值 | 否 | 向下兼容 |
| 删除枚举值 | **是** | 前端可能依赖该值 |

### 4.2 Breaking Change 流程

1. 后端在 PR 标题标注 `[BREAKING]`
2. PR 描述必须包含：变更原因、影响范围、前端适配方案
3. CI 自动检测 breaking change 并通知前端团队
4. 前端在同一个迭代周期内完成适配
5. 上线时前后端同步发布

## 5. 接口变更模板

每次接口变更必须填写变更记录：

```markdown
## 接口变更 - [日期]

### 变更类型
- [ ] 新增接口
- [ ] 修改接口
- [ ] 删除接口
- [ ] [BREAKING] 破坏性变更

### 影响接口
| Method | Path | 变更说明 |
|--------|------|---------|
| POST | /api/eval/suites | 新增 batchImport 参数 |

### 前端影响
- 需要更新：evalService.ts
- 类型变化：EvalSuite 新增 batchImport?: boolean
- 适配工时：约 0.5h

### 后端负责人：___  前端负责人：___
```
