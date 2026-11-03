import request from './request'
import { API_ENDPOINTS } from '@/config/api'
import type { ApiResponse } from '@/types/api.types'
import type { components } from '@/types/api-schema.gen'
import { toTTSConfigPayload, toTTSConfigValues, type TTSConfigValues } from './ttsService'

/**
 * 三步流程服务（契约层 snake_case → 前端 camelCase）。
 * 类型全部来自 openapi-typescript 生成的 api-schema.gen.ts，禁止手写。
 */

/** Step2 文章（前端驼峰） */
interface Step2ArticleValues {
  title: string
  content: string
  wordCount: number
  ttsConfig: TTSConfigValues | null
}

/** Step1 表单：契约层 snake_case → 前端 camelCase */
type Step1Form = components['schemas']['Step1Form']
type Step1Outline = components['schemas']['Step1Outline']
type AudioItem = components['schemas']['AudioItem']
type VideoItem = components['schemas']['VideoItem']
type VideoMark = components['schemas']['VideoMark']

/** 前端表单：驼峰命名 */
export interface Step1FormValues {
  title: string
  author: string
  intro: string
  style: string
  targetDuration: number
  episodeIds: string[]
  textFiles: string[]
  keywords: string[]
  refTitles: string[]
  valuePoints: string[]
  goals: GoalValue[]
}

/** 快捷选项枚举（与后端 GOAL_TEXT_MAP 对应） */
export type GoalValue =
  | 'intro_episode'
  | 'random_story'
  | 'random_character'
  | 'random_perspective'

/** 前端大纲：驼峰命名 */
export interface Step1OutlineValues {
  coreKeywords: string[]
  coreWords: string[]
  refTitles: { title: string; subtitle: string }[]
  mainTask: string
  coreValue: string[]
  keypoints: string[]
}

/** 前端音频项 */
export interface AudioItemValues {
  path: string
  name: string
  duration: number
  durationStr: string
  source: 'system' | 'custom'
  selected: boolean
}

/** 前端视频项 */
export interface VideoItemValues {
  name: string
  duration: number
  durationStr: string
  selected: boolean
}

/** 前端视频标记 */
export interface VideoMarkValues {
  id: number
  source: string
  start: number
  end: number
  duration: number
  muted: boolean
  /** 进入本段的转场（覆盖全局），null/undefined = 继承全局 */
  transition?: TransitionConfigValues | null
}

/** 转场配置 */
export interface TransitionConfigValues {
  type: 'none' | 'fade' | 'slide' | 'zoom'
  duration: number
}

/** 主持人人像叠加配置 */
export interface AvatarConfigValues {
  fileId: string | null
  position: 'top_left' | 'top_right' | 'bottom_left' | 'bottom_right'
  sizeRatio: number
  borderColor: string
  borderWidth: number
  shadow: boolean
  start: number
  end: number | null
}

/** 成片质量预设 */
export interface QualityConfigValues {
  resolution: string
  crf: number
  preset: 'ultrafast' | 'veryfast' | 'fast' | 'medium' | 'slow'
}

/** 背景音乐配置 */
export interface BGMConfigValues {
  fileId: string | null
  volume: number
  ducking: boolean
  duckLevel: number
  fadeIn: number
  fadeOut: number
  loop: boolean
}

/** 片头 / 片尾字卡 */
export interface IntroOutroItemValues {
  enabled: boolean
  title: string
  subtitle: string
  duration: number
  backgroundColor: string
  textColor: string
  imageFileId: string | null
}

export interface IntroOutroConfigValues {
  intro: IntroOutroItemValues
  outro: IntroOutroItemValues
}

/** 字幕模板在烧录端的真实参数（用于等比换算预览） */
export interface SubtitleStyleSpecValues {
  name: string
  forceStyle: string
  fontSize: number
  marginV: number
  alignment: number
  outline: number
  borderStyle: number
  primaryColour: string
  outlineColour: string
  backColour: string
}

/** 字幕位置微调（0=跟随样式；1~9 对应 ASS 九宫格） */
export interface SubtitlePositionValues {
  alignment: number
  marginV: number
  marginH: number
}

/** Step3 素材列表 */
export interface MediaListValues {
  systemAudios: AudioItemValues[]
  customAudios: AudioItemValues[]
  videoFiles: VideoItemValues[]
  deletedAudioPaths: string[]
  deletedVideoPaths: string[]
}

// ============================================================
// 映射函数
// ============================================================

function toFormPayload(form: Step1FormValues): Step1Form {
  return {
    title: form.title,
    author: form.author,
    intro: form.intro,
    style: form.style,
    target_duration: form.targetDuration,
    episode_ids: form.episodeIds,
    text_files: form.textFiles,
    keywords: form.keywords,
    ref_titles: form.refTitles,
    value_points: form.valuePoints,
    goals: form.goals,
  }
}

function toFormValues(form?: Step1Form): Step1FormValues {
  return {
    title: form?.title ?? '',
    author: form?.author ?? '',
    intro: form?.intro ?? '',
    style: form?.style ?? '热血安利',
    targetDuration: form?.target_duration ?? 70,
    episodeIds: form?.episode_ids ?? [],
    textFiles: form?.text_files ?? [],
    keywords: form?.keywords ?? [],
    refTitles: form?.ref_titles ?? [],
    valuePoints: form?.value_points ?? [],
    goals: (form?.goals ?? []) as GoalValue[],
  }
}

function toOutlineValues(outline?: Step1Outline): Step1OutlineValues {
  return {
    coreKeywords: outline?.core_keywords ?? [],
    coreWords: outline?.core_words ?? [],
    refTitles: (outline?.ref_titles ?? []).map((t) => ({
      title: t?.title ?? '',
      subtitle: t?.subtitle ?? '',
    })),
    mainTask: outline?.main_task ?? '',
    coreValue: outline?.core_value ?? [],
    keypoints: outline?.keypoints ?? [],
  }
}

function toOutlinePayload(outline: Step1OutlineValues): Step1Outline {
  return {
    core_keywords: outline.coreKeywords,
    core_words: outline.coreWords,
    ref_titles: outline.refTitles,
    main_task: outline.mainTask,
    core_value: outline.coreValue,
    keypoints: outline.keypoints,
  }
}

function toAudioItem(item: AudioItem): AudioItemValues {
  return {
    path: item.path ?? '',
    name: item.name ?? '',
    duration: item.duration ?? 0,
    durationStr: item.duration_str ?? '00:00',
    source: item.source === 'custom' ? 'custom' : 'system',
    selected: item.selected ?? true,
  }
}

function toVideoItem(item: VideoItem): VideoItemValues {
  return {
    name: item.name ?? '',
    duration: item.duration ?? 0,
    durationStr: item.duration_str ?? '00:00',
    selected: item.selected ?? true,
  }
}

function toVideoMark(mark: VideoMark): VideoMarkValues {
  return {
    id: mark.id ?? 0,
    source: mark.source ?? '',
    start: mark.start ?? 0,
    end: mark.end ?? 0,
    duration: mark.duration ?? 0,
    muted: mark.muted ?? true,
    transition: mark.transition
      ? {
          type: (mark.transition.type ?? 'none') as TransitionConfigValues['type'],
          duration: mark.transition.duration ?? 0.5,
        }
      : null,
  }
}

// ============================================================
// Step 服务
// ============================================================

function toCardPayload(item: IntroOutroItemValues) {
  return {
    enabled: item.enabled,
    title: item.title,
    subtitle: item.subtitle,
    duration: item.duration,
    background_color: item.backgroundColor,
    text_color: item.textColor,
    image_file_id: item.imageFileId ?? undefined,
  }
}

export const stepService = {
  /** Step1：读取已保存的表单与大纲（用于刷新后恢复进度）。 */
  loadStep1: async (creationId: string): Promise<Step1LoadValues> => {
    const res = await request.get<never, ApiResponse<components['schemas']['Step1SaveResponse']>>(
      '/step1/load',
      { params: { creation_id: creationId } },
    )
    return {
      currentStep: res.data?.current_step ?? 1,
      form: res.data?.form ? toFormValues(res.data.form) : null,
      outline: res.data?.outline ? toOutlineValues(res.data.outline) : null,
    }
  },

  /** Step1：生成大纲（AI，不落库）。 */
  generateOutline: async (
    creationId: string,
    form: Step1FormValues,
  ): Promise<Step1OutlineValues> => {
    const res = await request.post<never, ApiResponse<components['schemas']['Step1OutlineResponse']>>(
      '/step1/outline',
      { creation_id: creationId, form: toFormPayload(form) },
    )
    return toOutlineValues(res.data?.outline)
  },

  /** Step1：保存创作信息与大纲。 */
  saveStep1: async (
    creationId: string,
    form: Step1FormValues,
    outline: Step1OutlineValues,
  ): Promise<number> => {
    const res = await request.post<never, ApiResponse<components['schemas']['Step1SaveResponse']>>(
      '/step1/save',
      { creation_id: creationId, form: toFormPayload(form), outline: toOutlinePayload(outline) },
    )
    return res.data?.current_step ?? 1
  },

  /** Step2：生成口播长文。 */
  generateArticle: async (creationId: string): Promise<Step2ArticleValues> => {
    const res = await request.post<never, ApiResponse<components['schemas']['Step2GenerateResponse']>>(
      '/step2/generate',
      { creation_id: creationId },
    )
    return {
      title: res.data?.title ?? '',
      content: res.data?.content ?? '',
      wordCount: res.data?.word_count ?? 0,
      ttsConfig: res.data?.tts_config ? toTTSConfigValues(res.data.tts_config) : null,
    }
  },

  /** Step2：读取已保存的口播长文。 */
  loadArticle: async (creationId: string): Promise<Step2ArticleValues | null> => {
    const res = await request.get<never, ApiResponse<components['schemas']['Step2GenerateResponse']>>(
      '/step2/load',
      { params: { creation_id: creationId } },
    )
    if (!res.data) return null
    return {
      title: res.data.title ?? '',
      content: res.data.content ?? '',
      wordCount: res.data.word_count ?? 0,
      ttsConfig: res.data.tts_config ? toTTSConfigValues(res.data.tts_config) : null,
    }
  },

  /** Step2：保存口播长文（可触发异步 TTS）。 */
  saveArticle: async (params: {
    creationId: string
    title: string
    content: string
    wordCount: number
    skipTts?: boolean
    ttsConfig?: TTSConfigValues | null
  }): Promise<{ currentStep: number; ttsTaskId: string | null }> => {
    const res = await request.post<never, ApiResponse<components['schemas']['Step2SaveResponse']>>(
      '/step2/save',
      {
        creation_id: params.creationId,
        title: params.title,
        content: params.content,
        word_count: params.wordCount,
        skip_tts: params.skipTts ?? false,
        tts_config: params.ttsConfig ? toTTSConfigPayload(params.ttsConfig) : undefined,
      },
    )
    return {
      currentStep: res.data?.current_step ?? 2,
      ttsTaskId: res.data?.tts_task_id ?? null,
    }
  },

  /** Step3：获取素材列表。 */
  getMediaList: async (creationId: string): Promise<MediaListValues> => {
    const res = await request.get<
      never,
      ApiResponse<components['schemas']['Step3MediaListResponse']>
    >('/step3/media-list', { params: { creation_id: creationId } })
    const d = res.data
    return {
      systemAudios: (d?.system_audios ?? []).map(toAudioItem),
      customAudios: (d?.custom_audios ?? []).map(toAudioItem),
      videoFiles: (d?.video_files ?? []).map(toVideoItem),
      deletedAudioPaths: d?.deleted_audio_paths ?? [],
      deletedVideoPaths: d?.deleted_video_paths ?? [],
    }
  },

  /** Step3：读取已保存的标记（刷新后恢复手动指定）。 */
  getMarkers: async (
    creationId: string,
  ): Promise<{ markers: VideoMarkValues[]; totalDuration: number; videoFiles: VideoItemValues[] }> => {
    const res = await request.get<
      never,
      ApiResponse<{ markers?: components['schemas']['VideoMark'][]; total_duration?: number; video_files?: components['schemas']['VideoItem'][] }>
    >('/step3/markers', { params: { creation_id: creationId } })
    const d = res.data
    return {
      markers: (d?.markers ?? []).map(toVideoMark),
      totalDuration: d?.total_duration ?? 0,
      videoFiles: (d?.video_files ?? []).map(toVideoItem),
    }
  },

  /** Step3：保存手动编辑后的标记（刷新后仍可恢复）。 */
  saveMarkers: async (
    creationId: string,
    markers: VideoMarkValues[],
  ): Promise<{ markers: VideoMarkValues[]; totalDuration: number }> => {
    const res = await request.post<
      never,
      ApiResponse<{ markers?: components['schemas']['VideoMark'][]; total_duration?: number }>
    >('/step3/markers', {
      creation_id: creationId,
      markers: markers.map((m) => ({
        id: m.id,
        source: m.source,
        start: m.start,
        end: m.end,
        duration: m.duration,
        muted: m.muted,
        transition: m.transition
          ? {
              type: m.transition.type,
              duration: m.transition.duration,
            }
          : null,
      })),
    })
    const d = res.data
    return {
      markers: (d?.markers ?? []).map(toVideoMark),
      totalDuration: d?.total_duration ?? 0,
    }
  },

  /** Step3：重新随机标记。 */
  remark: async (params: {
    creationId: string
    videoFiles?: string[]
    targetDuration?: number | null
  }): Promise<{
    markersPath: string
    markerCount: number
    totalDuration: number
    sourcesUsed: string[]
    videoFiles: VideoItemValues[]
    markers: VideoMarkValues[]
  }> => {
    const res = await request.post<never, ApiResponse<components['schemas']['Step3RemarkResponse']>>(
      '/step3/remark',
      {
        creation_id: params.creationId,
        video_files: params.videoFiles ?? [],
        target_duration: params.targetDuration ?? null,
      },
    )
    const d = res.data
    return {
      markersPath: d?.markers_path ?? '',
      markerCount: d?.marker_count ?? 0,
      totalDuration: d?.total_duration ?? 0,
      sourcesUsed: d?.sources_used ?? [],
      videoFiles: (d?.video_files ?? []).map(toVideoItem),
      markers: (d?.markers ?? []).map(toVideoMark),
    }
  },

  /** Step3：保存素材选择状态。 */
  saveState: async (params: {
    creationId: string
    audioFiles: AudioItemValues[]
    videoFiles: VideoItemValues[]
    deletedMedia: { audio_paths: string[]; video_paths: string[] }
    composeSettings?: Record<string, unknown>
  }): Promise<number> => {
    const res = await request.post<never, ApiResponse<components['schemas']['Step3SaveStateResponse']>>(
      '/step3/save-state',
      {
        creation_id: params.creationId,
        audio_files: params.audioFiles,
        video_files: params.videoFiles,
        deleted_media: params.deletedMedia,
        compose_settings: params.composeSettings,
      },
    )
    return res.data?.current_step ?? 3
  },

  /** Step3：提交一键合成任务。 */
  compose: async (params: {
    creationId: string
    audioFiles: string[]
    markers: VideoMarkValues[]
    fastMode?: boolean
    resolution?: string
    subtitleStyle?: string
    subtitlePosition?: SubtitlePositionValues
    globalTransition?: TransitionConfigValues
    avatar?: AvatarConfigValues | null
    quality?: QualityConfigValues
    bgm?: BGMConfigValues | null
    introOutro?: IntroOutroConfigValues | null
  }): Promise<string> => {
    const res = await request.post<never, ApiResponse<components['schemas']['Step3ComposeResponse']>>(
      '/step3/compose',
      {
        creation_id: params.creationId,
        audio_files: params.audioFiles,
        markers: params.markers,
        fast_mode: params.fastMode ?? false,
        resolution: params.resolution ?? '1080x1920',
        subtitle_style: params.subtitleStyle ?? '默认白字黑描边',
        subtitle_position: params.subtitlePosition
          ? {
              alignment: params.subtitlePosition.alignment,
              margin_v: params.subtitlePosition.marginV,
              margin_h: params.subtitlePosition.marginH,
            }
          : undefined,
        global_transition: params.globalTransition
          ? { type: params.globalTransition.type, duration: params.globalTransition.duration }
          : undefined,
        avatar: params.avatar
          ? {
              file_id: params.avatar.fileId ?? undefined,
              position: params.avatar.position,
              size_ratio: params.avatar.sizeRatio,
              border_color: params.avatar.borderColor,
              border_width: params.avatar.borderWidth,
              shadow: params.avatar.shadow,
              start: params.avatar.start,
              end: params.avatar.end ?? undefined,
            }
          : undefined,
        quality: params.quality
          ? {
              resolution: params.quality.resolution,
              crf: params.quality.crf,
              preset: params.quality.preset,
            }
          : undefined,
        bgm: params.bgm
          ? {
              file_id: params.bgm.fileId ?? undefined,
              volume: params.bgm.volume,
              ducking: params.bgm.ducking,
              duck_level: params.bgm.duckLevel,
              fade_in: params.bgm.fadeIn,
              fade_out: params.bgm.fadeOut,
              loop: params.bgm.loop,
            }
          : undefined,
        intro_outro: params.introOutro
          ? {
              intro: toCardPayload(params.introOutro.intro),
              outro: toCardPayload(params.introOutro.outro),
            }
          : undefined,
      },
    )
    return res.data?.task_id ?? ''
  },

  /** Step3：从成片导出封面帧（返回 JPEG blob）。 */
  exportCover: async (params: {
    creationId: string
    outputPath?: string
    time?: number
  }): Promise<Blob> => {
    const res = await request.post<never, Blob>(
      API_ENDPOINTS.STEP.STEP3_COVER,
      {
        creation_id: params.creationId,
        output_path: params.outputPath ?? undefined,
        time: params.time ?? undefined,
      },
      { responseType: 'blob', timeout: 5 * 60_000 },
    )
    return res as unknown as Blob
  },

  /** Step3：绑定批量上传的视频素材，返回最新视频列表。 */
  bindVideoSources: async (
    creationId: string,
    fileIds: string[],
  ): Promise<VideoItemValues[]> => {
    const res = await request.post<
      never,
      ApiResponse<{ video_files: Array<Record<string, unknown>> }>
    >(API_ENDPOINTS.STEP.STEP3_VIDEO_SOURCES, {
      creation_id: creationId,
      file_ids: fileIds,
    })
    return (res.data?.video_files ?? []).map((v) => ({
      name: String(v.name ?? ''),
      duration: Number(v.duration ?? 0),
      durationStr: String(v.duration_str ?? ''),
      selected: Boolean(v.selected ?? true),
    }))
  },

  /** Step3：字幕模板 + 烧录端真实参数（字号/边距/对齐）。 */
  getSubtitleStyles: async (): Promise<SubtitleStyleSpecValues[]> => {
    const res = await request.get<
      never,
      ApiResponse<Array<Record<string, unknown>>>
    >(API_ENDPOINTS.STEP.STEP3_SUBTITLE_STYLES)
    return (res.data ?? []).map((s) => ({
      name: String(s.name ?? ''),
      forceStyle: String(s.force_style ?? ''),
      fontSize: Number(s.font_size ?? 18),
      marginV: Number(s.margin_v ?? 30),
      alignment: Number(s.alignment ?? 2),
      outline: Number(s.outline ?? 1),
      borderStyle: Number(s.border_style ?? 1),
      primaryColour: String(s.primary_colour ?? '&H00FFFFFF'),
      outlineColour: String(s.outline_colour ?? '&H00000000'),
      backColour: String(s.back_colour ?? '&H00000000'),
    }))
  },

  /** 完成页：多次合成列表。 */
  listOutputs: async (creationId: string): Promise<OutputValues[]> => {
    const res = await request.get<never, ApiResponse<components['schemas']['Output'][]>>(
      `/creations/${creationId}/outputs`,
    )
    return (res.data ?? []).map((o) => ({
      id: o.id ?? '',
      creationId: o.creation_id ?? '',
      version: o.version ?? 0,
      outputPath: o.output_path ?? '',
      duration: o.duration ?? 0,
      durationStr: o.duration_str ?? '00:00',
      fileSize: o.file_size ?? 0,
      resolution: o.resolution ?? '',
      isLatest: o.is_latest ?? false,
      createdAt: o.created_at ?? '',
    }))
  },

  /** 获取某 Step 的历史版本（倒序）。 */
  listHistory: async (
    projectId: string,
    creationId: string,
    stepNo: number,
  ): Promise<StepHistoryValues[]> => {
    const res = await request.get<never, ApiResponse<components['schemas']['StepResult'][]>>(
      API_ENDPOINTS.CREATIONS.HISTORY(projectId, creationId, stepNo),
    )
    return (res.data ?? []).map((h) => ({
      id: h.id ?? '',
      stepNo: h.step_no ?? stepNo,
      version: h.version ?? 0,
      createdAt: h.created_at ?? '',
    }))
  },

  /** 回滚到指定历史版本（复制为新版本，不删除历史）。 */
  rollbackStep: async (
    projectId: string,
    creationId: string,
    stepNo: number,
    version: number,
  ): Promise<StepHistoryValues> => {
    const res = await request.post<never, ApiResponse<components['schemas']['StepResult']>>(
      API_ENDPOINTS.CREATIONS.ROLLBACK(projectId, creationId, stepNo, version),
    )
    const d = res.data
    return {
      id: d?.id ?? '',
      stepNo: d?.step_no ?? stepNo,
      version: d?.version ?? version,
      createdAt: d?.created_at ?? '',
    }
  },

  /** 拉取成片二进制（带 Bearer 鉴权），返回 blob URL 供内联播放。 */
  fetchOutputObjectUrl: async (creationId: string, outputId: string): Promise<string> => {
    const res = await request.get<never, Blob>(
      API_ENDPOINTS.OUTPUTS.FILE(creationId, outputId),
      { responseType: 'blob', timeout: 30 * 60_000 },
    )
    return URL.createObjectURL(res as unknown as Blob)
  },

  /** 拉取素材预览二进制（音频/视频串播），返回 blob URL。 */
  fetchMediaObjectUrl: async (
    creationId: string,
    scope: 'video' | 'audio',
    name: string,
  ): Promise<string> => {
    const res = await request.get<never, Blob>(API_ENDPOINTS.STEP.STEP3_PREVIEW, {
      params: { creation_id: creationId, scope, name },
      responseType: 'blob',
      timeout: 10 * 60_000,
    })
    return URL.createObjectURL(res as unknown as Blob)
  },

  /** 下载成片（带 Bearer 鉴权，触发浏览器保存）。 */
  downloadOutput: async (
    creationId: string,
    outputId: string,
    filename: string,
  ): Promise<void> => {
    const res = await request.get<never, Blob>(API_ENDPOINTS.OUTPUTS.FILE(creationId, outputId), {
      params: { download: true },
      responseType: 'blob',
      timeout: 30 * 60_000,
    })
    const url = URL.createObjectURL(res as unknown as Blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  },
}

/** Step1 已保存进度 */
export interface Step1LoadValues {
  currentStep: number
  form: Step1FormValues | null
  outline: Step1OutlineValues | null
}

/** Step 历史版本项 */
export interface StepHistoryValues {
  id: string
  stepNo: number
  version: number
  createdAt: string
}

/** 成品项 */
export interface OutputValues {
  id: string
  creationId: string
  version: number
  outputPath: string
  duration: number
  durationStr: string
  fileSize: number
  resolution: string
  isLatest: boolean
  createdAt: string
}
