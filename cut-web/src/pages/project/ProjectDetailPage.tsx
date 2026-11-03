import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Alert,
  Button,
  Card,
  Col,
  Empty,
  Form,
  Input,
  List,
  Modal,
  Row,
  Space,
  Spin,
  Tag,
  Typography,
  Upload,
} from 'antd'
import type { UploadFile } from 'antd/es/upload/interface'

import { ApiError } from '@/services/request'
import { fileService } from '@/services/fileService'
import {
  projectService,
  type CreationValues,
  type EpisodeValues,
  type ProjectValues,
} from '@/services/projectService'

/** 项目详情页：管理剧集 → 选择剧集创建创作 → 进入三步向导 */
export default function ProjectDetailPage() {
  const { projectId = '' } = useParams()
  const navigate = useNavigate()

  const [project, setProject] = useState<ProjectValues | null>(null)
  const [episodes, setEpisodes] = useState<EpisodeValues[]>([])
  const [creations, setCreations] = useState<CreationValues[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [episodeOpen, setEpisodeOpen] = useState(false)
  const [creationOpen, setCreationOpen] = useState(false)
  const [selectedEpisodeId, setSelectedEpisodeId] = useState('')
  const [episodeForm] = Form.useForm()
  const [creationForm] = Form.useForm()

  // 视频源配置
  const [videoOpen, setVideoOpen] = useState(false)
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [videoFileList, setVideoFileList] = useState<UploadFile[]>([])
  const [serverVideoDir, setServerVideoDir] = useState('')
  const [savingVideo, setSavingVideo] = useState(false)

  const load = useCallback(async () => {
    if (!projectId) return
    setLoading(true)
    try {
      const [detail, eps, crs] = await Promise.all([
        projectService.get(projectId).catch(() => null),
        projectService.listEpisodes(projectId),
        projectService.listCreations(projectId),
      ])
      setProject(detail)
      setEpisodes(eps)
      setCreations(crs)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    void load()
  }, [load])

  const openVideoConfig = () => {
    setServerVideoDir(project?.videoDir ?? '')
    setVideoFile(null)
    setVideoFileList([])
    setVideoOpen(true)
  }

  const handleSaveVideo = async () => {
    setError(null)
    setSavingVideo(true)
    try {
      if (videoFile) {
        const uploaded = await fileService.upload(videoFile, { subDir: 'video' })
        if (!uploaded.id) throw new Error('视频上传失败')
        await projectService.update(projectId, { videoFileIds: [uploaded.id], videoDir: null })
      } else {
        // 未选择文件时使用服务器绝对路径；空值表示解绑
        await projectService.update(projectId, { videoDir: serverVideoDir.trim() || null })
      }
      setVideoOpen(false)
      setVideoFile(null)
      setVideoFileList([])
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '保存视频源失败')
    } finally {
      setSavingVideo(false)
    }
  }

  const handleCreateEpisode = async () => {
    setError(null)
    let values: { title: string; description?: string }
    try {
      values = await episodeForm.validateFields()
    } catch {
      return
    }
    try {
      await projectService.createEpisode(projectId, values)
      setEpisodeOpen(false)
      episodeForm.resetFields()
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '创建剧集失败')
    }
  }

  const handleCreateCreation = async () => {
    setError(null)
    let values: { title?: string }
    try {
      values = await creationForm.validateFields()
    } catch {
      return
    }
    if (!selectedEpisodeId) {
      setError('请先选择一个剧集')
      return
    }
    try {
      const creation = await projectService.createCreation(projectId, {
        episodeId: selectedEpisodeId,
        title: values.title,
      })
      navigate(`/creations/${creation.id}?projectId=${projectId}`)
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '创建创作失败')
    }
  }

  return (
    <div style={{ width: '100%' }}>
      <Space direction="vertical" size={16} style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          <Space align="start">
            <Button onClick={() => navigate('/projects')}>← 返回</Button>
            <div>
              <Typography.Title level={4} style={{ margin: 0 }}>
                {project?.cover || '🎬'} {project?.title || '项目详情'}
              </Typography.Title>
              <Typography.Text type="secondary">
                {project?.author ? `作者：${project.author} · ` : ''}
                {project?.intro || '剧集与创作管理'}
              </Typography.Text>
            </div>
          </Space>
          <Space>
            <Tag color={project?.videoDir ? 'green' : 'orange'}>
              视频源：{project?.videoDir ? '已配置' : '未配置'}
            </Tag>
            <Button onClick={openVideoConfig}>配置视频源</Button>
            <Button onClick={() => setEpisodeOpen(true)}>新建剧集</Button>
            <Button type="primary" onClick={() => setCreationOpen(true)} disabled={episodes.length === 0}>
              新建创作
            </Button>
          </Space>
        </div>

        {error && (
          <Alert type="error" message={error} showIcon closable onClose={() => setError(null)} />
        )}

        {loading ? (
          <Card><Spin /></Card>
        ) : (
          <Row gutter={16}>
            <Col xs={24} lg={12}>
              <Card title={`剧集（${episodes.length}）`}>
                {episodes.length === 0 ? (
                  <Empty description="还没有剧集" />
                ) : (
                  <List
                    dataSource={episodes}
                    renderItem={(e) => (
                      <List.Item
                        actions={[
                          <Button
                            key="create"
                            type="link"
                            size="small"
                            onClick={() => {
                              setSelectedEpisodeId(e.id)
                              setCreationOpen(true)
                            }}
                          >
                            用它创作
                          </Button>,
                        ]}
                      >
                        <List.Item.Meta
                          title={e.title}
                          description={e.description || '—'}
                        />
                      </List.Item>
                    )}
                  />
                )}
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title={`创作（${creations.length}）`}>
                {creations.length === 0 ? (
                  <Empty description="还没有创作" />
                ) : (
                  <List
                    dataSource={creations}
                    renderItem={(c) => (
                      <List.Item
                        actions={[
                          <Button
                            key="open"
                            type="link"
                            size="small"
                            onClick={() => navigate(`/creations/${c.id}?projectId=${projectId}`)}
                          >
                            打开
                          </Button>,
                        ]}
                      >
                        <List.Item.Meta
                          title={
                            <Space>
                              <span>{c.title || '未命名创作'}</span>
                              <Tag color="blue">Step {c.currentStep}/3</Tag>
                            </Space>
                          }
                          description={new Date(c.createdAt).toLocaleString('zh-CN')}
                        />
                      </List.Item>
                    )}
                  />
                )}
              </Card>
            </Col>
          </Row>
        )}
      </Space>

      <Modal
        title="配置视频源"
        open={videoOpen}
        onCancel={() => setVideoOpen(false)}
        onOk={() => void handleSaveVideo()}
        confirmLoading={savingVideo}
        okText="保存"
        cancelText="取消"
      >
        <Space direction="vertical" size={12} style={{ width: '100%' }}>
          <Typography.Text type="secondary">
            选择本地视频上传后，系统会把文件所在目录作为该项目的素材目录。
          </Typography.Text>
          <Upload
            accept=".mp4,.mov,.avi,.mkv,.webm"
            maxCount={1}
            fileList={videoFileList}
            beforeUpload={(file) => {
              setVideoFile(file)
              setVideoFileList([file])
              return false
            }}
            onRemove={() => {
              setVideoFile(null)
              setVideoFileList([])
            }}
          >
            <Button>选择本地视频</Button>
          </Upload>
          <div>
            <Typography.Text strong>高级：服务器绝对路径</Typography.Text>
            <Input
              style={{ marginTop: 8 }}
              value={serverVideoDir}
              onChange={(e) => setServerVideoDir(e.target.value)}
              placeholder="例如：D:\videos\doupo（仅未选择本地视频时生效）"
            />
          </div>
        </Space>
      </Modal>

      <Modal
        title="新建剧集"
        open={episodeOpen}
        onCancel={() => setEpisodeOpen(false)}
        onOk={() => void handleCreateEpisode()}
        okText="创建"
        cancelText="取消"
      >
        <Form form={episodeForm} layout="vertical">
          <Form.Item label="剧集名称" name="title" rules={[{ required: true, message: '请输入剧集名称' }]}>
            <Input placeholder="例如：第一集 陨落的天才" maxLength={128} />
          </Form.Item>
          <Form.Item label="剧情描述" name="description">
            <Input.TextArea rows={3} maxLength={2000} placeholder="这一步的剧情概要，将作为 Step1 大纲的参考" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="新建创作"
        open={creationOpen}
        onCancel={() => setCreationOpen(false)}
        onOk={() => void handleCreateCreation()}
        okText="创建并进入"
        cancelText="取消"
      >
        <Form form={creationForm} layout="vertical">
          <Form.Item label="创作标题" name="title">
            <Input placeholder="例如：萧炎逆袭路" maxLength={128} />
          </Form.Item>
          {selectedEpisodeId ? (
            <Typography.Text type="secondary">
              归属剧集：{episodes.find((e) => e.id === selectedEpisodeId)?.title ?? '—'}
            </Typography.Text>
          ) : (
            <Alert
              type="info"
              showIcon
              message="请先在左侧点击「用它创作」选择一个剧集"
              style={{ marginBottom: 16 }}
            />
          )}
        </Form>
      </Modal>
    </div>
  )
}
