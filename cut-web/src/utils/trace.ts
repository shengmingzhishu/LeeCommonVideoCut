/**
 * traceId 生成（跨端协作约定 §9）
 * 前端请求未携带 X-Trace-Id 时自动生成 UUID，便于前后端日志关联。
 */
export function generateTraceId(): string {
  return crypto.randomUUID().replace(/-/g, '')
}
