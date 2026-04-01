'use client'

import { useMutation, useQuery } from '@tanstack/react-query'
import { useEffect, useMemo } from 'react'

import { api } from '@/lib/api'
import { useAppStore } from '@/lib/stores/app-store'
import type { DocumentItem } from '@/lib/types'

function toSizeLabel(bytes: number) {
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} KB`
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function normalizeDocumentStatus(status?: string, hasErrors?: boolean): DocumentItem['status'] {
  if (hasErrors) {
    return 'failed'
  }

  if (status === 'queued' || status === 'processing' || status === 'completed' || status === 'failed') {
    return status
  }

  if (status === 'uploaded') {
    return 'queued'
  }

  return 'completed'
}

export function useDocuments() {
  const documents = useAppStore((state) => state.documents)
  const addDocuments = useAppStore((state) => state.addDocuments)
  const replaceDocuments = useAppStore((state) => state.replaceDocuments)
  const updateDocument = useAppStore((state) => state.updateDocument)
  const removeDocumentFromStore = useAppStore((state) => state.removeDocument)

  const query = useQuery({
    queryKey: ['documents'],
    queryFn: () => api.getDocuments(),
    staleTime: 15000
  })

  useEffect(() => {
    if (query.data) {
      replaceDocuments(query.data)
    }
  }, [query.data, replaceDocuments])

  const uploadMutation = useMutation({
    mutationFn: async (files: File[]) => {
      const results: DocumentItem[] = []
      for (const file of files) {
        const localId = `local-${Date.now()}-${file.name}`
        addDocuments([
          {
            id: localId,
            name: file.name,
            status: 'processing',
            sizeLabel: toSizeLabel(file.size),
            uploadedAt: new Date().toISOString(),
            progress: 5
          }
        ])
        const response = await api.uploadDocument(file, (progress) => updateDocument(localId, { progress }))
        const next: DocumentItem = {
          id: response.document_id || localId,
          name: file.name,
          status: normalizeDocumentStatus(response.status, Boolean(response.errors?.length)),
          sizeLabel: toSizeLabel(file.size),
          uploadedAt: new Date().toISOString(),
          parserUsed: response.parser_used,
          chunksIndexed: response.chunks_indexed,
          progress: 100,
          error: response.errors?.[0]
        }
        removeDocumentFromStore(localId)
        addDocuments([next])
        results.push(next)
      }
      return results
    }
  })

  const removeMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.deleteDocument(id)
      return id
    },
    onSuccess: (id) => removeDocumentFromStore(id)
  })

  return useMemo(
    () => ({
      documents,
      isLoading: query.isLoading || uploadMutation.isPending,
      upload: (files: File[]) => uploadMutation.mutateAsync(files),
      remove: (id: string) => removeMutation.mutate(id),
      error: (query.error || uploadMutation.error || removeMutation.error) as Error | null
    }),
    [documents, query.error, query.isLoading, removeMutation, uploadMutation]
  )
}
