'use client'

import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'

import type { DocumentItem, QueryHistoryItem } from '@/lib/types'

interface AppState {
  mobileSidebarOpen: boolean
  queryHistory: QueryHistoryItem[]
  documents: DocumentItem[]
  operatorApiUrl: string | null
  operatorApiKey: string | null
  setMobileSidebarOpen: (value: boolean) => void
  upsertHistory: (item: QueryHistoryItem) => void
  addDocuments: (items: DocumentItem[]) => void
  updateDocument: (id: string, patch: Partial<DocumentItem>) => void
  removeDocument: (id: string) => void
  replaceDocuments: (items: DocumentItem[]) => void
  setOperatorConnection: (apiUrl: string | null, apiKey: string | null) => void
  clearWorkspace: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      mobileSidebarOpen: false,
      queryHistory: [],
      documents: [],
      operatorApiUrl: null,
      operatorApiKey: null,
      setMobileSidebarOpen: (value) => set({ mobileSidebarOpen: value }),
      upsertHistory: (item) =>
        set((state) => ({
          queryHistory: [item, ...state.queryHistory.filter((entry) => entry.id !== item.id)].slice(0, 12)
        })),
      addDocuments: (items) =>
        set((state) => ({
          documents: [...items, ...state.documents.filter((entry) => !items.some((candidate) => candidate.id === entry.id))]
        })),
      updateDocument: (id, patch) =>
        set((state) => ({
          documents: state.documents.map((document) => (document.id === id ? { ...document, ...patch } : document))
        })),
      removeDocument: (id) => set((state) => ({ documents: state.documents.filter((document) => document.id !== id) })),
      replaceDocuments: (items) => set({ documents: items }),
      setOperatorConnection: (apiUrl, apiKey) =>
        set({
          operatorApiUrl: apiUrl,
          operatorApiKey: apiKey
        }),
      clearWorkspace: () =>
        set({
          mobileSidebarOpen: false,
          queryHistory: [],
          documents: [],
          operatorApiUrl: null,
          operatorApiKey: null
        })
    }),
    {
      name: 'nexusrag-frontend-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        operatorApiUrl: state.operatorApiUrl,
        operatorApiKey: state.operatorApiKey,
        queryHistory: state.queryHistory,
        documents: state.documents
      })
    }
  )
)
