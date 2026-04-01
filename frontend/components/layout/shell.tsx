import { ReactNode } from 'react'

import { cn } from '@/lib/utils'

export function Shell({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('mx-auto w-full max-w-7xl px-4 py-6 md:px-6', className)}>{children}</div>
}