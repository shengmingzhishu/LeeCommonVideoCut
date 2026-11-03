/**
 * 环境变量集中读取（react-stack 规则 §9.1）
 */
export const env = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || '/api',
  APP_NAME: import.meta.env.VITE_APP_NAME || '漫剧推广素材剪辑师',
} as const
