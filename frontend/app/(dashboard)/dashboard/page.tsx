'use client'

import { Sparkles } from 'lucide-react'
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
  const queryDisabled = !EXTERNAL_BACKEND_ENABLED
  const hostedTrialRemaining = trialRemaining ?? 0

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col xl:flex-row">
      <div className="min-w-0 flex-1">
        <div className="sticky top-0 z-20 border-b border-border-subtle bg-bg-primary/90 backdrop-blur">
          <Shell className="max-w-5xl py-5">
            <div className="mb-4 grid gap-3 lg:grid-cols-[minmax(0,1fr)_300px]">
              <div className="rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-4 text-sm leading-6 text-text-secondary">
                {usingHostedTrial ? (
                  <>
                    Hosted evaluation is active. You have{' '}
                    <span className="font-semibold text-text-primary">
                      {hostedTrialRemaining} of {trialLimit}
                    </span>{' '}
                    free questions remaining on our shared API. For unlimited usage, switch to{' '}
                    <Link href="/login" className="font-semibold text-accent-700 dark:text-accent-100">
                      Bring Your Own API
                    </Link>
                    .
                  </>
                ) : (
                  <>
                    Bring Your Own API mode is active. Queries will use the NexusRAG endpoint and
                    API key stored in this browser.
                  </>
                )}
              </div>
              <div className="rounded-2xl border border-border-subtle bg-bg-elevated px-4 py-4 text-sm text-text-secondary">
                <p className="font-semibold text-text-primary">How answers are structured</p>
                <p className="mt-2 leading-6">
                  Ask a question, review the answer, then inspect the evidence panel for cited
                  excerpts, document names, and relevance context.
                </p>
              </div>
            </div>
            <QueryInput onSubmit={submitQuery} isLoading={isLoading} disabled={queryDisabled} />
            {queryDisabled ? (
              <p className="mt-3 text-sm text-text-secondary">
                Querying is currently unavailable until this workspace can reach a NexusRAG API.
              </p>
            ) : null}
            {error ? (
              <p className="mt-3 text-sm text-error">
                {error.message}{' '}
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
            ) : (
              <EmptyState
                title="Ask your first grounded question"
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
          </div>
          <QueryHistory items={history} onSelect={selectHistoryItem} />
        </Shell>
      </div>
      <aside className="w-full xl:w-96">
        <EvidencePanel
          citations={answer?.citations ?? []}
          answerStatus={answer?.status ?? null}
          usingHostedTrial={usingHostedTrial}
          trialLimit={trialLimit}
          trialRemaining={hostedTrialRemaining}
        />
      </aside>
    </div>
  )
}
