import { ArrowRight, Mail, Phone, Server } from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'
import { FOUNDER_CONTACT } from '@/lib/site-content'

const launchModes = [
  {
    title: 'Hosted free evaluation',
    description: `${PUBLIC_TRIAL_QUERY_LIMIT} questions on the managed NexusRAG API so candidates, customers, and evaluators can see the product live immediately.`,
  },
  {
    title: 'Bring your own API',
    description:
      'Connect your own NexusRAG API endpoint and access key for unlimited usage, private data boundaries, and your own operational controls.',
  },
]

export function CTA() {
  return (
    <section className="py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="surface overflow-hidden bg-gradient-to-br from-bg-elevated via-bg-elevated to-accent-50/80 p-10 dark:to-accent-500/10 md:p-14">
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1.2fr)_360px]">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
                Ready to launch
              </p>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight text-text-primary md:text-4xl">
                Start free, prove the workflow, then switch to your own API without changing the UI
              </h2>
              <p className="mt-4 max-w-2xl text-base leading-7 text-text-secondary">
                NexusRAG is built for a serious evaluation path. Reviewers can use the hosted public
                experience immediately, while teams that want ongoing usage can bring their own API
                endpoint and keep the same interface, evidence model, and operating rhythm.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Button size="lg" asChild>
                  <Link href="/dashboard">
                    Start free
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link href="/login">Use your own API</Link>
                </Button>
              </div>
              <div className="mt-8 grid gap-4 md:grid-cols-2">
                {launchModes.map((mode) => (
                  <div
                    key={mode.title}
                    className="rounded-2xl border border-border-subtle bg-bg-primary/80 p-4"
                  >
                    <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-2xl bg-accent-100 text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
                      <Server className="h-4 w-4" />
                    </div>
                    <h3 className="text-base font-semibold text-text-primary">{mode.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-text-secondary">
                      {mode.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-border-subtle bg-bg-primary/85 p-6 shadow-sm">
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
                Contact
              </p>
              <h3 className="mt-4 text-2xl font-semibold text-text-primary">
                {FOUNDER_CONTACT.name}
              </h3>
              <p className="mt-2 text-sm text-text-secondary">{FOUNDER_CONTACT.role}</p>
              <div className="mt-6 space-y-4 text-sm text-text-secondary">
                <a
                  href={`mailto:${FOUNDER_CONTACT.email}`}
                  className="flex items-center gap-3 rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-3 transition-colors hover:border-border-default hover:text-text-primary"
                >
                  <Mail className="h-4 w-4 text-accent-700 dark:text-accent-100" />
                  <span>{FOUNDER_CONTACT.email}</span>
                </a>
                <a
                  href={`tel:${FOUNDER_CONTACT.phone.replace(/\s+/g, '')}`}
                  className="flex items-center gap-3 rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-3 transition-colors hover:border-border-default hover:text-text-primary"
                >
                  <Phone className="h-4 w-4 text-accent-700 dark:text-accent-100" />
                  <span>{FOUNDER_CONTACT.phone}</span>
                </a>
              </div>
              <p className="mt-6 text-sm leading-6 text-text-secondary">
                If you want a walkthrough, deployment discussion, or a private API setup for your
                team, reach out directly and we can take it from evaluation to production.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
