import { ArrowRight, CheckCircle2, ChevronRight } from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'

const heroSignals = [
  'Citation-backed answers with abstention',
  'Hybrid retrieval: dense vectors + BM25',
  'Multi-provider generation with failover',
  'Self-hostable with full API access',
]

const flowSteps = [
  {
    label: 'Query',
    title: 'User question',
    detail: 'Natural-language intent enters the workspace.',
    accent: false,
  },
  {
    label: 'Retrieval',
    title: 'Hybrid search',
    detail: 'Dense vectors and BM25 surface the strongest context.',
    accent: true,
  },
  {
    label: 'Evidence',
    title: 'Grounded context',
    detail: 'Filenames, scored passages, and source metadata are preserved.',
    accent: false,
  },
  {
    label: 'LLM',
    title: 'Cited answer',
    detail: 'The model answers with citations or abstains when evidence is thin.',
    accent: true,
  },
]

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-bg-primary">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_72%_14%,rgba(15,98,254,0.06),transparent_32%)]" />

      <div className="relative mx-auto w-full max-w-[1920px] px-6 pb-20 pt-14 lg:px-8 xl:px-10 2xl:px-12">
        {/* Hero grid: text left, architecture right */}
        <div className="grid items-center gap-16 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
          {/* Left column */}
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-accent-100 bg-accent-50/80 px-4 py-2 text-[0.82rem] font-medium text-accent-700">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Open-source &middot; Multi-provider LLM failover &middot; Self-hostable
            </div>

            <h1 className="mt-8 text-[3.4rem] font-semibold leading-[1.06] tracking-[-0.04em] text-text-primary md:text-[4.2rem] xl:text-[5rem] 2xl:text-[5.6rem]">
              Enterprise RAG with{' '}
              <span className="text-accent-600">evidence built in.</span>
            </h1>

            <p className="mt-8 max-w-[620px] text-[1.08rem] leading-[1.8] text-text-secondary">
              NexusRAG is a retrieval engine for grounded AI systems. Teams use it when
              ChatGPT and Claude stop being enough — they need visible evidence,
              controllable retrieval, plug-in APIs, and a clean path from shared evaluation
              to private rollout.
            </p>

            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <Button size="lg" className="h-14 px-8 text-base" asChild>
                <Link href="/dashboard">
                  Try it free
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="h-14 px-8 text-base" asChild>
                <Link href="/login">Connect your own API</Link>
              </Button>
            </div>

            <p className="mt-4 text-sm text-text-tertiary">
              {PUBLIC_TRIAL_QUERY_LIMIT} free queries on the hosted API &middot; No account
              required
            </p>
          </div>

          {/* Right column: architecture flow diagram */}
          <div className="w-full">
            <p className="text-[0.72rem] font-medium uppercase tracking-[0.26em] text-accent-700">
              How NexusRAG processes a query
            </p>

            <div className="mt-5 flex flex-col gap-0">
              {flowSteps.map((step, i) => (
                <div key={step.label}>
                  <div
                    className={`rounded-2xl px-6 py-5 ${
                      step.accent
                        ? 'bg-accent-50/60 dark:bg-accent-500/8'
                        : 'bg-bg-secondary/60'
                    }`}
                  >
                    <div className="flex items-baseline gap-3">
                      <span className="text-[0.68rem] font-semibold uppercase tracking-[0.22em] text-accent-600">
                        {step.label}
                      </span>
                      <span className="text-[1rem] font-semibold tracking-[-0.02em] text-text-primary">
                        {step.title}
                      </span>
                    </div>
                    <p className="mt-1.5 text-[0.88rem] leading-6 text-text-secondary">
                      {step.detail}
                    </p>
                  </div>
                  {i < flowSteps.length - 1 && (
                    <div className="flex justify-center py-1">
                      <ChevronRight className="h-4 w-4 rotate-90 text-accent-300" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Signal pills — full width */}
        <div className="mt-14 grid gap-4 xl:grid-cols-4">
          {heroSignals.map((signal) => (
            <div
              key={signal}
              className="flex min-h-[60px] items-center rounded-full border border-border-subtle/50 bg-bg-secondary/50 px-5 py-3 text-[0.85rem] font-medium leading-6 text-text-secondary"
            >
              {signal}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
