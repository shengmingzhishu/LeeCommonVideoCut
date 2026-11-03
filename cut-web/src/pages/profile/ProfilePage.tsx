import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Alert,
  Avatar,
  Button,
  Card,
  Descriptions,
  Form,
  Input,
  message,
  Progress,
  Row,
  Col,
  Space,
  Tag,
  Typography,
} from 'antd'

import { ApiError } from '@/services/request'
import { authService } from '@/services/authService'
import { membershipService, TIER_LABEL, formatLimit, type QuotaValues } from '@/services/membershipService'
import { useAuthStore } from '@/store/useAuthStore'

/** 个人中心：资料编辑 + 修改密码 + 配额概览 */
export default function ProfilePage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const setUser = useAuthStore((s) => s.setUser)

  const [quota, setQuota] = useState<QuotaValues | null>(null)
  const [saving, setSaving] = useState(false)
  const [pwdSaving, setPwdSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [profileForm] = Form.useForm()
  const [pwdForm] = Form.useForm()

  useEffect(() => {
    membershipService.getMyQuota().then(setQuota).catch(() => setQuota(null))
  }, [])

  useEffect(() => {
    profileForm.setFieldsValue({
      displayName: user?.displayName ?? '',
      avatarUrl: user?.avatarUrl ?? '',
      bio: user?.bio ?? '',
    })
  }, [user, profileForm])

  const handleSaveProfile = async () => {
    setError(null)
    let values: { displayName?: string; avatarUrl?: string; bio?: string }
    try {
      values = await profileForm.validateFields()
    } catch {
      return
    }
    setSaving(true)
    try {
      const next = await authService.updateMe(values)
      setUser(next)
      message.success('资料已保存')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '保存失败')
    } finally {
      setSaving(false)
    }
  }

  const handleChangePassword = async () => {
    setError(null)
    let values: { oldPassword: string; newPassword: string; confirmPassword: string }
    try {
      values = await pwdForm.validateFields()
    } catch {
      return
    }
    setPwdSaving(true)
    try {
      await authService.changePassword(values.oldPassword, values.newPassword)
      message.success('密码已修改，请重新登录')
      pwdForm.resetFields()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '修改密码失败')
    } finally {
      setPwdSaving(false)
    }
  }

  const storagePercent =
    quota && quota.storageLimitMb > 0
      ? Math.min(100, Math.round((quota.storageUsedMb / quota.storageLimitMb) * 100))
      : 0

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Typography.Title level={4} style={{ margin: 0 }}>
        个人中心
      </Typography.Title>

      {error && <Alert type="error" message={error} showIcon closable onClose={() => setError(null)} />}

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <Card title="基本资料">
            <Space size={20} align="start" style={{ marginBottom: 16 }}>
              <Avatar size={64} src={user?.avatarUrl || undefined} style={{ background: 'var(--primary)' }}>
                {(user?.displayName || user?.username || 'U').slice(0, 1).toUpperCase()}
              </Avatar>
              <Descriptions column={1} size="small">
                <Descriptions.Item label="用户名">{user?.username}</Descriptions.Item>
                <Descriptions.Item label="邮箱">{user?.email || '—'}</Descriptions.Item>
                <Descriptions.Item label="会员等级">
                  <Tag color={user?.membershipTier === 'free' ? 'default' : 'gold'}>
                    {TIER_LABEL[user?.membershipTier ?? 'free']}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="注册时间">
                  {user?.createdAt ? new Date(user.createdAt).toLocaleString('zh-CN') : '—'}
                </Descriptions.Item>
              </Descriptions>
            </Space>

            <Form form={profileForm} layout="vertical">
              <Form.Item label="昵称" name="displayName">
                <Input placeholder="展示用昵称" maxLength={64} />
              </Form.Item>
              <Form.Item label="头像地址" name="avatarUrl">
                <Input placeholder="https://..." maxLength={512} />
              </Form.Item>
              <Form.Item label="个人简介" name="bio">
                <Input.TextArea rows={3} maxLength={500} showCount placeholder="简单介绍一下自己" />
              </Form.Item>
              <Button type="primary" loading={saving} onClick={() => void handleSaveProfile()}>
                保存资料
              </Button>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Card
              title="我的配额"
              extra={<Button type="link" onClick={() => navigate('/membership')}>会员中心 →</Button>}
            >
              <Space direction="vertical" size={14} style={{ width: '100%' }}>
                <div>
                  <Typography.Text type="secondary">项目数</Typography.Text>
                  <Progress
                    percent={
                      quota && quota.projectsLimit > 0
                        ? Math.min(100, Math.round((quota.projectsUsed / quota.projectsLimit) * 100))
                        : 0
                    }
                    strokeColor="var(--primary)"
                    format={() => `${quota?.projectsUsed ?? 0}/${formatLimit(quota?.projectsLimit ?? 0)}`}
                  />
                </div>
                <div>
                  <Typography.Text type="secondary">本月 AI 调用</Typography.Text>
                  <Progress
                    percent={
                      quota && quota.monthlyStepCallsLimit > 0
                        ? Math.min(
                            100,
                            Math.round(
                              (quota.monthlyStepCallsUsed / quota.monthlyStepCallsLimit) * 100,
                            ),
                          )
                        : 0
                    }
                    strokeColor="var(--info)"
                    format={() =>
                      `${quota?.monthlyStepCallsUsed ?? 0}/${formatLimit(quota?.monthlyStepCallsLimit ?? 0)}`
                    }
                  />
                </div>
                <div>
                  <Typography.Text type="secondary">存储用量</Typography.Text>
                  <Progress
                    percent={storagePercent}
                    strokeColor="var(--success)"
                    format={() => `${quota?.storageUsedMb ?? 0} MB`}
                  />
                </div>
              </Space>
            </Card>

            <Card title="修改密码">
              <Form form={pwdForm} layout="vertical">
                <Form.Item
                  label="当前密码"
                  name="oldPassword"
                  rules={[{ required: true, message: '请输入当前密码' }]}
                >
                  <Input.Password placeholder="当前密码" />
                </Form.Item>
                <Form.Item
                  label="新密码"
                  name="newPassword"
                  rules={[{ required: true, message: '请输入新密码' }, { min: 6, message: '至少 6 位' }]}
                >
                  <Input.Password placeholder="至少 6 位" />
                </Form.Item>
                <Form.Item
                  label="确认新密码"
                  name="confirmPassword"
                  dependencies={['newPassword']}
                  rules={[
                    { required: true, message: '请再次输入新密码' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('newPassword') === value) {
                          return Promise.resolve()
                        }
                        return Promise.reject(new Error('两次输入不一致'))
                      },
                    }),
                  ]}
                >
                  <Input.Password placeholder="再次输入新密码" />
                </Form.Item>
                <Button loading={pwdSaving} onClick={() => void handleChangePassword()}>
                  修改密码
                </Button>
              </Form>
            </Card>
          </Space>
        </Col>
      </Row>
    </Space>
  )
}