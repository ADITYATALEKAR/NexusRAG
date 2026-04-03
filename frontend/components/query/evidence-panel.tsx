'use client'

import { useState } from 'react'

import { CitationCard } from '@/components/query/citation-card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useScrollActivity } from '@/lib/hooks/use-scroll-activity'
import type { AnswerPayload, CitationItem } from '@/lib/types'

export function EvidencePanel({
  citations,
  answerStatus,
}: {
  citations: CitationItem[]
  answerStatus: AnswerPayload['status'] | null
}) {
  const [expanded, setExpanded] = useState(0)
  const scrollRef = useScrollActivity<HTMLDivElement>()

  return (
    <div
      ref={scrollRef}
      className="app-scroll h-full overflow-y-auto border-l border-border-subtle bg-bg-secondary p-4 md:p-5"
    >
      <div className="mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-text-primary">Sources and evidence</h3>
          <Badge>{citations.length} items</Badge>
        </div>
        <p className="mt-2 text-xs leading-6 text-text-tertiary">
          Matching passages and cited file names appear here.
        </p>
      </div>

      {citations.length > 0 ? (
        <div className="space-y-3">
          {citations.map((citation, index) => (
            <div key={citation.chunk_id}>
              <Button
                variant={expanded === index ? 'default' : 'outline'}
                className="mb-2 h-auto w-full justify-start px-3 py-2 text-left"
                onClick={() => setExpanded(expanded === index ? -1 : index)}
              >
                <span className="mr-2 rounded-full bg-bg-primary px-2 py-1 text-[11px] font-semibold text-text-secondary">
                  [{index + 1}]
                </span>
                <span className="truncate">{citation.document_name}</span>
              </Button>
              {expanded === index ? <CitationCard citation={citation} index={index} /> : null}
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-border-subtle bg-bg-primary px-4 py-4">
          <p className="text-sm font-semibold text-text-primary">No evidence attached yet</p>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Upload a document and ask a focused question. Evidence will appear here once retrieval finds a grounded match.
          </p>
          {answerStatus ? (
            <p className="mt-3 text-xs uppercase tracking-[0.18em] text-text-tertiary">
              Latest answer status: {answerStatus}
            </p>
          ) : null}
        </div>
      )}
    </div>
  )
}
