import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'

import type { UserInfo } from '@/types/user.types'

interface AuthState {
  token: string | null
  user: UserInfo | null
  isLoggedIn: boolean
  setAuth: (token: string, user: UserInfo) => void
  setUser: (user: UserInfo) => void
  clearAuth: () => void
}

/**
 * 登录态全局 Store（react-stack 规则 §5）。
 * Token 只允许内存 + sessionStorage，禁止 localStorage（§11.3）。
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isLoggedIn: false,
      setAuth: (token, user) => set({ token, user, isLoggedIn: true }),
      setUser: (user) => set({ user }),
      clearAuth: () => set({ token: null, user: null, isLoggedIn: false }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({ token: state.token, user: state.user, isLoggedIn: state.isLoggedIn }),
    },
  ),
)
