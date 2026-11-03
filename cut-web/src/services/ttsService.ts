import request from './request'
import { API_ENDPOINTS } from '@/config/api'
import type { ApiResponse } from '@/types/api.types'
import type { components } from '@/types/api-schema.gen'

type ApiVoice = components['schemas']['TTSVoice']
type ApiTTSConfig = components['schemas']['TTSConfig']
type ApiTTSSegment = components['schemas']['TTSSegment']

/** 音色目录项（前端驼峰） */
export interface TTSVoiceValues {
  id: string
  name: string
  gender: string
  style: string
  voice: string
  rate: number
  pitch: number
  volume: number
  description: string
}

/** 段落音色配置（前端驼峰） */
export interface TTSSegmentValues {
  index: number
  text: string
  voiceId: string | null
  rate: number
  pitch: number
  volume: number
  pauseAfterMs: number
}

/** 整篇 TTS 配置（前端驼峰） */
export interface TTSConfigValues {
  provider: string
  globalVoiceId: string
  rate: number
  pitch: number
  volume: number
  paragraphGapMs: number
  segments: TTSSegmentValues[]
}

export const DEFAULT_TTS_CONFIG: TTSConfigValues = {
  provider: 'edge-tts',
  globalVoiceId: 'female_sweet',
  rate: 0,
  pitch: 0,
  volume: 0,
  paragraphGapMs: 300,
  segments: [],
}

function toVoice(v: ApiVoice): TTSVoiceValues {
  return {
    id: v.id ?? '',
    name: v.name ?? '',
    gender: v.gender ?? '',
    style: v.style ?? '',
    voice: v.voice ?? '',
    rate: v.rate ?? 0,
    pitch: v.pitch ?? 0,
    volume: v.volume ?? 0,
    description: v.description ?? '',
  }
}

/** 契约 TTSConfig → 前端驼峰 */
export function toTTSConfigValues(config?: ApiTTSConfig | null): TTSConfigValues {
  if (!config) return { ...DEFAULT_TTS_CONFIG }
  return {
    provider: config.provider ?? DEFAULT_TTS_CONFIG.provider,
    globalVoiceId: config.global_voice_id ?? DEFAULT_TTS_CONFIG.globalVoiceId,
    rate: config.rate ?? 0,
    pitch: config.pitch ?? 0,
    volume: config.volume ?? 0,
    paragraphGapMs: config.paragraph_gap_ms ?? 300,
    segments: (config.segments ?? []).map((s) => ({
      index: s.index ?? 0,
      text: s.text ?? '',
      voiceId: s.voice_id ?? null,
      rate: s.rate ?? 0,
      pitch: s.pitch ?? 0,
      volume: s.volume ?? 0,
      pauseAfterMs: s.pause_after_ms ?? 0,
    })),
  }
}

/** 前端驼峰 → 契约 TTSConfig */
export function toTTSConfigPayload(config: TTSConfigValues): ApiTTSConfig {
  return {
    provider: config.provider,
    global_voice_id: config.globalVoiceId,
    rate: config.rate,
    pitch: config.pitch,
    volume: config.volume,
    paragraph_gap_ms: config.paragraphGapMs,
    segments: config.segments.map(
      (s): ApiTTSSegment => ({
        index: s.index,
        text: s.text,
        voice_id: s.voiceId ?? undefined,
        rate: s.rate,
        pitch: s.pitch,
        volume: s.volume,
        pause_after_ms: s.pauseAfterMs,
      }),
    ),
  }
}

/** TTS 服务：音色目录 + 试听。 */
export const ttsService = {
  /** 获取音色目录（13 个中文风格预设）。 */
  listVoices: async (): Promise<TTSVoiceValues[]> => {
    const res = await request.get<never, ApiResponse<ApiVoice[]>>(API_ENDPOINTS.TTS.VOICES)
    return (res.data ?? []).map(toVoice)
  },

  /** 试听：返回可播放的 blob URL（调用方负责 revoke）。 */
  previewUrl: async (params: {
    text?: string
    voiceId: string
    rate?: number
    pitch?: number
    volume?: number
  }): Promise<string> => {
    const res = await request.post<never, Blob>(API_ENDPOINTS.TTS.PREVIEW, {
      text: params.text ?? '这是一段音色试听，欢迎使用漫剧推广素材剪辑师。',
      voice_id: params.voiceId,
      rate: params.rate ?? 0,
      pitch: params.pitch ?? 0,
      volume: params.volume ?? 0,
    }, { responseType: 'blob', timeout: 60_000 })
    return URL.createObjectURL(res as unknown as Blob)
  },
}
