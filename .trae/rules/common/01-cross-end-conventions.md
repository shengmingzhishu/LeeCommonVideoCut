# 跨端协作约定

> alwaysApply: true
> 版本: v1.0.0

---

## 1. 接口契约权威性

**权威文档**: `cut-server/docs/04-接口契约.md`（v1.0.0）

### 1.1 变更流程

```
需求 → 先改契约文档 → 后端实现 → 前端对齐类型 → 联调验证
```

任何接口变更必须遵循此顺序。禁止「先改代码再补契约」。

### 1.2 契约内容约束

每新增/修改一个接口，契约文档必须包含：
- 请求方法 + 路径
- 请求体 Schema（字段名、类型、必填、说明）
- 响应体 Schema
- 错误码（属于哪个区间）
- 是否长任务（需轮询）

## 2. 字段命名策略

| 端 | 命名风格 | 示例 |
|----|---------|------|
| 后端 Pydantic | snake_case | `video_dir`, `current_step`, `output_path` |
| 前端 TypeScript | camelCase | `videoDir`, `currentStep`, `outputPath` |
| 接口契约 | snake_case（与后端一致） | `video_dir`, `current_step` |

### 2.1 转换规则

后端通过 `to_camel()` 转换器将 snake_case → camelCase 后返回给前端。

前端发送请求时使用 camelCase，后端接收时自动转 snake_case。

### 2.2 字段映射铁律

1. 前端 TypeScript 类型必须与接口契约附录 A 的字段映射严格对齐
2. 后端修改字段名时，必须同步更新契约文档附录 A
3. 前端发现字段不匹配时，以契约文档为准，不自行 mock

## 3. 统一响应结构

```json
{
  "code": 0,
  "msg": "ok",
  "data": { ... }
}
```

- HTTP 状态码固定 200（含错误）
- `code: 0` 表示成功
- `code: 非0` 表示业务/服务/任务错误
- `data` 可为 null、对象、数组、分页结构

## 4. 错误码体系

| 区间 | 含义 | 示例 |
|------|------|------|
| 0 | 成功 | — |
| 40001-40105 | 业务错误（参数/状态/锁定） | 40001 参数缺失, 40003 项目不存在, 40010 步骤锁定 |
| 50001-50006 | 服务异常（AI/搜索/TTS/ffmpeg/IO/内部） | 50001 AI 服务异常, 50004 ffmpeg 异常 |
| 60001-60003 | 长任务失败 | 60001 任务失败, 60002 任务已取消, 60003 任务超时 |

### 4.1 前端错误处理约定

- `40xxx`: 显示 `msg` 给用户，不跳转
- `50xxx`: 显示「服务异常，请稍后重试」，记录 traceId
- `60xxx`: 长任务面板显示失败状态，提供「重试」按钮

## 5. Trace ID

### 5.1 生成与传递

- 前端每个请求生成 `X-Trace-Id` header（UUID v4）
- 后端在日志中贯穿 traceId
- 响应头回传 `X-Trace-Id`

### 5.2 日志格式

```
时间 | 级别 | tx:{traceId} | 模块 | 函数 | 行号 | 消息
```

## 6. CORS 配置

- 后端允许源: `http://localhost:5173`
- 允许方法: GET, POST, PUT, DELETE, OPTIONS
- 允许头: `Content-Type, Authorization, X-Trace-Id`
- 前端 Vite proxy: `/api` → `http://localhost:8000`

## 7. 长任务轮询约定

### 7.1 任务提交

长任务（Step4 音频/标记, Step6 裁切, Step7 合成）通过 POST 提交，立即返回 `taskId`。

### 7.2 任务轮询

前端通过 `GET /api/task/{id}` 轮询任务状态：
- 轮询间隔: 1-2 秒
- 页卸载时必须取消轮询（避免 setState on unmounted）
- 任务完成/失败/超时后停止轮询

### 7.3 任务取消

通过 `POST /api/step{N}/cancel` 取消正在执行的长任务。

## 8. 鉴权约定

- 本期默认放行（无强制鉴权）
- 预留 `Authorization: Bearer <token>` header
- 未来需要时，在契约文档中补充鉴权章节

## 9. 文件交互约定

- 文件预览: `GET /api/file/preview?path=xxx`（返回文件流）
- 文件下载: `GET /api/file/download?path=xxx`（返回 attachment）
- 目录浏览: `GET /api/dir/browse?path=xxx`（返回文件列表 JSON）
- 路径参数必须经过后端校验，防止目录遍历攻击
