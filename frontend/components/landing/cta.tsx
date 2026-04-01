import Link from 'next/link'

import { PUBLIC_APP_ENABLED } from '@/lib/public-config'
import { Button } from '@/components/ui/button'

export function CTA() {
  return (
    <section className="py-24">
      <div className="mx-auto max-w-4xl px-6">
        <div className="surface overflow-hidden bg-gradient-to-br from-bg-elevated via-bg-elevated to-accent-50/80 p-10 dark:to-accent-500/10 md:p-14">
          <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">Ready to ship</p>
          <h2 className="mt-4 text-3xl font-semibold tracking-tight text-text-primary md:text-4xl">Turn your knowledge base into a calm, trustworthy workspace.</h2>
          <p className="mt-4 max-w-2xl text-base leading-7 text-text-secondary">Start with the live dashboard, upload a few files, and see grounded answers with inline evidence in under five minutes.</p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button size="lg" asChild>
              <Link href={PUBLIC_APP_ENABLED ? '/dashboard' : '/signup'}>
                {PUBLIC_APP_ENABLED ? 'Open public workspace' : 'Create workspace'}
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/dashboard">Try demo dashboard</Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
