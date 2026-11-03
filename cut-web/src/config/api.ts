/**
 * API 路径常量（react-stack 规则 §9.2）
 * Service 层引用这里的常量，禁止硬编码 URL。
 * 路径与 docs/openapi.yaml 保持一致。
 */
export const API_ENDPOINTS = {
  SYSTEM: {
    HEALTH: '/health',
  },
  AUTH: {
    REGISTER: '/auth/register',
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    CHANGE_PASSWORD: '/auth/change-password',
  },
  USERS: {
    ME: '/users/me',
  },
  PROJECTS: {
    LIST: '/projects',
    DETAIL: (id: string) => `/projects/${id}`,
    COPY: (id: string) => `/projects/${id}/copy`,
    EPISODES: (id: string) => `/projects/${id}/episodes`,
    CREATIONS: (id: string) => `/projects/${id}/creations`,
  },
  CREATIONS: {
    DETAIL: (id: string) => `/creations/${id}`,
    OUTPUTS: (id: string) => `/creations/${id}/outputs`,
    HISTORY: (projectId: string, creationId: string, stepNo: number) =>
      `/projects/${projectId}/creations/${creationId}/history/${stepNo}`,
    ROLLBACK: (projectId: string, creationId: string, stepNo: number, version: number) =>
      `/projects/${projectId}/creations/${creationId}/rollback/${stepNo}/${version}`,
  },
  STEP: {
    STEP1_OUTLINE: '/step1/outline',
    STEP1_SAVE: '/step1/save',
    STEP1_LOAD: '/step1/load',
    STEP2_GENERATE: '/step2/generate',
    STEP2_SAVE: '/step2/save',
    STEP2_LOAD: '/step2/load',
    STEP3_MEDIA_LIST: '/step3/media-list',
    STEP3_PREVIEW: '/step3/preview',
    STEP3_REMARK: '/step3/remark',
    STEP3_SAVE_STATE: '/step3/save-state',
    STEP3_COMPOSE: '/step3/compose',
    STEP3_COVER: '/step3/cover',
    STEP3_VIDEO_SOURCES: '/step3/video-sources',
    STEP3_SUBTITLE_STYLES: '/step3/subtitle-styles',
  },
  TTS: {
    VOICES: '/tts/voices',
    PREVIEW: '/tts/preview',
  },
  TASKS: {
    LIST: '/tasks',
    DETAIL: (id: string) => `/tasks/${id}`,
    RETRY: (id: string) => `/tasks/${id}/retry`,
  },
  OUTPUTS: {
    LIST: (creationId: string) => `/creations/${creationId}/outputs`,
    FILE: (creationId: string, outputId: string) =>
      `/creations/${creationId}/outputs/${outputId}/file`,
  },
  FILES: {
    LIST: '/files',
    UPLOAD: '/files/upload',
    DETAIL: (id: string) => `/files/${id}`,
    PREVIEW: (id: string) => `/files/${id}/preview`,
    DOWNLOAD: (id: string) => `/files/${id}/download`,
    BROWSE_DIR: '/dirs/browse',
  },
  MEMBERSHIPS: {
    ME: '/memberships/me',
    MY_QUOTA: '/memberships/me/quota',
  },
  ADMIN: {
    USERS: '/admin/users',
    USER: (id: string) => `/admin/users/${id}`,
    USER_PASSWORD: (id: string) => `/admin/users/${id}/password`,
    MEMBERSHIPS: '/admin/memberships',
    MEMBERSHIP: (id: string) => `/admin/memberships/${id}`,
    AUDIT_LOGS: '/admin/audit-logs',
    CONFIGS: '/admin/configs',
  },
  CONFIGS: {
    LIST: '/configs',
    DETAIL: (key: string) => `/configs/${key}`,
    TEST: '/configs/test',
  },
} as const