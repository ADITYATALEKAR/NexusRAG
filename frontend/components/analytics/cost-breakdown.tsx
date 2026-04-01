import { PieChart } from 'lucide-react'

import { EmptyState } from '@/components/shared/empty-state'
import { formatCurrency } from '@/lib/utils'

export function CostBreakdown({ data }: { data: Array<{ name: string; value: number }> }) {
  if (data.length === 0) {
    return <EmptyState title="No cost data yet" description="Once the workspace handles live traffic, model-level spend will show up here." icon={<PieChart className="h-6 w-6 text-text-tertiary" />} />
  }

  const total = data.reduce((sum, item) => sum + item.value, 0)

  return (
    <div className="surface p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-sm font-semibold text-text-primary">Cost breakdown</h3>
          <p className="mt-1 text-xs text-text-tertiary">Spend by model over the current lookback window.</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-text-tertiary">Total</p>
          <p className="text-lg font-semibold text-text-primary">{formatCurrency(total)}</p>
        </div>
      </div>
      <div className="mt-5 space-y-3">
        {data.map((item) => {
          const percent = total === 0 ? 0 : (item.value / total) * 100
          return (
            <div key={item.name} className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-primary">{item.name}</span>
                <span className="text-text-secondary">{formatCurrency(item.value)}</span>
              </div>
              <div className="h-2 rounded-full bg-bg-tertiary">
                <div className="h-2 rounded-full bg-accent-600" style={{ width: `${percent}%` }} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}