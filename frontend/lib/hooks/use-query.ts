'use client'

import { useMutation } from '@tanstack/react-query'
import { useMemo, useState } from 'react'

import { api } from '@/lib/api'
import { useAppStore } from '@/lib/stores/app-store'
import type { AnswerPayload, QueryHistoryItem } from '@/lib/types'

export function useQuery() {
  const [currentPrompt, setCurrentPrompt] = useState('')
  const [answer, setAnswer] = useState<AnswerPayload | null>(null)
  const upsertHistory = useAppStore((state) => state.upsertHistory)
  const queryHistory = useAppStore((state) => state.queryHistory)

  const mutation = useMutation({
    mutationFn: async (prompt: string) => api.query(prompt),
    onMutate: async (prompt) => {
      setCurrentPrompt(prompt)
      const optimistic: QueryHistoryItem = {
        id: `optimistic-${Date.now()}`,
        prompt,
        createdAt: new Date().toISOString(),
        status: 'loading',
        citations: []
      }
      upsertHistory(optimistic)
      return optimistic
    },
    onSuccess: (result, prompt, context) => {
      setAnswer(result)
      upsertHistory({
        id: result.query_id || context?.id || `query-${Date.now()}`,
        prompt,
        createdAt: new Date().toISOString(),
        answer: result.text,
        status: 'success',
        citations: result.citations
      })
    },
    onError: (error, prompt, context) => {
      upsertHistory({
        id: context?.id || `query-${Date.now()}`,
        prompt,
        createdAt: new Date().toISOString(),
        answer: error instanceof Error ? error.message : 'Unable to complete the query.',
        status: 'error',
        citations: []
      })
    }
  })

  const isLoading = mutation.isPending
  const error = mutation.error instanceof Error ? mutation.error : null

  return useMemo(
    () => ({
      query: currentPrompt,
      answer,
      error,
      history: queryHistory,
      isLoading,
      submitQuery: (prompt: string) => mutation.mutate(prompt),
      selectHistoryItem: (item: QueryHistoryItem) => {
        setCurrentPrompt(item.prompt)
        if (item.answer) {
          setAnswer({
            answer_id: item.id,
            query_id: item.id,
            text: item.answer,
            status: item.status === 'error' ? 'failed' : 'success',
            citations: item.citations,
            trace: null
          })
        }
      }
    }),
    [answer, currentPrompt, error, isLoading, mutation, queryHistory]
  )
}