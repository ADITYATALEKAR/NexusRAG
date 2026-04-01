'use client'

import { CostBreakdown } from '@/components/analytics/cost-breakdown'
import { LatencyChart } from '@/components/analytics/latency-chart'
import { MetricsGrid } from '@/components/analytics/metrics-grid'
import { UsageChart } from '@/components/analytics/usage-chart'
import { Shell } from '@/components/layout/shell'
import { LoadingBlock } from '@/components/shared/loading'
import { useAnalytics } from '@/lib/hooks/use-analytics'

export default function AnalyticsPage() {
  const { metrics, latencySeries, usageSeries, costByModel, isLoading, error } = useAnalytics()

  return (
    <Shell className="space-y-6">
      <div>
        <h1 className="section-title">Analytics</h1>
        <p className="section-copy">System performance, traffic, and spend without visual noise.</p>
      </div>
      {error ? <p className="text-sm text-error">{error.message}</p> : null}
      {isLoading ? (
        <div className="surface p-6"><LoadingBlock rows={6} /></div>
      ) : (
        <>
          <MetricsGrid metrics={metrics} />
          <div className="grid gap-6 xl:grid-cols-2">
            <LatencyChart data={latencySeries} />
            <UsageChart data={usageSeries} />
          </div>
          <CostBreakdown data={costByModel} />
        </>
      )}
    </Shell>
  )
}