/**
 * API 通用类型（与 docs/00-跨端协作约定.md 对齐）
 * 字段命名：契约层 snake_case，前端 camelCase 由 openapi-typescript codegen 转换。
 */

/** 统一成功响应：{code, msg, data, traceId} */
export interface ApiResponse<T = unknown> {
  code: number
  msg: string
  data: T
  traceId: string | null
}

/** 统一错误响应：{code, message, detail, traceId, timestamp, data} */
export interface ApiErrorResponse {
  code: string
  message: string
  detail: string | null
  traceId: string | null
  timestamp: string
  data: null
}

/** 分页响应（跨端协作约定 §10） */
export interface PageData<T> {
  page: number
  pageSize: number
  total: number
  items: T[]
}

/** 分页请求参数 */
export interface PageParams {
  page?: number
  pageSize?: number
}
