import { useEffect, useMemo, useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  Avatar,
  Badge,
  Button,
  Dropdown,
  Layout,
  Menu,
  Space,
  Tag,
  Tooltip,
  Typography,
} from 'antd'
import {
  AppstoreIcon,
  CrownIcon,
  DashboardIcon,
  LogoutIcon,
  MenuFoldIcon,
  MenuUnfoldIcon,
  ShieldIcon,
  UserIcon,
  VideoIcon,
} from '@/components/icons'

import { authService } from '@/services/authService'
import { healthService, type HealthStatus } from '@/services/healthService'
import { TIER_LABEL } from '@/services/membershipService'
import { useAuthStore } from '@/store/useAuthStore'

const { Header, Sider, Content } = Layout

/** 菜单 key → 顶部标题 */
const TITLE_BY_PATH: Record<string, string> = {
  '/': '工作台',
  '/projects': '项目管理',
  '/profile': '个人中心',
  '/membership': '会员中心',
  '/admin': '管理后台',
}

/** 根据路径推导当前选中菜单（v5：全局左侧菜单 + 顶部 Header） */
function resolveSelectedKey(pathname: string): string {
  if (pathname.startsWith('/projects') || pathname.startsWith('/creations')) return '/projects'
  if (pathname.startsWith('/profile')) return '/profile'
  if (pathname.startsWith('/membership')) return '/membership'
  if (pathname.startsWith('/admin')) return '/admin'
  return '/'
}

/** 应用主框架：左侧菜单 + 顶部 Header + 内容区 Outlet。 */
export default function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const user = useAuthStore((s) => s.user)
  const clearAuth = useAuthStore((s) => s.clearAuth)

  const [collapsed, setCollapsed] = useState(false)
  const [health, setHealth] = useState<HealthStatus | null>(null)

  useEffect(() => {
    healthService
      .getHealth()
      .then((res) => setHealth(res.data))
      .catch(() => setHealth(null))
  }, [])

  const selectedKey = useMemo(() => resolveSelectedKey(location.pathname), [location.pathname])

  /** 顶部标题：向导页与项目详情页单独命名，避免出现「项目管理」错位 */
  const pageTitle = useMemo(() => {
    if (location.pathname.startsWith('/creations/')) return '创作向导'
    if (location.pathname.startsWith('/projects/')) return '项目详情'
    return TITLE_BY_PATH[resolveSelectedKey(location.pathname)] ?? '工作台'
  }, [location.pathname])

  const menuItems = useMemo(() => {
    const items = [
      { key: '/', icon: <DashboardIcon />, label: '工作台' },
      { key: '/projects', icon: <AppstoreIcon />, label: '项目管理' },
      { key: '/creations', icon: <VideoIcon />, label: '创作中心', disabled: true },
      { key: '/profile', icon: <UserIcon />, label: '个人中心' },
      { key: '/membership', icon: <CrownIcon />, label: '会员中心' },
    ]
    if (user?.isAdmin) {
      items.push({ key: '/admin', icon: <ShieldIcon />, label: '管理后台', disabled: false })
    }
    return items
  }, [user?.isAdmin])

  const handleLogout = async () => {
    try {
      await authService.logout()
    } catch {
      // 登出接口失败不阻塞本地清理（JWT 无状态）
    }
    clearAuth()
    navigate('/login', { replace: true })
  }

  const healthOk = health?.status === 'ok'

  return (
    <Layout style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        trigger={null}
        width={220}
        style={{
          background: 'var(--surface)',
          borderRight: '1px solid var(--border)',
          position: 'sticky',
          top: 0,
          height: '100vh',
          overflow: 'auto',
        }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: collapsed ? '0 20px' : '0 18px',
            borderBottom: '1px solid var(--border)',
            cursor: 'pointer',
          }}
          onClick={() => navigate('/')}
        >
          <span style={{ fontSize: 22 }}>🎬</span>
          {!collapsed && (
            <div style={{ lineHeight: 1.2 }}>
              <Typography.Text strong style={{ fontSize: 14, display: 'block' }}>
                漫剧剪辑师
              </Typography.Text>
              <Typography.Text type="secondary" style={{ fontSize: 11 }}>
                v4.0 前后端分离版
              </Typography.Text>
            </div>
          )}
        </div>

        <Menu
          mode="inline"
          theme="dark"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => {
            if (key === '/creations') return
            navigate(key)
          }}
          style={{ background: 'transparent', borderInlineEnd: 'none', paddingTop: 8 }}
        />
      </Sider>

      <Layout style={{ background: 'var(--bg)' }}>
        <Header
          style={{
            height: 64,
            lineHeight: '64px',
            padding: '0 24px',
            background: 'var(--surface)',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            position: 'sticky',
            top: 0,
            zIndex: 10,
          }}
        >
          <Space size={12}>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldIcon /> : <MenuFoldIcon />}
              onClick={() => setCollapsed((v) => !v)}
            />
            <Typography.Text strong style={{ fontSize: 15 }}>
              {pageTitle}
            </Typography.Text>
          </Space>

          <Space size={16}>
            <Tooltip title="后端服务状态（/api/health）">
              <Badge
                status={healthOk ? 'success' : 'error'}
                text={
                  <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
                    {healthOk ? `服务正常 · v${health?.version ?? '—'}` : '后端未连接'}
                  </span>
                }
              />
            </Tooltip>

            <Dropdown
              menu={{
                items: [
                  { key: 'profile', icon: <UserIcon />, label: '个人中心' },
                  { key: 'membership', icon: <CrownIcon />, label: '会员中心' },
                  { type: 'divider' },
                  { key: 'logout', icon: <LogoutIcon />, label: '退出登录', danger: true },
                ],
                onClick: ({ key }) => {
                  if (key === 'logout') void handleLogout()
                  else navigate(`/${key}`)
                },
              }}
              placement="bottomRight"
            >
              <Space style={{ cursor: 'pointer' }} size={8}>
                <Avatar size={30} style={{ background: 'var(--primary)' }}>
                  {(user?.displayName || user?.username || 'U').slice(0, 1).toUpperCase()}
                </Avatar>
                <div style={{ lineHeight: 1.3 }}>
                  <Typography.Text style={{ fontSize: 13, display: 'block' }}>
                    {user?.displayName || user?.username}
                  </Typography.Text>
                  <Typography.Text type="secondary" style={{ fontSize: 11 }}>
                    {TIER_LABEL[user?.membershipTier ?? 'free']}
                  </Typography.Text>
                </div>
                {user?.isAdmin && <Tag color="gold" style={{ marginInlineEnd: 0 }}>管理员</Tag>}
              </Space>
            </Dropdown>
          </Space>
        </Header>

        <Content style={{ padding: 24, overflow: 'auto' }}>
          <div style={{ maxWidth: 1360, margin: '0 auto' }}>
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}