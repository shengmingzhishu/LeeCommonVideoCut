import { useCallback, useEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'
import {
  Alert,
  Button,
  Card,
  Col,
  Checkbox,
  Divider,
  Empty,
  Input,
  InputNumber,
  List,
  Modal,
  Progress,
  Row,
  Select,
  Slider,
  Space,
  Spin,
  Statistic,
  Switch,
  Table,
  Tag,
  Typography,
  Upload,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'

import { fileService } from '@/services/fileService'
import { ApiError } from '@/services/request'
import {
  stepService,
  type AudioItemValues,
  type AvatarConfigValues,
  type BGMConfigValues,
  type IntroOutroConfigValues,
  type IntroOutroItemValues,
  type QualityConfigValues,
  type SubtitleStyleSpecValues,
  type TransitionConfigValues,
  type VideoItemValues,
  type VideoMarkValues,
} from '@/services/stepService'
import { taskService, type TaskInfo } from '@/services/taskService'

interface Step3PanelProps {
  creationId: string
  /** 合成成功后回调 */
  onComposed: () => void
}

/**
 * 字幕预览换算基准：
 * ffmpeg/libass 未显式指定 PlayResY 时按 288 为基准，烧录后的实际字号 =
 * FontSize × 视频高 / 288，MarginV 换算同理。预览框高度取 PREVIEW_FRAME_HEIGHT，
 * 因此预览字号 = FontSize × PREVIEW_FRAME_HEIGHT / 288，位置比例与成片一致。
 */
const ASS_PLAY_RES_Y = 288
/** libass 默认 PlayResX=384，对应默认左右安全边距 MarginL/R=10 */
const ASS_PLAY_RES_X = 384
const ASS_DEFAULT_MARGIN_X = 10
const PREVIEW_FRAME_HEIGHT = 200

/** 后端 /step3/subtitle-styles 不可用时的兜底参数（与 SUBTITLE_STYLES 保持一致） */
const DEFAULT_SUBTITLE_SPECS: SubtitleStyleSpecValues[] = [
  { name: '默认白字黑描边', forceStyle: '', fontSize: 18, marginV: 40, alignment: 2, outline: 2, borderStyle: 1, primaryColour: '&H00FFFFFF', outlineColour: '&H00000000', backColour: '&H00000000' },
  { name: '大号黄字', forceStyle: '', fontSize: 28, marginV: 60, alignment: 2, outline: 3, borderStyle: 1, primaryColour: '&H0000D7FF', outlineColour: '&H00000000', backColour: '&H00000000' },
  { name: '底部居中白字', forceStyle: '', fontSize: 16, marginV: 20, alignment: 2, outline: 1, borderStyle: 1, primaryColour: '&H00FFFFFF', outlineColour: '&H00000000', backColour: '&H00000000' },
  { name: '背景条白字', forceStyle: '', fontSize: 20, marginV: 50, alignment: 2, outline: 0, borderStyle: 4, primaryColour: '&H00FFFFFF', outlineColour: '&H00000000', backColour: '&H80000000' },
  { name: '综艺黄字', forceStyle: '', fontSize: 26, marginV: 70, alignment: 2, outline: 4, borderStyle: 1, primaryColour: '&H0000E5FF', outlineColour: '&H00000000', backColour: '&H00000000' },
  { name: '小清新白字', forceStyle: '', fontSize: 16, marginV: 90, alignment: 2, outline: 1, borderStyle: 1, primaryColour: '&H00FFFFFF', outlineColour: '&H40000000', backColour: '&H00000000' },
  { name: '白底黑字条', forceStyle: '', fontSize: 18, marginV: 45, alignment: 2, outline: 0, borderStyle: 4, primaryColour: '&H00000000', outlineColour: '&H00FFFFFF', backColour: '&H00FFFFFF' },
  { name: '描边加粗白字', forceStyle: '', fontSize: 20, marginV: 55, alignment: 2, outline: 6, borderStyle: 1, primaryColour: '&H00FFFFFF', outlineColour: '&H00000000', backColour: '&H00000000' },
  { name: '顶部居中白字', forceStyle: '', fontSize: 18, marginV: 60, alignment: 8, outline: 3, borderStyle: 1, primaryColour: '&H00FFFFFF', outlineColour: '&H00000000', backColour: '&H00000000' },
  { name: '超大综艺字', forceStyle: '', fontSize: 34, marginV: 140, alignment: 2, outline: 5, borderStyle: 1, primaryColour: '&H0000E5FF', outlineColour: '&H00000000', backColour: '&H00000000' },
]

/** ASS &HAABBGGRR → CSS #RRGGBB */
function assColour(value: string, fallback = '#FFFFFF'): string {
  const hex = value.replace(/^&H/i, '')
  if (hex.length < 6) return fallback
  const bgr = hex.slice(-6)
  return `#${bgr.slice(4, 6)}${bgr.slice(2, 4)}${bgr.slice(0, 2)}`
}

/** 按烧录参数等比换算预览样式与位置 */
function subtitlePreviewStyle(
  spec: SubtitleStyleSpecValues,
  frameHeight: number,
  frameWidth: number,
): CSSProperties {
  const scale = frameHeight / ASS_PLAY_RES_Y
  const fontSize = Math.max(9, spec.fontSize * scale)
  const margin = Math.max(2, spec.marginV * scale)
  const sideMargin = Math.max(2, (ASS_DEFAULT_MARGIN_X * frameWidth) / ASS_PLAY_RES_X)
  const stroke = spec.outline * scale
  const isTop = spec.alignment >= 7 && spec.alignment <= 9
  const isBox = spec.borderStyle === 3 || spec.borderStyle === 4
  return {
    position: 'absolute',
    left: sideMargin,
    right: sideMargin,
    textAlign: 'center',
    fontSize,
    lineHeight: 1.35,
    fontWeight: isBox || spec.outline >= 4 ? 700 : 500,
    color: assColour(spec.primaryColour),
    background: isBox ? assColour(spec.backColour, '#FFFFFF') : 'transparent',
    padding: isBox ? `${Math.max(1, fontSize * 0.12)}px ${Math.max(4, fontSize * 0.45)}px` : '0',
    WebkitTextStroke:
      !isBox && stroke > 0
        ? `${Math.max(0.4, stroke)}px ${assColour(spec.outlineColour, '#000000')}`
        : undefined,
    textShadow:
      !isBox && stroke > 0
        ? `0 0 ${Math.max(1, stroke / 2)}px ${assColour(spec.outlineColour, '#000000')}`
        : 'none',
    ...(isTop ? { top: margin } : { bottom: margin }),
  }
}

/** 平台质量预设（分辨率 + CRF + preset） */
const PLATFORM_PRESETS = [
  {
    key: 'douyin',
    label: '抖音竖屏 · 1080×1920',
    resolution: '1080x1920',
    crf: 20,
    preset: 'fast' as const,
    note: '9:16 高清，画质优先',
  },
  {
    key: 'channels',
    label: '视频号竖屏 · 1080×1920',
    resolution: '1080x1920',
    crf: 23,
    preset: 'medium' as const,
    note: '9:16 均衡，体积更小',
  },
  {
    key: 'square',
    label: '方形 · 1080×1080',
    resolution: '1080x1080',
    crf: 21,
    preset: 'medium' as const,
    note: '1:1 信息流',
  },
  {
    key: 'landscape',
    label: '横屏 · 1920×1080',
    resolution: '1920x1080',
    crf: 20,
    preset: 'fast' as const,
    note: '16:9 B 站 / YouTube',
  },
]


/** 片头片尾字卡默认值 */
const EMPTY_CARD: IntroOutroItemValues = {
  enabled: false,
  title: '',
  subtitle: '',
  duration: 3,
  backgroundColor: '#0F1117',
  textColor: '#FFFFFF',
  imageFileId: null,
}

/** 批量上传任务 */
interface UploadTask {
  uid: string
  name: string
  status: 'uploading' | 'done' | 'failed'
  percent: number
  error?: string
  file: File
  fileId?: string
  objectUrl?: string
}

const VIDEO_EXT = /\.(mp4|mov|mkv|webm|avi|m4v)$/i
const IMAGE_EXT = /\.(jpg|jpeg|png|webp|bmp)$/i

/** Step3 音视频素材：音频列表 + 视频列表 + 随机标记 + 一键合成 */
export default function Step3Panel({ creationId, onComposed }: Step3PanelProps) {
  const [audios, setAudios] = useState<AudioItemValues[]>([])
  const [videos, setVideos] = useState<VideoItemValues[]>([])
  const [marks, setMarks] = useState<VideoMarkValues[]>([])
  const [totalDuration, setTotalDuration] = useState(0)
  const [loading, setLoading] = useState(true)
  const [remarking, setRemarking] = useState(false)
  const [composing, setComposing] = useState(false)
  const [retrying, setRetrying] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [task, setTask] = useState<TaskInfo | null>(null)
  /** 虚拟串播预览 */
  const [previewOpen, setPreviewOpen] = useState(false)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewUrls, setPreviewUrls] = useState<Record<string, string>>({})
  const [previewAudioUrl, setPreviewAudioUrl] = useState<string | null>(null)
  const [playingIndex, setPlayingIndex] = useState(-1)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const objectUrlsRef = useRef<string[]>([])
  /** 音色无关的成片观感配置 */
  const [subtitleStyle, setSubtitleStyle] = useState('默认白字黑描边')
  const [globalTransition, setGlobalTransition] = useState<TransitionConfigValues>({
    type: 'none',
    duration: 0.5,
  })
  const [avatar, setAvatar] = useState<AvatarConfigValues>({
    fileId: null,
    position: 'bottom_right',
    sizeRatio: 0.18,
    borderColor: '#FFFFFF',
    borderWidth: 4,
    shadow: true,
    start: 0,
    end: null,
  })
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null)
  const [avatarUploading, setAvatarUploading] = useState(false)
  const [quality, setQuality] = useState<QualityConfigValues>({
    resolution: '1080x1920',
    crf: 23,
    preset: 'medium',
  })
  /** 背景音乐 */
  const [bgm, setBgm] = useState<BGMConfigValues>({
    fileId: null,
    volume: 30,
    ducking: true,
    duckLevel: 30,
    fadeIn: 0.6,
    fadeOut: 0.8,
    loop: true,
  })
  const [bgmName, setBgmName] = useState<string>('')
  const [bgmUrl, setBgmUrl] = useState<string | null>(null)
  const [bgmUploading, setBgmUploading] = useState(false)
  /** 片头 / 片尾 */
  const [introOutro, setIntroOutro] = useState<IntroOutroConfigValues>({
    intro: { ...EMPTY_CARD },
    outro: { ...EMPTY_CARD },
  })
  const [cardImageUrls, setCardImageUrls] = useState<Record<'intro' | 'outro', string | null>>({
    intro: null,
    outro: null,
  })
  /** 封面帧导出 */
  const [coverTime, setCoverTime] = useState(1.0)
  const [coverUrl, setCoverUrl] = useState<string | null>(null)
  const [coverExporting, setCoverExporting] = useState(false)
  /** 字幕模板真实参数（后端下发，用于等比预览） */
  const [subtitleSpecs, setSubtitleSpecs] =
    useState<SubtitleStyleSpecValues[]>(DEFAULT_SUBTITLE_SPECS)
  /** 批量上传任务队列 */
  const [videoUploads, setVideoUploads] = useState<UploadTask[]>([])
  const [imageUploads, setImageUploads] = useState<UploadTask[]>([])
  const [bindingUploads, setBindingUploads] = useState(false)

  const audioTotal = audios.filter((a) => a.selected).reduce((sum, a) => sum + a.duration, 0)
  const durationMismatch = Math.abs(audioTotal - totalDuration) >= 2

  const loadMedia = useCallback(async () => {
    setLoading(true)
    try {
      const list = await stepService.getMediaList(creationId)
      setAudios([...list.systemAudios, ...list.customAudios])
      setVideos(list.videoFiles)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载素材失败')
    } finally {
      setLoading(false)
    }
  }, [creationId])

  useEffect(() => {
    void loadMedia()
  }, [loadMedia])

  /** 拉取字幕模板真实参数（失败时保留内置兜底参数） */
  useEffect(() => {
    let alive = true
    void stepService
      .getSubtitleStyles()
      .then((list) => {
        if (alive && list.length > 0) setSubtitleSpecs(list)
      })
      .catch(() => undefined)
    return () => {
      alive = false
    }
  }, [])

  /** 释放预览产生的 blob URL（关闭弹窗/卸载时） */
  const releasePreviewUrls = useCallback(() => {
    videoRef.current?.pause()
    audioRef.current?.pause()
    objectUrlsRef.current.forEach((u) => URL.revokeObjectURL(u))
    objectUrlsRef.current = []
    setPreviewUrls({})
    setPreviewAudioUrl(null)
    setPlayingIndex(-1)
  }, [])

  useEffect(() => {
    return () => {
      objectUrlsRef.current.forEach((u) => URL.revokeObjectURL(u))
    }
  }, [])

  /** 打开虚拟串播预览：拉取标记涉及的源视频与首个选中音频 */
  const handlePreview = async () => {
    setError(null)
    if (marks.length === 0) {
      setError('请先生成视频标记')
      return
    }
    releasePreviewUrls()
    setPreviewOpen(true)
    setPreviewLoading(true)
    try {
      const sources = Array.from(new Set(marks.map((m) => m.source)))
      const entries = await Promise.all(
        sources.map(
          async (s) => [s, await stepService.fetchMediaObjectUrl(creationId, 'video', s)] as const,
        ),
      )
      const urls: Record<string, string> = {}
      entries.forEach(([s, u]) => {
        urls[s] = u
        objectUrlsRef.current.push(u)
      })
      setPreviewUrls(urls)

      const firstAudio = audios.find((a) => a.selected)
      if (firstAudio) {
        const u = await stepService.fetchMediaObjectUrl(creationId, 'audio', firstAudio.path)
        objectUrlsRef.current.push(u)
        setPreviewAudioUrl(u)
      }
      setPlayingIndex(0)
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}`
          : '加载预览素材失败',
      )
    } finally {
      setPreviewLoading(false)
    }
  }

  const closePreview = () => {
    setPreviewOpen(false)
    releasePreviewUrls()
  }

  /** 片段推进：按标记顺序切换源视频并定位到 start */
  useEffect(() => {
    if (playingIndex < 0) return
    const mark = marks[playingIndex]
    const v = videoRef.current
    if (!mark || !v) return
    const url = previewUrls[mark.source]
    if (!url) return

    v.src = url
    const onLoaded = () => {
      v.currentTime = mark.start
      void v.play().catch(() => undefined)
    }
    v.addEventListener('loadedmetadata', onLoaded, { once: true })
    v.load()
    return () => v.removeEventListener('loadedmetadata', onLoaded)
  }, [playingIndex, marks, previewUrls])

  /** 预览打开后自动播放首个选中音频 */
  useEffect(() => {
    if (!previewOpen || !previewAudioUrl) return
    const a = audioRef.current
    if (!a) return
    a.currentTime = 0
    void a.play().catch(() => undefined)
  }, [previewOpen, previewAudioUrl])

  /** 到达当前片段 end 时切到下一段 */
  const handleTimeUpdate = () => {
    const v = videoRef.current
    const mark = marks[playingIndex]
    if (!v || !mark) return
    if (v.currentTime < mark.end) return

    if (playingIndex + 1 < marks.length) {
      setPlayingIndex(playingIndex + 1)
    } else {
      setPlayingIndex(-1)
      v.pause()
      audioRef.current?.pause()
    }
  }

  /** 主持人人像上传：先落库再取带鉴权预览流 */
  const handleAvatarUpload = async (file: File) => {
    setError(null)
    setAvatarUploading(true)
    try {
      const uploaded = await fileService.upload(file, { subDir: 'avatar' })
      if (avatarUrl) URL.revokeObjectURL(avatarUrl)
      const url = await fileService.fetchObjectUrl(uploaded.id)
      setAvatarUrl(url)
      setAvatar((prev) => ({ ...prev, fileId: uploaded.id }))
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '头像上传失败')
    } finally {
      setAvatarUploading(false)
    }
  }

  useEffect(() => {
    return () => {
      if (avatarUrl) URL.revokeObjectURL(avatarUrl)
    }
  }, [avatarUrl])

  /** BGM 上传：落库 + 取带鉴权预览流 */
  const handleBgmUpload = async (file: File) => {
    setError(null)
    setBgmUploading(true)
    try {
      const uploaded = await fileService.upload(file, { subDir: 'bgm' })
      if (bgmUrl) URL.revokeObjectURL(bgmUrl)
      const url = await fileService.fetchObjectUrl(uploaded.id)
      setBgmUrl(url)
      setBgmName(file.name)
      setBgm((prev) => ({ ...prev, fileId: uploaded.id }))
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : 'BGM 上传失败')
    } finally {
      setBgmUploading(false)
    }
  }

  useEffect(() => {
    return () => {
      if (bgmUrl) URL.revokeObjectURL(bgmUrl)
    }
  }, [bgmUrl])

  /** 片头/片尾背景图上传 */
  const handleCardImageUpload = async (slot: 'intro' | 'outro', file: File) => {
    setError(null)
    try {
      const uploaded = await fileService.upload(file, { subDir: 'cards' })
      const url = await fileService.fetchObjectUrl(uploaded.id)
      const oldUrl = cardImageUrls[slot]
      if (oldUrl) URL.revokeObjectURL(oldUrl)
      setCardImageUrls((prev) => ({ ...prev, [slot]: url }))
      setIntroOutro((prev) => ({
        ...prev,
        [slot]: { ...prev[slot], imageFileId: uploaded.id },
      }))
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '背景图上传失败')
    }
  }

  useEffect(() => {
    return () => {
      Object.values(cardImageUrls).forEach((u) => u && URL.revokeObjectURL(u))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // ---------- 批量上传（进度 / 失败重试） ----------

  const patchUpload = (
    setter: React.Dispatch<React.SetStateAction<UploadTask[]>>,
    uid: string,
    patch: Partial<UploadTask>,
  ) => {
    setter((prev) => prev.map((t) => (t.uid === uid ? { ...t, ...patch } : t)))
  }

  /** 绑定批量上传的视频到素材目录，并作废旧标记 */
  const bindUploadedVideos = useCallback(
    async (ids: string[]) => {
      if (ids.length === 0) return
      setBindingUploads(true)
      try {
        const list = await stepService.bindVideoSources(creationId, ids)
        setVideos(list)
        setMarks([])
        setTotalDuration(0)
      } catch (err) {
        setError(
          err instanceof ApiError
            ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}`
            : '素材绑定失败',
        )
      } finally {
        setBindingUploads(false)
      }
    },
    [creationId],
  )

  const uploadVideoTask = async (task: UploadTask): Promise<string | null> => {
    patchUpload(setVideoUploads, task.uid, {
      status: 'uploading',
      percent: 0,
      error: undefined,
    })
    try {
      const uploaded = await fileService.upload(task.file, {
        subDir: 'videos',
        onProgress: (percent) => patchUpload(setVideoUploads, task.uid, { percent }),
      })
      patchUpload(setVideoUploads, task.uid, { status: 'done', percent: 100, fileId: uploaded.id })
      return uploaded.id
    } catch (err) {
      patchUpload(setVideoUploads, task.uid, {
        status: 'failed',
        error: err instanceof ApiError ? err.message : '上传失败',
      })
      return null
    }
  }

  const handleBatchVideoUpload = async (files: File[]) => {
    setError(null)
    const accepted = files.filter((f) => VIDEO_EXT.test(f.name))
    if (accepted.length < files.length) {
      setError(`已忽略 ${files.length - accepted.length} 个非视频文件`)
    }
    if (accepted.length === 0) return

    const tasks: UploadTask[] = accepted.map((file, index) => ({
      uid: `v_${Date.now()}_${index}`,
      name: file.name,
      status: 'uploading',
      percent: 0,
      file,
    }))
    setVideoUploads((prev) => [...tasks, ...prev])

    const ids: string[] = []
    for (const task of tasks) {
      const fileId = await uploadVideoTask(task)
      if (fileId) ids.push(fileId)
    }
    await bindUploadedVideos(ids)
  }

  const handleRetryVideoUpload = async (task: UploadTask) => {
    const fileId = await uploadVideoTask(task)
    if (fileId) await bindUploadedVideos([fileId])
  }

  const uploadImageTask = async (task: UploadTask): Promise<string | null> => {
    patchUpload(setImageUploads, task.uid, {
      status: 'uploading',
      percent: 0,
      error: undefined,
    })
    try {
      const uploaded = await fileService.upload(task.file, {
        subDir: 'cards',
        onProgress: (percent) => patchUpload(setImageUploads, task.uid, { percent }),
      })
      patchUpload(setImageUploads, task.uid, { status: 'done', percent: 100, fileId: uploaded.id })
      return uploaded.id
    } catch (err) {
      patchUpload(setImageUploads, task.uid, {
        status: 'failed',
        error: err instanceof ApiError ? err.message : '上传失败',
      })
      return null
    }
  }

  const handleBatchImageUpload = async (files: File[]) => {
    setError(null)
    const accepted = files.filter((f) => IMAGE_EXT.test(f.name))
    if (accepted.length < files.length) {
      setError(`已忽略 ${files.length - accepted.length} 个非图片文件`)
    }
    if (accepted.length === 0) return

    const tasks: UploadTask[] = accepted.map((file, index) => ({
      uid: `i_${Date.now()}_${index}`,
      name: file.name,
      status: 'uploading',
      percent: 0,
      file,
    }))
    setImageUploads((prev) => [...tasks, ...prev])
    for (const task of tasks) {
      await uploadImageTask(task)
    }
  }

  const handleRetryImageUpload = async (task: UploadTask) => {
    await uploadImageTask(task)
  }

  /** 把批量上传的图片用作片头/片尾背景 */
  const applyImageToCard = async (slot: 'intro' | 'outro', fileId: string) => {
    setError(null)
    try {
      const url = await fileService.fetchObjectUrl(fileId)
      const oldUrl = cardImageUrls[slot]
      if (oldUrl) URL.revokeObjectURL(oldUrl)
      setCardImageUrls((prev) => ({ ...prev, [slot]: url }))
      setIntroOutro((prev) => ({
        ...prev,
        [slot]: { ...prev[slot], imageFileId: fileId },
      }))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '背景图读取失败')
    }
  }

  /** 从最新成片导出封面帧 */
  const handleExportCover = async () => {
    setError(null)
    setCoverExporting(true)
    try {
      const blob = await stepService.exportCover({ creationId, time: coverTime })
      const url = URL.createObjectURL(blob)
      setCoverUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev)
        return url
      })
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}`
          : '封面导出失败（请先合成一次成片）',
      )
    } finally {
      setCoverExporting(false)
    }
  }

  // ---------- 按段绑定素材 ----------

  const videoDurationMap = new Map(videos.map((v) => [v.name, v.duration]))
  const activePreset = PLATFORM_PRESETS.find(
    (p) =>
      p.resolution === quality.resolution &&
      p.crf === quality.crf &&
      p.preset === quality.preset,
  )
  const activeSubtitleSpec =
    subtitleSpecs.find((s) => s.name === subtitleStyle) ?? subtitleSpecs[0]
  const previewRatioW = Number(quality.resolution.split('x')[0]) || 9
  const previewRatioH = Number(quality.resolution.split('x')[1]) || 16
  const previewFrameWidth = (PREVIEW_FRAME_HEIGHT * previewRatioW) / previewRatioH

  /** 换源后按新素材时长收敛起点/终点（服务端合成前还会再校验一次） */
  const reassignMarkSource = (mark: VideoMarkValues, source: string): VideoMarkValues => {
    const total = videoDurationMap.get(source) ?? 0
    if (total <= 0) return { ...mark, source }
    const wanted = Math.max(0.5, mark.end - mark.start)
    let start = mark.start
    if (start >= total - 0.3) start = 0
    let end = Math.min(start + wanted, total)
    if (end - start < 0.3) {
      start = 0
      end = Math.min(wanted, total)
    }
    return {
      ...mark,
      source,
      start: Number(start.toFixed(3)),
      end: Number(end.toFixed(3)),
      duration: Number((end - start).toFixed(3)),
    }
  }

  /** 按段轮换：把勾选的视频素材依次分配给每一段 */
  const handleDistributeMarkSources = () => {
    setError(null)
    if (marks.length === 0) {
      setError('请先生成视频标记')
      return
    }
    const selected = videos.filter((v) => v.selected)
    if (selected.length === 0) {
      setError('请至少勾选一个视频素材')
      return
    }
    setMarks((prev) =>
      prev.map((mark, index) =>
        reassignMarkSource(mark, selected[index % selected.length].name),
      ),
    )
  }

  const handleRemark = async () => {
    setError(null)
    setRemarking(true)
    try {
      const selectedVideos = videos.filter((v) => v.selected).map((v) => v.name)
      const result = await stepService.remark({
        creationId,
        videoFiles: selectedVideos,
        targetDuration: null,
      })
      setMarks(result.markers)
      setTotalDuration(result.totalDuration)
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '标记失败')
    } finally {
      setRemarking(false)
    }
  }

  const handleCompose = async () => {
    setError(null)
    const selectedAudios = audios.filter((a) => a.selected).map((a) => a.path)
    if (selectedAudios.length === 0) {
      setError('请至少选择一个音频')
      return
    }
    if (marks.length === 0) {
      setError('请先生成视频标记')
      return
    }

    setComposing(true)
    try {
      const composeSettings = {
        subtitle_style: subtitleStyle,
        global_transition: globalTransition,
        avatar,
        quality,
        bgm: bgm.fileId ? bgm : null,
        intro_outro: introOutro,
      }
      await stepService.saveState({
        creationId,
        audioFiles: audios,
        videoFiles: videos,
        deletedMedia: { audio_paths: [], video_paths: [] },
        composeSettings,
      })
      const taskId = await stepService.compose({
        creationId,
        audioFiles: selectedAudios,
        markers: marks,
        resolution: quality.resolution,
        subtitleStyle,
        globalTransition,
        avatar,
        quality,
        bgm: bgm.fileId ? bgm : null,
        introOutro,
      })
      const final = await taskService.poll(taskId, setTask)
      if (final.status === 'completed') {
        onComposed()
      } else if (final.status === 'failed') {
        setError(`合成失败：${final.error ?? '未知错误'}`)
      }
    } catch (err) {
      setError(err instanceof ApiError ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}` : '提交合成失败')
    } finally {
      setComposing(false)
    }
  }

  /** 重试失败/取消的合成任务（后端沿用原 payload 重新入队） */
  const handleRetryTask = async () => {
    if (!task) return
    setError(null)
    setRetrying(true)
    try {
      const newTaskId = await taskService.retry(task.id)
      const final = await taskService.poll(newTaskId, setTask)
      if (final.status === 'completed') {
        onComposed()
      } else if (final.status === 'failed') {
        setError(`合成失败：${final.error ?? '未知错误'}`)
      }
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `${err.message}${err.traceId ? `（traceId: ${err.traceId}）` : ''}`
          : '重试任务失败',
      )
    } finally {
      setRetrying(false)
    }
  }

  const audioColumns: ColumnsType<AudioItemValues> = [
    {
      title: '选择',
      dataIndex: 'selected',
      width: 60,
      render: (_, record) => (
        <Checkbox
          checked={record.selected}
          onChange={(e) =>
            setAudios((prev) =>
              prev.map((a) => (a.path === record.path ? { ...a, selected: e.target.checked } : a)),
            )
          }
        />
      ),
    },
    { title: '音频', dataIndex: 'name', ellipsis: true },
    {
      title: '来源',
      dataIndex: 'source',
      width: 80,
      render: (v: string) => <Tag color={v === 'system' ? 'purple' : 'cyan'}>{v === 'system' ? 'AI' : '上传'}</Tag>,
    },
    { title: '时长', dataIndex: 'durationStr', width: 70 },
  ]

  const videoColumns: ColumnsType<VideoItemValues> = [
    {
      title: '选择',
      dataIndex: 'selected',
      width: 60,
      render: (_, record) => (
        <Checkbox
          checked={record.selected}
          onChange={(e) =>
            setVideos((prev) =>
              prev.map((v) => (v.name === record.name ? { ...v, selected: e.target.checked } : v)),
            )
          }
        />
      ),
    },
    { title: '视频', dataIndex: 'name', ellipsis: true },
    { title: '时长', dataIndex: 'durationStr', width: 70 },
  ]

  /** 更新片头/片尾字卡字段 */
  const updateCard = (slot: 'intro' | 'outro', patch: Partial<IntroOutroItemValues>) => {
    setIntroOutro((prev) => ({ ...prev, [slot]: { ...prev[slot], ...patch } }))
  }

  const markColumns: ColumnsType<VideoMarkValues> = [
    { title: '#', dataIndex: 'id', width: 50 },
    {
      title: '源视频（按段绑定）',
      dataIndex: 'source',
      width: 220,
      render: (source: string, record) => (
        <Select
          size="small"
          value={source}
          style={{ width: '100%' }}
          options={videos.map((v) => ({
            value: v.name,
            label: `${v.name}（${v.durationStr || `${v.duration.toFixed(1)}s`}）`,
          }))}
          onChange={(next) =>
            setMarks((prev) =>
              prev.map((m) => (m.id === record.id ? reassignMarkSource(m, next) : m)),
            )
          }
        />
      ),
    },
    { title: '开始', dataIndex: 'start', width: 80, render: (v: number) => `${v.toFixed(2)}s` },
    { title: '结束', dataIndex: 'end', width: 80, render: (v: number) => `${v.toFixed(2)}s` },
    { title: '时长', dataIndex: 'duration', width: 80, render: (v: number) => `${v.toFixed(2)}s` },
    {
      title: '转场（单段覆盖）',
      key: 'transition',
      width: 210,
      render: (_, record) => (
        <Space size={4}>
          <Select
            size="small"
            allowClear
            placeholder="继承全局"
            value={record.transition?.type}
            style={{ width: 110 }}
            options={[
              { value: 'none', label: '直切' },
              { value: 'fade', label: '淡入淡出' },
              { value: 'slide', label: '滑移' },
              { value: 'zoom', label: '缩放' },
            ]}
            onChange={(type) =>
              setMarks((prev) =>
                prev.map((m) =>
                  m.id === record.id
                    ? {
                        ...m,
                        transition: type
                          ? { type, duration: m.transition?.duration ?? globalTransition.duration }
                          : null,
                      }
                    : m,
                ),
              )
            }
          />
          {record.transition && (
            <InputNumber
              size="small"
              min={0.2}
              max={1.5}
              step={0.1}
              value={record.transition.duration}
              onChange={(duration) =>
                setMarks((prev) =>
                  prev.map((m) =>
                    m.id === record.id
                      ? {
                          ...m,
                          transition: m.transition
                            ? { ...m.transition, duration: duration ?? 0.5 }
                            : null,
                        }
                      : m,
                  ),
                )
              }
            />
          )}
        </Space>
      ),
    },
  ]

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      {error && (
        <Alert type="error" message={error} showIcon closable onClose={() => setError(null)} />
      )}

      <Row gutter={16}>
        <Col xs={24} lg={12}>
          <Card title="音频素材" extra={<Button onClick={() => void loadMedia()}>刷新</Button>}>
            {loading ? (
              <Spin />
            ) : audios.length === 0 ? (
              <Empty description="暂无音频（可在 Step2 生成 TTS 音频）" />
            ) : (
              <Table
                size="small"
                rowKey="path"
                columns={audioColumns}
                dataSource={audios}
                pagination={false}
              />
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card
            title="视频素材"
            extra={
              <Space>
                <Upload
                  multiple
                  accept="video/*"
                  showUploadList={false}
                  beforeUpload={(file, fileList) => {
                    const current = file as File
                    const first = fileList[0] as File
                    if (current === first) {
                      const files = fileList as unknown as File[]
                      void handleBatchVideoUpload(files)
                    }
                    return false
                  }}
                >
                  <Button>批量上传视频</Button>
                </Upload>
                <Button onClick={() => void loadMedia()} loading={loading}>
                  刷新
                </Button>
              </Space>
            }
          >
            {bindingUploads && (
              <Alert
                type="info"
                showIcon
                style={{ marginBottom: 10 }}
                message="正在把上传的视频绑定为素材目录…"
              />
            )}
            {videoUploads.length > 0 && (
              <div style={{ marginBottom: 12 }}>
                <Typography.Text strong>视频上传队列</Typography.Text>
                <List
                  size="small"
                  dataSource={videoUploads.slice(0, 8)}
                  renderItem={(task) => (
                    <List.Item
                      actions={
                        task.status === 'failed'
                          ? [
                              <Button
                                key="retry"
                                size="small"
                                onClick={() => void handleRetryVideoUpload(task)}
                              >
                                重试
                              </Button>,
                            ]
                          : task.status === 'done'
                            ? [<Tag key="ok" color="green">已绑定</Tag>]
                            : []
                      }
                    >
                      <List.Item.Meta
                        title={task.name}
                        description={
                          <div>
                            <Progress
                              percent={task.status === 'failed' ? 0 : task.percent}
                              size="small"
                              status={task.status === 'failed' ? 'exception' : undefined}
                            />
                            {task.error && (
                              <Typography.Text type="danger" style={{ fontSize: 12 }}>
                                {task.error}
                              </Typography.Text>
                            )}
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              </div>
            )}

            {loading ? (
              <Spin />
            ) : videos.length === 0 ? (
              <Empty description="项目未配置视频素材目录，可直接批量上传" />
            ) : (
              <Table
                size="small"
                rowKey="name"
                columns={videoColumns}
                dataSource={videos}
                pagination={false}
              />
            )}

            <Divider style={{ margin: '12px 0' }} />

            <Space wrap style={{ marginBottom: 8 }}>
              <Typography.Text strong>图片素材</Typography.Text>
              <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                用于片头 / 片尾背景
              </Typography.Text>
              <Upload
                multiple
                accept="image/*"
                showUploadList={false}
                beforeUpload={(file, fileList) => {
                  const current = file as File
                  const first = fileList[0] as File
                  if (current === first) {
                    const files = fileList as unknown as File[]
                    void handleBatchImageUpload(files)
                  }
                  return false
                }}
              >
                <Button size="small">批量上传图片</Button>
              </Upload>
            </Space>
            {imageUploads.length > 0 && (
              <List
                size="small"
                dataSource={imageUploads.slice(0, 8)}
                renderItem={(task) => (
                  <List.Item
                    actions={
                      task.status === 'done' && task.fileId
                        ? [
                            <Button
                              key="intro"
                              size="small"
                              onClick={() => void applyImageToCard('intro', task.fileId as string)}
                            >
                              设为片头
                            </Button>,
                            <Button
                              key="outro"
                              size="small"
                              onClick={() => void applyImageToCard('outro', task.fileId as string)}
                            >
                              设为片尾
                            </Button>,
                          ]
                        : task.status === 'failed'
                          ? [
                              <Button
                                key="retry"
                                size="small"
                                onClick={() => void handleRetryImageUpload(task)}
                              >
                                重试
                              </Button>,
                            ]
                          : []
                    }
                  >
                    <List.Item.Meta
                      title={task.name}
                      description={
                        <Progress
                          percent={task.status === 'failed' ? 0 : task.percent}
                          size="small"
                          status={task.status === 'failed' ? 'exception' : undefined}
                        />
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>
      </Row>

      <Card title="成片观感（转场 / 主持人人像 / 质量）">
        <Row gutter={24}>
          <Col xs={24} lg={10}>
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <div>
                <Typography.Text strong>全局转场</Typography.Text>
                <Space style={{ marginTop: 8 }}>
                  <Select
                    value={globalTransition.type}
                    style={{ width: 140 }}
                    options={[
                      { value: 'none', label: '直切' },
                      { value: 'fade', label: '淡入淡出' },
                      { value: 'slide', label: '滑移' },
                      { value: 'zoom', label: '缩放' },
                    ]}
                    onChange={(type: TransitionConfigValues['type']) =>
                      setGlobalTransition((prev) => ({
                        ...prev,
                        type,
                        duration: type === 'none' ? prev.duration : Math.max(prev.duration, 0.2),
                      }))
                    }
                  />
                  <Typography.Text type="secondary">时长</Typography.Text>
                  <InputNumber
                    min={0.2}
                    max={1.5}
                    step={0.1}
                    value={globalTransition.duration}
                    onChange={(v) =>
                      setGlobalTransition((prev) => ({ ...prev, duration: v ?? 0.5 }))
                    }
                    addonAfter="秒"
                    disabled={globalTransition.type === 'none'}
                  />
                </Space>
                <Typography.Paragraph type="secondary" style={{ fontSize: 12, marginTop: 6 }}>
                  单段可在「视频切片标记」表中覆盖；转场会消耗时长，合成时自动用音频时长对齐。
                </Typography.Paragraph>
              </div>

              <Divider style={{ margin: 0 }} />

              <div>
                <Typography.Text strong>字幕样式</Typography.Text>
                <Select
                  value={subtitleStyle}
                  style={{ width: '100%', marginTop: 8 }}
                  onChange={setSubtitleStyle}
                  options={subtitleSpecs.map((s) => ({ value: s.name, label: s.name }))}
                />
                <div style={{ marginTop: 10, display: 'flex', justifyContent: 'center' }}>
                  <div
                    style={{
                      position: 'relative',
                      height: PREVIEW_FRAME_HEIGHT,
                      aspectRatio: `${previewRatioW} / ${previewRatioH}`,
                      maxWidth: '100%',
                      borderRadius: 6,
                      overflow: 'hidden',
                      background: 'linear-gradient(135deg, #232526, #414345)',
                      border: '1px solid #3a3a3a',
                    }}
                  >
                    <span
                      style={subtitlePreviewStyle(
                        activeSubtitleSpec,
                        PREVIEW_FRAME_HEIGHT,
                        previewFrameWidth,
                      )}
                    >
                      这是字幕预览效果
                    </span>
                  </div>
                </div>
                <Typography.Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 6 }}>
                  换算：FontSize {activeSubtitleSpec.fontSize} → 预览{' '}
                  {Math.round((activeSubtitleSpec.fontSize * PREVIEW_FRAME_HEIGHT) / ASS_PLAY_RES_Y)}px；
                  MarginV {activeSubtitleSpec.marginV} →{' '}
                  {Math.round((activeSubtitleSpec.marginV * PREVIEW_FRAME_HEIGHT) / ASS_PLAY_RES_Y)}px；
                  对齐 {activeSubtitleSpec.alignment}
                </Typography.Text>
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  按 libass PlayResY=288 等比换算（左右边距按 PlayResX=384 的 MarginL/R=10 换算）。
                  实测已知偏差：底条样式的字高与底距误差 0%，描边样式位置误差 ≤3.4%；
                  中文墨迹高度比 em-box 小约 26%，超大字号会自动换行（预览与烧录一致）。
                  最终以 ffmpeg 烧录结果为准。
                </Typography.Text>
              </div>

              <Divider style={{ margin: 0 }} />

              <div>
                <Typography.Text strong>成片质量预设</Typography.Text>
                <Space direction="vertical" size={8} style={{ width: '100%', marginTop: 8 }}>
                  <Select
                    value={activePreset?.key ?? 'custom'}
                    style={{ width: '100%' }}
                    onChange={(key) => {
                      const preset = PLATFORM_PRESETS.find((p) => p.key === key)
                      if (preset) {
                        setQuality({
                          resolution: preset.resolution,
                          crf: preset.crf,
                          preset: preset.preset,
                        })
                      }
                    }}
                    options={[
                      ...PLATFORM_PRESETS.map((p) => ({
                        value: p.key,
                        label: `${p.label} · CRF ${p.crf}`,
                      })),
                      { value: 'custom', label: '自定义参数' },
                    ]}
                  />
                  {activePreset && (
                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                      {activePreset.note} · {activePreset.resolution} / CRF {activePreset.crf} /{' '}
                      {activePreset.preset}
                    </Typography.Text>
                  )}
                  <Space style={{ width: '100%' }}>
                    <Typography.Text type="secondary">CRF</Typography.Text>
                    <Slider
                      min={18}
                      max={32}
                      value={quality.crf}
                      onChange={(crf) => setQuality((prev) => ({ ...prev, crf }))}
                      style={{ width: 160 }}
                    />
                    <Typography.Text>{quality.crf}</Typography.Text>
                    <Select
                      value={quality.preset}
                      style={{ width: 120 }}
                      onChange={(preset: QualityConfigValues['preset']) =>
                        setQuality((prev) => ({ ...prev, preset }))
                      }
                      options={['ultrafast', 'veryfast', 'fast', 'medium', 'slow'].map((p) => ({
                        value: p,
                        label: p,
                      }))}
                    />
                  </Space>
                  <Select
                    value={quality.resolution}
                    style={{ width: '100%' }}
                    onChange={(resolution) => setQuality((prev) => ({ ...prev, resolution }))}
                    options={[
                      { value: '1080x1920', label: '1080x1920 · 竖屏 9:16' },
                      { value: '720x1280', label: '720x1280 · 竖屏标清 9:16' },
                      { value: '1080x1080', label: '1080x1080 · 方形 1:1' },
                      { value: '1920x1080', label: '1920x1080 · 横屏 16:9' },
                    ]}
                  />
                </Space>
              </div>
            </Space>
          </Col>

          <Col xs={24} lg={14}>
            <Space direction="vertical" size={10} style={{ width: '100%' }}>
              <Typography.Text strong>主持人人像</Typography.Text>
              <Space wrap>
                <Upload
                  accept="image/*"
                  showUploadList={false}
                  beforeUpload={(file) => {
                    void handleAvatarUpload(file as File)
                    return false
                  }}
                >
                  <Button loading={avatarUploading}>上传人像</Button>
                </Upload>
                {avatar.fileId && <Tag color="green">已上传</Tag>}
                {avatar.fileId && (
                  <Button size="small" onClick={() => setAvatar((prev) => ({ ...prev, fileId: null }))}>
                    清除
                  </Button>
                )}
              </Space>

              <Row gutter={12}>
                <Col span={12}>
                  <Typography.Text type="secondary">位置</Typography.Text>
                  <Select
                    value={avatar.position}
                    style={{ width: '100%' }}
                    onChange={(position: AvatarConfigValues['position']) =>
                      setAvatar((prev) => ({ ...prev, position }))
                    }
                    options={[
                      { value: 'top_left', label: '左上' },
                      { value: 'top_right', label: '右上' },
                      { value: 'bottom_left', label: '左下' },
                      { value: 'bottom_right', label: '右下' },
                    ]}
                  />
                </Col>
                <Col span={12}>
                  <Typography.Text type="secondary">尺寸占比 {Math.round(avatar.sizeRatio * 100)}%</Typography.Text>
                  <Slider
                    min={0.05}
                    max={0.5}
                    step={0.01}
                    value={avatar.sizeRatio}
                    onChange={(sizeRatio) => setAvatar((prev) => ({ ...prev, sizeRatio }))}
                  />
                </Col>
                <Col span={12}>
                  <Typography.Text type="secondary">描边宽度</Typography.Text>
                  <InputNumber
                    min={0}
                    max={20}
                    value={avatar.borderWidth}
                    onChange={(borderWidth) =>
                      setAvatar((prev) => ({ ...prev, borderWidth: borderWidth ?? 4 }))
                    }
                    style={{ width: '100%' }}
                  />
                </Col>
                <Col span={12}>
                  <Typography.Text type="secondary">描边颜色</Typography.Text>
                  <input
                    type="color"
                    value={avatar.borderColor}
                    onChange={(e) => setAvatar((prev) => ({ ...prev, borderColor: e.target.value }))}
                    style={{ width: '100%', height: 32, border: 'none', background: 'transparent' }}
                  />
                </Col>
                <Col span={8}>
                  <Typography.Text type="secondary">开始（秒）</Typography.Text>
                  <InputNumber
                    min={0}
                    value={avatar.start}
                    onChange={(start) => setAvatar((prev) => ({ ...prev, start: start ?? 0 }))}
                    style={{ width: '100%' }}
                  />
                </Col>
                <Col span={8}>
                  <Typography.Text type="secondary">结束（秒）</Typography.Text>
                  <InputNumber
                    min={0}
                    value={avatar.end ?? undefined}
                    placeholder="全程"
                    onChange={(end) => setAvatar((prev) => ({ ...prev, end: end ?? null }))}
                    style={{ width: '100%' }}
                  />
                </Col>
                <Col span={8}>
                  <Typography.Text type="secondary">阴影</Typography.Text>
                  <div>
                    <Switch
                      checked={avatar.shadow}
                      onChange={(shadow) => setAvatar((prev) => ({ ...prev, shadow }))}
                    />
                  </div>
                </Col>
              </Row>

              <div
                style={{
                  position: 'relative',
                  width: '100%',
                  maxWidth: 220,
                  aspectRatio: `${quality.resolution.split('x')[0]} / ${quality.resolution.split('x')[1]}`,
                  background: 'linear-gradient(135deg, #1f1f1f, #3a3a3a)',
                  borderRadius: 8,
                  overflow: 'hidden',
                  margin: '0 auto',
                }}
              >
                <Typography.Text
                  type="secondary"
                  style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', fontSize: 12 }}
                >
                  定位预览
                </Typography.Text>
                {avatar.fileId && (
                  <div
                    style={{
                      position: 'absolute',
                      width: `${avatar.sizeRatio * 100}%`,
                      aspectRatio: '1 / 1',
                      borderRadius: '50%',
                      overflow: 'hidden',
                      border: `${avatar.borderWidth}px solid ${avatar.borderColor}`,
                      boxShadow: avatar.shadow ? '0 4px 12px rgba(0,0,0,0.55)' : 'none',
                      ...(avatar.position === 'top_left' && { top: '4%', left: '4%' }),
                      ...(avatar.position === 'top_right' && { top: '4%', right: '4%' }),
                      ...(avatar.position === 'bottom_left' && { bottom: '4%', left: '4%' }),
                      ...(avatar.position === 'bottom_right' && { bottom: '4%', right: '4%' }),
                    }}
                  >
                    {avatarUrl ? (
                      <img src={avatarUrl} alt="主持人" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                      <div style={{ width: '100%', height: '100%', background: '#888' }} />
                    )}
                  </div>
                )}
              </div>
            </Space>
          </Col>
        </Row>
      </Card>

      <Card title="配乐 / 片头片尾 / 封面">
        <Row gutter={24}>
          <Col xs={24} lg={12}>
            <Space direction="vertical" size={10} style={{ width: '100%' }}>
              <Typography.Text strong>背景音乐（BGM）</Typography.Text>
              <Space wrap>
                <Upload
                  accept="audio/*"
                  showUploadList={false}
                  beforeUpload={(file) => {
                    void handleBgmUpload(file as File)
                    return false
                  }}
                >
                  <Button loading={bgmUploading}>上传 BGM</Button>
                </Upload>
                {bgmName && <Tag color="green">{bgmName}</Tag>}
                {bgm.fileId && (
                  <Button
                    size="small"
                    onClick={() => {
                      if (bgmUrl) URL.revokeObjectURL(bgmUrl)
                      setBgmUrl(null)
                      setBgmName('')
                      setBgm((prev) => ({ ...prev, fileId: null }))
                    }}
                  >
                    清除
                  </Button>
                )}
              </Space>
              {bgmUrl && <audio controls src={bgmUrl} style={{ width: '100%' }} />}

              <div>
                <Typography.Text type="secondary">BGM 音量 {bgm.volume}%</Typography.Text>
                <Slider
                  min={0}
                  max={100}
                  value={bgm.volume}
                  onChange={(volume) => setBgm((prev) => ({ ...prev, volume }))}
                  disabled={!bgm.fileId}
                />
              </div>

              <Space wrap>
                <Typography.Text type="secondary">人声闪避</Typography.Text>
                <Switch
                  checked={bgm.ducking}
                  onChange={(ducking) => setBgm((prev) => ({ ...prev, ducking }))}
                  disabled={!bgm.fileId}
                />
                <Typography.Text type="secondary">闪避后保留 {bgm.duckLevel}%</Typography.Text>
                <Slider
                  min={5}
                  max={100}
                  value={bgm.duckLevel}
                  onChange={(duckLevel) => setBgm((prev) => ({ ...prev, duckLevel }))}
                  style={{ width: 140 }}
                  disabled={!bgm.fileId || !bgm.ducking}
                />
              </Space>

              <Space wrap>
                <Typography.Text type="secondary">淡入</Typography.Text>
                <InputNumber
                  min={0}
                  max={5}
                  step={0.1}
                  value={bgm.fadeIn}
                  onChange={(fadeIn) => setBgm((prev) => ({ ...prev, fadeIn: fadeIn ?? 0 }))}
                  addonAfter="秒"
                  disabled={!bgm.fileId}
                />
                <Typography.Text type="secondary">淡出</Typography.Text>
                <InputNumber
                  min={0}
                  max={5}
                  step={0.1}
                  value={bgm.fadeOut}
                  onChange={(fadeOut) => setBgm((prev) => ({ ...prev, fadeOut: fadeOut ?? 0 }))}
                  addonAfter="秒"
                  disabled={!bgm.fileId}
                />
                <Typography.Text type="secondary">循环</Typography.Text>
                <Switch
                  checked={bgm.loop}
                  onChange={(loop) => setBgm((prev) => ({ ...prev, loop }))}
                  disabled={!bgm.fileId}
                />
              </Space>
              <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                BGM 基准音量建议 20~35%，闪避保留 25~40%，避免盖住人声。
              </Typography.Text>
            </Space>
          </Col>

          <Col xs={24} lg={12}>
            <Space direction="vertical" size={10} style={{ width: '100%' }}>
              <Typography.Text strong>片头 / 片尾字卡</Typography.Text>
              {(['intro', 'outro'] as const).map((slot) => {
                const item = introOutro[slot]
                const label = slot === 'intro' ? '片头' : '片尾'
                return (
                  <div key={slot} style={{ border: '1px solid #333', borderRadius: 6, padding: 10 }}>
                    <Space wrap>
                      <Typography.Text strong>{label}</Typography.Text>
                      <Switch
                        checked={item.enabled}
                        onChange={(enabled) => updateCard(slot, { enabled })}
                      />
                      <Typography.Text type="secondary">时长</Typography.Text>
                      <InputNumber
                        min={1}
                        max={8}
                        step={0.5}
                        value={item.duration}
                        onChange={(duration) => updateCard(slot, { duration: duration ?? 3 })}
                        addonAfter="秒"
                        disabled={!item.enabled}
                      />
                    </Space>
                    <Space direction="vertical" size={6} style={{ width: '100%', marginTop: 8 }}>
                      <Input
                        placeholder="标题（如：第 1 集 先导课）"
                        value={item.title}
                        maxLength={40}
                        onChange={(e) => updateCard(slot, { title: e.target.value })}
                        disabled={!item.enabled}
                      />
                      <Input
                        placeholder="副标题（可选）"
                        value={item.subtitle}
                        maxLength={60}
                        onChange={(e) => updateCard(slot, { subtitle: e.target.value })}
                        disabled={!item.enabled}
                      />
                      <Space wrap>
                        <Typography.Text type="secondary">背景色</Typography.Text>
                        <input
                          type="color"
                          value={item.backgroundColor}
                          onChange={(e) => updateCard(slot, { backgroundColor: e.target.value })}
                          disabled={!item.enabled}
                          style={{ width: 44, height: 28, border: 'none', background: 'transparent' }}
                        />
                        <Typography.Text type="secondary">文字色</Typography.Text>
                        <input
                          type="color"
                          value={item.textColor}
                          onChange={(e) => updateCard(slot, { textColor: e.target.value })}
                          disabled={!item.enabled}
                          style={{ width: 44, height: 28, border: 'none', background: 'transparent' }}
                        />
                        <Upload
                          accept="image/*"
                          showUploadList={false}
                          beforeUpload={(file) => {
                            void handleCardImageUpload(slot, file as File)
                            return false
                          }}
                        >
                          <Button size="small" disabled={!item.enabled}>
                            {item.imageFileId ? '更换背景图' : '上传背景图'}
                          </Button>
                        </Upload>
                        {item.imageFileId && (
                          <Button
                            size="small"
                            onClick={() => {
                              const old = cardImageUrls[slot]
                              if (old) URL.revokeObjectURL(old)
                              setCardImageUrls((prev) => ({ ...prev, [slot]: null }))
                              updateCard(slot, { imageFileId: null })
                            }}
                          >
                            清除图
                          </Button>
                        )}
                      </Space>
                      {cardImageUrls[slot] && (
                        <img
                          src={cardImageUrls[slot] as string}
                          alt={`${label}背景`}
                          style={{ width: '100%', maxHeight: 64, objectFit: 'cover', borderRadius: 4 }}
                        />
                      )}
                    </Space>
                  </div>
                )
              })}
            </Space>
          </Col>
        </Row>

        <Divider />

        <Space wrap align="center">
          <Typography.Text strong>封面帧导出</Typography.Text>
          <Typography.Text type="secondary">截取时间</Typography.Text>
          <InputNumber
            min={0}
            step={0.5}
            value={coverTime}
            onChange={(v) => setCoverTime(v ?? 1)}
            addonAfter="秒"
          />
          <Button onClick={() => void handleExportCover()} loading={coverExporting}>
            从最新成片导出封面
          </Button>
          {coverUrl && (
            <>
              <img
                src={coverUrl}
                alt="封面"
                style={{ height: 96, borderRadius: 4, border: '1px solid #444' }}
              />
              <a href={coverUrl} download={`cover_${coverTime}s.jpg`}>
                下载封面
              </a>
            </>
          )}
        </Space>
        <Typography.Paragraph type="secondary" style={{ fontSize: 12, marginTop: 6, marginBottom: 0 }}>
          需先完成一次合成；封面按所选时间点从最新成片截帧（JPEG）。
        </Typography.Paragraph>
      </Card>

      <Card
        title="视频切片标记"
        extra={
          <Space>
            <Button onClick={handleDistributeMarkSources} disabled={marks.length === 0}>
              按段轮换素材
            </Button>
            <Button onClick={() => void handlePreview()} disabled={marks.length === 0}>
              虚拟串播预览
            </Button>
            <Button onClick={handleRemark} loading={remarking} disabled={videos.length === 0}>
              重新随机标记
            </Button>
            <Button type="primary" onClick={handleCompose} loading={composing} disabled={marks.length === 0}>
              一键合成
            </Button>
          </Space>
        }
      >
        <Space direction="vertical" size={12} style={{ width: '100%' }}>
          <Row gutter={16}>
            <Col span={8}>
              <Statistic title="片段数" value={marks.length} />
            </Col>
            <Col span={8}>
              <Statistic title="标记总时长" value={totalDuration} suffix="秒" precision={1} />
            </Col>
            <Col span={8}>
              <Statistic
                title="音频总时长"
                value={audioTotal}
                suffix="秒"
                precision={1}
              />
            </Col>
          </Row>

          {marks.length === 0 ? (
            <Empty description="点击「重新随机标记」生成切片方案" />
          ) : (
            <Table
              size="small"
              rowKey="id"
              columns={markColumns}
              dataSource={marks}
              pagination={{ pageSize: 10, size: 'small' }}
            />
          )}

          {marks.length > 0 && (
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              每段可在「源视频」列单独换素材；「按段轮换素材」会把勾选的视频依次分配给各段。
              合成前服务端按源视频真实时长再次收敛切片，越界会自动修正。
            </Typography.Text>
          )}

          {task && (
            <div>
              <Typography.Text strong>合成任务</Typography.Text>
              <Progress
                percent={task.progress}
                status={
                  task.status === 'completed'
                    ? 'success'
                    : task.status === 'failed'
                      ? 'exception'
                      : 'active'
                }
              />
              <Space>
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  {task.status}
                </Typography.Text>
                {(task.status === 'failed' || task.status === 'cancelled') && (
                  <Button size="small" onClick={() => void handleRetryTask()} loading={retrying}>
                    重试任务
                  </Button>
                )}
              </Space>
            </div>
          )}
        </Space>
      </Card>

      {audios.length > 0 && (
        <Card title="音频列表">
          <List
            size="small"
            dataSource={audios.filter((a) => a.selected)}
            renderItem={(a) => (
              <List.Item>
                <Typography.Text>{a.name}</Typography.Text>
                <Typography.Text type="secondary">{a.durationStr}</Typography.Text>
              </List.Item>
            )}
          />
        </Card>
      )}

      <Modal
        title="虚拟串播预览"
        open={previewOpen}
        onCancel={closePreview}
        footer={null}
        width={720}
      >
        {durationMismatch && (
          <Alert
            type="warning"
            showIcon
            style={{ marginBottom: 12 }}
            message={`标记总时长 ${totalDuration.toFixed(1)}s 与音频总时长 ${audioTotal.toFixed(1)}s 相差 ${Math.abs(audioTotal - totalDuration).toFixed(1)}s（≥2s）`}
          />
        )}
        {previewLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin />
            <div style={{ marginTop: 8 }}>加载预览素材…</div>
          </div>
        ) : (
          <>
            <video
              ref={videoRef}
              controls
              onTimeUpdate={handleTimeUpdate}
              style={{ width: '100%', maxHeight: 420, background: '#000' }}
            />
            <audio ref={audioRef} src={previewAudioUrl ?? undefined} style={{ display: 'none' }} />
            <Space style={{ marginTop: 12 }}>
              <Typography.Text>
                片段：{playingIndex >= 0 ? playingIndex + 1 : 0} / {marks.length}
              </Typography.Text>
              {playingIndex >= 0 && marks[playingIndex] && (
                <Typography.Text type="secondary">
                  {marks[playingIndex].source} · {marks[playingIndex].start.toFixed(2)}s -
                  {marks[playingIndex].end.toFixed(2)}s
                </Typography.Text>
              )}
              {previewAudioUrl ? <Tag color="green">音频同步</Tag> : <Tag>无音频</Tag>}
            </Space>
          </>
        )}
      </Modal>
    </Space>
  )
}
