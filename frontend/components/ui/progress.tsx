'use client'

import * as ProgressPrimitive from '@radix-ui/react-progress'

import { cn } from '@/lib/utils'

export function Progress({ className, value }: { className?: string; value: number }) {
  return (
    <ProgressPrimitive.Root className={cn('relative h-2 w-full overflow-hidden rounded-full bg-bg-tertiary', className)} value={value}>
      <ProgressPrimitive.Indicator
        className="h-full bg-accent-600 transition-transform duration-300"
        style={{ transform: `translateX(-${100 - Math.max(0, Math.min(100, value))}%)` }}
      />
    </ProgressPrimitive.Root>
  )
}