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
    <div className="surface-muted flex min-h-[320px] flex-col items-center justify-center px-6 py-14 text-center">
      {icon ? <div className="mb-5 rounded-sm border border-border-subtle bg-bg-primary p-4">{icon}</div> : null}
      <h3 className="text-[2rem] font-semibold tracking-[-0.05em] text-text-primary">{title}</h3>
      <p className="mt-4 max-w-[620px] text-base leading-8 text-text-secondary">{description}</p>
      {action ? (
        <Button variant="outline" className="mt-7 h-12 px-5" onClick={action.onClick}>
          {action.label}
        </Button>
      ) : null}
    </div>
  )
}
