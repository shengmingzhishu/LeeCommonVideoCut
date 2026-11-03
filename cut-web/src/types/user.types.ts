/**
 * 用户域类型（前端 camelCase；由 services 层从契约 snake_case 映射）。
 * 字段与契约 components.schemas.User 对齐。
 */
export type MembershipTier = 'free' | 'pro' | 'enterprise'

export interface UserInfo {
  id: string
  username: string
  email: string | null
  displayName: string | null
  avatarUrl: string | null
  bio: string | null
  isAdmin: boolean
  membershipTier: MembershipTier
  isActive: boolean
  createdAt: string
  updatedAt: string
}

/** 登录/注册成功结果。 */
export interface LoginResult {
  user: UserInfo
  token: string
  /** token 过期时间（ISO 8601） */
  expiresAt: string
}
