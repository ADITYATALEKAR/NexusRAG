'use client'

import { Shell } from '@/components/layout/shell'
import { DocumentList } from '@/components/documents/document-list'
import { UploadZone } from '@/components/documents/upload-zone'
import { EXTERNAL_BACKEND_ENABLED } from '@/lib/public-config'
import { useDocuments } from '@/lib/hooks/use-documents'

export default function DocumentsPage() {
  const { documents, isLoading, upload, remove, error } = useDocuments()
  const stagedMode = !EXTERNAL_BACKEND_ENABLED

  return (
    <Shell className="space-y-6">
      <div>
        <h1 className="section-title">Documents</h1>
        <p className="section-copy">Manage the knowledge base that powers every answer.</p>
      </div>
      {stagedMode ? (
        <div className="rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-4 text-sm text-text-secondary">
          This deployment needs a reachable backend API to process and index uploaded files. Set the public backend URL or configure an operator backend in Settings.
        </div>
      ) : null}
      <UploadZone onUpload={upload} />
      {error ? <p className="text-sm text-error">{error.message}</p> : null}
      <DocumentList documents={documents} isLoading={isLoading} onRemove={remove} />
    </Shell>
  )
}
