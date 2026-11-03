import type { CSSProperties, SVGProps } from 'react'

/**
 * 轻量内联图标集（零依赖）。
 * 避免引入 @ant-design/icons 造成 pnpm 依赖结构变动，同时保证暗色主题下描边可继承 currentColor。
 */
type IconProps = {
  style?: CSSProperties
  className?: string
  size?: number
}

function Svg({ children, size = 16, style, className, ...rest }: IconProps & SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ verticalAlign: '-0.15em', ...style }}
      className={className}
      aria-hidden="true"
      {...rest}
    >
      {children}
    </svg>
  )
}

export function DashboardIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <rect x="3" y="3" width="7" height="9" rx="1.5" />
      <rect x="14" y="3" width="7" height="5" rx="1.5" />
      <rect x="14" y="12" width="7" height="9" rx="1.5" />
      <rect x="3" y="16" width="7" height="5" rx="1.5" />
    </Svg>
  )
}

export function AppstoreIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <rect x="3" y="3" width="8" height="8" rx="2" />
      <rect x="13" y="3" width="8" height="8" rx="2" />
      <rect x="3" y="13" width="8" height="8" rx="2" />
      <rect x="13" y="13" width="8" height="8" rx="2" />
    </Svg>
  )
}

export function VideoIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <rect x="2" y="6" width="13" height="12" rx="2.5" />
      <path d="M15 10.5 22 7v10l-7-3.5z" />
    </Svg>
  )
}

export function UserIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5" />
    </Svg>
  )
}

export function CrownIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M3 8l4 4 5-7 5 7 4-4-2 12H5L3 8z" />
    </Svg>
  )
}

export function ShieldIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M12 3l8 3v6c0 5-3.4 8.2-8 9-4.6-.8-8-4-8-9V6l8-3z" />
      <path d="m9 12 2 2 4-4" />
    </Svg>
  )
}

export function MenuFoldIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M3 6h18M3 12h10M3 18h18" />
      <path d="m20 9 3 3-3 3" />
    </Svg>
  )
}

export function MenuUnfoldIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M3 6h18M11 12h10M3 18h18" />
      <path d="m4 9-3 3 3 3" />
    </Svg>
  )
}

export function LogoutIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M9 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h4" />
      <path d="M16 17l5-5-5-5M21 12H9" />
    </Svg>
  )
}

export function PlusIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M12 5v14M5 12h14" />
    </Svg>
  )
}

export function PlayIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M7 4.5v15l13-7.5-13-7.5z" fill="currentColor" stroke="none" />
    </Svg>
  )
}

export function ScissorIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <circle cx="6" cy="6" r="2.5" />
      <circle cx="6" cy="18" r="2.5" />
      <path d="M8 8l12 10M8 16L20 6" />
    </Svg>
  )
}

export function SparkIcon(props: IconProps) {
  return (
    <Svg {...props}>
      <path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9L12 3z" />
    </Svg>
  )
}