import { useEffect, useState } from 'react'
import {
  Alert,
  Button,
  Card,
  Col,
  Divider,
  Input,
  InputNumber,
  Progress,
  Row,
  Select,
  Slider,
  Space,
  Spin,
  Statistic,
  Switch,
  Tag,
  Typography,
} from 'antd'

import { ApiError } from '@/services/request'
import { stepService } from '@/services/stepService'
import { taskService, type TaskInfo } from '@/services/taskService'
import {
  DEFAULT_TTS_CONFIG,
  ttsService,
  type TTSConfigValues,
  type TTSVoiceValues,
} from '@/services/ttsService'

interface Step2PanelProps {
  creationId: string
  /** 保存成功回调（携带新的 currentStep） */
  onSaved: (currentStep: number) => void
}

/** 从正文拆分段落（与后端 `\n+` 规则一致） */
function splitParagraphs(text: string): string[] {
  return text.split(/\n+/).map((s) => s.trim()).filter(Boolean)
}

/** Step2 口播长文：AI 生成 + 编辑 + 多音色配音（试听 / 全局音色 / 按段落覆盖） */
export default function Step2Panel({ creationId, onSaved }: Step2PanelProps) {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [wordCount, setWordCount] = useState(0)
  const [skipTts, setSkipTts] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [ttsTask, setTtsTask] = useState<TaskInfo | null>(null)

  // 音色与配音配置
  const [voices, setVoices] = useState<TTSVoiceValues[]>([])
  const [ttsConfig, setTtsConfig] = useState<TTSConfigValues>({ ...DEFAULT_TTS_CONFIG })
  const [segmentVoices, setSegmentVoices] = useState<Record<number, string | null>>({})
  const [previewing, setPreviewing] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  // 加载音色目录
  useEffect(() => {
    let cancelled = false
    ttsService
      .listVoices()
      .then((list) => {
        if (!cancelled) setVoices(list)
      })
      .catch(() => {
        // 音色目录加载失败不阻塞编辑
      })
    return () => {
      cancelled = true
    }
  }, [])

  // 进入页面时加载已保存的长文与配音配置
  useEffect(() => {
    let cancelled = false
    stepService
      .loadArticle(creationId)
      .then((article) => {
        if (cancelled || !article) return
        setTitle(article.title ?? '')
        setContent(article.content ?? '')
        setWordCount(article.wordCount ?? 0)
        if (article.ttsConfig) {
          setTtsConfig(article.ttsConfig)
          const map: Record<number, string | null> = {}
          article.ttsConfig.segments.forEach((s) => {
            if (s.voiceId) map[s.index] = s.voiceId
          })
          setSegmentVoices(map)
        }
      })
      .catch(() => {
        // 未保存过时忽略
      })
    return () => {
      cancelled = true
    }
  }, [creationId])

  // 释放试听 blob URL
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const updateConfig = (patch: Partial<TTSConfigValues>) => {
    setTtsConfig((prev) => ({ ...prev, ...patch }))
  }

  const handlePreview = async () => {
    setError(null)
    setPreviewing(true)
    try {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
      const url = await ttsService.previewUrl({
        voiceId: ttsConfig.globalVoiceId,
        rate: ttsConfig.rate,
        pitch: ttsConfig.pitch,
        volume: ttsConfig.volume,
      })
      setPreviewUrl(url)
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '试听失败')
    } finally {
      setPreviewing(false)
    }
  }

  const handleGenerate = async () => {
    setError(null)
    setGenerating(true)
    try {
      const article = await stepService.generateArticle(creationId)
      setTitle(article.title ?? '')
      setContent(article.content ?? '')
      setWordCount(article.wordCount ?? 0)
      if (article.ttsConfig) setTtsConfig(article.ttsConfig)
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '生成口播长文失败')
    } finally {
      setGenerating(false)
    }
  }

  /** 组装含段落覆盖的完整配置（段落文本始终取当前正文，避免过期） */
  const buildTtsConfig = (): TTSConfigValues => {
    const paragraphs = splitParagraphs(content)
    return {
      ...ttsConfig,
      segments: paragraphs.map((text, index) => ({
        index,
        text,
        voiceId: segmentVoices[index] ?? null,
        rate: 0,
        pitch: 0,
        volume: 0,
        pauseAfterMs: ttsConfig.paragraphGapMs,
      })),
    }
  }

  const handleSave = async () => {
    if (!content.trim()) {
      setError('口播长文不能为空')
      return
    }
    setError(null)
    setSaving(true)
    try {
      const result = await stepService.saveArticle({
        creationId,
        title,
        content,
        wordCount,
        skipTts,
        ttsConfig: buildTtsConfig(),
      })
      onSaved(result.currentStep)
      if (result.ttsTaskId) {
        const task = await taskService.poll(result.ttsTaskId, setTtsTask)
        if (task.status === 'failed') {
          setError(`TTS 合成失败：${task.error ?? '未知错误'}`)
        }
      }
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '保存失败')
    } finally {
      setSaving(false)
    }
  }

  const paragraphs = splitParagraphs(content)
  const ttsMeta = ttsTask?.result as
    | { provider?: string; provider_label?: string; voice_id?: string; voices_used?: string[]; warning?: string }
    | undefined

  const voiceOptions = voices.map((v) => ({
    value: v.id,
    label: `${v.name} · ${v.style}`,
  }))

  return (
    <Row gutter={16}>
      <Col xs={24} lg={16}>
        <Card
          title="口播长文"
          extra={
            <Space>
              <Button onClick={handleGenerate} loading={generating}>重新生成</Button>
              <Button type="primary" onClick={handleSave} loading={saving}>保存并进入下一步</Button>
            </Space>
          }
        >
          {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} closable onClose={() => setError(null)} />}

          {generating ? (
            <div style={{ textAlign: 'center', padding: '48px 0' }}>
              <Spin tip="AI 正在创作口播长文…" />
            </div>
          ) : (
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Input
                placeholder="标题"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                maxLength={200}
              />
              <Input.TextArea
                placeholder="AI 生成的口播长文会显示在这里，可直接编辑"
                value={content}
                onChange={(e) => {
                  setContent(e.target.value)
                  setWordCount(e.target.value.replace(/\s/g, '').length)
                }}
                rows={18}
                maxLength={20000}
                showCount
              />
            </Space>
          )}
        </Card>

        <Card title="配音音色与节奏" style={{ marginTop: 16 }} extra={<Tag color="blue">{ttsConfig.provider}</Tag>}>
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <div>
              <Typography.Text strong>全局音色</Typography.Text>
              <Space.Compact style={{ width: '100%', marginTop: 8 }}>
                <Select
                  value={ttsConfig.globalVoiceId}
                  options={voiceOptions}
                  onChange={(id) => updateConfig({ globalVoiceId: id })}
                  style={{ flex: 1 }}
                  placeholder="选择音色"
                />
                <Button onClick={handlePreview} loading={previewing}>试听</Button>
              </Space.Compact>
              {voices.find((v) => v.id === ttsConfig.globalVoiceId) && (
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  {voices.find((v) => v.id === ttsConfig.globalVoiceId)?.description}
                </Typography.Text>
              )}
              {previewUrl && (
                <audio controls src={previewUrl} style={{ width: '100%', marginTop: 8 }} />
              )}
            </div>

            <Row gutter={16}>
              <Col span={8}>
                <Typography.Text>语速（{ttsConfig.rate >= 0 ? '+' : ''}{ttsConfig.rate}%）</Typography.Text>
                <Slider min={-50} max={50} value={ttsConfig.rate} onChange={(v) => updateConfig({ rate: v })} />
              </Col>
              <Col span={8}>
                <Typography.Text>音调（{ttsConfig.pitch >= 0 ? '+' : ''}{ttsConfig.pitch}Hz）</Typography.Text>
                <Slider min={-20} max={20} value={ttsConfig.pitch} onChange={(v) => updateConfig({ pitch: v })} />
              </Col>
              <Col span={8}>
                <Typography.Text>音量（{ttsConfig.volume >= 0 ? '+' : ''}{ttsConfig.volume}%）</Typography.Text>
                <Slider min={-50} max={50} value={ttsConfig.volume} onChange={(v) => updateConfig({ volume: v })} />
              </Col>
            </Row>

            <div>
              <Typography.Text strong>段落停顿</Typography.Text>
              <InputNumber
                min={0}
                max={3000}
                step={50}
                value={ttsConfig.paragraphGapMs}
                onChange={(v) => updateConfig({ paragraphGapMs: v ?? 300 })}
                addonAfter="毫秒"
                style={{ marginLeft: 12 }}
              />
            </div>

            {paragraphs.length > 1 && (
              <>
                <Divider style={{ margin: '8px 0' }} />
                <Typography.Text strong>按段落分配音色（可选覆盖）</Typography.Text>
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  共 {paragraphs.length} 段，未选择的段落沿用全局音色
                </Typography.Text>
                <Space direction="vertical" size={8} style={{ width: '100%' }}>
                  {paragraphs.map((text, index) => (
                    <Row key={index} gutter={8} align="middle">
                      <Col flex="auto">
                        <Typography.Text ellipsis style={{ maxWidth: '100%' }}>
                          {index + 1}. {text.slice(0, 48)}{text.length > 48 ? '…' : ''}
                        </Typography.Text>
                      </Col>
                      <Col flex="180px">
                        <Select
                          allowClear
                          placeholder="沿用全局"
                          value={segmentVoices[index] ?? undefined}
                          options={voiceOptions}
                          onChange={(id) => setSegmentVoices((prev) => ({ ...prev, [index]: id ?? null }))}
                          style={{ width: '100%' }}
                        />
                      </Col>
                    </Row>
                  ))}
                </Space>
              </>
            )}
          </Space>
        </Card>
      </Col>

      <Col xs={24} lg={8}>
        <Card title="状态">
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <Statistic title="字数" value={wordCount} suffix="字" />
            <Statistic title="预估时长" value={Math.round((wordCount / 3.5) * 10) / 10} suffix="秒" />
            <div>
              <Typography.Text strong>跳过自动 TTS</Typography.Text>
              <Typography.Paragraph type="secondary" style={{ fontSize: 12, marginBottom: 8 }}>
                开启后可在下一步手动上传录音
              </Typography.Paragraph>
              <Switch checked={skipTts} onChange={setSkipTts} />
            </div>
            {ttsTask && (
              <div>
                <Typography.Text strong>TTS 任务</Typography.Text>
                <Progress
                  percent={ttsTask.progress}
                  status={
                    ttsTask.status === 'completed'
                      ? 'success'
                      : ttsTask.status === 'failed'
                        ? 'exception'
                        : 'active'
                  }
                  style={{ marginTop: 8 }}
                />
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  {ttsTask.status}
                </Typography.Text>
                {ttsTask.status === 'completed' && ttsMeta && (
                  <div style={{ marginTop: 8 }}>
                    <Tag color="green">{ttsMeta.provider_label || ttsMeta.provider || 'edge-tts'}</Tag>
                    {ttsMeta.voice_id && <Tag>{ttsMeta.voice_id}</Tag>}
                    {Array.isArray(ttsMeta.voices_used) && ttsMeta.voices_used.length > 0 && (
                      <Typography.Paragraph type="secondary" style={{ fontSize: 12, marginTop: 6 }}>
                        段落音色：{ttsMeta.voices_used.join(' / ')}
                      </Typography.Paragraph>
                    )}
                    {ttsMeta.warning && (
                      <Alert type="warning" showIcon message={ttsMeta.warning} style={{ marginTop: 8 }} />
                    )}
                  </div>
                )}
              </div>
            )}
          </Space>
        </Card>
      </Col>
    </Row>
  )
}
