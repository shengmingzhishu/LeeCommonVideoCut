import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Alert,
  Button,
  Card,
  Col,
  Empty,
  Form,
  Input,
  message,
  Modal,
  Popconfirm,
  Row,
  Space,
  Spin,
  Tag,
  Typography,
  Upload,
} from 'antd'
import type { UploadFile } from 'antd/es/upload/interface'

import { PlusIcon } from '@/components/icons'
import { ApiError } from '@/services/request'
import { fileService } from '@/services/fileService'
import { projectService, type ProjectValues } from '@/services/projectService'

/** 项目列表页：新建项目 → 进入项目详情（剧集 / 创作） */
export default function ProjectListPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  const [projects, setProjects] = useState<ProjectValues[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [keyword, setKeyword] = useState('')

  const [createOpen, setCreateOpen] = useState(false)
  const [creating, setCreating] = useState(false)
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [form] = Form.useForm()

  const [editOpen, setEditOpen] = useState(false)
  const [editingProject, setEditingProject] = useState<ProjectValues | null>(null)
  const [saving, setSaving] = useState(false)
  const [editForm] = Form.useForm()

  const loadProjects = useCallback(async () => {
    setLoading(true)
    try {
      const page = await projectService.list({ page: 1, pageSize: 50, keyword: keyword || undefined })
      setProjects(page.items)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载项目失败')
    } finally {
      setLoading(false)
    }
  }, [keyword])

  useEffect(() => {
    void loadProjects()
  }, [loadProjects])

  // /projects?create=1 直接打开新建弹窗（工作台快捷入口使用）
  useEffect(() => {
    if (searchParams.get('create') === '1') {
      setCreateOpen(true)
      const next = new URLSearchParams(searchParams)
      next.delete('create')
      setSearchParams(next, { replace: true })
    }
  }, [searchParams, setSearchParams])

  const handleCreate = async () => {
    setError(null)
    let values: { title: string; author: string; intro: string; videoDir?: string; introDir?: string }
    try {
      values = await form.validateFields()
    } catch {
      return
    }
    setCreating(true)
    try {
      // 优先上传浏览器选择的本地视频，并以其所在目录作为项目素材目录
      let videoFileIds: string[] | undefined
      if (videoFile) {
        const uploaded = await fileService.upload(videoFile, { subDir: 'video' })
        if (!uploaded.id) throw new Error('视频上传失败')
        videoFileIds = [uploaded.id]
      }
      const created = await projectService.create({ ...values, videoFileIds })
      setCreateOpen(false)
      form.resetFields()
      setVideoFile(null)
      setFileList([])
      if (created.id) {
        // 最短链路：自动建「第1集」+ 一次创作，并带上提示词直达向导
        try {
          const episode = await projectService.createEpisode(created.id, {
            title: '第1集',
            description: values.intro.slice(0, 500),
          })
          const creation = await projectService.createCreation(created.id, {
            episodeId: episode.id,
            title: created.title || values.title,
          })
          if (creation.id) {
            navigate(
              `/creations/${creation.id}?projectId=${created.id}&prompt=${encodeURIComponent(values.intro)}`,
            )
            return
          }
        } catch {
          // 自动建剧集失败时回退到项目详情，不影响项目本身
        }
        navigate(`/projects/${created.id}`)
      } else {
        await loadProjects()
      }
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}`
          : '创建项目失败',
      )
    } finally {
      setCreating(false)
    }
  }

  const handleRemove = async (projectId: string) => {
    try {
      await projectService.remove(projectId)
      await loadProjects()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '删除项目失败')
    }
  }

  const handleCopy = async (p: ProjectValues) => {
    try {
      await projectService.copy(p.id)
      message.success(`已复制项目「${p.title}」`)
      await loadProjects()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '复制项目失败')
    }
  }

  const handleOpenEdit = (p: ProjectValues) => {
    setEditingProject(p)
    editForm.setFieldsValue({ title: p.title, author: p.author, intro: p.intro })
    setEditOpen(true)
  }

  const handleSaveEdit = async () => {
    if (!editingProject) return
    let values: { title: string; author: string; intro: string }
    try {
      values = await editForm.validateFields()
    } catch {
      return
    }
    setSaving(true)
    try {
      await projectService.update(editingProject.id, values)
      message.success('项目已更新')
      setEditOpen(false)
      await loadProjects()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '更新项目失败')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
        <div>
          <Typography.Title level={4} style={{ margin: 0 }}>
            项目管理
          </Typography.Title>
          <Typography.Text type="secondary">
            一个项目下可创建多个剧集，每个剧集可发起多次创作
          </Typography.Text>
        </div>
        <Space>
          <Input.Search
            placeholder="搜索项目名称"
            allowClear
            style={{ width: 220 }}
            onSearch={(v) => setKeyword(v)}
          />
          <Button type="primary" icon={<PlusIcon />} onClick={() => setCreateOpen(true)}>
            新建项目
          </Button>
        </Space>
      </div>

      {error && <Alert type="error" message={error} showIcon closable onClose={() => setError(null)} />}

      {loading ? (
        <Card>
          <Spin />
        </Card>
      ) : projects.length === 0 ? (
        <Card>
          <Empty description="还没有项目，点击「新建项目」开始">
            <Button type="primary" onClick={() => setCreateOpen(true)}>
              新建项目
            </Button>
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {projects.map((p) => (
            <Col xs={24} sm={12} xl={8} key={p.id}>
              <Card
                hoverable
                onClick={() => navigate(`/projects/${p.id}`)}
                title={
                  <Space>
                    <span style={{ fontSize: 20 }}>{p.cover || '🎬'}</span>
                    <span>{p.title}</span>
                  </Space>
                }
                extra={<Tag color={p.status === 'active' ? 'green' : 'default'}>{p.status}</Tag>}
                actions={[
                  <Button
                    key="open"
                    type="link"
                    onClick={(e) => {
                      e.stopPropagation()
                      navigate(`/projects/${p.id}`)
                    }}
                  >
                    进入
                  </Button>,
                  <Button
                    key="edit"
                    type="link"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleOpenEdit(p)
                    }}
                  >
                    编辑
                  </Button>,
                  <Button
                    key="copy"
                    type="link"
                    onClick={(e) => {
                      e.stopPropagation()
                      void handleCopy(p)
                    }}
                  >
                    复制
                  </Button>,
                  <Popconfirm
                    key="del"
                    title="删除项目？"
                    description="该项目及其剧集、创作将被删除，操作不可恢复。"
                    onConfirm={() => void handleRemove(p.id)}
                    onCancel={(e) => e?.stopPropagation()}
                  >
                    <Button type="link" danger onClick={(e) => e.stopPropagation()}>
                      删除
                    </Button>
                  </Popconfirm>,
                ]}
              >
                <Typography.Paragraph type="secondary" ellipsis={{ rows: 2 }} style={{ minHeight: 44 }}>
                  {p.intro || '暂无简介'}
                </Typography.Paragraph>
                <Space direction="vertical" size={2}>
                  <Typography.Text type="secondary">作者：{p.author || '—'}</Typography.Text>
                  <Typography.Text type="secondary">
                    素材目录：{p.videoDir ? '已配置' : '未配置'}
                  </Typography.Text>
                  <Typography.Text type="secondary">
                    更新：{p.updatedAt ? new Date(p.updatedAt).toLocaleString('zh-CN') : '—'}
                  </Typography.Text>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      <Modal
        title="新建项目"
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        onOk={() => void handleCreate()}
        confirmLoading={creating}
        okText="创建并进入"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item label="漫剧标题" name="title" rules={[{ required: true, message: '请输入标题' }]}>
            <Input placeholder="例如：斗破苍穹" maxLength={128} />
          </Form.Item>
          <Form.Item
            label="作者"
            name="author"
            rules={[{ required: true, message: '请输入作者' }]}
          >
            <Input placeholder="例如：天蚕土豆" maxLength={128} />
          </Form.Item>
          <Form.Item
            label="简介"
            name="intro"
            rules={[{ required: true, message: '请输入简介' }, { min: 10, message: '简介至少 10 个字符' }]}
          >
            <Input.TextArea rows={3} maxLength={2000} showCount placeholder="用一段话介绍这部漫剧" />
          </Form.Item>
          <Form.Item
            label="本地视频素材"
            extra="从浏览器选择一个视频，上传后自动绑定为项目素材目录；支持 mp4/mov/avi/mkv/webm"
          >
            <Upload
              accept=".mp4,.mov,.avi,.mkv,.webm"
              maxCount={1}
              fileList={fileList}
              beforeUpload={(file) => {
                setVideoFile(file)
                setFileList([file])
                return false
              }}
              onRemove={() => {
                setVideoFile(null)
                setFileList([])
              }}
            >
              <Button icon={<PlusIcon />}>选择本地视频</Button>
            </Upload>
          </Form.Item>
          <Form.Item
            label="视频素材目录（高级）"
            name="videoDir"
            extra="仅高级用户使用：服务器上的绝对路径目录；若同时选择了上方本地视频，则以上传视频所在目录为准"
          >
            <Input placeholder="例如：D:\videos\doupo" />
          </Form.Item>
          <Form.Item label="文本资料目录" name="introDir" extra="可选，供 Step1 生成大纲时参考">
            <Input placeholder="例如：D:\docs\doupo" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="编辑项目"
        open={editOpen}
        onCancel={() => setEditOpen(false)}
        onOk={() => void handleSaveEdit()}
        confirmLoading={saving}
        okText="保存"
        cancelText="取消"
      >
        <Form form={editForm} layout="vertical">
          <Form.Item label="漫剧标题" name="title" rules={[{ required: true, message: '请输入标题' }]}>
            <Input maxLength={128} />
          </Form.Item>
          <Form.Item label="作者" name="author" rules={[{ required: true, message: '请输入作者' }]}>
            <Input maxLength={128} />
          </Form.Item>
          <Form.Item
            label="简介"
            name="intro"
            rules={[{ required: true, message: '请输入简介' }, { min: 10, message: '简介至少 10 个字符' }]}
          >
            <Input.TextArea rows={3} maxLength={2000} showCount />
          </Form.Item>
          <Typography.Text type="secondary">
            视频源与文本目录请在项目详情页「配置视频源」中调整。
          </Typography.Text>
        </Form>
      </Modal>
    </Space>
  )
}