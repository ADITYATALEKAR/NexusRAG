'use client'

import { FileText, Sparkles, UploadCloud } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import { AnswerDisplay } from '@/components/query/answer-display'
import { EvidencePanel } from '@/components/query/evidence-panel'
import { QueryHistory } from '@/components/query/query-history'
import { QueryInput } from '@/components/query/query-input'
import { EmptyState } from '@/components/shared/empty-state'
import { useDocuments } from '@/lib/hooks/use-documents'
import { useScrollActivity } from '@/lib/hooks/use-scroll-activity'
import { useQuery } from '@/lib/hooks/use-query'
import { EXTERNAL_BACKEND_ENABLED } from '@/lib/public-config'
import { cn } from '@/lib/utils'

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
  const workspaceError = documentsError || error
  const documentsCount = documents.length
  const scrollRef = useScrollActivity<HTMLDivElement>()
  const showEvidencePanel = Boolean(answer || isLoading)

  return (
    <div
      className={cn(
        'grid h-full min-h-0 min-w-0',
        showEvidencePanel ? 'xl:grid-cols-[minmax(0,1fr)_360px]' : undefined,
      )}
    >
      <section className="grid min-h-0 min-w-0 grid-rows-[minmax(0,1fr)_auto] bg-bg-primary">
        <div ref={scrollRef} className="app-scroll min-h-0 overflow-y-auto">
          <div className="flex min-h-full w-full flex-col gap-8 px-6 pb-8 pt-10 md:px-8 xl:px-10 2xl:px-12">
            {workspaceError ? (
              <div className="rounded-[8px] border border-error/25 bg-error/5 px-5 py-4 text-sm leading-6 text-error">
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
                description="Use the paperclip in the composer below or open Documents to add a PDF, DOCX, Markdown, or TXT file. Once the first file is indexed, NexusRAG keeps the answer surface calm and the evidence easy to inspect."
                icon={<UploadCloud className="h-6 w-6 text-text-tertiary" />}
                action={{ label: 'Open documents', onClick: () => router.push('/dashboard/documents') }}
              />
            ) : history.length === 0 ? (
              <EmptyState
                title="Ask your first grounded question"
                description="Start with a focused question about the knowledge base you uploaded. NexusRAG answers in plain language and shows the strongest supporting evidence beside the response."
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
            ) : null}

            {history.length > 0 ? <QueryHistory items={history} onSelect={selectHistoryItem} /> : null}
          </div>
        </div>

        <div className="border-t border-border-subtle bg-bg-primary/96 shadow-[0_-18px_36px_-34px_rgba(15,23,42,0.22)] backdrop-blur-xl">
          <div className="w-full px-6 pb-6 pt-4 md:px-8 xl:px-10 2xl:px-12">
            <QueryInput
              onSubmit={submitQuery}
              onAttach={upload}
              isLoading={isLoading}
              isUploading={isUploading}
              disabled={queryDisabled}
            />

            <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-sm text-text-secondary">
              <div className="flex flex-wrap items-center gap-2">
                {usingHostedTrial ? (
                  <span>
                    Hosted evaluation: {hostedTrialRemaining} of {trialLimit ?? 2} shared queries remaining.
                  </span>
                ) : (
                  <span>Connected to your own NexusRAG API.</span>
                )}
                <span className="text-text-tertiary">•</span>
                <span>{documentsCount} documents indexed</span>
              </div>

              <Link
                href="/dashboard/documents"
                className="inline-flex items-center gap-2 font-medium text-accent-700 transition-colors hover:text-accent-600 dark:text-accent-100"
              >
                <FileText className="h-4 w-4" />
                Documents
              </Link>
            </div>

            {queryDisabled ? (
              <p className="mt-3 text-sm text-text-secondary">
                Querying is currently unavailable until this workspace can reach a NexusRAG API.
              </p>
            ) : null}
          </div>
        </div>
      </section>

      {showEvidencePanel ? (
        <aside className="hidden h-full xl:block">
          <EvidencePanel citations={answer?.citations ?? []} answerStatus={answer?.status ?? null} />
        </aside>
      ) : null}
    </div>
  )
}

