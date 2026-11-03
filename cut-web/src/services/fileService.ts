import request, { API_ENDPOINTS } from './request'
import type { ApiResponse, PageData, PageParams } from '@/types/api.types'
import type { components } from '@/types/api-schema.gen'

type ApiFileMeta = components['schemas']['FileMeta']

/** 文件元信息（前端驼峰） */
export interface FileMetaValues {
  id: string
  filename: string
  path: string
  sizeBytes: number
  mimeType: string | null
  createdAt: string
}

function toFileMeta(f: ApiFileMeta): FileMetaValues {
  return {
    id: f.id ?? '',
    filename: f.filename ?? '',
    path: f.path ?? '',
    sizeBytes: f.size_bytes ?? 0,
    mimeType: f.mime_type ?? null,
    createdAt: f.created_at ?? '',
  }
}

/** 文件服务：上传 / 列表 / 预览（带鉴权取流）/ 下载 / 删除 / 目录浏览。 */
export const fileService = {
  /** 上传单个文件（multipart）。onProgress 回调用于进度条。 */
  upload: async (
    file: File,
    options: { subDir?: string; onProgress?: (percent: number) => void } = {},
  ) => {
    const form = new FormData()
    form.append('file', file, file.name)
    if (options.subDir) form.append('sub_dir', options.subDir)

    const res = await request.post<never, ApiResponse<components['schemas']['FileUploadResponse']>>(
      API_ENDPOINTS.FILES.UPLOAD,
      form,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30 * 60_000,
        onUploadProgress: (e) => {
          if (options.onProgress && e.total) {
            options.onProgress(Math.round((e.loaded / e.total) * 100))
          }
        },
      },
    )
    return {
      id: res.data?.id ?? '',
      filename: res.data?.filename ?? '',
      path: res.data?.path ?? '',
      sizeBytes: res.data?.size_bytes ?? 0,
      mimeType: res.data?.mime_type ?? '',
    }
  },

  /** 我的文件列表（分页） */
  list: async (params: PageParams & { subDir?: string } = {}) => {
    const res = await request.get<never, ApiResponse<PageData<ApiFileMeta>>>(API_ENDPOINTS.FILES.LIST, {
      params: {
        page: params.page ?? 1,
        pageSize: params.pageSize ?? 20,
        sub_dir: params.subDir || undefined,
      },
    })
    const d = res.data
    return {
      page: d?.page ?? 1,
      pageSize: d?.pageSize ?? 20,
      total: d?.total ?? 0,
      items: (d?.items ?? []).map(toFileMeta),
    }
  },

  /** 拉取文件二进制（带 Bearer 鉴权），返回 blob URL。 */
  fetchObjectUrl: async (fileId: string): Promise<string> => {
    const res = await request.get<never, Blob>(API_ENDPOINTS.FILES.PREVIEW(fileId), {
      responseType: 'blob',
      timeout: 10 * 60_000,
    })
    return URL.createObjectURL(res as unknown as Blob)
  },

  /** 下载文件（带鉴权），触发浏览器保存。 */
  download: async (fileId: string, filename: string): Promise<void> => {
    const res = await request.get<never, Blob>(API_ENDPOINTS.FILES.DOWNLOAD(fileId), {
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

  remove: (fileId: string) => request.delete(API_ENDPOINTS.FILES.DETAIL(fileId)),

  /** 浏览服务器目录（新建剧集选素材用） */
  browseDir: async (path: string) => {
    const res = await request.get<
      never,
      ApiResponse<{ path: string; parent: string | null; dirs: string[]; files: string[] }>
    >(API_ENDPOINTS.FILES.BROWSE_DIR, { params: { path } })
    return res.data
  },
}