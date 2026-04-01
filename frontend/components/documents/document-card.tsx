import { FileText, Trash2 } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ProcessingStatus } from '@/components/documents/processing-status'
import type { DocumentItem } from '@/lib/types'
import { formatRelativeTime } from '@/lib/utils'

export function DocumentCard({ document, onRemove }: { document: DocumentItem; onRemove: (id: string) => void }) {
  const badgeVariant = document.status === 'completed' ? 'success' : document.status === 'failed' ? 'error' : 'accent'

  return (
    <div className="surface p-5">
      <div className="flex items-start gap-4">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-bg-secondary text-text-secondary">
          <FileText className="h-5 w-5" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <h3 className="truncate text-sm font-semibold text-text-primary">{document.name}</h3>
            <Badge variant={badgeVariant}>{document.status}</Badge>
          </div>
          <div className="mt-2 flex flex-wrap gap-3 text-xs text-text-tertiary">
            <span>{document.sizeLabel}</span>
            <span>Uploaded {formatRelativeTime(document.uploadedAt)}</span>
            {document.chunksIndexed ? <span>{document.chunksIndexed} chunks</span> : null}
            {document.parserUsed ? <span>{document.parserUsed}</span> : null}
          </div>
          <div className="mt-4">
            <ProcessingStatus document={document} />
          </div>
          {document.error ? <p className="mt-3 text-sm text-error">{document.error}</p> : null}
        </div>
        <Button variant="ghost" size="icon" onClick={() => onRemove(document.id)} aria-label={`Remove ${document.name}`}>
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}