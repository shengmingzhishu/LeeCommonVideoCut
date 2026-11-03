import { theme } from 'antd'
import type { ThemeConfig } from 'antd'

/**
 * Ant Design 主题配置（暗色主题）
 *
 * 必须使用 darkAlgorithm：若只手动指定暗色背景而沿用默认 lightAlgorithm，
 * colorTextHeading / colorTextDescription / colorTextPlaceholder / colorIcon 等
 * 派生 Token 仍会按「浅底深字」推导成接近黑色，在暗背景上不可读。
 * 因此这里以 darkAlgorithm 为基底，再用旧版 CSS 变量覆盖色板。
 */
export const antdTheme: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#7c3aed',
    colorInfo: '#7c3aed',
    colorSuccess: '#10b981',
    colorWarning: '#f59e0b',
    colorError: '#ef4444',

    // 背景层
    colorBgBase: '#0f1117',
    colorBgLayout: '#0f1117',
    colorBgContainer: '#1a1d27',
    colorBgElevated: '#21252f',
    colorBgSpotlight: '#2a2f3d',

    // 描边
    colorBorder: '#2d3142',
    colorBorderSecondary: '#3a3f52',
    colorSplit: 'rgba(255, 255, 255, 0.08)',

    // 文本层（全部显式指定为浅色，避免任何派生 Token 回落到深色）
    colorText: '#e4e7ec',
    colorTextHeading: '#f5f7fa',
    colorTextLabel: '#c9cfdb',
    colorTextSecondary: '#9ca3af',
    colorTextTertiary: '#8b93a7',
    colorTextQuaternary: '#6b7280',
    colorTextDescription: '#9ca3af',
    colorTextPlaceholder: '#8b93a7',
    colorTextDisabled: '#5b6373',

    // 链接 / 文字型按钮：darkAlgorithm 会把主色压暗成 #6c34cc，在深底上仅 2.4:1，
    // 因此显式指定浅紫，保证「全部项目 →」「进入」这类链接文字可读。
    colorLink: '#a78bfa',
    colorLinkHover: '#c4b5fd',
    colorLinkActive: '#8b5cf6',

    // 图标
    colorIcon: '#9ca3af',
    colorIconHover: '#e4e7ec',

    borderRadius: 8,
    fontFamily:
      "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif",
  },
  components: {
    Button: { colorPrimary: '#7c3aed' },
    Layout: { headerBg: '#1a1d27', bodyBg: '#0f1117', siderBg: '#1a1d27' },
    Card: { colorBgContainer: '#1a1d27', colorTextHeading: '#f5f7fa' },
    Table: {
      colorBgContainer: '#1a1d27',
      headerBg: '#21252f',
      headerColor: '#e4e7ec',
      rowHoverBg: '#21252f',
      borderColor: '#2d3142',
    },
    Input: {
      colorBgContainer: '#21252f',
      colorTextPlaceholder: '#8b93a7',
    },
    InputNumber: { colorBgContainer: '#21252f' },
    Select: { colorBgContainer: '#21252f', optionSelectedColor: '#f5f7fa' },
    Modal: { contentBg: '#1a1d27', headerBg: '#1a1d27', titleColor: '#f5f7fa' },
    Tabs: {
      itemColor: '#9ca3af',
      itemHoverColor: '#e4e7ec',
      itemSelectedColor: '#7c3aed',
      inkBarColor: '#7c3aed',
    },
    Menu: {
      darkItemBg: '#1a1d27',
      darkSubMenuItemBg: '#21252f',
      darkItemColor: '#9ca3af',
      darkItemSelectedBg: '#7c3aed',
      darkItemSelectedColor: '#ffffff',
      darkItemHoverColor: '#e4e7ec',
      darkItemDisabledColor: 'rgba(255, 255, 255, 0.45)',
    },
    Steps: {
      colorTextDescription: '#9ca3af',
    },
    Descriptions: {
      labelBg: '#21252f',
      titleMarginBottom: 12,
    },
    Form: {
      labelColor: '#c9cfdb',
    },
    Pagination: {
      itemBg: 'transparent',
    },
  },
}