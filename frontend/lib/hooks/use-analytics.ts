'use client'

import { useQuery } from '@tanstack/react-query'
import { useMemo } from 'react'

import { api } from '@/lib/api'
import type { MetricsResponse, TraceSpan } from '@/lib/types'
import { formatCurrency, formatLatency } from '@/lib/utils'

function sumCounter(metrics: MetricsResponse | undefined, matcher: (key: string) => boolean) {
  return Object.entries(metrics?.counters || {}).reduce((total, [key, value]) => {
    return matcher(key) ? total + value : total
  }, 0)
}

function getHistogramSummary(
  metrics: MetricsResponse | undefined,
  matcher: (key: string) => boolean
) {
  const entries = Object.entries(metrics?.histograms || {})
  const match = entries.find(([key]) => matcher(key))
  return match?.[1]
}

function deriveSeriesFromTraces(traces: TraceSpan[]) {
  const rootSpans = traces
    .filter((span) => span.operation.startsWith('POST /answer') || span.operation.startsWith('POST /query'))
    .filter((span) => span.end_time)
    .sort((left, right) => left.start_time.localeCompare(right.start_time))

  const buckets = new Map<string, { latencies: number[]; count: number }>()

  for (const span of rootSpans) {
    const start = new Date(span.start_time)
    const end = new Date(span.end_time || span.start_time)
    const durationMs = Math.max(0, end.getTime() - start.getTime())
    const label = start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    const bucket = buckets.get(label) || { latencies: [], count: 0 }
    bucket.latencies.push(durationMs)
    bucket.count += 1
    buckets.set(label, bucket)
  }

  const recentBuckets = Array.from(buckets.entries()).slice(-8)

  return {
    latencySeries: recentBuckets.map(([time, bucket]) => ({
      time,
      p95: bucket.latencies.length === 0 ? 0 : Math.max(...bucket.latencies)
    })),
    usageSeries: recentBuckets.map(([time, bucket]) => ({
      day: time,
      queries: bucket.count
    }))
  }
}

export function useAnalytics() {
  const metricsQuery = useQuery({ queryKey: ['metrics'], queryFn: () => api.getMetrics() })
  const costQuery = useQuery({ queryKey: ['costs'], queryFn: () => api.getCosts(24) })
  const providersQuery = useQuery({ queryKey: ['providers-health'], queryFn: () => api.getProvidersHealth() })
  const tracesQuery = useQuery({ queryKey: ['traces'], queryFn: () => api.getTraces(200) })

  return useMemo(() => {
    const metrics = metricsQuery.data
    const totalQueries = sumCounter(
      metrics,
      (key) => key.startsWith('http_requests_total') && key.includes('path=/answer')
    )
    const successfulQueries = sumCounter(
      metrics,
      (key) =>
        key.startsWith('http_requests_total') &&
        key.includes('path=/answer') &&
        (key.includes('status=200') || key.includes('status=201'))
    )
    const requestDuration = getHistogramSummary(
      metrics,
      (key) => key.startsWith('http_request_duration') && key.includes('path=/answer')
    )
    const avgLatency = requestDuration?.avg || 0
    const successRate = totalQueries === 0 ? 100 : (successfulQueries / totalQueries) * 100
    const totalCost = Number(costQuery.data?.total_usd || 0)
    const { latencySeries, usageSeries } = deriveSeriesFromTraces(tracesQuery.data || [])

    return {
      metrics: [
        { label: 'Total queries', value: totalQueries.toLocaleString(), change: 'Live', trend: 'neutral' as const },
        { label: 'Avg latency', value: formatLatency(avgLatency), change: 'Measured', trend: 'neutral' as const },
        { label: 'Success rate', value: `${successRate.toFixed(1)}%`, change: 'Live', trend: 'neutral' as const },
        { label: 'Cost (24h)', value: formatCurrency(totalCost), change: 'Live', trend: 'neutral' as const }
      ],
      latencySeries,
      usageSeries,
      costByModel: Object.entries(costQuery.data?.by_model || {}).map(([name, value]) => ({ name, value })),
      providers: providersQuery.data || [],
      isLoading:
        metricsQuery.isLoading ||
        costQuery.isLoading ||
        providersQuery.isLoading ||
        tracesQuery.isLoading,
      error: (
        metricsQuery.error ||
        costQuery.error ||
        providersQuery.error ||
        tracesQuery.error
      ) as Error | null
    }
  }, [
    costQuery.data,
    costQuery.error,
    costQuery.isLoading,
    metricsQuery.data,
    metricsQuery.error,
    metricsQuery.isLoading,
    providersQuery.data,
    providersQuery.error,
    providersQuery.isLoading,
    tracesQuery.data,
    tracesQuery.error,
    tracesQuery.isLoading
  ])
}
