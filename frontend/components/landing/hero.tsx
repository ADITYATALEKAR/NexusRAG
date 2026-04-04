import { ArrowRight, CheckCircle2, Cloud, Database, Server, ShieldCheck } from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'

const productSignals = [
  'Evidence-first answers with abstention',
  'Hybrid retrieval: dense vectors and BM25 together',
  'Hosted trial now, private API later',
]

const deploymentModes = [
  {
    title: 'Try the hosted evaluation',
    description:
      'Use the shared NexusRAG API for a fast first pass, inspect answer quality, and decide whether the workflow fits your team.',
    footnote: `${PUBLIC_TRIAL_QUERY_LIMIT} free queries · no account required`,
  },
  {
    title: 'Switch to your own API',
    description:
      'Keep the same workspace and point it at your own NexusRAG runtime for private data, unlimited usage, and controlled rollout.',
    footnote: 'Same interface · your infrastructure · your limits',
  },
]

const infrastructureRail = [
  { label: 'Frontend', value: 'Cloudflare Pages', icon: Cloud },
  { label: 'API runtime', value: 'Render / FastAPI', icon: Server },
  { label: 'Vectors', value: 'Neon pgvector', icon: Database },
]

export function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border-subtle/80 bg-bg-primary">
      <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(240,246,255,0.88)_0%,rgba(255,255,255,0)_30%),radial-gradient(circle_at_86%_18%,rgba(15,98,254,0.08),transparent_26%)]" />

      <div className="relative mx-auto grid w-full max-w-[1920px] gap-10 px-6 pb-20 pt-12 lg:grid-cols-[minmax(0,1.06fr)_minmax(560px,0.94fr)] lg:px-10 xl:px-12 2xl:px-16">
        <div className="max-w-[980px]">
          <div className="inline-flex items-center gap-2 rounded-full border border-accent-100 bg-accent-50 px-4 py-2 text-sm font-medium text-accent-700">
            <CheckCircle2 className="h-4 w-4" />
            Open-source · GPT-4o + multi-provider failover · Self-hostable
          </div>

          <h1 className="mt-7 max-w-[1120px] text-balance text-[4.35rem] font-semibold leading-[0.91] tracking-[-0.085em] text-text-primary md:text-[5.5rem] xl:text-[6.5rem]">
            Enterprise RAG with
            <span className="block text-accent-600">evidence built in.</span>
          </h1>

          <p className="mt-8 max-w-[820px] text-[1.22rem] leading-[1.76] text-text-secondary">
            NexusRAG is the retrieval workspace for teams that need grounded answers from private
            documents, calm review surfaces, and an upgrade path from hosted evaluation to their own
            deployment without retraining the team on a different UI.
          </p>

          <div className="mt-10 flex flex-col gap-4 sm:flex-row">
            <Button size="lg" asChild>
              <Link href="/dashboard">
                Try it free
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/login">Connect your own API</Link>
            </Button>
          </div>

          <p className="mt-5 text-sm text-text-tertiary">
            {PUBLIC_TRIAL_QUERY_LIMIT} free hosted queries on the shared API. The same workspace can
            switch to your own NexusRAG endpoint when you are ready.
          </p>

          <div className="mt-10 grid gap-3 md:grid-cols-3">
            {productSignals.map((signal) => (
              <div
                key={signal}
                className="rounded-sm border border-border-subtle bg-bg-elevated px-4 py-4 text-sm font-medium text-text-secondary shadow-sm"
              >
                {signal}
              </div>
            ))}
          </div>
        </div>

        <div className="surface overflow-hidden border-border-default/70 bg-[linear-gradient(180deg,rgba(255,255,255,0.99),rgba(246,249,255,0.96))] p-8 md:p-9">
          <div className="flex flex-wrap items-start justify-between gap-6 border-b border-border-subtle/80 pb-6">
            <div className="max-w-[460px]">
              <p className="text-sm font-medium uppercase tracking-[0.24em] text-accent-700">
                Evaluate the product the way teams actually buy it
              </p>
              <h2 className="mt-3 text-[2.05rem] font-semibold tracking-[-0.055em] text-text-primary">
                Start public. Move private. Keep the same workspace.
              </h2>
            </div>

            <div className="rounded-sm border border-border-subtle bg-bg-secondary px-4 py-4 text-right">
              <p className="text-[0.72rem] font-medium uppercase tracking-[0.24em] text-text-tertiary">
                Default mode
              </p>
              <p className="mt-1 text-2xl font-semibold tracking-[-0.05em] text-text-primary">
                Hosted trial
              </p>
              <p className="mt-1 text-xs text-text-tertiary">Upgrade to your own API when ready</p>
            </div>
          </div>

          <div className="mt-6 grid gap-4">
            {deploymentModes.map((mode, index) => (
              <div
                key={mode.title}
                className="rounded-sm border border-border-subtle bg-bg-primary px-5 py-5"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-[0.78rem] font-medium uppercase tracking-[0.24em] text-text-tertiary">
                      Option 0{index + 1}
                    </p>
                    <h3 className="mt-2 text-[1.22rem] font-semibold tracking-[-0.04em] text-text-primary">
                      {mode.title}
                    </h3>
                    <p className="mt-2 text-sm leading-7 text-text-secondary">{mode.description}</p>
                  </div>
                  <ShieldCheck className="mt-1 h-5 w-5 shrink-0 text-accent-600" />
                </div>
                <p className="mt-4 text-[0.78rem] font-medium uppercase tracking-[0.22em] text-accent-700">
                  {mode.footnote}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-6 rounded-sm border border-border-subtle bg-bg-primary px-5 py-5">
            <p className="text-[0.78rem] font-medium uppercase tracking-[0.24em] text-text-tertiary">
              Current live stack
            </p>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {infrastructureRail.map((item) => (
                <div key={item.label} className="rounded-sm border border-border-subtle bg-bg-secondary px-4 py-4">
                  <div className="flex items-center gap-2 text-accent-700">
                    <item.icon className="h-4 w-4" />
                    <span className="text-[0.72rem] font-medium uppercase tracking-[0.2em] text-text-tertiary">
                      {item.label}
                    </span>
                  </div>
                  <p className="mt-3 text-sm font-semibold text-text-primary">{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
