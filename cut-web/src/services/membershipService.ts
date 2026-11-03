import request from './request'
import { API_ENDPOINTS } from '@/config/api'
import type { ApiResponse } from '@/types/api.types'
import type { components } from '@/types/api-schema.gen'

type ApiMembership = components['schemas']['Membership']
type ApiQuota = components['schemas']['QuotaInfo']

/** 会员信息（前端驼峰） */
export interface MembershipValues {
  id: string
  userId: string
  tier: string
  status: string
  startedAt: string
  expiresAt: string | null
  assignedBy: string
  note: string | null
  createdAt: string
}

/** 配额快照（前端驼峰） */
export interface QuotaValues {
  tier: string
  projectsLimit: number
  projectsUsed: number
  monthlyStepCallsLimit: number
  monthlyStepCallsUsed: number
  storageLimitMb: number
  storageUsedMb: number
  currentPeriod: string
}

export const TIER_LABEL: Record<string, string> = {
  free: '免费版',
  pro: '专业版',
  enterprise: '企业版',
}

/** -1 表示不限 */
export function formatLimit(value: number, unit = ''): string {
  if (value < 0) return `不限${unit}`
  return `${value}${unit}`
}

function toMembership(m: ApiMembership): MembershipValues {
  return {
    id: m.id ?? '',
    userId: m.user_id ?? '',
    tier: m.tier ?? 'free',
    status: m.status ?? 'active',
    startedAt: m.started_at ?? '',
    expiresAt: m.expires_at ?? null,
    assignedBy: m.assigned_by ?? '',
    note: m.note ?? null,
    createdAt: m.created_at ?? '',
  }
}

function toQuota(q: ApiQuota): QuotaValues {
  return {
    tier: q.tier ?? 'free',
    projectsLimit: q.projects_limit ?? 0,
    projectsUsed: q.projects_used ?? 0,
    monthlyStepCallsLimit: q.monthly_step_calls_limit ?? 0,
    monthlyStepCallsUsed: q.monthly_step_calls_used ?? 0,
    storageLimitMb: q.storage_limit_mb ?? 0,
    storageUsedMb: q.storage_used_mb ?? 0,
    currentPeriod: q.current_period ?? '',
  }
}

/** 会员服务：我的会员状态 + 配额用量。 */
export const membershipService = {
  getMine: async (): Promise<MembershipValues | null> => {
    const res = await request.get<never, ApiResponse<ApiMembership | null>>(
      API_ENDPOINTS.MEMBERSHIPS.ME,
    )
    return res.data ? toMembership(res.data) : null
  },

  getMyQuota: async (): Promise<QuotaValues> => {
    const res = await request.get<never, ApiResponse<ApiQuota>>(API_ENDPOINTS.MEMBERSHIPS.MY_QUOTA)
    return toQuota(res.data ?? ({} as ApiQuota))
  },
}