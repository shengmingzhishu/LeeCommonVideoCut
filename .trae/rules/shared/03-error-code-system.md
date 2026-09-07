---
alwaysApply: false
description: 统一错误码体系，包括错误码段位分配、错误响应格式、traceId 对齐。涉及错误处理、异常定义、接口错误响应时使用此规则。
---

# 错误码体系（共享层）

> 前后端共用同一套错误码体系，确保错误可追溯、可对齐。

## 1. 错误响应统一格式

所有 API 错误响应必须使用以下 JSON 结构：

```json
{
  "code": "EVAL_401_001",
  "message": "评测套件不存在",
  "detail": "Suite ID 123 not found",
  "trace_id": "a1b2c3d4e5f6",
  "timestamp": "2026-09-07T10:30:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 错误码，格式 `{DOMAIN}_{HTTP_STATUS}_{SEQ}` |
| message | string | 面向用户的简洁描述 |
| detail | string | 面向开发者的详细信息（生产环境可选关闭） |
| trace_id | string | 请求追踪 ID，前后端共享 |
| timestamp | string | ISO 8601 时间戳 |

## 2. 错误码段位分配

| 段位 | 领域 | HTTP Status | 示例 |
|------|------|-------------|------|
| AUTH | 认证/授权 | 401, 403 | `AUTH_401_001`（未登录） |
| EVAL | 评测 | 400, 404, 409 | `EVAL_404_001`（套件不存在） |
| TASK | 任务 | 400, 409, 422 | `TASK_409_001`（任务重复运行） |
| FILE | 文件 | 400, 413 | `FILE_413_001`（文件超限） |
| USER | 用户 | 400, 404 | `USER_404_001`（用户不存在） |
| MCP | MCP 集成 | 502, 503 | `MCP_503_001`（MCP 服务不可用） |
| SYS | 系统 | 500 | `SYS_500_001`（内部异常） |
| COMMON | 通用 | 400, 429 | `COMMON_429_001`（限流） |

## 3. traceId 规则

### 3.1 生成与传递

- 后端在请求入口（中间件）生成 traceId
- 通过响应头 `X-Trace-Id` 返回给前端
- 前端在 axios 拦截器中读取并存入全局变量
- 前端日志和 Sentry 上报中携带 traceId

### 3.2 日志关联

- 后端所有日志携带 `[tx:{trace_id}]` 前缀
- 前端 Console 日志和 Network 请求可携带 `trace-id` header
- 前端 Sentry 事件 tag 中包含 `trace_id`

## 4. 前端错误处理规则

- axios 拦截器统一解析错误响应，提取 code/message/trace_id
- 按错误码段位决定处理策略：
  - AUTH 段 → 跳转登录页
  - COMMON_429 → 提示限流
  - SYS_500 → 提示系统异常 + 显示 trace_id
  - 其他 → 按业务场景展示
- 所有错误必须记录到前端日志（含 trace_id），便于联查后端日志
