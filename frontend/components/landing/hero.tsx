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

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-bg-primary">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_18%,rgba(15,98,254,0.08),transparent_28%),linear-gradient(180deg,rgba(240,246,255,0.84)_0%,rgba(255,255,255,0)_32%)]" />

      <div className="relative mx-auto flex w-full max-w-[1920px] flex-col gap-12 px-6 pb-16 pt-12 lg:px-8 xl:px-10 2xl:px-12">
        <div className="max-w-[1280px]">
          <div className="inline-flex items-center gap-2 rounded-full border border-accent-100 bg-accent-50/88 px-4 py-2 text-sm font-medium text-accent-700">
            <CheckCircle2 className="h-4 w-4" />
            Open-source · GPT-4o + multi-provider failover · self-hostable
          </div>

          <div className="mt-7 max-w-[1280px]">
            <h1 className="max-w-[1260px] text-balance text-[4.15rem] font-semibold leading-[0.96] tracking-[-0.072em] text-text-primary md:text-[5.15rem] xl:text-[6.1rem] 2xl:text-[6.55rem]">
              Enterprise RAG with
              <span className="block text-accent-600">evidence built in.</span>
            </h1>

            <p className="mt-8 max-w-[1080px] text-[1.22rem] leading-[1.76] text-text-secondary">
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

          <div className="mt-12">
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
      </div>
    </section>
  )
}

