'use client'

import { useState, useEffect } from 'react'
import { X, CheckCircle2, AlertCircle, Info } from 'lucide-react'
import { setToastHandler, type Toast } from '@/lib/hooks/use-toast'
import { cn } from '@/lib/utils'

export function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([])

  useEffect(() => {
    setToastHandler((toast) => {
      setToasts((prev) => [...prev, toast])

      const timer = setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== toast.id))
      }, toast.duration || 4000)

      return () => clearTimeout(timer)
    })
  }, [])

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            'flex items-start gap-3 rounded-lg px-4 py-3 shadow-lg animate-in fade-in slide-in-from-right',
            toast.type === 'success' && 'bg-success/10 border border-success/20',
            toast.type === 'error' && 'bg-error/10 border border-error/20',
            toast.type === 'info' && 'bg-info/10 border border-info/20'
          )}
        >
          <div className="mt-0.5">
            {toast.type === 'success' && <CheckCircle2 className="h-5 w-5 text-success" />}
            {toast.type === 'error' && <AlertCircle className="h-5 w-5 text-error" />}
            {toast.type === 'info' && <Info className="h-5 w-5 text-info" />}
          </div>
          <div className="flex-1 min-w-0">
            <p className={cn(
              'font-semibold',
              toast.type === 'success' && 'text-success',
              toast.type === 'error' && 'text-error',
              toast.type === 'info' && 'text-info'
            )}>
              {toast.title}
            </p>
            {toast.description && (
              <p className="text-sm text-text-secondary mt-1">
                {toast.description}
              </p>
            )}
          </div>
          <button
            onClick={() => removeToast(toast.id)}
            className="shrink-0 text-text-tertiary hover:text-text-primary transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  )
}
