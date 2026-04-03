'use client'

import { FileText, Sparkles, UploadCloud } from 'lucide-react'
import Link from 'next/link'

import {
  EXTERNAL_BACKEND_ENABLED
} from '@/lib/public-config'
import { AnswerDisplay } from '@/components/query/answer-display'
import { EvidencePanel } from '@/components/query/evidence-panel'
import { QueryHistory } from '@/components/query/query-history'
import { QueryInput } from '@/components/query/query-input'
import { EmptyState } from '@/components/shared/empty-state'
import { Shell } from '@/components/layout/shell'
import { useDocuments } from '@/lib/hooks/use-documents'
import { useQuery } from '@/lib/hooks/use-query'

export default function DashboardPage() {
  const {
    answer,
    history,
    isLoading,
    submitQuery,
    selectHistoryItem,
    error,
    trialLimit,
    trialRemaining,
    usingHostedTrial,
  } = useQuery()
  const {
    documents,
    upload,
    isUploading,
    error: documentsError,
  } = useDocuments()
  const queryDisabled = !EXTERNAL_BACKEND_ENABLED
  const hostedTrialRemaining = trialRemaining ?? 0
  const documentsCount = documents.length
  const workspaceError = documentsError || error

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col xl:flex-row">
      <div className="min-w-0 flex-1">
        <div className="sticky top-0 z-20 border-b border-border-subtle bg-bg-primary/90 backdrop-blur">
          <Shell className="max-w-5xl py-5">
            <div className="mb-4 rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-4 text-sm leading-6 text-text-secondary">
              <div className="flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="font-semibold text-text-primary">
                    {documentsCount > 0
                      ? `${documentsCount} document${documentsCount === 1 ? '' : 's'} ready for retrieval`
                      : 'Upload your first document to start querying'}
                  </p>
                  <p className="mt-1">
                    {usingHostedTrial ? (
                      <>
                        Hosted evaluation is active with{' '}
                        <span className="font-semibold text-text-primary">
                          {hostedTrialRemaining} of {trialLimit}
                        </span>{' '}
                        free queries remaining.
                      </>
                    ) : (
                      'Bring Your Own API mode is active for unlimited usage on your own deployment.'
                    )}
                  </p>
                </div>
                <Link
                  href="/dashboard/documents"
                  className="inline-flex items-center gap-2 text-sm font-medium text-accent-700 dark:text-accent-100"
                >
                  <FileText className="h-4 w-4" />
                  Manage documents
                </Link>
              </div>
            </div>
            <QueryInput
              onSubmit={submitQuery}
              onAttach={upload}
              isLoading={isLoading}
              isUploading={isUploading}
              disabled={queryDisabled}
            />
            <div className="mt-3 flex flex-wrap gap-3 text-sm text-text-secondary">
              <span>Attach files with the paperclip.</span>
              <span>Supported: PDF, DOCX, Markdown, TXT.</span>
              {isUploading ? <span className="font-medium text-text-primary">Uploading documents...</span> : null}
            </div>
            {queryDisabled ? (
              <p className="mt-3 text-sm text-text-secondary">
                Querying is currently unavailable until this workspace can reach a NexusRAG API.
              </p>
            ) : null}
            {workspaceError ? (
              <p className="mt-3 text-sm text-error">
                {workspaceError.message}{' '}
                {usingHostedTrial ? (
                  <Link href="/login" className="font-semibold underline decoration-accent-500/40 underline-offset-4">
                    Use your own API
                  </Link>
                ) : null}
              </p>
            ) : null}
          </Shell>
        </div>
        <Shell className="grid max-w-6xl gap-6 py-6 xl:grid-cols-[minmax(0,1fr)_340px]">
          <div className="space-y-6">
            {answer ? (
              <AnswerDisplay answer={answer} isLoading={isLoading} />
            ) : isLoading ? (
              <AnswerDisplay answer={null} isLoading />
            ) : documentsCount === 0 ? (
              <EmptyState
                title="Upload a document to activate your workspace"
                description="Use the paperclip above or open Documents to add a PDF, DOCX, Markdown, or TXT file. Once one file is indexed, NexusRAG can answer with grounded citations."
                icon={<UploadCloud className="h-6 w-6 text-text-tertiary" />}
              />
            ) : (
              <EmptyState
                title="Ask a grounded question"
                description="Start with a focused question about the documents you uploaded. NexusRAG will answer in plain language and show source evidence alongside the response."
                icon={<Sparkles className="h-6 w-6 text-text-tertiary" />}
                action={
                  usingHostedTrial && hostedTrialRemaining > 0
                    ? {
                        label: `Start free (${hostedTrialRemaining} left)`,
                        onClick: () => submitQuery('What are the main themes across the uploaded knowledge base?'),
                      }
                    : undefined
                  }
              />
            )}
            <QueryHistory items={history} onSelect={selectHistoryItem} />
          </div>
          <div className="xl:pt-1">
            <EvidencePanel
              citations={answer?.citations ?? []}
              answerStatus={answer?.status ?? null}
            />
          </div>
        </Shell>
      </div>
    </div>
  )
}
