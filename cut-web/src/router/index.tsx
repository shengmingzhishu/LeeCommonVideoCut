import { lazy, Suspense, type ReactNode } from 'react'
import { Navigate, type RouteObject } from 'react-router-dom'

import AppLayout from '@/components/layout/AppLayout'
import { useAuthStore } from '@/store/useAuthStore'

const HomePage = lazy(() => import('@/pages/home/HomePage'))
const LoginPage = lazy(() => import('@/pages/login/LoginPage'))
const ProjectListPage = lazy(() => import('@/pages/project/ProjectListPage'))
const ProjectDetailPage = lazy(() => import('@/pages/project/ProjectDetailPage'))
const CreationWizardPage = lazy(() => import('@/pages/creation/CreationWizardPage'))
const ProfilePage = lazy(() => import('@/pages/profile/ProfilePage'))
const MembershipPage = lazy(() => import('@/pages/membership/MembershipPage'))
const AdminPage = lazy(() => import('@/pages/admin/AdminPage'))

function PageLoading() {
  return (
    <div style={{ padding: 64, textAlign: 'center', color: 'var(--text-secondary)' }}>加载中…</div>
  )
}

/** 懒加载页面统一 Suspense 包裹（react-stack 规则 §12.1）。 */
function lazyPage(node: ReactNode) {
  return <Suspense fallback={<PageLoading />}>{node}</Suspense>
}

/** 路由守卫（react-stack 规则 §6.2）：未登录重定向，带 redirect 回跳。 */
function ProtectedRoute({ children }: { children: ReactNode }) {
  const isLoggedIn = useAuthStore((s) => s.isLoggedIn)
  if (!isLoggedIn) {
    const redirect = encodeURIComponent(window.location.pathname + window.location.search)
    return <Navigate to={`/login?redirect=${redirect}`} replace />
  }
  return <>{children}</>
}

export const routes: RouteObject[] = [
  { path: '/login', element: lazyPage(<LoginPage />) },
  {
    // 登录后的应用主框架：左侧菜单 + 顶部 Header
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: lazyPage(<HomePage />) },
      { path: 'projects', element: lazyPage(<ProjectListPage />) },
      { path: 'projects/:projectId', element: lazyPage(<ProjectDetailPage />) },
      { path: 'creations/:creationId', element: lazyPage(<CreationWizardPage />) },
      { path: 'profile', element: lazyPage(<ProfilePage />) },
      { path: 'membership', element: lazyPage(<MembershipPage />) },
      { path: 'admin', element: lazyPage(<AdminPage />) },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
]