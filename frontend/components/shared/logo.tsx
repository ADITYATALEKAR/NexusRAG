import Image from 'next/image'
import Link from 'next/link'

export function Logo({
  subtitle = 'by Fundamental Labs',
  className = '',
}: {
  subtitle?: string
  className?: string
}) {
  return (
    <Link href="/" className={`flex items-center gap-3 ${className}`.trim()} aria-label="NexusRAG home">
      <Image src="/logo.svg" alt="NexusRAG" width={34} height={34} className="rounded-xl" priority />
      <div className="flex flex-col leading-none">
        <span className="text-base font-semibold tracking-tight text-text-primary">NexusRAG</span>
        <span className="text-xs font-medium text-text-tertiary">{subtitle}</span>
      </div>
    </Link>
  )
}
