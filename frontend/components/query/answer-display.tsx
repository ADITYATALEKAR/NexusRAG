'use client'

import { motion } from 'framer-motion'

import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import type { AnswerPayload, CitationItem } from '@/lib/types'
import { formatLatency } from '@/lib/utils'

function parseAnswerWithCitations(text: string, citations: CitationItem[]) {
  const regex = /(\[(\d+)\])/g
  const segments: Array<
    { type: 'text'; content: string } | { type: 'citation'; citationNumber: number }
  > = []
  let lastIndex = 0

  for (const match of text.matchAll(regex)) {
    const index = match.index ?? 0
    if (index > lastIndex) {
      segments.push({ type: 'text', content: text.slice(lastIndex, index) })
    }

    const citationNumber = Number(match[2])
    if (!Number.isNaN(citationNumber) && citations[citationNumber - 1]) {
      segments.push({ type: 'citation', citationNumber })
    }
    lastIndex = index + match[0].length
  }

  if (lastIndex < text.length) {
    segments.push({ type: 'text', content: text.slice(lastIndex) })
  }

  return segments.length > 0 ? segments : [{ type: 'text' as const, content: text }]
}

export function AnswerDisplay({
  answer,
  isLoading
}: {
  answer: AnswerPayload | null
  isLoading?: boolean
}) {
  if (isLoading && !answer) {
    return (
      <div className="surface space-y-5 p-6">
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
      </div>
    )
  }

  if (!answer) {
    return null
  }

  const segments = parseAnswerWithCitations(answer.text, answer.citations)

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="surface space-y-5 p-6"
    >
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant="accent">Citation-backed answer</Badge>
        <Badge>{answer.citations.length} sources</Badge>
        {answer.trace?.provider_used ? <Badge>{answer.trace.provider_used}</Badge> : null}
      </div>

      <div className="prose prose-slate max-w-none leading-8 text-text-primary dark:prose-invert">
        {segments.map((segment, index) =>
          segment.type === 'text' ? (
            <span key={index}>{segment.content}</span>
          ) : (
            <button
              key={index}
              type="button"
              className="mx-1 inline-flex h-6 min-w-6 items-center justify-center rounded-full border border-accent-500/30 bg-accent-100 px-2 text-xs font-semibold text-accent-700 transition-colors hover:bg-accent-500 hover:text-white dark:bg-accent-500/15 dark:text-accent-100"
              aria-label={`Citation ${segment.citationNumber}`}
            >
              [{segment.citationNumber}]
            </button>
          )
        )}
      </div>

      <div className="flex flex-wrap items-center gap-3 border-t border-border-subtle pt-4 text-xs text-text-tertiary">
        <span>{answer.status}</span>
        <span>|</span>
        <span>{formatLatency(answer.trace?.latency_ms || 0)}</span>
        {answer.trace?.model_used ? (
          <>
            <span>|</span>
            <span>{answer.trace.model_used}</span>
          </>
        ) : null}
      </div>
    </motion.div>
  )
}
