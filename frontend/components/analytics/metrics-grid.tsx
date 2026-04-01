import { Minus, TrendingDown, TrendingUp } from 'lucide-react'

import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'

export function MetricsGrid({ metrics }: { metrics: Array<{ label: string; value: string; change: string; trend: 'up' | 'down' | 'neutral' }> }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <Card key={metric.label}>
          <CardContent className="p-5">
            <p className="text-sm text-text-secondary">{metric.label}</p>
            <div className="mt-3 flex items-end justify-between gap-3">
              <span className="text-2xl font-semibold tracking-tight text-text-primary">{metric.value}</span>
              <span className={cn('flex items-center gap-1 text-sm', metric.trend === 'up' && 'text-success', metric.trend === 'down' && 'text-error', metric.trend === 'neutral' && 'text-text-tertiary')}>
                {metric.trend === 'up' ? <TrendingUp className="h-3 w-3" /> : metric.trend === 'down' ? <TrendingDown className="h-3 w-3" /> : <Minus className="h-3 w-3" />}
                {metric.change}
              </span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}