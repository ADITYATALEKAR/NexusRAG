'use client'

import { motion } from 'framer-motion'

import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import type { AnswerPayload, CitationItem } from '@/lib/types'
import { formatLatency } from '@/lib/utils'

type Segment = { type: 'text'; content: string } | { type: 'citation'; citationNumber: number }

function parseAnswerWithCitations(text: string, citations: CitationItem[]): Segment[] {
  const regex = /(\[(\d+)\])/g
  const segments: Segment[] = []
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

function renderTextWithFormatting(content: string, keyPrefix: string) {
  const lines = content.split('\n')
  const elements: React.ReactNode[] = []
  let listItems: string[] = []
  let listKey = 0

  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`${keyPrefix}-ul-${listKey}`} className="my-2 ml-1 space-y-1.5">
          {listItems.map((item, i) => (
            <li key={i} className="flex gap-2 text-text-primary">
              <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-accent-500" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      )
      listItems = []
      listKey++
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const trimmed = line.trim()

    if (!trimmed) {
      flushList()
      continue
    }

    const bulletMatch = trimmed.match(/^[-*•]\s+(.+)$/)
    const numberedMatch = trimmed.match(/^\d+[.)]\s+(.+)$/)

    if (bulletMatch) {
      listItems.push(bulletMatch[1])
    } else if (numberedMatch) {
      listItems.push(numberedMatch[1])
    } else if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
      flushList()
      elements.push(
        <p key={`${keyPrefix}-h-${i}`} className="mt-3 mb-1 font-semibold text-text-primary">
          {trimmed.slice(2, -2)}
        </p>
      )
    } else if (trimmed.startsWith('### ') || trimmed.startsWith('## ')) {
      flushList()
      const headingText = trimmed.replace(/^#{2,3}\s+/, '')
      elements.push(
        <p key={`${keyPrefix}-h-${i}`} className="mt-3 mb-1 font-semibold text-text-primary">
          {headingText}
        </p>
      )
    } else {
      flushList()
      elements.push(
        <span key={`${keyPrefix}-p-${i}`}>
          {i > 0 && lines[i - 1]?.trim() ? ' ' : ''}
          {trimmed}
        </span>
      )
    }
  }

  flushList()
  return elements
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
  const hasCitations = answer.citations.length > 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="surface space-y-4 p-6"
    >
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant={hasCitations ? 'accent' : 'warning'}>
          {hasCitations ? `${answer.citations.length} cited source${answer.citations.length === 1 ? '' : 's'}` : 'No citations attached'}
        </Badge>
        {answer.trace?.provider_used ? <Badge>{answer.trace.provider_used}</Badge> : null}
        {answer.trace?.model_used ? (
          <Badge variant="outline">{answer.trace.model_used}</Badge>
        ) : null}
      </div>

      <div className="prose prose-slate max-w-none leading-7 text-text-primary dark:prose-invert">
        {segments.map((segment, index) =>
          segment.type === 'text' ? (
            <span key={index}>{renderTextWithFormatting(segment.content, `seg-${index}`)}</span>
          ) : (
            <button
              key={index}
              type="button"
              className="mx-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded-full border border-accent-500/30 bg-accent-100 px-1.5 text-[10px] font-bold text-accent-700 transition-colors hover:bg-accent-500 hover:text-white dark:bg-accent-500/15 dark:text-accent-100"
              aria-label={`Citation ${segment.citationNumber}`}
            >
              {segment.citationNumber}
            </button>
          )
        )}
      </div>

      {!hasCitations ? (
        <div className="rounded-xl border border-border-subtle bg-bg-secondary px-4 py-3 text-sm leading-6 text-text-secondary">
          This response completed, but retrieval did not attach supporting excerpts. Upload more
          relevant documents or narrow the question for stronger evidence.
        </div>
      ) : null}

      <div className="flex flex-wrap items-center gap-3 border-t border-border-subtle pt-3 text-xs text-text-tertiary">
        <span className={answer.status === 'success' ? 'text-success' : 'text-error'}>
          {answer.status}
        </span>
        {answer.trace?.latency_ms ? (
          <>
            <span>|</span>
            <span>{formatLatency(answer.trace.latency_ms)}</span>
          </>
        ) : null}
        {answer.trace?.prompt_tokens || answer.trace?.completion_tokens ? (
          <>
            <span>|</span>
            <span>
              {(answer.trace.prompt_tokens ?? 0) + (answer.trace.completion_tokens ?? 0)} tokens
            </span>
          </>
        ) : null}
      </div>
    </motion.div>
  )
}
