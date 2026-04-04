'use client'

import { useMutation, useQuery } from '@tanstack/react-query'
import { useEffect, useMemo } from 'react'

import { api } from '@/lib/api'
import { useAppStore } from '@/lib/stores/app-store'
import { useToast } from '@/lib/hooks/use-toast'
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
  const toast = useToast()
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
    },
    onSuccess: (results) => {
      const successCount = results.filter((r) => r.status === 'completed' || r.status === 'processing').length
      const failureCount = results.filter((r) => r.status === 'failed').length

      if (successCount > 0) {
        toast({
          type: 'success',
          title: `${successCount} document${successCount === 1 ? '' : 's'} uploaded`,
          description: `${successCount === 1 ? 'Your document is' : 'Your documents are'} being indexed and will be ready for queries shortly.`,
          duration: 4000
        })
      }

      if (failureCount > 0) {
        toast({
          type: 'error',
          title: `${failureCount} document${failureCount === 1 ? '' : 's'} failed to upload`,
          description: 'Check the Documents tab for more details.',
          duration: 5000
        })
      }
    },
    onError: (error) => {
      toast({
        type: 'error',
        title: 'Upload failed',
        description: error instanceof Error ? error.message : 'Unable to upload documents. Please try again.',
        duration: 5000
      })
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
      isUploading: uploadMutation.isPending,
      upload: (files: File[]) => uploadMutation.mutateAsync(files),
      remove: (id: string) => removeMutation.mutate(id),
      error: (query.error || uploadMutation.error || removeMutation.error) as Error | null
    }),
    [documents, query.error, query.isLoading, removeMutation, uploadMutation]
  )
}
