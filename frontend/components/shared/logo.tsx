import Image from 'next/image'
import Link from 'next/link'

export function Logo({
  subtitle = 'by Fundamental Labs',
  className = '',
  showText = true,
  showSubtitle = true,
  iconSize = 34,
}: {
  subtitle?: string
  className?: string
  showText?: boolean
  showSubtitle?: boolean
  iconSize?: number
}) {
  return (
    <Link href="/" className={`flex items-center gap-3 ${className}`.trim()} aria-label="NexusRAG home">
      <Image src="/logo.svg" alt="NexusRAG" width={iconSize} height={iconSize} className="shrink-0" priority />
      {showText ? (
        <div className="flex flex-col leading-none">
          <span className="text-base font-semibold tracking-tight text-text-primary">NexusRAG</span>
          {showSubtitle && subtitle ? (
            <span className="text-xs font-medium text-text-tertiary">{subtitle}</span>
          ) : null}
        </div>
      ) : null}
    </Link>
  )
}
