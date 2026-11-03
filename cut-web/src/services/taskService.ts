import request from './request'
import { API_ENDPOINTS } from '@/config/api'
import type { ApiResponse } from '@/types/api.types'
import type { components } from '@/types/api-schema.gen'

type ApiTask = components['schemas']['Task']

/** 任务状态 */
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

/** 任务信息（驼峰） */
export interface TaskInfo {
  id: string
  type: string
  status: TaskStatus
  progress: number
  result: Record<string, unknown> | null
  error: string | null
  startedAt: string | null
  finishedAt: string | null
  createdAt: string
}

function toTask(t: ApiTask): TaskInfo {
  const status = (t.status ?? 'pending') as TaskStatus
  return {
    id: t.id ?? '',
    type: t.type ?? '',
    status,
    progress: t.progress ?? 0,
    result: (t.result as Record<string, unknown> | null) ?? null,
    error: t.error ?? null,
    startedAt: t.started_at ?? null,
    finishedAt: t.finished_at ?? null,
    createdAt: t.created_at ?? '',
  }
}

/** 任务服务：提交后轮询进度（跨端协作约定 §11，前端轮询间隔 ≥ 2 秒）。 */
export const taskService = {
  /** 查询任务详情。 */
  get: async (taskId: string): Promise<TaskInfo> => {
    const res = await request.get<never, ApiResponse<ApiTask>>(API_ENDPOINTS.TASKS.DETAIL(taskId))
    return toTask(res.data ?? ({} as ApiTask))
  },

  /** 取消任务。 */
  cancel: async (taskId: string): Promise<void> => {
    await request.delete(API_ENDPOINTS.TASKS.DETAIL(taskId))
  },

  /** 重试失败 / 已取消任务，返回新任务 ID。 */
  retry: async (taskId: string): Promise<string> => {
    const res = await request.post<never, ApiResponse<ApiTask>>(
      API_ENDPOINTS.TASKS.RETRY(taskId),
    )
    return res.data?.id ?? ''
  },

  /**
   * 轮询任务直到结束。
   *
   * @param taskId 任务 ID
   * @param onProgress 进度回调
   * @param interval 轮询间隔（毫秒，最小 2000）
   */
  poll: async (
    taskId: string,
    onProgress?: (task: TaskInfo) => void,
    interval = 2000,
  ): Promise<TaskInfo> => {
    const gap = Math.max(2000, interval)
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const task = await taskService.get(taskId)
      onProgress?.(task)
      if (task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled') {
        return task
      }
      await new Promise((resolve) => setTimeout(resolve, gap))
    }
  },
}
