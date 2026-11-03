import { useEffect, useState } from 'react'
import {
  Alert,
  Button,
  Card,
  Checkbox,
  Col,
  Form,
  Input,
  InputNumber,
  Row,
  Select,
  Space,
  Spin,
  Tag,
  Typography,
} from 'antd'

import { stepService, type Step1FormValues, type Step1OutlineValues } from '@/services/stepService'
import { ApiError } from '@/services/request'

interface Step1PanelProps {
  creationId: string
  /** 刷新后恢复：已保存的表单 */
  initialForm?: Step1FormValues | null
  /** 刷新后恢复：已保存的大纲 */
  initialOutline?: Step1OutlineValues | null
  /** 大纲生成成功后回调（父组件负责保存） */
  onOutlineReady: (form: Step1FormValues, outline: Step1OutlineValues) => void
}

const STYLE_OPTIONS = [
  { label: '热血安利', value: '热血安利' },
  { label: '客观测评', value: '客观测评' },
  { label: '悬念种草', value: '悬念种草' },
  { label: '剧情向', value: '剧情向' },
]

/** 快捷选项 → 生成目标（与后端 GOAL_TEXT_MAP 对应） */
const GOAL_OPTIONS = [
  { label: '介绍关联剧集片段', value: 'intro_episode' },
  { label: '随机一个故事钩子', value: 'random_story' },
  { label: '随机一个有价值的人物', value: 'random_character' },
  { label: '随机一个任务视角', value: 'random_perspective' },
]

/** Step1 创作信息：表单 + AI 大纲 */
export default function Step1Panel({
  creationId,
  initialForm,
  initialOutline,
  onOutlineReady,
}: Step1PanelProps) {
  const [form] = Form.useForm<Step1FormValues>()
  const [outline, setOutline] = useState<Step1OutlineValues | null>(initialOutline ?? null)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 恢复已保存进度（父组件异步加载完成后传入）
  useEffect(() => {
    if (initialForm) form.setFieldsValue(initialForm)
  }, [initialForm, form])

  useEffect(() => {
    if (initialOutline) setOutline(initialOutline)
  }, [initialOutline])

  const handleGenerate = async () => {
    setError(null)
    let values: Step1FormValues
    try {
      values = await form.validateFields()
    } catch {
      return
    }

    setGenerating(true)
    try {
      const result = await stepService.generateOutline(creationId, values)
      setOutline(result)
      onOutlineReady(values, result)
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '生成大纲失败')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <Row gutter={16}>
      <Col xs={24} lg={12}>
        <Card title="创作信息" extra={<Button type="primary" loading={generating} onClick={handleGenerate}>生成大纲</Button>}>
          {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} closable onClose={() => setError(null)} />}
          <Form<Step1FormValues>
            form={form}
            layout="vertical"
            initialValues={{ style: '热血安利', targetDuration: 70, episodeIds: [], textFiles: [], keywords: [], refTitles: [], valuePoints: [], goals: [] }}
          >
            <Form.Item label="漫剧标题" name="title" rules={[{ required: true, message: '请输入漫剧标题' }]}>
              <Input placeholder="例如：斗破苍穹" maxLength={128} />
            </Form.Item>
            <Form.Item label="作者" name="author">
              <Input placeholder="例如：天蚕土豆" maxLength={128} />
            </Form.Item>
            <Form.Item label="简介" name="intro" rules={[{ required: true, message: '请输入简介' }]}>
              <Input.TextArea placeholder="用一段话介绍这部漫剧" rows={3} maxLength={2000} showCount />
            </Form.Item>
            <Row gutter={12}>
              <Col span={12}>
                <Form.Item label="文案风格" name="style">
                  <Select options={STYLE_OPTIONS} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="目标时长（秒）" name="targetDuration">
                  <InputNumber min={20} max={300} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item label="用户关键词" name="keywords">
              <Select mode="tags" placeholder="回车添加关键词" open={false} suffixIcon={null} />
            </Form.Item>
            <Form.Item label="参考标题" name="refTitles">
              <Select mode="tags" placeholder="回车添加参考标题" open={false} suffixIcon={null} />
            </Form.Item>
            <Form.Item label="补充价值点" name="valuePoints">
              <Select mode="tags" placeholder="回车添加价值点" open={false} suffixIcon={null} />
            </Form.Item>
            <Form.Item label="生成目标（快捷选项）" name="goals">
              <Checkbox.Group options={GOAL_OPTIONS} />
            </Form.Item>
          </Form>
        </Card>
      </Col>

      <Col xs={24} lg={12}>
        <Card title="AI 大纲">
          {generating && (
            <div style={{ textAlign: 'center', padding: '48px 0' }}>
              <Spin tip="AI 正在生成大纲…" />
            </div>
          )}
          {!generating && !outline && (
            <Typography.Text type="secondary">填写左侧表单后点击「生成大纲」。</Typography.Text>
          )}
          {outline && (
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              <div>
                <Typography.Text strong>核心关键词</Typography.Text>
                <div style={{ marginTop: 8 }}>
                  {outline.coreKeywords.map((k) => (
                    <Tag key={k} color="purple" style={{ marginBottom: 4 }}>{k}</Tag>
                  ))}
                  {outline.coreKeywords.length === 0 && <Typography.Text type="secondary">—</Typography.Text>}
                </div>
              </div>
              <div>
                <Typography.Text strong>核心词</Typography.Text>
                <div style={{ marginTop: 8 }}>
                  {outline.coreWords.map((k) => (
                    <Tag key={k} style={{ marginBottom: 4 }}>{k}</Tag>
                  ))}
                  {outline.coreWords.length === 0 && <Typography.Text type="secondary">—</Typography.Text>}
                </div>
              </div>
              <div>
                <Typography.Text strong>参考标题</Typography.Text>
                <div style={{ marginTop: 8 }}>
                  {outline.refTitles.map((t, i) => (
                    <div key={`${t.title}-${i}`} style={{ marginBottom: 8 }}>
                      <Tag color="blue">{t.title}</Tag>
                      {t.subtitle && <Typography.Text type="secondary"> {t.subtitle}</Typography.Text>}
                    </div>
                  ))}
                  {outline.refTitles.length === 0 && <Typography.Text type="secondary">—</Typography.Text>}
                </div>
              </div>
              <div>
                <Typography.Text strong>主要任务</Typography.Text>
                <Typography.Paragraph style={{ marginTop: 8, marginBottom: 0 }}>{outline.mainTask || '—'}</Typography.Paragraph>
              </div>
              <div>
                <Typography.Text strong>核心价值</Typography.Text>
                <div style={{ marginTop: 8 }}>
                  {outline.coreValue.map((v) => (
                    <Tag key={v} color="green" style={{ marginBottom: 4 }}>{v}</Tag>
                  ))}
                  {outline.coreValue.length === 0 && <Typography.Text type="secondary">—</Typography.Text>}
                </div>
              </div>
              <div>
                <Typography.Text strong>关键点</Typography.Text>
                <div style={{ marginTop: 8 }}>
                  {outline.keypoints.map((k) => (
                    <Tag key={k} color="orange" style={{ marginBottom: 4 }}>{k}</Tag>
                  ))}
                  {outline.keypoints.length === 0 && <Typography.Text type="secondary">—</Typography.Text>}
                </div>
              </div>
            </Space>
          )}
        </Card>
      </Col>
    </Row>
  )
}
