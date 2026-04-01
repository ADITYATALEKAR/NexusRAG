'use client'

import { Sparkles } from 'lucide-react'

import { AnswerDisplay } from '@/components/query/answer-display'
import { EvidencePanel } from '@/components/query/evidence-panel'
import { QueryHistory } from '@/components/query/query-history'
import { QueryInput } from '@/components/query/query-input'
import { EmptyState } from '@/components/shared/empty-state'
import { Shell } from '@/components/layout/shell'
import { useQuery } from '@/lib/hooks/use-query'

export default function DashboardPage() {
  const { answer, history, isLoading, submitQuery, selectHistoryItem, error } = useQuery()

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col xl:flex-row">
      <div className="min-w-0 flex-1">
        <div className="sticky top-0 z-20 border-b border-border-subtle bg-bg-primary/90 backdrop-blur">
          <Shell className="max-w-4xl py-5">
            <QueryInput onSubmit={submitQuery} isLoading={isLoading} />
            {error ? <p className="mt-3 text-sm text-error">{error.message} Check backend health or API key settings, then try again.</p> : null}
          </Shell>
        </div>
        <Shell className="grid max-w-6xl gap-6 py-6 xl:grid-cols-[minmax(0,1fr)_340px]">
          <div className="space-y-6">
            {answer ? (
              <AnswerDisplay answer={answer} isLoading={isLoading} />
            ) : isLoading ? (
              <AnswerDisplay answer={null} isLoading />
            ) : (
              <EmptyState title="Ask anything" description="Query your documents with natural language. Every answer is backed by citations and visible source context." icon={<Sparkles className="h-6 w-6 text-text-tertiary" />} />
            )}
          </div>
          <QueryHistory items={history} onSelect={selectHistoryItem} />
        </Shell>
      </div>
      {answer?.citations?.length ? <aside className="w-full xl:w-96"><EvidencePanel citations={answer.citations} /></aside> : null}
    </div>
  )
}