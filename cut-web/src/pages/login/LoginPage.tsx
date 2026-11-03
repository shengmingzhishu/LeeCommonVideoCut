import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Alert, Button, Card, Form, Input, Tabs, Typography } from 'antd'

import { authService } from '@/services/authService'
import { ApiError } from '@/services/request'
import { useAuthStore } from '@/store/useAuthStore'

interface LoginFormValues {
  username: string
  password: string
}

interface RegisterFormValues {
  username: string
  password: string
  confirmPassword: string
  email?: string
  displayName?: string
}

export default function LoginPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const redirect = searchParams.get('redirect') || '/'
  const goNext = () => navigate(redirect, { replace: true })

  const handleLogin = async (values: LoginFormValues) => {
    setError(null)
    setSubmitting(true)
    try {
      const result = await authService.login(values.username, values.password)
      setAuth(result.token, result.user)
      goNext()
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '登录失败，请稍后重试')
    } finally {
      setSubmitting(false)
    }
  }

  const handleRegister = async (values: RegisterFormValues) => {
    setError(null)
    setSubmitting(true)
    try {
      const result = await authService.register({
        username: values.username,
        password: values.password,
        email: values.email || null,
        display_name: values.displayName || null,
      })
      setAuth(result.token, result.user)
      goNext()
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '注册失败，请稍后重试')
    } finally {
      setSubmitting(false)
    }
  }

  const loginTab = (
    <Form<LoginFormValues>
      layout="vertical"
      onFinish={handleLogin}
      autoComplete="off"
      initialValues={
        import.meta.env.DEV ? { username: 'admin', password: 'admin123456' } : undefined
      }
    >
      <Form.Item label="用户名" name="username" rules={[{ required: true, message: '请输入用户名' }]}>
        <Input placeholder="用户名" autoFocus />
      </Form.Item>
      <Form.Item label="密码" name="password" rules={[{ required: true, message: '请输入密码' }]}>
        <Input.Password placeholder="密码" />
      </Form.Item>
      <Button type="primary" htmlType="submit" block loading={submitting}>
        登录
      </Button>
      {import.meta.env.DEV && (
        <Typography.Text type="secondary" style={{ display: 'block', marginTop: 12, fontSize: 12 }}>
          开发环境已预填引导管理员账号（BOOTSTRAP_ADMIN_*），可直接点击登录。
        </Typography.Text>
      )}
    </Form>
  )

  const registerTab = (
    <Form<RegisterFormValues>
      layout="vertical"
      onFinish={handleRegister}
      autoComplete="off"
    >
      <Form.Item
        label="用户名"
        name="username"
        rules={[
          { required: true, message: '请输入用户名' },
          { min: 3, max: 32, message: '用户名 3~32 个字符' },
        ]}
      >
        <Input placeholder="用户名（3~32 个字符）" />
      </Form.Item>
      <Form.Item
        label="密码"
        name="password"
        rules={[
          { required: true, message: '请输入密码' },
          { min: 6, max: 64, message: '密码 6~64 位' },
        ]}
      >
        <Input.Password placeholder="密码（至少 6 位）" />
      </Form.Item>
      <Form.Item
        label="确认密码"
        name="confirmPassword"
        dependencies={['password']}
        rules={[
          { required: true, message: '请再次输入密码' },
          ({ getFieldValue }) => ({
            validator: (_, value) =>
              !value || value === getFieldValue('password')
                ? Promise.resolve()
                : Promise.reject(new Error('两次输入的密码不一致')),
          }),
        ]}
      >
        <Input.Password placeholder="再次输入密码" />
      </Form.Item>
      <Form.Item label="昵称" name="displayName">
        <Input placeholder="昵称（可选）" />
      </Form.Item>
      <Form.Item
        label="邮箱"
        name="email"
        rules={[{ type: 'email', message: '邮箱格式不正确' }]}
      >
        <Input placeholder="邮箱（可选）" />
      </Form.Item>
      <Button type="primary" htmlType="submit" block loading={submitting}>
        注册并登录
      </Button>
    </Form>
  )

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        padding: '40px 16px',
        background:
          'radial-gradient(1200px 500px at 15% -10%, rgba(124,58,237,0.28), transparent 60%), radial-gradient(900px 420px at 90% 110%, rgba(216,90,48,0.16), transparent 60%), var(--bg)',
      }}
    >
      <div style={{ width: '100%', maxWidth: 400 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 34 }}>🎬</div>
          <Typography.Title level={3} style={{ margin: '8px 0 4px' }}>
            漫剧推广素材剪辑师
          </Typography.Title>
          <Typography.Text type="secondary">
            口播长文 · 素材分段 · 预览裁切 · 一键合成
          </Typography.Text>
        </div>
        <Card>
          {error && (
            <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} closable onClose={() => setError(null)} />
          )}
          <Tabs
            centered
            items={[
              { key: 'login', label: '登录', children: loginTab },
              { key: 'register', label: '注册', children: registerTab },
            ]}
          />
        </Card>
      </div>
    </div>
  )
}
