/**
 * 统一 logger（react-stack 规则 §10.1）
 * 生产环境关闭 debug；API 日志统一携带 traceId。
 */
const logger = {
  info: (...args: unknown[]) => console.log('[INFO]', ...args),
  warn: (...args: unknown[]) => console.warn('[WARN]', ...args),
  error: (...args: unknown[]) => console.error('[ERROR]', ...args),
  debug: (...args: unknown[]) => {
    if (import.meta.env.DEV) console.log('[DEBUG]', ...args)
  },
}

export default logger
