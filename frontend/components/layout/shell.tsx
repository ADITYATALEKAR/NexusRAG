import { ReactNode } from 'react'

import { useScrollActivity } from '@/lib/hooks/use-scroll-activity'
import { cn } from '@/lib/utils'

export function Shell({ children, className }: { children: ReactNode; className?: string }) {
  const scrollRef = useScrollActivity<HTMLDivElement>()

  return (
    <div ref={scrollRef} className="app-scroll h-full overflow-y-auto">
      <div className={cn('mx-auto w-full max-w-[1880px] px-4 py-6 md:px-6 lg:px-10 xl:px-12', className)}>
        {children}
      </div>
    </div>
  )
}
