import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Alert, Button, Card, Col, Empty, List, Progress, Row, Space, Spin, Statistic, Tag, Typography } from 'antd'

import { AppstoreIcon, CrownIcon, PlayIcon, PlusIcon, ScissorIcon, SparkIcon } from '@/components/icons'
import { ApiError } from '@/services/request'
import { projectService, type ProjectValues } from '@/services/projectService'
import { membershipService, TIER_LABEL, formatLimit, type QuotaValues } from '@/services/membershipService'
import { useAuthStore } from '@/store/useAuthStore'

function percent(used: number, limit: number): number {
  if (limit < 0) return 0
  if (limit === 0) return 0
  return Math.min(100, Math.round((used / limit) * 100))
}

/** 工作台首页：配额概览 + 最近项目 + 三步流程快捷入口 */
export default function HomePage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)

  const [quota, setQuota] = useState<QuotaValues | null>(null)
  const [projects, setProjects] = useState<ProjectValues[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    setLoading(true)
    Promise.all([
      membershipService.getMyQuota().catch(() => null),
      projectService.list({ page: 1, pageSize: 6 }).catch((err: ApiError) => {
        if (alive) setError(err.message || '加载项目失败')
        return null
      }),
    ])
      .then(([q, page]) => {
        if (!alive) return
        setQuota(q)
        if (page) setProjects(page.items)
      })
      .finally(() => alive && setLoading(false))
    return () => {
      alive = false
    }
  }, [])

  const heroStyle: React.CSSProperties = {
    background: 'linear-gradient(120deg, rgba(124,58,237,0.28), rgba(216,90,48,0.12) 60%, transparent)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-card)',
    padding: '26px 28px',
    position: 'relative',
    overflow: 'hidden',
  }

  return (
    <Space direction="vertical" size={20} style={{ width: '100%' }}>
      {/* 顶部欢迎 + 快捷入口 */}
      <div style={heroStyle}>
        <Row align="middle" gutter={[16, 16]}>
          <Col flex="auto">
            <Typography.Title level={3} style={{ margin: 0 }}>
              你好，{user?.displayName || user?.username} 👋
            </Typography.Title>
            <Typography.Paragraph style={{ margin: '8px 0 0', color: 'var(--text-secondary)' }}>
              三步完成一条漫剧推广素材：<strong>口播与素材</strong> → <strong>预览与裁切</strong> → <strong>合成报告</strong>
            </Typography.Paragraph>
            <Space style={{ marginTop: 16 }} wrap>
              <Button type="primary" size="large" icon={<PlusIcon />} onClick={() => navigate('/projects?create=1')}>
                新建项目
              </Button>
              <Button size="large" icon={<AppstoreIcon />} onClick={() => navigate('/projects')}>
                我的项目
              </Button>
              <Button size="large" icon={<CrownIcon />} onClick={() => navigate('/membership')}>
                会员与配额
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {error && <Alert type="error" message={error} showIcon closable onClose={() => setError(null)} />}

      {/* 配额统计 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="项目数"
              value={quota?.projectsUsed ?? projects.length}
              suffix={quota ? `/ ${formatLimit(quota.projectsLimit)}` : ''}
              prefix={<AppstoreIcon size={18} style={{ color: 'var(--primary-hover)', marginRight: 6 }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="会员等级"
              value={TIER_LABEL[quota?.tier ?? user?.membershipTier ?? 'free']}
              valueStyle={{ fontSize: 22, color: 'var(--warning)' }}
              prefix={<CrownIcon size={18} style={{ marginRight: 6 }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={`本月 AI 调用（${quota?.currentPeriod || '—'}）`}
              value={quota?.monthlyStepCallsUsed ?? 0}
              suffix={quota ? `/ ${formatLimit(quota.monthlyStepCallsLimit)}` : ''}
              prefix={<SparkIcon size={18} style={{ color: 'var(--info)', marginRight: 6 }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <Typography.Text type="secondary" style={{ fontSize: 14 }}>
                存储用量
              </Typography.Text>
              <Progress
                percent={quota ? percent(quota.storageUsedMb, quota.storageLimitMb) : 0}
                strokeColor="var(--primary)"
                size={['100%', 8]}
                showInfo={false}
              />
              <Typography.Text style={{ fontSize: 20, fontWeight: 600 }}>
                {quota?.storageUsedMb ?? 0} MB
                <Typography.Text type="secondary" style={{ fontSize: 13 }}>
                  {' '}/ {quota ? formatLimit(quota.storageLimitMb, ' MB') : '—'}
                </Typography.Text>
              </Typography.Text>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 最近项目 + 流程指引 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={15}>
          <Card
            title="最近项目"
            extra={<Button type="link" onClick={() => navigate('/projects')}>全部项目 →</Button>}
          >
            {loading ? (
              <div style={{ padding: 24, textAlign: 'center' }}><Spin /></div>
            ) : projects.length === 0 ? (
              <Empty description="还没有项目">
                <Button type="primary" onClick={() => navigate('/projects?create=1')}>创建第一个项目</Button>
              </Empty>
            ) : (
              <List
                dataSource={projects}
                renderItem={(p) => (
                  <List.Item
                    actions={[
                      <Button key="open" type="link" onClick={() => navigate(`/projects/${p.id}`)}>
                        进入
                      </Button>,
                    ]}
                  >
                    <List.Item.Meta
                      avatar={<span style={{ fontSize: 24 }}>{p.cover || '🎬'}</span>}
                      title={
                        <Space>
                          <span>{p.title}</span>
                          <Tag color={p.status === 'active' ? 'green' : 'default'}>{p.status}</Tag>
                        </Space>
                      }
                      description={
                        <Typography.Text type="secondary" ellipsis style={{ maxWidth: 520 }}>
                          {p.author ? `作者：${p.author} · ` : ''}
                          {p.intro || '暂无简介'}
                        </Typography.Text>
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>

        <Col xs={24} lg={9}>
          <Card title="三步创作流程">
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              {[
                {
                  n: '01',
                  title: '口播与素材',
                  desc: '生成口播长文，上传视频素材并按秒分段',
                  icon: <SparkIcon size={18} />,
                  to: '/projects',
                },
                {
                  n: '02',
                  title: '预览与裁切',
                  desc: '依据口播时长挑片段，实时串播预览',
                  icon: <ScissorIcon size={18} />,
                  to: '/projects',
                },
                {
                  n: '03',
                  title: '合成与报告',
                  desc: '一键合成，查看历史版本并下载',
                  icon: <PlayIcon size={18} />,
                  to: '/projects',
                },
              ].map((s) => (
                <div
                  key={s.n}
                  onClick={() => navigate(s.to)}
                  style={{
                    display: 'flex',
                    gap: 14,
                    alignItems: 'flex-start',
                    cursor: 'pointer',
                    padding: '10px 12px',
                    borderRadius: 10,
                    background: 'var(--surface-2)',
                    border: '1px solid var(--border)',
                    transition: 'var(--transition)',
                  }}
                >
                  <div
                    style={{
                      minWidth: 34,
                      height: 34,
                      borderRadius: 9,
                      display: 'grid',
                      placeItems: 'center',
                      background: 'rgba(124,58,237,0.18)',
                      color: 'var(--primary-hover)',
                    }}
                  >
                    {s.icon}
                  </div>
                  <div>
                    <Typography.Text strong>
                      <span style={{ color: 'var(--text-muted)', marginRight: 6 }}>{s.n}</span>
                      {s.title}
                    </Typography.Text>
                    <Typography.Paragraph style={{ margin: 0, color: 'var(--text-secondary)', fontSize: 13 }}>
                      {s.desc}
                    </Typography.Paragraph>
                  </div>
                </div>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>
    </Space>
  )
}