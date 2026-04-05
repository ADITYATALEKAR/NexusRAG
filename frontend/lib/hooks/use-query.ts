'use client'

import { useMutation } from '@tanstack/react-query'
import { useMemo, useState } from 'react'

import { APIError, api } from '@/lib/api'
import { PUBLIC_DEMO_MODE, PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'
import { useToast } from '@/lib/hooks/use-toast'
import { useAppStore } from '@/lib/stores/app-store'
import type { AnswerPayload, QueryHistoryItem } from '@/lib/types'

export function useQuery() {
  const toast = useToast()
  const [currentPrompt, setCurrentPrompt] = useState('')
  const [answer, setAnswer] = useState<AnswerPayload | null>(null)
  const [localError, setLocalError] = useState<Error | null>(null)
  const upsertHistory = useAppStore((state) => state.upsertHistory)
  const queryHistory = useAppStore((state) => state.queryHistory)
  const operatorApiKey = useAppStore((state) => state.operatorApiKey)
  const llmApiKey = useAppStore((state) => state.llmApiKey)
  const publicTrialUsage = useAppStore((state) => state.publicTrialUsage)
  const syncPublicTrialUsage = useAppStore((state) => state.syncPublicTrialUsage)
  const usingHostedTrial = PUBLIC_DEMO_MODE && !operatorApiKey && !llmApiKey
  const trialRemaining = usingHostedTrial
    ? Math.max(PUBLIC_TRIAL_QUERY_LIMIT - publicTrialUsage, 0)
    : null

  const mutation = useMutation({
    mutationFn: async (prompt: string) => api.query(prompt),
    onMutate: async (prompt) => {
      setLocalError(null)
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
      if (typeof result.usage?.hosted_trial_used === 'number') {
        syncPublicTrialUsage(result.usage.hosted_trial_used)
      } else if (usingHostedTrial) {
        syncPublicTrialUsage(publicTrialUsage + 1)
      }
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
      if (error instanceof APIError) {
        const used = error.payload?.trial_used
        if (typeof used === 'number') {
          syncPublicTrialUsage(used)
        }
      }
      const errorMessage = error instanceof Error ? error.message : 'Unable to complete the query.'
      upsertHistory({
        id: context?.id || `query-${Date.now()}`,
        prompt,
        createdAt: new Date().toISOString(),
        answer: errorMessage,
        status: 'error',
        citations: []
      })
      toast({
        type: 'error',
        title: 'Query failed',
        description: errorMessage,
        duration: 5000
      })
    }
  })

  const isLoading = mutation.isPending
  const error = localError || (mutation.error instanceof Error ? mutation.error : null)

  return useMemo(
    () => ({
      query: currentPrompt,
      answer,
      error,
      history: queryHistory,
      isLoading,
      usingHostedTrial,
      trialLimit: PUBLIC_TRIAL_QUERY_LIMIT,
      trialUsed: publicTrialUsage,
      trialRemaining,
      submitQuery: (prompt: string) => {
        if (usingHostedTrial && publicTrialUsage >= PUBLIC_TRIAL_QUERY_LIMIT) {
          setLocalError(
            new Error(
              `Hosted free use includes ${PUBLIC_TRIAL_QUERY_LIMIT} questions. Connect your own API for unlimited usage.`
            )
          )
          return
        }
        mutation.mutate(prompt)
      },
      selectHistoryItem: (item: QueryHistoryItem) => {
        setLocalError(null)
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
    [
      answer,
      currentPrompt,
      error,
      isLoading,
      mutation,
      publicTrialUsage,
      queryHistory,
      trialRemaining,
      usingHostedTrial,
    ]
  )
}
