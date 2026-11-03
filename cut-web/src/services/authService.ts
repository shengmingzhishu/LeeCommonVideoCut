import request, { API_ENDPOINTS } from './request'
import type { ApiResponse } from '@/types/api.types'
import type { components } from '@/types/api-schema.gen'
import type { LoginResult, UserInfo } from '@/types/user.types'

type ApiUser = components['schemas']['User']

/** 契约 snake_case → 前端 camelCase（跨端协作约定 §1，禁止前端手写 snake_case 字段）。 */
function toUser(u: ApiUser): UserInfo {
  return {
    id: u.id ?? '',
    username: u.username ?? '',
    email: u.email ?? null,
    displayName: u.display_name ?? null,
    avatarUrl: u.avatar_url ?? null,
    bio: u.bio ?? null,
    isAdmin: u.is_admin ?? false,
    membershipTier: u.membership_tier ?? 'free',
    isActive: u.is_active ?? true,
    createdAt: u.created_at ?? '',
    updatedAt: u.updated_at ?? '',
  }
}

/** 认证服务：注册 / 登录 / 登出 / 当前用户。 */
export const authService = {
  /** 登录，返回 user + token + expiresAt。失败抛 ApiError（拦截器归一化）。 */
  login: async (username: string, password: string): Promise<LoginResult> => {
    const res = await request.post<never, ApiResponse<components['schemas']['LoginResponse']>>(
      API_ENDPOINTS.AUTH.LOGIN,
      { username, password },
    )
    return {
      user: toUser(res.data?.user ?? {}),
      token: res.data?.token ?? '',
      expiresAt: res.data?.expires_at ?? '',
    }
  },

  /** 注册（成功后自动登录，返回结构同登录）。 */
  register: async (req: components['schemas']['UserCreate']): Promise<LoginResult> => {
    const res = await request.post<never, ApiResponse<components['schemas']['LoginResponse']>>(
      API_ENDPOINTS.AUTH.REGISTER,
      req,
    )
    return {
      user: toUser(res.data?.user ?? {}),
      token: res.data?.token ?? '',
      expiresAt: res.data?.expires_at ?? '',
    }
  },

  /** 登出（JWT 无状态，后端仅记录；前端负责清 token）。 */
  logout: () => request.post(API_ENDPOINTS.AUTH.LOGOUT),

  /** 获取当前登录用户。 */
  getMe: async (): Promise<UserInfo> => {
    const res = await request.get<never, ApiResponse<ApiUser>>(API_ENDPOINTS.USERS.ME)
    return toUser(res.data ?? {})
  },

  /** 更新当前用户的资料（昵称 / 头像 / 简介）。 */
  updateMe: async (payload: {
    displayName?: string | null
    avatarUrl?: string | null
    bio?: string | null
  }): Promise<UserInfo> => {
    const res = await request.put<never, ApiResponse<ApiUser>>(API_ENDPOINTS.USERS.ME, {
      display_name: payload.displayName ?? null,
      avatar_url: payload.avatarUrl ?? null,
      bio: payload.bio ?? null,
    })
    return toUser(res.data ?? {})
  },

  /** 修改密码（成功后建议重新登录）。 */
  changePassword: (oldPassword: string, newPassword: string) =>
    request.post(API_ENDPOINTS.AUTH.CHANGE_PASSWORD, {
      old_password: oldPassword,
      new_password: newPassword,
    }),
}
