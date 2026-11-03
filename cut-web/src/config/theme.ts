import type { ThemeConfig } from 'antd'

/**
 * Ant Design 主题 Token 覆盖（cut-web 规则：旧版 CSS 变量作 token 基础）。
 */
export const antdTheme: ThemeConfig = {
  algorithm: undefined,
  token: {
    colorPrimary: '#7c3aed',
    colorInfo: '#7c3aed',
    colorSuccess: '#10b981',
    colorWarning: '#f59e0b',
    colorError: '#ef4444',
    colorBgBase: '#0f1117',
    colorBgContainer: '#1a1d27',
    colorBgElevated: '#21252f',
    colorBorder: '#2d3142',
    colorBorderSecondary: '#3a3f52',
    colorText: '#e4e7ec',
    colorTextSecondary: '#9ca3af',
    colorTextTertiary: '#6b7280',
    borderRadius: 8,
    fontFamily:
      "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif",
  },
  components: {
    Button: { colorPrimary: '#7c3aed' },
    Layout: { headerBg: '#1a1d27', bodyBg: '#0f1117' },
    Card: { colorBgContainer: '#1a1d27' },
    Table: {
      colorBgContainer: '#1a1d27',
      headerBg: '#21252f',
      rowHoverBg: '#21252f',
    },
    Input: { colorBgContainer: '#21252f' },
    Select: { colorBgContainer: '#21252f' },
    Modal: { contentBg: '#1a1d27', headerBg: '#1a1d27' },
    Tabs: { itemSelectedColor: '#7c3aed', inkBarColor: '#7c3aed' },
  },
}
