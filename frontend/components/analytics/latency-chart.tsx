'use client'

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export function LatencyChart({ data }: { data: Array<{ time: string; p95: number }> }) {
  return (
    <div className="surface p-5">
      <h3 className="text-sm font-semibold text-text-primary">Latency (P95)</h3>
      <p className="mt-1 text-xs text-text-tertiary">Smooth, predictable retrieval and generation timing.</p>
      <div className="mt-5 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="latencyGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--color-accent-500))" stopOpacity={0.28} />
                <stop offset="95%" stopColor="hsl(var(--color-accent-500))" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="hsl(var(--color-border-subtle))" vertical={false} />
            <XAxis dataKey="time" tickLine={false} axisLine={false} tick={{ fill: 'hsl(var(--color-text-tertiary))', fontSize: 12 }} />
            <YAxis tickLine={false} axisLine={false} tick={{ fill: 'hsl(var(--color-text-tertiary))', fontSize: 12 }} tickFormatter={(value) => `${value}ms`} />
            <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--color-bg-elevated))', border: '1px solid hsl(var(--color-border-default))', borderRadius: '12px' }} />
            <Area type="monotone" dataKey="p95" stroke="hsl(var(--color-accent-500))" fill="url(#latencyGradient)" strokeWidth={2.5} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}