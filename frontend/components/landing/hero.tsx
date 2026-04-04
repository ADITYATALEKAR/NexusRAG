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
    title: 'Cited context',
    detail: 'Relevant passages, filenames, and review context are preserved.',
    accent: false,
  },
  {
    label: 'Prompt',
    title: 'Answer assembly',
    detail: 'Evidence is organized into a grounded prompt with clear constraints.',
    accent: false,
  },
  {
    label: 'LLM',
    title: 'Generation',
    detail: 'The model answers with citations or abstains when evidence is thin.',
    accent: true,
  },
  {
    label: 'Output',
    title: 'Grounded response',
    detail: 'Teams receive a readable answer, sources, and audit-ready evidence.',
    accent: false,
  },
]

function HeroArchitectureDiagram() {
  return (
    <div className="relative rounded-[28px] border border-border-subtle/80 bg-white/84 p-5 shadow-[0_18px_60px_rgba(15,23,42,0.08)] backdrop-blur md:p-6 xl:p-7">
      <div className="flex items-center justify-between border-b border-border-subtle/70 pb-4">
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

      <div className="relative mt-5 space-y-3">
        <div className="absolute left-[15px] top-8 bottom-8 w-px bg-gradient-to-b from-accent-200 via-border-subtle to-accent-200" />
        {flowLayers.map((layer) => (
          <div key={layer.title} className="relative pl-10">
            <span
              className={`absolute left-0 top-5 h-[10px] w-[10px] rounded-full border ${
                layer.accent
                  ? 'border-accent-500 bg-accent-500 shadow-[0_0_0_4px_rgba(15,98,254,0.12)]'
                  : 'border-border-default bg-white'
              }`}
            />
            <div
              className={`rounded-[22px] border px-5 py-4 shadow-sm ${
                layer.accent
                  ? 'border-accent-200 bg-[linear-gradient(180deg,rgba(15,98,254,0.08),rgba(255,255,255,0.92))]'
                  : 'border-border-subtle bg-bg-primary/88'
              }`}
            >
              <p className="text-[0.68rem] font-medium uppercase tracking-[0.24em] text-text-tertiary">
                {layer.label}
              </p>
              <h4 className="mt-2 text-[1.08rem] font-semibold tracking-[-0.03em] text-text-primary">
                {layer.title}
              </h4>
              <p className="mt-2 text-sm leading-6 text-text-secondary">{layer.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-bg-primary">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_18%,rgba(15,98,254,0.08),transparent_28%),linear-gradient(180deg,rgba(240,246,255,0.84)_0%,rgba(255,255,255,0)_32%)]" />

      <div className="relative mx-auto flex w-full max-w-[1920px] flex-col gap-12 px-6 pb-16 pt-12 lg:px-8 xl:px-10 2xl:px-12">
        <div className="grid gap-12 xl:grid-cols-[minmax(0,1.12fr)_minmax(420px,0.88fr)] xl:items-start">
          <div className="max-w-[980px]">
            <div className="inline-flex items-center gap-2 rounded-full border border-accent-100 bg-accent-50/88 px-4 py-2 text-sm font-medium text-accent-700">
              <CheckCircle2 className="h-4 w-4" />
              Open-source - GPT-4o + multi-provider failover - self-hostable
            </div>

            <div className="mt-7">
              <h1 className="max-w-[980px] text-balance text-[4.15rem] font-semibold leading-[0.98] tracking-[-0.068em] text-text-primary md:text-[5.15rem] xl:text-[5.55rem] 2xl:text-[6.15rem]">
                Enterprise RAG with
                <span className="block text-accent-600">evidence built in.</span>
              </h1>

              <p className="mt-8 max-w-[840px] text-[1.18rem] leading-[1.8] text-text-secondary">
                NexusRAG gives teams a premium retrieval workspace that feels credible on first
                contact: grounded answers, inline citations, calm review surfaces, and a clear path
                from hosted evaluation to a private deployment with the same interface.
              </p>

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

              <p className="mt-5 text-sm text-text-tertiary">
                {PUBLIC_TRIAL_QUERY_LIMIT} free hosted queries on the shared API. Move to your own
                NexusRAG endpoint when you want private data and unlimited usage.
              </p>
            </div>
          </div>

          <div className="xl:pt-2">
            <HeroArchitectureDiagram />
          </div>
        </div>

        <div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
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
      </div>
    </section>
  )
}

