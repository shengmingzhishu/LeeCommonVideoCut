import { useCallback, useEffect, useState } from 'react'
import {
  Alert,
  Button,
  Card,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Switch,
  Table,
  Tabs,
  Tag,
  Typography,
  message,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'

import { ApiError } from '@/services/request'
import {
  adminService,
  type AdminConfigValues,
  type AdminMembershipValues,
  type AdminUserValues,
  type AuditLogValues,
  type ConfigTestValues,
} from '@/services/adminService'
import { TIER_LABEL } from '@/services/membershipService'
import type { MembershipTier } from '@/types/user.types'
import { useAuthStore } from '@/store/useAuthStore'

const TIER_OPTIONS = (['free', 'pro', 'enterprise'] as MembershipTier[]).map((t) => ({
  value: t,
  label: TIER_LABEL[t],
}))

/** 管理后台：用户管理 + 审计日志（仅管理员可见） */
export default function AdminPage() {
  const me = useAuthStore((s) => s.user)

  const [users, setUsers] = useState<AdminUserValues[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [keyword, setKeyword] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [pwdTarget, setPwdTarget] = useState<AdminUserValues | null>(null)
  const [pwdForm] = Form.useForm()

  const [logs, setLogs] = useState<AuditLogValues[]>([])
  const [logsLoading, setLogsLoading] = useState(false)

  const [memberships, setMemberships] = useState<AdminMembershipValues[]>([])
  const [membershipsLoading, setMembershipsLoading] = useState(false)
  const [assignOpen, setAssignOpen] = useState(false)
  const [assigning, setAssigning] = useState(false)
  const [assignForm] = Form.useForm()

  const [configs, setConfigs] = useState<AdminConfigValues[]>([])
  const [configsLoading, setConfigsLoading] = useState(false)
  const [configOpen, setConfigOpen] = useState(false)
  const [configSaving, setConfigSaving] = useState(false)
  const [configForm] = Form.useForm()

  const [testOpen, setTestOpen] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<ConfigTestValues | null>(null)
  const [testForm] = Form.useForm()

  const loadUsers = useCallback(async () => {
    setLoading(true)
    try {
      const res = await adminService.listUsers({ page, pageSize, keyword: keyword || undefined })
      setUsers(res.items)
      setTotal(res.total)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载用户列表失败')
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, keyword])

  useEffect(() => {
    void loadUsers()
  }, [loadUsers])

  const loadLogs = useCallback(async () => {
    setLogsLoading(true)
    try {
      const res = await adminService.listAuditLogs({ page: 1, pageSize: 30 })
      setLogs(res.items)
    } catch {
      setLogs([])
    } finally {
      setLogsLoading(false)
    }
  }, [])

  const loadMemberships = useCallback(async () => {
    setMembershipsLoading(true)
    try {
      const list = await adminService.listMemberships()
      setMemberships(list)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载会员列表失败')
    } finally {
      setMembershipsLoading(false)
    }
  }, [])

  const loadConfigs = useCallback(async () => {
    setConfigsLoading(true)
    try {
      setConfigs(await adminService.listConfigs())
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载全局配置失败')
    } finally {
      setConfigsLoading(false)
    }
  }, [])

  const openConfigModal = (cfg?: AdminConfigValues) => {
    configForm.setFieldsValue({
      key: cfg?.key ?? '',
      valueText: cfg ? JSON.stringify(cfg.value, null, 2) : '',
      description: cfg?.description ?? '',
    })
    setConfigOpen(true)
  }

  const handleSaveConfig = async () => {
    let values: { key: string; valueText: string; description?: string }
    try {
      values = await configForm.validateFields()
    } catch {
      return
    }
    let parsed: Record<string, unknown>
    try {
      const obj: unknown = JSON.parse(values.valueText)
      if (!obj || typeof obj !== 'object' || Array.isArray(obj)) {
        throw new Error('必须是 JSON 对象')
      }
      parsed = obj as Record<string, unknown>
    } catch (e) {
      setError(`配置值必须是合法 JSON 对象：${(e as Error).message}`)
      return
    }
    setConfigSaving(true)
    try {
      await adminService.saveConfig({
        key: values.key.trim(),
        value: parsed,
        description: values.description || null,
      })
      message.success('全局配置已保存')
      setConfigOpen(false)
      await loadConfigs()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '保存全局配置失败')
    } finally {
      setConfigSaving(false)
    }
  }

  const handleTestConnection = async () => {
    let values: { provider: string; apiKey?: string; baseUrl?: string; model?: string }
    try {
      values = await testForm.validateFields()
    } catch {
      return
    }
    setTesting(true)
    setTestResult(null)
    try {
      setTestResult(
        await adminService.testConnection({
          provider: values.provider,
          apiKey: values.apiKey ?? '',
          baseUrl: values.baseUrl,
          model: values.model,
        }),
      )
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '测试连接失败')
    } finally {
      setTesting(false)
    }
  }

  const handleAssignMembership = async () => {
    let values: { userId: string; tier: MembershipTier; expiresAt?: string; note?: string }
    try {
      values = await assignForm.validateFields()
    } catch {
      return
    }
    setAssigning(true)
    try {
      await adminService.assignMembership({
        userId: values.userId,
        tier: values.tier,
        expiresAt: values.expiresAt || null,
        note: values.note || null,
      })
      message.success('会员已分配')
      setAssignOpen(false)
      assignForm.resetFields()
      await Promise.all([loadMemberships(), loadUsers()])
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '分配会员失败')
    } finally {
      setAssigning(false)
    }
  }

  const handleCancelMembership = async (id: string) => {
    try {
      await adminService.cancelMembership(id)
      message.success('会员已停用')
      await loadMemberships()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '停用会员失败')
    }
  }

  const patchUser = async (
    userId: string,
    payload: { isAdmin?: boolean; isActive?: boolean; membershipTier?: MembershipTier },
  ) => {
    setError(null)
    try {
      const updated = await adminService.updateUser(userId, payload)
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)))
      message.success('已更新')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '更新失败')
    }
  }

  const handleResetPassword = async () => {
    if (!pwdTarget) return
    let values: { newPassword: string }
    try {
      values = await pwdForm.validateFields()
    } catch {
      return
    }
    try {
      await adminService.resetPassword(pwdTarget.id, values.newPassword)
      message.success(`已重置 ${pwdTarget.username} 的密码`)
      setPwdTarget(null)
      pwdForm.resetFields()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '重置密码失败')
    }
  }

  const columns: ColumnsType<AdminUserValues> = [
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username',
      render: (_, r) => (
        <Space direction="vertical" size={0}>
          <Space>
            <Typography.Text strong>{r.username}</Typography.Text>
            {r.isAdmin && <Tag color="gold">管理员</Tag>}
            {r.id === me?.id && <Tag color="blue">我</Tag>}
          </Space>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            {r.displayName || '—'} {r.email ? `· ${r.email}` : ''}
          </Typography.Text>
        </Space>
      ),
    },
    {
      title: '会员等级',
      dataIndex: 'membershipTier',
      key: 'tier',
      width: 150,
      render: (v: MembershipTier, r) => (
        <Select
          size="small"
          value={v}
          options={TIER_OPTIONS}
          style={{ width: 110 }}
          onChange={(next) => void patchUser(r.id, { membershipTier: next })}
        />
      ),
    },
    {
      title: '管理员',
      dataIndex: 'isAdmin',
      key: 'isAdmin',
      width: 90,
      render: (v: boolean, r) => (
        <Switch
          size="small"
          checked={v}
          disabled={r.id === me?.id}
          onChange={(next) => void patchUser(r.id, { isAdmin: next })}
        />
      ),
    },
    {
      title: '启用',
      dataIndex: 'isActive',
      key: 'isActive',
      width: 80,
      render: (v: boolean, r) => (
        <Switch
          size="small"
          checked={v}
          disabled={r.id === me?.id}
          onChange={(next) => void patchUser(r.id, { isActive: next })}
        />
      ),
    },
    {
      title: '注册时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
      render: (v: string) => (v ? new Date(v).toLocaleString('zh-CN') : '—'),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, r) => (
        <Button size="small" onClick={() => setPwdTarget(r)}>
          重置密码
        </Button>
      ),
    },
  ]

  const membershipColumns: ColumnsType<AdminMembershipValues> = [
    {
      title: '用户',
      dataIndex: 'userId',
      key: 'userId',
      render: (v: string) => users.find((u) => u.id === v)?.username ?? v,
    },
    {
      title: '等级',
      dataIndex: 'tier',
      key: 'tier',
      width: 120,
      render: (v: string) => <Tag>{TIER_LABEL[v as MembershipTier] ?? v}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (v: string) => (
        <Tag color={v === 'active' ? 'green' : 'default'}>{v === 'active' ? '生效中' : '已停用'}</Tag>
      ),
    },
    {
      title: '开始',
      dataIndex: 'startedAt',
      key: 'startedAt',
      width: 180,
      render: (v: string) => (v ? new Date(v).toLocaleString('zh-CN') : '—'),
    },
    {
      title: '到期',
      dataIndex: 'expiresAt',
      key: 'expiresAt',
      width: 180,
      render: (v: string | null) => (v ? new Date(v).toLocaleString('zh-CN') : '长期'),
    },
    {
      title: '备注',
      dataIndex: 'note',
      key: 'note',
      ellipsis: true,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, r) =>
        r.status === 'active' ? (
          <Popconfirm title="确认停用该会员？" onConfirm={() => void handleCancelMembership(r.id)}>
            <Button size="small" danger>
              停用
            </Button>
          </Popconfirm>
        ) : (
          <Typography.Text type="secondary">—</Typography.Text>
        ),
    },
  ]

  const logColumns: ColumnsType<AuditLogValues> = [
    {
      title: '时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
      render: (v: string) => (v ? new Date(v).toLocaleString('zh-CN') : '—'),
    },
    { title: '操作', dataIndex: 'action', key: 'action', width: 180 },
    {
      title: '对象',
      key: 'target',
      width: 200,
      render: (_, r) => `${r.targetType} / ${r.targetId}`,
    },
    {
      title: '操作人',
      dataIndex: 'adminUserId',
      key: 'adminUserId',
      width: 200,
    },
  ]

  const configColumns: ColumnsType<AdminConfigValues> = [
    { title: '配置键', dataIndex: 'key', key: 'key', width: 160 },
    {
      title: '值（JSON）',
      dataIndex: 'value',
      key: 'value',
      ellipsis: true,
      render: (v: Record<string, unknown>) => (
        <Typography.Text code style={{ fontSize: 12 }}>
          {JSON.stringify(v)}
        </Typography.Text>
      ),
    },
    { title: '说明', dataIndex: 'description', key: 'description', render: (v) => v || '—' },
    {
      title: '更新时间',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      width: 180,
      render: (v: string) => (v ? new Date(v).toLocaleString('zh-CN') : '—'),
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_, r) => (
        <Button type="link" size="small" onClick={() => openConfigModal(r)}>
          编辑
        </Button>
      ),
    },
  ]

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Typography.Title level={4} style={{ margin: 0 }}>
        管理后台
      </Typography.Title>

      {error && <Alert type="error" message={error} showIcon closable onClose={() => setError(null)} />}

      <Tabs
        items={[
          {
            key: 'users',
            label: '用户管理',
            children: (
              <Card>
                <Space style={{ marginBottom: 16 }}>
                  <Input.Search
                    placeholder="搜索用户名 / 邮箱"
                    allowClear
                    style={{ width: 260 }}
                    onSearch={(v) => {
                      setPage(1)
                      setKeyword(v)
                    }}
                  />
                  <Button onClick={() => void loadUsers()}>刷新</Button>
                </Space>
                <Table
                  rowKey="id"
                  size="middle"
                  loading={loading}
                  columns={columns}
                  dataSource={users}
                  pagination={{
                    current: page,
                    pageSize,
                    total,
                    showSizeChanger: true,
                    showTotal: (t) => `共 ${t} 个用户`,
                    onChange: (p, ps) => {
                      setPage(p)
                      setPageSize(ps)
                    },
                  }}
                />
              </Card>
            ),
          },
          {
            key: 'memberships',
            label: '会员管理',
            children: (
              <Card>
                <Space style={{ marginBottom: 16 }}>
                  <Button type="primary" onClick={() => setAssignOpen(true)}>
                    分配 / 续期会员
                  </Button>
                  <Button onClick={() => void loadMemberships()} loading={membershipsLoading}>
                    刷新
                  </Button>
                </Space>
                <Table
                  rowKey="id"
                  size="middle"
                  loading={membershipsLoading}
                  columns={membershipColumns}
                  dataSource={memberships}
                  pagination={false}
                />
              </Card>
            ),
          },
          {
            key: 'configs',
            label: '全局配置',
            children: (
              <Card>
                <Space style={{ marginBottom: 16 }}>
                  <Button type="primary" onClick={() => openConfigModal()}>
                    新增配置
                  </Button>
                  <Button onClick={() => void loadConfigs()} loading={configsLoading}>
                    刷新
                  </Button>
                  <Button
                    onClick={() => {
                      setTestResult(null)
                      setTestOpen(true)
                    }}
                  >
                    测试连接
                  </Button>
                </Space>
                <Table
                  rowKey="key"
                  size="middle"
                  loading={configsLoading}
                  columns={configColumns}
                  dataSource={configs}
                  pagination={false}
                />
                <Typography.Paragraph type="secondary" style={{ marginTop: 12 }}>
                  全局配置对所有用户生效；用户级配置可覆盖全局值。
                </Typography.Paragraph>
              </Card>
            ),
          },
          {
            key: 'logs',
            label: '审计日志',
            children: (
              <Card>
                <Space style={{ marginBottom: 16 }}>
                  <Button onClick={() => void loadLogs()} loading={logsLoading}>
                    加载最近 30 条
                  </Button>
                  <Typography.Text type="secondary">
                    所有管理员写操作都会记录在此
                  </Typography.Text>
                </Space>
                <Table
                  rowKey="id"
                  size="middle"
                  loading={logsLoading}
                  columns={logColumns}
                  dataSource={logs}
                  pagination={false}
                />
              </Card>
            ),
          },
        ]}
        onChange={(key) => {
          if (key === 'logs' && logs.length === 0) void loadLogs()
          if (key === 'memberships' && memberships.length === 0) void loadMemberships()
          if (key === 'configs' && configs.length === 0) void loadConfigs()
        }}
      />

      <Modal
        title="分配 / 续期会员"
        open={assignOpen}
        onCancel={() => {
          setAssignOpen(false)
          assignForm.resetFields()
        }}
        onOk={() => void handleAssignMembership()}
        confirmLoading={assigning}
        okText="确认分配"
        cancelText="取消"
      >
        <Form form={assignForm} layout="vertical" initialValues={{ tier: 'pro' }}>
          <Form.Item
            label="用户"
            name="userId"
            rules={[{ required: true, message: '请选择用户' }]}
          >
            <Select
              showSearch
              optionFilterProp="label"
              placeholder="选择用户（当前页）"
              options={users.map((u) => ({ value: u.id, label: u.username }))}
            />
          </Form.Item>
          <Form.Item
            label="会员等级"
            name="tier"
            rules={[{ required: true, message: '请选择等级' }]}
          >
            <Select options={TIER_OPTIONS} />
          </Form.Item>
          <Form.Item label="到期时间（留空为长期）" name="expiresAt">
            <Input type="date" />
          </Form.Item>
          <Form.Item label="备注" name="note">
            <Input placeholder="例如：活动赠送" maxLength={200} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`重置密码：${pwdTarget?.username ?? ''}`}
        open={!!pwdTarget}
        onCancel={() => setPwdTarget(null)}
        onOk={() => void handleResetPassword()}
        okText="确认重置"
        cancelText="取消"
      >
        <Form form={pwdForm} layout="vertical">
          <Form.Item
            label="新密码"
            name="newPassword"
            rules={[{ required: true, message: '请输入新密码' }, { min: 6, message: '至少 6 位' }]}
          >
            <Input.Password placeholder="至少 6 位" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="全局配置"
        open={configOpen}
        onCancel={() => {
          setConfigOpen(false)
          configForm.resetFields()
        }}
        onOk={() => void handleSaveConfig()}
        confirmLoading={configSaving}
        okText="保存"
        cancelText="取消"
        width={640}
      >
        <Form form={configForm} layout="vertical">
          <Form.Item
            label="配置键"
            name="key"
            rules={[{ required: true, message: '请输入配置键' }, { max: 64, message: '最多 64 字符' }]}
          >
            <Input placeholder="如 minimax / deepseek / bing_search" />
          </Form.Item>
          <Form.Item
            label="配置值（JSON 对象）"
            name="valueText"
            rules={[{ required: true, message: '请输入 JSON 对象' }]}
            extra='例如 {"api_key": "sk-...", "base_url": "https://...", "model": "..."}'
          >
            <Input.TextArea rows={8} placeholder='{"api_key": "sk-..."}' />
          </Form.Item>
          <Form.Item label="说明" name="description">
            <Input placeholder="可选" maxLength={200} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="测试连接"
        open={testOpen}
        onCancel={() => {
          setTestOpen(false)
          testForm.resetFields()
          setTestResult(null)
        }}
        onOk={() => void handleTestConnection()}
        confirmLoading={testing}
        okText="开始测试"
        cancelText="关闭"
      >
        <Form form={testForm} layout="vertical" initialValues={{ provider: 'minimax' }}>
          <Form.Item label="服务商" name="provider" rules={[{ required: true }]}>
            <Select
              options={[
                { value: 'minimax', label: 'MiniMax' },
                { value: 'deepseek', label: 'DeepSeek' },
                { value: 'bing_search', label: 'Bing Search' },
              ]}
            />
          </Form.Item>
          <Form.Item label="API Key" name="apiKey">
            <Input.Password placeholder="sk-..." />
          </Form.Item>
          <Form.Item label="Base URL（可选）" name="baseUrl">
            <Input placeholder="留空使用默认地址" />
          </Form.Item>
          <Form.Item label="模型（可选）" name="model">
            <Input placeholder="留空使用默认模型" />
          </Form.Item>
        </Form>
        {testResult && (
          <Alert
            type={testResult.success ? 'success' : 'error'}
            showIcon
            message={testResult.success ? '连接成功' : '连接失败'}
            description={`${testResult.message}${
              testResult.latencyMs != null ? `（耗时 ${testResult.latencyMs} ms）` : ''
            }`}
          />
        )}
      </Modal>
    </Space>
  )
}