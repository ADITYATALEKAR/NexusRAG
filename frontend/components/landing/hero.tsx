import { ArrowRight, CheckCircle2 } from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'

const heroSignals = [
  'Citation-backed answers with abstention',
  'Hybrid retrieval: dense vectors + BM25',
  'Multi-provider generation with failover',
  'Self-hostable when teams are ready to roll private',
]

const flowLayers = [
  {
    label: 'Query',
    title: 'User question',
    detail: 'Natural-language intent enters the workspace.',
    accent: false,
  },
  {
    label: 'Retrieval',
    title: 'Hybrid search',
    detail: 'Dense vectors and BM25 gather the strongest supporting context.',
    accent: true,
  },
  {
    label: 'Evidence',
    title: 'Grounded context',
    detail: 'Evidence, filenames, and scored passages are preserved.',
    accent: false,
  },
  {
    label: 'LLM',
    title: 'Answer generation',
    detail: 'The model answers with citations or abstains when evidence is thin.',
    accent: true,
  },
]

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-bg-primary">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_18%,rgba(15,98,254,0.08),transparent_28%),linear-gradient(180deg,rgba(240,246,255,0.84)_0%,rgba(255,255,255,0)_32%)]" />

      <div className="relative mx-auto w-full max-w-[1920px] px-6 pb-20 pt-12 lg:px-8 xl:px-10 2xl:px-12">
        {/* Top row: headline left, architecture right */}
        <div className="grid gap-12 xl:grid-cols-2 xl:items-start">
          {/* Left: headline + subtitle */}
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-accent-100 bg-accent-50/88 px-4 py-2 text-sm font-medium text-accent-700">
              <CheckCircle2 className="h-4 w-4" />
              Open-source - GPT-4o + multi-provider failover - self-hostable
            </div>

            <h1 className="mt-7 text-balance text-[4.05rem] font-semibold leading-[1.04] tracking-[-0.062em] text-text-primary md:text-[5rem] xl:text-[5.35rem] 2xl:text-[5.9rem]">
              Enterprise RAG with
              <span className="block text-accent-600">evidence built in.</span>
            </h1>

            <p className="mt-8 max-w-[680px] text-[1.16rem] leading-[1.84] text-text-secondary">
              NexusRAG is a retrieval engine for grounded AI systems. Teams use it when ChatGPT
              and Claude stop being enough: they need visible evidence, controllable retrieval,
              plug-in APIs, and a clean path from shared evaluation to private rollout.
            </p>
          </div>

          {/* Right: architecture diagram — no outer border */}
          <div className="w-full rounded-[24px] bg-[linear-gradient(180deg,rgba(248,251,255,0.92),rgba(255,255,255,0.88))] p-6 md:p-8">
            <div className="flex items-center justify-between pb-5">
              <div>
                <p className="text-[0.72rem] font-medium uppercase tracking-[0.26em] text-accent-700">
                  Architecture
                </p>
                <h3 className="mt-2 text-lg font-semibold tracking-[-0.03em] text-text-primary">
                  Retrieval before generation
                </h3>
              </div>
              <div className="rounded-full border border-accent-100 bg-accent-50 px-3 py-1 text-[0.68rem] font-medium uppercase tracking-[0.22em] text-accent-700">
                Live RAG stack
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {flowLayers.map((layer) => (
                <div
                  key={layer.title}
                  className={`rounded-[18px] border px-5 py-4 ${
                    layer.accent
                      ? 'border-accent-200 bg-[linear-gradient(180deg,rgba(15,98,254,0.08),rgba(255,255,255,0.92))]'
                      : 'border-border-subtle bg-bg-primary/88'
                  }`}
                >
                  <p className="text-[0.68rem] font-medium uppercase tracking-[0.24em] text-text-tertiary">
                    {layer.label}
                  </p>
                  <h4 className="mt-1.5 text-[0.95rem] font-semibold tracking-[-0.03em] text-text-primary">
                    {layer.title}
                  </h4>
                  <p className="mt-1.5 text-[0.85rem] leading-5 text-text-secondary">
                    {layer.detail}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CTA buttons + helper text — full width below both columns */}
        <div className="mt-10 flex flex-col gap-4 sm:flex-row">
          <Button size="lg" className="h-14 px-8 text-lg" asChild>
            <Link href="/dashboard">
              Try it free
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" className="h-14 px-8 text-lg" asChild>
            <Link href="/login">Connect your own API</Link>
          </Button>
        </div>
        <p className="mt-4 text-sm text-text-tertiary">
          {PUBLIC_TRIAL_QUERY_LIMIT} free hosted queries on the shared API. Move to your own
          NexusRAG endpoint when you want private data and unlimited usage.
        </p>

        {/* Signal pills */}
        <div className="mt-12 grid gap-4 xl:grid-cols-4">
          {heroSignals.map((signal) => (
            <div
              key={signal}
              className="flex min-h-[68px] items-center rounded-full border border-border-subtle/70 bg-bg-primary/88 px-5 py-3 text-sm font-medium leading-6 text-text-secondary shadow-sm"
            >
              {signal}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
