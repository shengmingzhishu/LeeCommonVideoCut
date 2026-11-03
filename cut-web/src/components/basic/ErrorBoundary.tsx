import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

/** 全局错误边界（react-stack 规则 §8.2）：App 级 + 懒加载页面级包裹。 */
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[ERROR] Uncaught render error:', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div style={{ padding: 48, textAlign: 'center' }}>
            <h2>页面出错了</h2>
            <p style={{ color: '#888' }}>{this.state.error?.message}</p>
            <button type="button" onClick={() => window.location.reload()}>
              刷新重试
            </button>
          </div>
        )
      )
    }
    return this.props.children
  }
}
