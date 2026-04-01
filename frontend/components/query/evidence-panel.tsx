'use client'

import { useState } from 'react'

import { CitationCard } from '@/components/query/citation-card'
import { Button } from '@/components/ui/button'
import type { CitationItem } from '@/lib/types'

export function EvidencePanel({ citations }: { citations: CitationItem[] }) {
  const [expanded, setExpanded] = useState(0)

  return (
    <div className="h-full border-l border-border-subtle bg-bg-secondary p-4 md:p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-text-primary">Evidence</h3>
          <p className="mt-1 text-xs text-text-tertiary">Inline citations and source excerpts.</p>
        </div>
      </div>
      <div className="space-y-3">
        {citations.map((citation, index) => (
          <div key={citation.chunk_id}>
            <Button variant={expanded === index ? 'default' : 'outline'} className="mb-2 h-auto w-full justify-start px-3 py-2 text-left" onClick={() => setExpanded(expanded === index ? -1 : index)}>
              <span className="mr-2 rounded-full bg-bg-primary px-2 py-1 text-[11px] font-semibold text-text-secondary">[{index + 1}]</span>
              <span className="truncate">{citation.document_name}</span>
            </Button>
            {expanded === index ? <CitationCard citation={citation} index={index} /> : null}
          </div>
        ))}
      </div>
    </div>
  )
}