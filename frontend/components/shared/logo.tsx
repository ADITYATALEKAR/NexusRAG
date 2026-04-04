import Link from 'next/link'

type LogoProps = {
  subtitle?: string
  className?: string
  showText?: boolean
  showSubtitle?: boolean
  iconSize?: number
  muted?: boolean
}

export function Logo({
  subtitle = 'by Fundamental Labs',
  className = '',
  showText = true,
  showSubtitle = true,
  iconSize = 38,
  muted = false,
}: LogoProps) {
  return (
    <Link
      href={showText ? '/' : '/dashboard'}
      className={`flex items-center gap-3 ${className}`.trim()}
      aria-label="NexusRAG home"
    >
      <LogoMark size={iconSize} className={muted ? 'text-text-secondary dark:text-text-secondary' : ''} />
      {showText ? (
        <div className="flex min-w-0 flex-col leading-none">
          <span className="truncate text-[1.14rem] font-semibold tracking-[-0.05em] text-text-primary">
            NexusRAG
          </span>
          {showSubtitle && subtitle ? (
            <span className="mt-1 truncate text-[0.77rem] font-medium tracking-[0.02em] text-text-tertiary">
              {subtitle}
            </span>
          ) : null}
        </div>
      ) : null}
    </Link>
  )
}

export function LogoMark({
  size = 38,
  className = '',
}: {
  size?: number
  className?: string
}) {
  return (
    <span
      className={`inline-flex shrink-0 items-center justify-center text-text-primary dark:text-text-inverted ${className}`.trim()}
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 120 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M49 34L37 60L49 86"
          stroke="currentColor"
          strokeWidth="7.2"
          strokeLinecap="square"
          strokeLinejoin="miter"
        />
        <path
          d="M71 34L83 60L71 86"
          stroke="currentColor"
          strokeWidth="7.2"
          strokeLinecap="square"
          strokeLinejoin="miter"
        />
      </svg>
    </span>
  )
}

