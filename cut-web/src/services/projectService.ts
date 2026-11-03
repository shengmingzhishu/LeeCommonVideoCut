import request from './request'
import { API_ENDPOINTS } from '@/config/api'
import type { ApiResponse, PageData } from '@/types/api.types'
import type { components } from '@/types/api-schema.gen'

type ApiProject = components['schemas']['Project']
type ApiEpisode = components['schemas']['Episode']
type ApiCreation = components['schemas']['Creation']

/** 项目（驼峰） */
export interface ProjectValues {
  id: string
  userId: string
  title: string
  author: string
  intro: string
  cover: string
  videoDir: string
  introDir: string
  status: string
  createdAt: string
  updatedAt: string
}

/** 剧集（驼峰） */
export interface EpisodeValues {
  id: string
  projectId: string
  userId: string
  title: string
  description: string
  status: string
  createdAt: string
}

/** 创作（驼峰） */
export interface CreationValues {
  id: string
  episodeId: string
  userId: string
  title: string
  currentStep: number
  status: string
  createdAt: string
}

function toProject(p: ApiProject): ProjectValues {
  return {
    id: p.id ?? '',
    userId: p.user_id ?? '',
    title: p.title ?? '',
    author: p.author ?? '',
    intro: p.intro ?? '',
    cover: p.cover ?? '🎬',
    videoDir: p.video_dir ?? '',
    introDir: p.intro_dir ?? '',
    status: p.status ?? 'active',
    createdAt: p.created_at ?? '',
    updatedAt: p.updated_at ?? '',
  }
}

function toEpisode(e: ApiEpisode): EpisodeValues {
  return {
    id: e.id ?? '',
    projectId: e.project_id ?? '',
    userId: e.user_id ?? '',
    title: e.title ?? '',
    description: e.description ?? '',
    status: e.status ?? 'active',
    createdAt: e.created_at ?? '',
  }
}

function toCreation(c: ApiCreation): CreationValues {
  return {
    id: c.id ?? '',
    episodeId: c.episode_id ?? '',
    userId: c.user_id ?? '',
    title: c.title ?? '',
    currentStep: c.current_step ?? 1,
    status: c.status ?? 'active',
    createdAt: c.created_at ?? '',
  }
}

export const projectService = {
  /** 项目列表（分页）。 */
  list: async (params: { page?: number; pageSize?: number; keyword?: string } = {}) => {
    const res = await request.get<never, ApiResponse<PageData<ApiProject>>>(
      API_ENDPOINTS.PROJECTS.LIST,
      {
        params: {
          page: params.page ?? 1,
          pageSize: params.pageSize ?? 20,
          keyword: params.keyword || undefined,
        },
      },
    )
    const d = res.data
    return {
      page: d?.page ?? 1,
      pageSize: d?.pageSize ?? 20,
      total: d?.total ?? 0,
      items: (d?.items ?? []).map(toProject),
    }
  },

  /** 创建项目。videoFileIds 由已上传文件解析为素材目录（优先于 videoDir）。 */
  create: async (payload: {
    title: string
    author: string
    intro: string
    videoDir?: string
    introDir?: string
    cover?: string
    videoFileIds?: string[]
  }): Promise<ProjectValues> => {
    const res = await request.post<never, ApiResponse<ApiProject>>(API_ENDPOINTS.PROJECTS.LIST, {
      title: payload.title,
      author: payload.author,
      intro: payload.intro,
      video_dir: payload.videoDir || null,
      intro_dir: payload.introDir || null,
      cover: payload.cover ?? '🎬',
      video_file_ids: payload.videoFileIds?.length ? payload.videoFileIds : null,
    })
    return toProject(res.data ?? ({} as ApiProject))
  },

  /** 更新项目（videoFileIds 优先于 videoDir；传空数组可解绑视频源）。 */
  update: async (
    projectId: string,
    payload: {
      title?: string
      author?: string
      intro?: string
      videoDir?: string | null
      introDir?: string | null
      cover?: string
      videoFileIds?: string[]
    },
  ): Promise<ProjectValues> => {
    const body: Record<string, unknown> = {
      title: payload.title,
      author: payload.author,
      intro: payload.intro,
      cover: payload.cover,
    }
    if (payload.videoDir !== undefined) body.video_dir = payload.videoDir
    if (payload.introDir !== undefined) body.intro_dir = payload.introDir
    if (payload.videoFileIds !== undefined) body.video_file_ids = payload.videoFileIds
    const res = await request.put<never, ApiResponse<ApiProject>>(
      API_ENDPOINTS.PROJECTS.DETAIL(projectId),
      body,
    )
    return toProject(res.data ?? ({} as ApiProject))
  },

  /** 项目详情。 */
  get: async (projectId: string): Promise<ProjectValues> => {
    const res = await request.get<never, ApiResponse<ApiProject>>(
      API_ENDPOINTS.PROJECTS.DETAIL(projectId),
    )
    return toProject(res.data ?? ({} as ApiProject))
  },

  /** 复制项目（仅元数据，不含剧集/创作）。 */
  copy: async (projectId: string): Promise<ProjectValues> => {
    const res = await request.post<never, ApiResponse<ApiProject>>(
      API_ENDPOINTS.PROJECTS.COPY(projectId),
    )
    return toProject(res.data ?? ({} as ApiProject))
  },

  /** 删除项目。 */
  remove: async (projectId: string): Promise<void> => {
    await request.delete(API_ENDPOINTS.PROJECTS.DETAIL(projectId))
  },

  /** 剧集列表。 */
  listEpisodes: async (projectId: string): Promise<EpisodeValues[]> => {
    const res = await request.get<never, ApiResponse<ApiEpisode[]>>(
      API_ENDPOINTS.PROJECTS.EPISODES(projectId),
    )
    return (res.data ?? []).map(toEpisode)
  },

  /** 创建剧集。 */
  createEpisode: async (projectId: string, payload: { title: string; description?: string }) => {
    const res = await request.post<never, ApiResponse<ApiEpisode>>(
      API_ENDPOINTS.PROJECTS.EPISODES(projectId),
      { title: payload.title, description: payload.description ?? null },
    )
    return toEpisode(res.data ?? ({} as ApiEpisode))
  },

  /** 创作列表。 */
  listCreations: async (projectId: string): Promise<CreationValues[]> => {
    const res = await request.get<never, ApiResponse<ApiCreation[]>>(
      API_ENDPOINTS.PROJECTS.CREATIONS(projectId),
    )
    return (res.data ?? []).map(toCreation)
  },

  /** 创建创作。 */
  createCreation: async (projectId: string, payload: { episodeId: string; title?: string }) => {
    const res = await request.post<never, ApiResponse<ApiCreation>>(
      API_ENDPOINTS.PROJECTS.CREATIONS(projectId),
      { episode_id: payload.episodeId, title: payload.title ?? null },
    )
    return toCreation(res.data ?? ({} as ApiCreation))
  },
}
