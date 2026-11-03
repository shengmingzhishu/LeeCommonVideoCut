import { useEffect, useState } from 'react'
import { Alert, Card, Col, Descriptions, Row, Space, Spin, Tag, Typography } from 'antd'

import { CrownIcon } from '@/components/icons'
import { ApiError } from '@/services/request'
import {
  membershipService,
  TIER_LABEL,
  formatLimit,
  type MembershipValues,
  type QuotaValues,
} from '@/services/membershipService'

const TIER_PLAN = [
  {
    tier: 'free',
    price: '免费',
    color: 'default',
    features: ['3 个项目', '每月 50 次 AI 调用', '500 MB 存储'],
  },
  {
    tier: 'pro',
    price: '专业版',
    color: 'gold',
    features: ['20 个项目', '每月 500 次 AI 调用', '5 GB 存储'],
  },
  {
    tier: 'enterprise',
    price: '企业版',
    color: 'purple',
    features: ['项目数量不限', 'AI 调用不限', '存储不限'],
  },
] as const

/** 会员中心：当前等级 + 配额明细 + 等级权益对比 */
export default function MembershipPage() {
  const [membership, setMembership] = useState<MembershipValues | null>(null)
  const [quota, setQuota] = useState<QuotaValues | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    Promise.all([membershipService.getMine(), membershipService.getMyQuota()])
      .then(([m, q]) => {
        if (!alive) return
        setMembership(m)
        setQuota(q)
      })
      .catch((err: ApiError) => alive && setError(err.message || '加载会员信息失败'))
      .finally(() => alive && setLoading(false))
    return () => {
      alive = false
    }
  }, [])

  if (loading) {
    return (
      <Card>
        <Spin />
      </Card>
    )
  }

  const currentTier = quota?.tier ?? 'free'

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Typography.Title level={4} style={{ margin: 0 }}>
        会员中心
      </Typography.Title>

      {error && <Alert type="error" message={error} showIcon closable onClose={() => setError(null)} />}

      <Card
        style={{
          background: 'linear-gradient(120deg, rgba(124,58,237,0.26), rgba(245,158,11,0.10) 70%, transparent)',
        }}
      >
        <Space align="center" size={18}>
          <div
            style={{
              width: 52,
              height: 52,
              borderRadius: 14,
              display: 'grid',
              placeItems: 'center',
              background: 'rgba(245,158,11,0.16)',
              color: 'var(--warning)',
            }}
          >
            <CrownIcon size={26} />
          </div>
          <div>
            <Typography.Title level={4} style={{ margin: 0 }}>
              当前等级：{TIER_LABEL[currentTier]}
            </Typography.Title>
            <Typography.Text type="secondary">
              {membership?.expiresAt
                ? `有效期至 ${new Date(membership.expiresAt).toLocaleDateString('zh-CN')}`
                : '长期有效（升级请联系管理员）'}
            </Typography.Text>
          </div>
        </Space>
      </Card>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="配额明细">
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="统计周期">{quota?.currentPeriod || '—'}</Descriptions.Item>
              <Descriptions.Item label="项目数">
                {quota?.projectsUsed ?? 0} / {formatLimit(quota?.projectsLimit ?? 0)}
              </Descriptions.Item>
              <Descriptions.Item label="本月 AI 调用">
                {quota?.monthlyStepCallsUsed ?? 0} / {formatLimit(quota?.monthlyStepCallsLimit ?? 0)}
              </Descriptions.Item>
              <Descriptions.Item label="存储用量">
                {quota?.storageUsedMb ?? 0} MB / {formatLimit(quota?.storageLimitMb ?? 0, ' MB')}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="等级权益">
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              {TIER_PLAN.map((plan) => {
                const active = plan.tier === currentTier
                return (
                  <div
                    key={plan.tier}
                    style={{
                      padding: '12px 14px',
                      borderRadius: 10,
                      border: `1px solid ${active ? 'var(--primary)' : 'var(--border)'}`,
                      background: active ? 'rgba(124,58,237,0.12)' : 'var(--surface-2)',
                    }}
                  >
                    <Space style={{ marginBottom: 6 }}>
                      <Typography.Text strong>{plan.price}</Typography.Text>
                      {active && <Tag color="purple">当前</Tag>}
                    </Space>
                    <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
                      {plan.features.join(' · ')}
                    </div>
                  </div>
                )
              })}
            </Space>
          </Card>
        </Col>
      </Row>
    </Space>
  )
}