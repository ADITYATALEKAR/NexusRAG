import { Skeleton } from '@/components/ui/skeleton'

export function LoadingBlock({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, index) => (
        <Skeleton key={index} className={`h-4 ${index === rows - 1 ? 'w-2/3' : 'w-full'}`} />
      ))}
    </div>
  )
}