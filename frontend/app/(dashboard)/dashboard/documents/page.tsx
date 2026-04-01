'use client'

import { Shell } from '@/components/layout/shell'
import { DocumentList } from '@/components/documents/document-list'
import { UploadZone } from '@/components/documents/upload-zone'
import { useDocuments } from '@/lib/hooks/use-documents'

export default function DocumentsPage() {
  const { documents, isLoading, upload, remove, error } = useDocuments()

  return (
    <Shell className="space-y-6">
      <div>
        <h1 className="section-title">Documents</h1>
        <p className="section-copy">Manage the knowledge base that powers every answer.</p>
      </div>
      <UploadZone onUpload={upload} />
      {error ? <p className="text-sm text-error">{error.message}</p> : null}
      <DocumentList documents={documents} isLoading={isLoading} onRemove={remove} />
    </Shell>
  )
}