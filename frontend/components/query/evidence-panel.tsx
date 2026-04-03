'use client'

import { useState } from 'react'

import { CitationCard } from '@/components/query/citation-card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { AnswerPayload, CitationItem } from '@/lib/types'

export function EvidencePanel({
  citations,
  answerStatus,
}: {
  citations: CitationItem[]
  answerStatus: AnswerPayload['status'] | null
}) {
  const [expanded, setExpanded] = useState(0)

  return (
    <div className="h-full border-l border-border-subtle bg-bg-secondary p-4 md:p-5">
      <div className="mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-text-primary">Sources and evidence</h3>
          <Badge>{citations.length} items</Badge>
        </div>
        <p className="mt-2 text-xs leading-6 text-text-tertiary">
          Review the passages and source files that grounded the current answer.
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
        <div className="space-y-4">
          <div className="rounded-2xl border border-border-subtle bg-bg-primary px-4 py-4">
            <p className="text-sm font-semibold text-text-primary">No evidence attached yet</p>
            <p className="mt-2 text-sm leading-6 text-text-secondary">
              Upload a document, ask a focused question, and this panel will show the source
              passages that grounded the answer.
            </p>
          </div>
          {answerStatus ? (
            <div className="rounded-2xl border border-border-subtle bg-bg-primary px-4 py-4">
              <p className="text-sm font-semibold text-text-primary">Current answer status</p>
              <p className="mt-2 text-sm leading-6 text-text-secondary">
                The latest answer finished with status <span className="font-medium text-text-primary">{answerStatus}</span>.
                Evidence-backed answers are the target operating mode.
              </p>
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}
