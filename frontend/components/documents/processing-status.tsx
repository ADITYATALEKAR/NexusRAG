import { AlertCircle, CheckCircle2, Clock3 } from 'lucide-react'

import { Progress } from '@/components/ui/progress'
import type { DocumentItem } from '@/lib/types'

export function ProcessingStatus({ document }: { document: DocumentItem }) {
  const statusMap = {
    queued: { label: 'Queued', icon: Clock3 },
    processing: { label: 'Processing', icon: Clock3 },
    completed: { label: 'Indexed', icon: CheckCircle2 },
    failed: { label: 'Needs attention', icon: AlertCircle }
  } as const
  const meta = statusMap[document.status]
  const Icon = meta.icon

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-xs text-text-tertiary">
        <Icon className={`h-3.5 w-3.5 ${document.status === 'completed' ? 'text-success' : document.status === 'failed' ? 'text-error' : 'text-info'}`} />
        <span>{meta.label}</span>
      </div>
      <Progress value={document.progress || (document.status === 'completed' ? 100 : document.status === 'failed' ? 100 : 12)} />
    </div>
  )
}
