---
alwaysApply: false
description: 结构化日志规范，包括日志级别、JSON 格式、敏感信息过滤、前端日志上报。涉及日志编写、日志配置、日志分析时使用此规则。
---

# 日志规范（共享层）

> 前后端共用同一套日志规范，确保日志可追溯、可联查。

## 1. 日志级别

| 级别 | 后端 (Python) | 前端 (TS) | 使用场景 |
|------|---------------|-----------|---------|
| DEBUG | `logger.debug()` | `console.debug()` | 开发调试，生产环境关闭 |
| INFO | `logger.info()` | `console.log()` | 正常业务流程记录 |
| WARN | `logger.warning()` | `console.warn()` | 异常但可恢复的情况 |
| ERROR | `logger.error()` | `console.error()` | 异常且影响功能 |
| CRITICAL | `logger.critical()` | Sentry capture | 严重故障，需立即处理 |

### 1.1 级别使用规则

- **禁止用 print() 替代日志**（后端业务代码）
- **禁止在前端业务代码中使用 console.log()**（仅限调试，提交前清除）
- ERROR 级别日志必须包含：错误堆栈、traceId、上下文信息
- WARN 级别必须记录：触发条件、降级行为

## 2. 后端日志格式

### 2.1 结构化 JSON 日志

```python
import structlog

logger = structlog.get_logger()

logger.info("eval_started",
    trace_id=trace_id,
    user_id=user_id,
    suite_id=suite_id,
    direction="rag",
    duration_ms=None,  # 开始时为 None
)
```

输出示例：
```json
{
  "timestamp": "2026-09-07T10:30:00.123Z",
  "level": "info",
  "event": "eval_started",
  "trace_id": "a1b2c3d4e5f6",
  "user_id": 42,
  "suite_id": 100,
  "direction": "rag"
}
```

### 2.2 日志必须包含的字段

| 字段 | 必填 | 说明 |
|------|------|------|
| timestamp | 是 | ISO 8601 |
| level | 是 | 日志级别 |
| event | 是 | 事件名（snake_case） |
| trace_id | 是（有请求上下文时） | 请求追踪 ID |
| user_id | 否 | 用户 ID |
| module | 否 | 模块名 |

### 2.3 日志输出位置

| 环境 | 输出位置 | 说明 |
|------|---------|------|
| 开发 | 控制台（彩色） | 方便阅读 |
| 测试 | 控制台 + `logs/test/` | 按日期分文件 |
| 生产 | stdout（容器标准输出） | 由日志收集系统采集 |

## 3. 前端日志规范

### 3.1 日志分类

| 类型 | 工具 | 用途 |
|------|------|------|
| 开发日志 | console（debug/log/warn/error） | 开发时调试 |
| 运行日志 | Sentry | 生产环境错误监控 |
| 请求日志 | axios interceptor | API 调用记录 |

### 3.2 Sentry 上报规则

- **自动上报**：未捕获的 JS 错误、Promise rejection
- **手动上报**：捕获的异常中，影响用户体验的需手动上报
- **不上报**：已处理的非影响性错误（如表单校验失败）
- **必须携带**：trace_id、用户信息（脱敏）、页面路由、操作上下文

### 3.3 前端日志结构

```typescript
interface LogEntry {
  level: 'debug' | 'info' | 'warn' | 'error';
  event: string;          // 事件名
  trace_id?: string;      // 后端返回的 traceId
  user_id?: number;       // 当前用户
  page?: string;          // 当前路由
  context?: Record<string, unknown>; // 额外上下文
}
```

## 4. 敏感信息过滤

### 4.1 禁止记录的字段

- 密码、密码哈希
- API Key / Token（完整值）
- 数据库连接串
- 身份证号、手机号（完整值）
- 请求体中可能包含的敏感数据

### 4.2 脱敏规则

```python
# 后端示例
def mask_token(token: str) -> str:
    if not token or len(token) <= 8:
        return "***"
    return f"{token[:4]}***{token[-4:]}"

logger.info("api_called", token=mask_token(token))  # sk-a1b2c3d4***e5f6g7h8
```

```typescript
// 前端示例
function maskToken(token: string): string {
  if (!token || token.length <= 8) return '***';
  return `${token.slice(0, 4)}***${token.slice(-4)}`;
}
```

### 4.3 Sentry 脱敏配置

- 配置 `beforeSend` 钩子，过滤敏感字段
- 配置 `denyUrls` 排除第三方库的错误
- 配置 `tracesSampleRate`：生产环境 0.1，开发环境 1.0

## 5. 日志分析规则

- 通过 trace_id 串联前后端日志链路
- 后端日志查询：按 trace_id 过滤
- 前端问题排查：Sentry 事件 → 提取 trace_id → 查后端日志
- 日志保留周期：生产 30 天，测试 7 天
