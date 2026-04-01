import { FolderOpen } from 'lucide-react'

import { DocumentCard } from '@/components/documents/document-card'
import { EmptyState } from '@/components/shared/empty-state'
import { Skeleton } from '@/components/ui/skeleton'
import type { DocumentItem } from '@/lib/types'

export function DocumentList({ documents, isLoading, onRemove }: { documents: DocumentItem[]; isLoading?: boolean; onRemove: (id: string) => void }) {
  if (isLoading && documents.length === 0) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="surface p-5">
            <Skeleton className="h-5 w-40" />
            <Skeleton className="mt-4 h-3 w-full" />
            <Skeleton className="mt-2 h-3 w-2/3" />
          </div>
        ))}
      </div>
    )
  }

  if (documents.length === 0) {
    return <EmptyState title="No documents yet" description="Upload a small set of PDFs or Markdown files to start building grounded answers." icon={<FolderOpen className="h-6 w-6 text-text-tertiary" />} />
  }

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      {documents.map((document) => (
        <DocumentCard key={document.id} document={document} onRemove={onRemove} />
      ))}
    </div>
  )
}