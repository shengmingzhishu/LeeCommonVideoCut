import request, { API_ENDPOINTS } from './request'
import type { ApiResponse } from '@/types/api.types'

export interface HealthStatus {
  status: string
  ffmpeg_available: boolean
  ffprobe_available: boolean
  postgres_available: boolean
  minimax_configured: boolean
  version: string
}

/** 系统健康检查服务。 */
export const healthService = {
  /** 获取后端依赖可用性（ffmpeg/PostgreSQL/MiniMax）。 */
  getHealth: (): Promise<ApiResponse<HealthStatus>> =>
    request.get<never, ApiResponse<HealthStatus>>(API_ENDPOINTS.SYSTEM.HEALTH),
}
