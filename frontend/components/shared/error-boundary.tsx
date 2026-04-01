'use client'

import { AlertTriangle } from 'lucide-react'
import { Component, ErrorInfo, ReactNode } from 'react'

import { Button } from '@/components/ui/button'

interface State {
  hasError: boolean
}

export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('NexusRAG frontend error', error, info)
  }

  render() {
    if (!this.state.hasError) {
      return this.props.children
    }

    return (
      <div className="flex min-h-screen items-center justify-center bg-bg-primary px-6">
        <div className="surface max-w-lg p-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-error/10 text-error">
            <AlertTriangle className="h-7 w-7" />
          </div>
          <h1 className="text-2xl font-semibold text-text-primary">Something went off course</h1>
          <p className="mt-3 text-sm leading-6 text-text-secondary">
            The interface hit an unexpected state. Refresh to recover, and if this keeps happening check the backend health and API key settings.
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <Button onClick={() => window.location.reload()}>Refresh</Button>
            <Button variant="outline" onClick={() => (window.location.href = '/dashboard/settings')}>
              Open settings
            </Button>
          </div>
        </div>
      </div>
    )
  }
}