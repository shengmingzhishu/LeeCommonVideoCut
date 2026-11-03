import axios, { AxiosError } from 'axios'

import { API_ENDPOINTS } from '@/config/api'
import { env } from '@/config/env'
import type { ApiErrorResponse, ApiResponse } from '@/types/api.types'
import { generateTraceId } from '@/utils/trace'
import logger from '@/utils/logger'
import { useAuthStore } from '@/store/useAuthStore'

/** 业务/API 错误统一包装（react-stack 规则 §8.1） */
export class ApiError extends Error {
  /** 业务错误码，如 "AUTH_401_001" */
  code: string
  detail: string | null
  traceId: string | null
  httpStatus?: number

  constructor(init: {
    code: string
    message: string
    detail?: string | null
    traceId?: string | null
    httpStatus?: number
  }) {
    super(init.message)
    this.name = 'ApiError'
    this.code = init.code
    this.detail = init.detail ?? null
    this.traceId = init.traceId ?? null
    this.httpStatus = init.httpStatus
  }
}

const request = axios.create({
  baseURL: env.API_BASE_URL,
  timeout: 30_000,
})

request.interceptors.request.use((config) => {
  // 跨端协作约定 §8/§9：鉴权头 + traceId 贯穿
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  if (!config.headers['X-Trace-Id']) {
    config.headers['X-Trace-Id'] = generateTraceId()
  }
  const traceId = config.headers['X-Trace-Id']
  logger.debug(`→ ${config.method?.toUpperCase()} ${config.url} [${traceId}]`)
  return config
})

request.interceptors.response.use(
  (response) => {
    // HTTP 200 但业务 code !== 0 也按错误处理（后端业务错误一般走非 2xx，这里兜底）
    const body = response.data as ApiResponse
    if (body && typeof body === 'object' && 'code' in body && body.code !== 0) {
      return Promise.reject(
        new ApiError({
          code: String(body.code),
          message: body.msg,
          traceId: body.traceId,
          httpStatus: response.status,
        }),
      )
    }
    // 统一解包：调用方拿到 {code, msg, data, traceId} 响应体
    // （axios 类型声明要求返回 AxiosResponse，这里故意解包，需断言）
    return body as unknown as typeof response
  },
  (error: AxiosError<ApiErrorResponse>) => {
    const body = error.response?.data
    const traceId = body?.traceId ?? null

    // 401 → 清登录态，跳登录页（携带 redirect）
    if (error.response?.status === 401) {
      useAuthStore.getState().clearAuth()
      const { pathname, search } = window.location
      if (pathname !== '/login') {
        window.location.href = `/login?redirect=${encodeURIComponent(pathname + search)}`
      }
    }

    logger.error(
      `← ${error.config?.method?.toUpperCase()} ${error.config?.url} 失败:`,
      body?.code ?? error.message,
      traceId ? `[traceId=${traceId}]` : '',
    )

    if (body) {
      return Promise.reject(
        new ApiError({
          code: body.code,
          message: body.message,
          detail: body.detail,
          traceId: body.traceId,
          httpStatus: error.response?.status,
        }),
      )
    }
    // 网络层错误（断网/超时）
    return Promise.reject(
      new ApiError({
        code: 'NETWORK_ERROR',
        message: '网络异常，请检查连接后重试',
        traceId,
      }),
    )
  },
)

export { API_ENDPOINTS }
export default request
