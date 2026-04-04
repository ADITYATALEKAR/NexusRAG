'use client'

import { useCallback } from 'react'

// Simple in-memory toast store
let toastCallback: ((toast: Toast) => void) | null = null

export interface Toast {
  id: string
  title: string
  description?: string
  type: 'success' | 'error' | 'info'
  duration?: number
}

export function useToast() {
  return useCallback(
    (toast: Omit<Toast, 'id'>) => {
      const id = `toast-${Date.now()}`
      if (toastCallback) {
        toastCallback({ ...toast, id })
      }
    },
    []
  )
}

export function setToastHandler(callback: (toast: Toast) => void) {
  toastCallback = callback
}
