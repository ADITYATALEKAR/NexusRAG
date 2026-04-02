'use client'

import { Clock3 } from 'lucide-react'

import { EmptyState } from '@/components/shared/empty-state'
import type { QueryHistoryItem } from '@/lib/types'
import { formatRelativeTime } from '@/lib/utils'

export function QueryHistory({ items, onSelect }: { items: QueryHistoryItem[]; onSelect: (item: QueryHistoryItem) => void }) {
  if (items.length === 0) {
    return (
      <EmptyState
        title="No recent queries yet"
        description="Your most recent answers stay in this browser so you can compare prompts, revisit wording, and reopen the evidence attached to earlier runs."
        icon={<Clock3 className="h-6 w-6 text-text-tertiary" />}
      />
    )
  }

  return (
    <div className="surface p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-text-primary">Recent queries</h3>
          <p className="mt-1 text-xs text-text-tertiary">
            Reopen prior prompts to compare answers, sources, and follow-up questions.
          </p>
        </div>
      </div>
      <div className="space-y-2">
        {items.map((item) => (
          <button
            key={item.id}
            onClick={() => onSelect(item)}
            className="w-full rounded-lg border border-border-subtle bg-bg-primary px-4 py-3 text-left transition-colors hover:border-border-default hover:bg-bg-secondary"
          >
            <div className="flex items-center justify-between gap-3">
              <p className="truncate text-sm font-medium text-text-primary">{item.prompt}</p>
              <span className="text-[11px] uppercase tracking-[0.18em] text-text-tertiary">{item.status}</span>
            </div>
            <p className="mt-2 line-clamp-2 text-sm text-text-secondary">{item.answer || 'Waiting for answer...'}</p>
            <div className="mt-2 flex items-center justify-between gap-3 text-xs text-text-tertiary">
              <span>{formatRelativeTime(item.createdAt)}</span>
              <span>{item.citations.length} sources</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
