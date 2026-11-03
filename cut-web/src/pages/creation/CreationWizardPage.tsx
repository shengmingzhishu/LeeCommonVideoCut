import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import {
  Alert,
  Button,
  Card,
  Empty,
  Modal,
  Space,
  Steps,
  Table,
  Tag,
  Typography,
  message,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'

import { ApiError } from '@/services/request'
import { taskService } from '@/services/taskService'
import {
  stepService,
  type OutputValues,
  type Step1FormValues,
  type Step1OutlineValues,
  type StepHistoryValues,
} from '@/services/stepService'
import Step1Panel from './step1/Step1Panel'
import Step2Panel from './step2/Step2Panel'
import Step3Panel from './step3/Step3Panel'

/** 三步名称：口播与素材 → 预览与裁切 → 合成与报告 */
const STEP_NAMES = ['口播与素材', '预览与裁切', '合成与报告']

/** 每步的引导文案（信息层级：目标 → 要点 → 解锁条件） */
const STEP_GUIDES = [
  {
    goal: '填写创作信息，生成口播长文与配音，并导入音视频素材',
    tips: [
      '标题 / 作者 / 风格 / 目标时长，生成大纲并保存',
      'AI 生成口播稿后可人工润色，选用音色完成配音',
      '批量上传视频素材，配音音频自动进入素材池',
    ],
  },
  {
    goal: '按配音时长生成视频切片，逐段换素材并虚拟串播预览',
    tips: ['一键随机标记，自动对齐音频总时长', '每段可单独换源视频、调整起止与转场', '预览不重编码，0 IO 秒开；确认后进入合成'],
  },
  {
    goal: '配置转场 / 人像 / 配乐 / 片头片尾，合成并回看历史成片',
    tips: [
      '全局转场 + 单段覆盖，时长 0.2~1.5s',
      '配乐闪避、片头片尾、封面导出、平台质量预设',
      '每次合成生成新版本，可预览 / 下载 / 返回裁切再编辑',
    ],
  },
]

interface OutputRow extends OutputValues {
  key: string
}

/**
 * 创作向导页：3 步流程 + 完成页。
 * 步骤锁定规则：前一步未完成时后续步骤不可点击。
 */
export default function CreationWizardPage() {
  const { creationId = '' } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const quickPrompt = searchParams.get('prompt') ?? ''

  const [currentStep, setCurrentStep] = useState(0)
  const [maxUnlocked, setMaxUnlocked] = useState(0)
  const [savedForm, setSavedForm] = useState<Step1FormValues | null>(null)
  const [savedOutline, setSavedOutline] = useState<Step1OutlineValues | null>(null)
  const [outputs, setOutputs] = useState<OutputRow[]>([])
  const [error, setError] = useState<string | null>(null)
  const [savingStep1, setSavingStep1] = useState(false)
  const [previewOpen, setPreviewOpen] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [previewTitle, setPreviewTitle] = useState('')
  const [previewingId, setPreviewingId] = useState<string | null>(null)
  const [downloadingId, setDownloadingId] = useState<string | null>(null)
  const [autoRunning, setAutoRunning] = useState(false)
  const [autoStage, setAutoStage] = useState('')
  /** 素材刷新令牌：TTS 产物就绪后驱动素材区重新加载 */
  const [mediaRefreshToken, setMediaRefreshToken] = useState(0)
  /** 历史版本（依赖 projectId，旧链接未带时可隐藏入口） */
  const projectId = searchParams.get('projectId') ?? ''
  const [historyOpen, setHistoryOpen] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyStep, setHistoryStep] = useState(1)
  const [historyRows, setHistoryRows] = useState<StepHistoryValues[]>([])
  const [rollingBack, setRollingBack] = useState<number | null>(null)

  /** 从「一句话创作」入口带入的预填表单 */
  const quickForm = useMemo<Step1FormValues | null>(() => {
    if (!quickPrompt) return null
    return {
      title: quickPrompt.slice(0, 30),
      author: 'AI 智能创作',
      intro: quickPrompt,
      style: '热血安利',
      targetDuration: 70,
      episodeIds: [],
      textFiles: [],
      keywords: [],
      refTitles: [],
      valuePoints: [],
      goals: ['random_story'],
    }
  }, [quickPrompt])

  const loadOutputs = useCallback(async () => {
    if (!creationId) return
    try {
      const list = await stepService.listOutputs(creationId)
      setOutputs(list.map((o) => ({ ...o, key: o.id })))
    } catch {
      // 未合成过时忽略
    }
  }, [creationId])

  useEffect(() => {
    void loadOutputs()
  }, [loadOutputs])

  // 刷新后恢复进度：Step1 表单/大纲 + Step2 长文是否存在，决定解锁到第几步
  useEffect(() => {
    if (!creationId) return
    let alive = true
    Promise.all([
      stepService.loadStep1(creationId).catch(() => null),
      stepService.loadArticle(creationId).catch(() => null),
    ]).then(([step1, article]) => {
      if (!alive) return
      if (step1?.form && step1.outline) {
        setSavedForm(step1.form)
        setSavedOutline(step1.outline)
      }
      const unlocked = article ? 1 : 0
      if (unlocked > 0) {
        setMaxUnlocked((prev) => Math.max(prev, unlocked))
        setCurrentStep((prev) => Math.max(prev, unlocked))
      }
    })
    return () => {
      alive = false
    }
  }, [creationId])

  // 已合成过成片时解锁「合成与报告」，刷新后可回到报告页
  useEffect(() => {
    if (outputs.length === 0) return
    setMaxUnlocked((prev) => Math.max(prev, 2))
    setCurrentStep((prev) => Math.max(prev, 2))
  }, [outputs.length])

  const handlePreview = async (record: OutputRow) => {
    setError(null)
    setPreviewingId(record.id)
    try {
      const url = await stepService.fetchOutputObjectUrl(creationId, record.id)
      setPreviewUrl(url)
      setPreviewTitle(`成片 v${record.version}`)
      setPreviewOpen(true)
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '预览失败')
    } finally {
      setPreviewingId(null)
    }
  }

  const handleClosePreview = () => {
    setPreviewOpen(false)
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(null)
  }

  const handleDownload = async (record: OutputRow) => {
    setError(null)
    setDownloadingId(record.id)
    try {
      await stepService.downloadOutput(creationId, record.id, `${creationId}_v${record.version}.mp4`)
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '下载失败')
    } finally {
      setDownloadingId(null)
    }
  }

  /** Step1 生成大纲后保存（停留在「口播与素材」，继续生成口播长文） */
  const handleOutlineReady = async (form: Step1FormValues, outline: Step1OutlineValues) => {
    setSavedForm(form)
    setSavedOutline(outline)
    setSavingStep1(true)
    setError(null)
    try {
      await stepService.saveStep1(creationId, form, outline)
      message.success('创作信息已保存，请继续生成口播长文')
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '保存失败')
    } finally {
      setSavingStep1(false)
    }
  }

  /** 口播与配音完成 → 进入「预览与裁切」 */
  const handleStep2Saved = () => {
    setMaxUnlocked((prev) => Math.max(prev, 1))
    setCurrentStep(1)
  }

  /** 切片确认 → 进入「合成与报告」 */
  const handleReadyToCompose = () => {
    setMaxUnlocked((prev) => Math.max(prev, 2))
    setCurrentStep(2)
  }

  /** 打开当前步骤的历史版本列表 */
  const openHistory = async (stepNo: number) => {
    if (!projectId) return
    setHistoryStep(stepNo)
    setHistoryOpen(true)
    setHistoryLoading(true)
    try {
      const rows = await stepService.listHistory(projectId, creationId, stepNo)
      setHistoryRows(rows)
    } catch (err) {
      setHistoryRows([])
      setError(err instanceof ApiError ? err.message : '获取历史版本失败')
    } finally {
      setHistoryLoading(false)
    }
  }

  /** 回滚到某个历史版本（后端复制为新版本），成功后刷新当前步骤内容 */
  const handleRollback = async (row: StepHistoryValues) => {
    if (!projectId) return
    setRollingBack(row.version)
    setError(null)
    try {
      const result = await stepService.rollbackStep(projectId, creationId, historyStep, row.version)
      message.success(`已回滚到 v${row.version}，生成新版本 v${result.version}`)
      if (historyStep === 1) {
        const step1 = await stepService.loadStep1(creationId)
        if (step1.form && step1.outline) {
          setSavedForm(step1.form)
          setSavedOutline(step1.outline)
        }
      } else if (historyStep === 2) {
        await stepService.loadArticle(creationId).catch(() => null)
      }
      const rows = await stepService.listHistory(projectId, creationId, historyStep)
      setHistoryRows(rows)
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}`
          : '回滚失败',
      )
    } finally {
      setRollingBack(null)
    }
  }

  const handleComposed = () => {
    message.success('成片已生成，报告已刷新')
    void loadOutputs()
  }

  /** 一句话成片：大纲 → 口播 → TTS → 随机标记 → 合成 → 完成页 */
  const runAutoPipeline = async () => {
    const form = savedForm ?? quickForm
    if (!form) {
      setError('缺少创作信息，请先填写 Step1 表单')
      return
    }

    setAutoRunning(true)
    setError(null)
    try {
      setAutoStage('1/6 生成大纲…')
      const outline = await stepService.generateOutline(creationId, form)
      setSavedForm(form)
      setSavedOutline(outline)

      setAutoStage('2/6 保存创作信息…')
      await stepService.saveStep1(creationId, form, outline)

      setAutoStage('3/6 生成口播长文…')
      const article = await stepService.generateArticle(creationId)

      setAutoStage('4/6 合成配音…')
      const saved = await stepService.saveArticle({
        creationId,
        title: article.title,
        content: article.content,
        wordCount: article.wordCount,
        skipTts: false,
      })
      if (saved.ttsTaskId) {
        const task = await taskService.poll(saved.ttsTaskId, (t) =>
          setAutoStage(`4/6 配音中 ${t.progress}%…`),
        )
        if (task.status !== 'completed') {
          throw new Error(task.error || '配音任务失败')
        }
      }
      setMaxUnlocked((prev) => Math.max(prev, 1))
      setCurrentStep(1)

      setAutoStage('5/6 扫描素材并生成标记…')
      const media = await stepService.getMediaList(creationId)
      const audios = [...media.systemAudios, ...media.customAudios].filter((a) => a.selected)
      if (audios.length === 0) throw new Error('没有可用配音音频，请回到第 1 步重新生成口播')
      if (media.videoFiles.length === 0) {
        throw new Error('项目未配置视频素材，请先在项目详情上传本地视频')
      }

      const remark = await stepService.remark({
        creationId,
        videoFiles: media.videoFiles.map((v) => v.name),
        targetDuration: null,
      })
      await stepService.saveState({
        creationId,
        audioFiles: audios,
        videoFiles: remark.videoFiles,
        deletedMedia: { audio_paths: [], video_paths: [] },
      })

      setAutoStage('6/6 合成成片…')
      const taskId = await stepService.compose({
        creationId,
        audioFiles: audios.map((a) => a.path),
        markers: remark.markers,
      })
      if (!taskId) throw new Error('合成任务提交失败')
      const task = await taskService.poll(taskId, (t) =>
        setAutoStage(`6/6 合成中 ${t.progress}%…`),
      )
      if (task.status !== 'completed') {
        throw new Error(task.error || '合成任务失败')
      }

      setAutoStage('合成完成')
      setMaxUnlocked((prev) => Math.max(prev, 2))
      setCurrentStep(2)
      message.success('一键生成成片完成')
      await loadOutputs()
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}`
          : err instanceof Error
            ? err.message
            : '自动成片失败',
      )
    } finally {
      setAutoRunning(false)
    }
  }

  const outputColumns: ColumnsType<OutputRow> = [
    {
      title: '版本',
      dataIndex: 'version',
      width: 80,
      render: (v: number, record) => (
        <Space>
          <span>v{v}</span>
          {record.isLatest && <Tag color="green">最新</Tag>}
        </Space>
      ),
    },
    { title: '文件', dataIndex: 'outputPath', ellipsis: true },
    { title: '时长', dataIndex: 'durationStr', width: 90 },
    { title: '大小', dataIndex: 'fileSize', width: 110, render: (v: number) => `${(v / 1024 / 1024).toFixed(1)} MB` },
    { title: '分辨率', dataIndex: 'resolution', width: 100 },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space size={4}>
          <Button
            type="link"
            size="small"
            loading={previewingId === record.id}
            onClick={() => void handlePreview(record)}
          >
            预览
          </Button>
          <Button
            type="link"
            size="small"
            loading={downloadingId === record.id}
            onClick={() => void handleDownload(record)}
          >
            下载
          </Button>
        </Space>
      ),
    },
  ]

  const historyColumns: ColumnsType<StepHistoryValues> = [
    { title: '版本', dataIndex: 'version', width: 80, render: (v: number) => `v${v}` },
    {
      title: '生成时间',
      dataIndex: 'createdAt',
      width: 190,
      render: (v: string) => (v ? new Date(v).toLocaleString('zh-CN') : '—'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          loading={rollingBack === record.version}
          onClick={() => void handleRollback(record)}
        >
          回滚到此版本
        </Button>
      ),
    },
  ]

  if (!creationId) {
    return <Empty description="缺少创作 ID" />
  }

  return (
    <div style={{ width: '100%' }}>
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Typography.Title level={4} style={{ margin: 0 }}>
              创作向导
            </Typography.Title>
            <Typography.Text type="secondary">
              第 {currentStep + 1}/3 步 · {STEP_NAMES[currentStep]} · 创作 {creationId}
            </Typography.Text>
          </div>
          <Button onClick={() => navigate('/projects')}>返回项目列表</Button>
        </div>

        {error && (
          <Alert type="error" message={error} showIcon closable onClose={() => setError(null)} />
        )}

        {(quickPrompt || savedForm) && (
          <Alert
            type="info"
            showIcon
            message="一句话生成成片"
            description={
              <Space direction="vertical" size={8} style={{ width: '100%' }}>
                {quickPrompt && <Typography.Text>提示词：{quickPrompt}</Typography.Text>}
                <Typography.Text type="secondary">
                  将自动串联：生成大纲 → 生成口播 → 配音 → 随机标记 → 合成。AI 额度不足时会提示失败原因。
                </Typography.Text>
                <Button
                  type="primary"
                  loading={autoRunning}
                  disabled={autoRunning}
                  onClick={() => void runAutoPipeline()}
                >
                  {autoRunning ? autoStage : '一键生成成片'}
                </Button>
              </Space>
            }
          />
        )}

        {autoRunning && (
          <Alert type="info" showIcon message={autoStage || '自动成片进行中…'} />
        )}

        {outputs.length > 0 && (
          <Alert
            type="success"
            showIcon
            message={`已有 ${outputs.length} 个成片`}
            description="可随时回到「合成与报告」预览、下载历史版本，或返回「预览与裁切」调整后再次合成。"
            action={
              <Button
                size="small"
                onClick={() => {
                  setMaxUnlocked((prev) => Math.max(prev, 2))
                  setCurrentStep(2)
                }}
              >
                查看成片
              </Button>
            }
          />
        )}

        <Card>
          <Steps
            current={currentStep}
            items={STEP_NAMES.map((title, i) => ({
              title,
              description:
                i < maxUnlocked || (i === 0 && savedOutline)
                  ? '已完成'
                  : i === currentStep
                    ? '进行中'
                    : '待解锁',
            }))}
            onChange={(step) => {
              if (step <= maxUnlocked) setCurrentStep(step)
            }}
          />

          <Space wrap size={8} style={{ marginTop: 12 }}>
            <Tag color="blue">第 {currentStep + 1}/3 步</Tag>
            <Tag color={maxUnlocked >= 1 ? 'green' : 'default'}>
              口播与素材 · {maxUnlocked >= 1 ? '配音已完成' : savedOutline ? '待生成口播' : '待开始'}
            </Tag>
            <Tag color={maxUnlocked >= 2 ? 'green' : 'default'}>
              预览与裁切 · {maxUnlocked >= 2 ? '切片已确认' : '待裁切'}
            </Tag>
            <Tag color={outputs.length > 0 ? 'green' : 'default'}>
              合成与报告 · {outputs.length > 0 ? `${outputs.length} 个成片` : '待合成'}
            </Tag>
            {projectId && (
              <Button size="small" onClick={() => void openHistory(currentStep + 1)}>
                第 {currentStep + 1} 步历史版本
              </Button>
            )}
          </Space>

          <Alert
            type="info"
            showIcon
            style={{ marginTop: 12 }}
            message={`本步目标：${STEP_GUIDES[currentStep].goal}`}
            description={
              <Space direction="vertical" size={2}>
                {STEP_GUIDES[currentStep].tips.map((tip) => (
                  <Typography.Text key={tip} type="secondary">
                    · {tip}
                  </Typography.Text>
                ))}
              </Space>
            }
          />

          <div style={{ marginTop: 12, display: 'flex', justifyContent: 'space-between' }}>
            <Button disabled={currentStep === 0} onClick={() => setCurrentStep((s) => s - 1)}>
              上一步
            </Button>
            {currentStep < 2 ? (
              <Button
                type="primary"
                disabled={currentStep === 0 && maxUnlocked < 1}
                onClick={() => {
                  if (currentStep === 1) handleReadyToCompose()
                  else setCurrentStep((s) => s + 1)
                }}
              >
                下一步：{STEP_NAMES[currentStep + 1]}
              </Button>
            ) : (
              <Button onClick={() => setCurrentStep(1)}>返回裁切</Button>
            )}
          </div>
        </Card>

        {currentStep === 0 && (
          <>
            <Step1Panel
              creationId={creationId}
              initialForm={savedForm ?? quickForm}
              initialOutline={savedOutline}
              onOutlineReady={handleOutlineReady}
            />
            {savedOutline ? (
              <Step2Panel
                creationId={creationId}
                onSaved={handleStep2Saved}
                onMediaUpdated={() => setMediaRefreshToken((v) => v + 1)}
              />
            ) : (
              <Alert
                type="info"
                showIcon
                message="先完成上方创作信息并生成大纲，口播长文与配音面板会自动出现"
              />
            )}
          </>
        )}

        <Step3Panel
          creationId={creationId}
          phase={currentStep === 0 ? 'materials' : currentStep === 1 ? 'edit' : 'compose'}
          refreshToken={mediaRefreshToken}
          onComposed={handleComposed}
          onNext={handleReadyToCompose}
        />

        {currentStep === 2 && (
          <Card
            title="合成报告 · 多次合成"
            extra={
              <Space>
                <Button onClick={() => setCurrentStep(1)}>返回裁切</Button>
                <Button type="primary" onClick={() => void loadOutputs()}>
                  刷新
                </Button>
              </Space>
            }
          >
            {outputs.length === 0 ? (
              <Empty description="还没有合成记录：完成上方参数配置后点击「一键合成」" />
            ) : (
              <Table size="small" columns={outputColumns} dataSource={outputs} pagination={false} />
            )}
            <Typography.Paragraph type="secondary" style={{ fontSize: 12, marginTop: 8, marginBottom: 0 }}>
              每次合成生成新版本；预览 / 下载不影响当前工程，点击「返回裁切」可调整切片后再次合成。
            </Typography.Paragraph>
          </Card>
        )}

        {savingStep1 && (
          <Typography.Text type="secondary">正在保存创作信息…</Typography.Text>
        )}
      </Space>

      <Modal
        title={`第 ${historyStep} 步历史版本`}
        open={historyOpen}
        onCancel={() => setHistoryOpen(false)}
        footer={null}
        width={640}
      >
        {historyRows.length === 0 && !historyLoading ? (
          <Empty description="该步骤暂无历史版本" />
        ) : (
          <Table
            size="small"
            loading={historyLoading}
            columns={historyColumns}
            dataSource={historyRows.map((h) => ({ ...h, key: h.id }))}
            pagination={false}
          />
        )}
      </Modal>

      <Modal
        title={previewTitle || '成片预览'}
        open={previewOpen}
        onCancel={handleClosePreview}
        footer={null}
        width={720}
        destroyOnClose
      >
        {previewUrl ? (
          <video
            src={previewUrl}
            controls
            autoPlay
            style={{ width: '100%', maxHeight: '70vh', background: '#000' }}
          />
        ) : null}
      </Modal>
    </div>
  )
}
