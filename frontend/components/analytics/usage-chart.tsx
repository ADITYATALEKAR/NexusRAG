'use client'

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export function UsageChart({ data }: { data: Array<{ day: string; queries: number }> }) {
  return (
    <div className="surface p-5">
      <h3 className="text-sm font-semibold text-text-primary">Usage volume</h3>
      <p className="mt-1 text-xs text-text-tertiary">Daily query throughput across the active workspace.</p>
      <div className="mt-5 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke="hsl(var(--color-border-subtle))" vertical={false} />
            <XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fill: 'hsl(var(--color-text-tertiary))', fontSize: 12 }} />
            <YAxis tickLine={false} axisLine={false} tick={{ fill: 'hsl(var(--color-text-tertiary))', fontSize: 12 }} />
            <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--color-bg-elevated))', border: '1px solid hsl(var(--color-border-default))', borderRadius: '12px' }} />
            <Bar dataKey="queries" fill="hsl(var(--color-accent-600))" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}