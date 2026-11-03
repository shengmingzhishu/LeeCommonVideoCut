import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { RouterProvider, createBrowserRouter } from 'react-router-dom'

import ErrorBoundary from '@/components/basic/ErrorBoundary'
import { antdTheme } from '@/config/theme'
import { routes } from '@/router'

const router = createBrowserRouter(routes)

function App() {
  return (
    <ConfigProvider locale={zhCN} theme={antdTheme}>
      <ErrorBoundary>
        <RouterProvider router={router} />
      </ErrorBoundary>
    </ConfigProvider>
  )
}

export default App
