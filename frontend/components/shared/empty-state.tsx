import { ReactNode } from 'react'

import { Button } from '@/components/ui/button'

export function EmptyState({
  title,
  description,
  action,
  icon
}: {
  title: string
  description: string
  action?: { label: string; onClick: () => void }
  icon?: ReactNode
}) {
  return (
    <div className="surface-muted flex min-h-[260px] flex-col items-center justify-center px-6 py-12 text-center">
      {icon ? <div className="mb-5 rounded-2xl bg-bg-primary p-4">{icon}</div> : null}
      <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
      <p className="mt-2 max-w-md text-sm text-text-secondary">{description}</p>
      {action ? (
        <Button variant="outline" className="mt-6" onClick={action.onClick}>
          {action.label}
        </Button>
      ) : null}
    </div>
  )
}