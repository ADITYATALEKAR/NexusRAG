'use client'

import { Trash2 } from 'lucide-react'
import { useState } from 'react'

import type { QueryHistoryItem } from '@/lib/types'
import { formatRelativeTime } from '@/lib/utils'
import { useAppStore } from '@/lib/stores/app-store'

export function QueryHistory({
  items,
  onSelect,
}: {
  items: QueryHistoryItem[]
  onSelect: (item: QueryHistoryItem) => void
}) {
  const [hoveredId, setHoveredId] = useState<string | null>(null)
  const removeHistoryItem = useAppStore((state) => state.removeHistoryItem)

  if (items.length === 0) {
    return null
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
          <div
            key={item.id}
            className="group rounded-lg border border-border-subtle bg-bg-primary transition-colors hover:border-border-default hover:bg-bg-secondary"
            onMouseEnter={() => setHoveredId(item.id)}
            onMouseLeave={() => setHoveredId(null)}
          >
            <button
              onClick={() => onSelect(item)}
              className="w-full px-4 py-3 text-left"
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
            {hoveredId === item.id && (
              <div className="border-t border-border-subtle px-4 py-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    removeHistoryItem(item.id)
                  }}
                  className="inline-flex items-center gap-2 text-xs font-medium text-error transition-colors hover:text-error/80"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Delete
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
