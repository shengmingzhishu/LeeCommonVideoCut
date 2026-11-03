import request from './request'
import { API_ENDPOINTS } from '@/config/api'
import type { ApiResponse, PageData } from '@/types/api.types'
import type { components } from '@/types/api-schema.gen'
import type { MembershipTier } from '@/types/user.types'

type ApiUser = components['schemas']['User']
type ApiMembership = components['schemas']['Membership']
type ApiConfig = components['schemas']['Config']
type ApiConfigTestResult = components['schemas']['ConfigTestResult']

/** 全局配置项（前端驼峰） */
export interface AdminConfigValues {
  key: string
  value: Record<string, unknown>
  description: string | null
  updatedAt: string
}

/** 连接测试结果 */
export interface ConfigTestValues {
  success: boolean
  message: string
  latencyMs: number | null
}

function toAdminConfig(c: ApiConfig): AdminConfigValues {
  return {
    key: c.key ?? '',
    value: (c.value ?? {}) as Record<string, unknown>,
    description: c.description ?? null,
    updatedAt: c.updated_at ?? '',
  }
}

/** 管理端用户（前端驼峰） */
export interface AdminUserValues {
  id: string
  username: string
  email: string | null
  displayName: string | null
  isAdmin: boolean
  isActive: boolean
  membershipTier: MembershipTier
  createdAt: string
}

/** 管理端会员记录（前端驼峰） */
export interface AdminMembershipValues {
  id: string
  userId: string
  tier: string
  status: string
  startedAt: string
  expiresAt: string | null
  note: string | null
  createdAt: string
}

/** 审计日志 */
export interface AuditLogValues {
  id: string
  adminUserId: string
  action: string
  targetType: string
  targetId: string
  payload: Record<string, unknown>
  createdAt: string
}

function toAdminUser(u: ApiUser): AdminUserValues {
  return {
    id: u.id ?? '',
    username: u.username ?? '',
    email: u.email ?? null,
    displayName: u.display_name ?? null,
    isAdmin: u.is_admin ?? false,
    isActive: u.is_active ?? true,
    membershipTier: (u.membership_tier ?? 'free') as MembershipTier,
    createdAt: u.created_at ?? '',
  }
}

function toAdminMembership(m: ApiMembership): AdminMembershipValues {
  return {
    id: m.id ?? '',
    userId: m.user_id ?? '',
    tier: m.tier ?? 'free',
    status: m.status ?? 'active',
    startedAt: m.started_at ?? '',
    expiresAt: m.expires_at ?? null,
    note: m.note ?? null,
    createdAt: m.created_at ?? '',
  }
}

/** 管理后台服务（仅 is_admin 可用）。 */
export const adminService = {
  listUsers: async (params: {
    page?: number
    pageSize?: number
    keyword?: string
    tier?: string
    isActive?: boolean
  } = {}) => {
    const res = await request.get<never, ApiResponse<PageData<ApiUser>>>(API_ENDPOINTS.ADMIN.USERS, {
      params: {
        page: params.page ?? 1,
        pageSize: params.pageSize ?? 20,
        keyword: params.keyword || undefined,
        tier: params.tier || undefined,
        is_active: typeof params.isActive === 'boolean' ? params.isActive : undefined,
      },
    })
    const d = res.data
    return {
      page: d?.page ?? 1,
      pageSize: d?.pageSize ?? 20,
      total: d?.total ?? 0,
      items: (d?.items ?? []).map(toAdminUser),
    }
  },

  updateUser: async (
    userId: string,
    payload: { isAdmin?: boolean; isActive?: boolean; membershipTier?: MembershipTier },
  ): Promise<AdminUserValues> => {
    const res = await request.put<never, ApiResponse<ApiUser>>(API_ENDPOINTS.ADMIN.USER(userId), {
      is_admin: payload.isAdmin,
      is_active: payload.isActive,
      membership_tier: payload.membershipTier,
    })
    return toAdminUser(res.data ?? ({} as ApiUser))
  },

  resetPassword: (userId: string, newPassword: string) =>
    request.post(API_ENDPOINTS.ADMIN.USER_PASSWORD(userId), { new_password: newPassword }),

  listMemberships: async (params: { tier?: string; status?: string } = {}) => {
    const res = await request.get<never, ApiResponse<ApiMembership[]>>(
      API_ENDPOINTS.ADMIN.MEMBERSHIPS,
      {
        params: {
          tier: params.tier || undefined,
          status: params.status || undefined,
        },
      },
    )
    return (res.data ?? []).map(toAdminMembership)
  },

  assignMembership: async (payload: {
    userId: string
    tier: MembershipTier
    expiresAt?: string | null
    note?: string | null
  }): Promise<AdminMembershipValues> => {
    const res = await request.post<never, ApiResponse<ApiMembership>>(
      API_ENDPOINTS.ADMIN.MEMBERSHIPS,
      {
        user_id: payload.userId,
        tier: payload.tier,
        expires_at: payload.expiresAt || null,
        note: payload.note || null,
      },
    )
    return toAdminMembership(res.data ?? ({} as ApiMembership))
  },

  cancelMembership: (membershipId: string) =>
    request.delete(API_ENDPOINTS.ADMIN.MEMBERSHIP(membershipId)),

  listAuditLogs: async (params: { page?: number; pageSize?: number; action?: string } = {}) => {
    const res = await request.get<never, ApiResponse<PageData<Record<string, unknown>>>>(
      API_ENDPOINTS.ADMIN.AUDIT_LOGS,
      {
        params: {
          page: params.page ?? 1,
          pageSize: params.pageSize ?? 20,
          action: params.action || undefined,
        },
      },
    )
    const d = res.data
    return {
      page: d?.page ?? 1,
      pageSize: d?.pageSize ?? 20,
      total: d?.total ?? 0,
      items: (d?.items ?? []).map((r) => ({
        id: String(r.id ?? ''),
        adminUserId: String(r.admin_user_id ?? ''),
        action: String(r.action ?? ''),
        targetType: String(r.target_type ?? ''),
        targetId: String(r.target_id ?? ''),
        payload: (r.payload ?? {}) as Record<string, unknown>,
        createdAt: String(r.created_at ?? ''),
      })) as AuditLogValues[],
    }
  },

  listConfigs: async (): Promise<AdminConfigValues[]> => {
    const res = await request.get<never, ApiResponse<ApiConfig[]>>(API_ENDPOINTS.ADMIN.CONFIGS)
    return (res.data ?? []).map(toAdminConfig)
  },

  saveConfig: async (payload: {
    key: string
    value: Record<string, unknown>
    description?: string | null
  }): Promise<AdminConfigValues> => {
    const res = await request.put<never, ApiResponse<ApiConfig>>(API_ENDPOINTS.ADMIN.CONFIGS, {
      key: payload.key,
      value: payload.value,
      description: payload.description ?? null,
    })
    return toAdminConfig(res.data ?? ({} as ApiConfig))
  },

  testConnection: async (payload: {
    provider: string
    apiKey: string
    baseUrl?: string
    model?: string
  }): Promise<ConfigTestValues> => {
    const res = await request.post<never, ApiResponse<ApiConfigTestResult>>(
      API_ENDPOINTS.CONFIGS.TEST,
      {
        provider: payload.provider,
        api_key: payload.apiKey,
        base_url: payload.baseUrl || null,
        model: payload.model || null,
      },
    )
    const d = res.data
    return {
      success: d?.success ?? false,
      message: d?.message ?? '',
      latencyMs: d?.latency_ms ?? null,
    }
  },
}