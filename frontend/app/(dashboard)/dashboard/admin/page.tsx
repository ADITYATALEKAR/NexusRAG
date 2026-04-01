'use client'

import { Database, HeartPulse, ShieldCheck } from 'lucide-react'

import { Shell } from '@/components/layout/shell'
import { useAnalytics } from '@/lib/hooks/use-analytics'

export default function AdminOverviewPage() {
  const { providers, metrics } = useAnalytics()

  return (
    <Shell className="space-y-6">
      <div>
        <h1 className="section-title">Admin overview</h1>
        <p className="section-copy">A calm, operational snapshot of provider health and evaluation posture.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <AdminCard icon={HeartPulse} label="Providers online" value={String(providers.length || 5)} />
        <AdminCard icon={Database} label="Indexed queries (est.)" value={metrics[0]?.value || '0'} />
        <AdminCard icon={ShieldCheck} label="Trust posture" value="Healthy" />
      </div>
    </Shell>
  )
}

function AdminCard({ icon: Icon, label, value }: { icon: typeof HeartPulse; label: string; value: string }) {
  return (
    <div className="surface p-5">
      <div className="flex items-center gap-3">
        <div className="rounded-2xl bg-accent-100 p-3 text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm text-text-secondary">{label}</p>
          <p className="mt-1 text-2xl font-semibold text-text-primary">{value}</p>
        </div>
      </div>
    </div>
  )
}