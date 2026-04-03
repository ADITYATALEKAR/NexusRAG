'use client'

import { FileText, Sparkles, UploadCloud } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import { AnswerDisplay } from '@/components/query/answer-display'
import { EvidencePanel } from '@/components/query/evidence-panel'
import { QueryHistory } from '@/components/query/query-history'
import { QueryInput } from '@/components/query/query-input'
import { EmptyState } from '@/components/shared/empty-state'
import { useScrollActivity } from '@/lib/hooks/use-scroll-activity'
import { EXTERNAL_BACKEND_ENABLED } from '@/lib/public-config'
import { useDocuments } from '@/lib/hooks/use-documents'
import { useQuery } from '@/lib/hooks/use-query'

export default function DashboardPage() {
  const router = useRouter()
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
  const { documents, upload, isUploading, error: documentsError } = useDocuments()

  const queryDisabled = !EXTERNAL_BACKEND_ENABLED
  const hostedTrialRemaining = trialRemaining ?? 0
  const documentsCount = documents.length
  const workspaceError = documentsError || error
  const scrollRef = useScrollActivity<HTMLDivElement>()

  return (
    <div className="grid h-full min-h-0 xl:grid-cols-[minmax(0,1fr)_340px]">
      <section className="flex min-h-0 min-w-0 flex-col">
        <div ref={scrollRef} className="app-scroll min-h-0 flex-1 overflow-y-auto">
          <div className="mx-auto flex w-full max-w-[1880px] flex-col gap-6 px-4 pb-8 pt-5 md:px-6 lg:px-10 xl:px-12">
            {documentsCount > 0 ? (
              <div className="flex justify-end">
                <Link
                  href="/dashboard/documents"
                  className="inline-flex items-center gap-2 rounded-full border border-border-subtle bg-bg-elevated px-3 py-1.5 text-sm font-medium text-accent-700 transition-colors hover:border-border-default dark:text-accent-100"
                >
                  <FileText className="h-4 w-4" />
                  Manage documents
                </Link>
              </div>
            ) : null}

            {workspaceError ? (
              <div className="rounded-2xl border border-error/25 bg-error/5 px-4 py-3 text-sm text-error">
                {workspaceError.message}{' '}
                {usingHostedTrial ? (
                  <Link
                    href="/login"
                    className="font-semibold underline decoration-accent-500/40 underline-offset-4"
                  >
                    Switch to your own API
                  </Link>
                ) : null}
              </div>
            ) : null}

            {answer ? (
              <AnswerDisplay answer={answer} isLoading={isLoading} />
            ) : isLoading ? (
              <AnswerDisplay answer={null} isLoading />
            ) : documentsCount === 0 ? (
              <EmptyState
                title="Upload a document to start querying"
                description="Use the paperclip in the composer below or open Documents to add a PDF, DOCX, Markdown, or TXT file. Once the first file is indexed, NexusRAG answers with grounded citations."
                icon={<UploadCloud className="h-6 w-6 text-text-tertiary" />}
                action={{ label: 'Open documents', onClick: () => router.push('/dashboard/documents') }}
              />
            ) : (
              <EmptyState
                title="Ask your first grounded question"
                description="Start with a specific question about the knowledge base you uploaded. NexusRAG will answer in plain language and attach the supporting evidence on the right."
                icon={<Sparkles className="h-6 w-6 text-text-tertiary" />}
                action={
                  usingHostedTrial && hostedTrialRemaining > 0
                    ? {
                        label: `Start free (${hostedTrialRemaining} left)`,
                        onClick: () =>
                          submitQuery(
                            'What are the main themes across the uploaded knowledge base?',
                          ),
                      }
                    : undefined
                }
              />
            )}

            <QueryHistory items={history} onSelect={selectHistoryItem} />
          </div>
        </div>

        <div className="border-t border-border-subtle bg-bg-primary/95 backdrop-blur">
          <div className="mx-auto w-full max-w-[1880px] px-4 pb-4 pt-3 md:px-6 lg:px-10 xl:px-12">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-3 text-sm text-text-secondary">
              <div className="flex flex-wrap gap-x-4 gap-y-1">
                <span>Ask grounded questions against your uploaded documents.</span>
              </div>
              {isUploading ? (
                <span className="font-medium text-text-primary">Uploading documents...</span>
              ) : null}
            </div>
            <QueryInput
              onSubmit={submitQuery}
              onAttach={upload}
              isLoading={isLoading}
              isUploading={isUploading}
              disabled={queryDisabled}
            />
            {queryDisabled ? (
              <p className="mt-3 text-sm text-text-secondary">
                Querying is currently unavailable until this workspace can reach a NexusRAG API.
              </p>
            ) : null}
          </div>
        </div>
      </section>

      <aside className="hidden h-full xl:block">
        <EvidencePanel citations={answer?.citations ?? []} answerStatus={answer?.status ?? null} />
      </aside>
    </div>
  )
}
