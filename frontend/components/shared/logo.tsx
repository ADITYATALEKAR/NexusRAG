import Image from 'next/image'
import Link from 'next/link'

export function Logo({
  subtitle = 'by Fundamental Labs',
  className = '',
  showText = true,
  showSubtitle = true,
  iconSize = 42,
}: {
  subtitle?: string
  className?: string
  showText?: boolean
  showSubtitle?: boolean
  iconSize?: number
}) {
  return (
    <Link
      href={showText ? '/' : '/dashboard'}
      className={`flex items-center gap-4 ${className}`.trim()}
      aria-label="NexusRAG home"
    >
      <Image
        src="/logo.svg"
        alt="NexusRAG"
        width={iconSize}
        height={iconSize}
        className="shrink-0"
        priority
      />
      {showText ? (
        <div className="flex min-w-0 flex-col leading-none">
          <span className="truncate text-[1.12rem] font-semibold tracking-[-0.05em] text-text-primary">
            NexusRAG
          </span>
          {showSubtitle && subtitle ? (
            <span className="mt-1.5 truncate text-[0.76rem] font-medium tracking-[0.02em] text-text-tertiary">
              {subtitle}
            </span>
          ) : null}
        </div>
      ) : null}
    </Link>
  )
}

