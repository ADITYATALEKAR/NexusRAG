import Image from 'next/image'
import Link from 'next/link'

export function Logo() {
  return (
    <Link href="/" className="flex items-center gap-3" aria-label="NexusRAG home">
      <Image src="/logo.svg" alt="NexusRAG" width={34} height={34} className="rounded-xl" priority />
      <div className="flex flex-col leading-none">
        <span className="text-sm font-semibold tracking-wide text-text-primary">NexusRAG</span>
        <span className="text-xs text-text-tertiary">Retrieval OS</span>
      </div>
    </Link>
  )
}