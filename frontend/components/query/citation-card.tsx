import { ExternalLink, FileText } from 'lucide-react'

import type { CitationItem } from '@/lib/types'
import { cn } from '@/lib/utils'

export function CitationCard({ citation, index, compact = false }: { citation: CitationItem; index: number; compact?: boolean }) {
  return (
    <div className={cn('rounded-lg border border-border-subtle bg-bg-elevated p-3', compact ? 'space-y-2' : 'space-y-3')}>
      <div className="flex items-start gap-3">
        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-accent-100 text-xs font-semibold text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
          {index + 1}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-text-tertiary" />
            <p className="truncate text-sm font-medium text-text-primary">{citation.document_name}</p>
          </div>
          <p className="mt-1 text-xs text-text-tertiary">Relevance {(citation.score * 100).toFixed(0)}%</p>
        </div>
        <ExternalLink className="h-4 w-4 text-text-tertiary" />
      </div>
      {!compact ? <p className="text-sm leading-6 text-text-secondary">{citation.content}</p> : null}
    </div>
  )
}