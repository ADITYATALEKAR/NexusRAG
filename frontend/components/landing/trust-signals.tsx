import { ArrowRightLeft, Sparkles, ShieldCheck } from 'lucide-react'

import { PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'

const evaluationModes = [
  {
    eyebrow: 'Start public',
    title: 'Hosted evaluation',
    description:
      'Use the shared NexusRAG API to test upload, retrieval, evidence, and answer quality without any setup.',
    footnote: `${PUBLIC_TRIAL_QUERY_LIMIT} free hosted queries`,
    icon: Sparkles,
  },
  {
    eyebrow: 'Move private',
    title: 'Bring your own API',
    description:
      'Point the same workspace at your own NexusRAG runtime for private data, unlimited usage, and your own controls.',
    footnote: 'Same workflow, different backend',
    icon: ShieldCheck,
  },
]

export function TrustSignals() {
  return (
    <section className="bg-bg-primary py-14">
      <div className="mx-auto w-full max-w-[1920px] px-6 lg:px-10 xl:px-12 2xl:px-16">
        <div className="overflow-hidden rounded-[28px] bg-[linear-gradient(180deg,rgba(248,251,255,0.92),rgba(255,255,255,0.88))] p-8 md:p-10">
          <div className="flex flex-col gap-8 xl:flex-row xl:items-center xl:justify-between">
            <div className="max-w-[760px]">
              <p className="text-sm font-medium uppercase tracking-[0.24em] text-accent-700">
                Evaluate the product the way teams actually buy it
              </p>
              <h2 className="mt-4 max-w-[760px] text-balance text-[2.85rem] font-semibold leading-[1.02] tracking-[-0.07em] text-text-primary md:text-[3.75rem]">
                Start public. Move private. Keep the same workspace.
              </h2>
              <p className="mt-5 max-w-[700px] text-base leading-8 text-text-secondary">
                The first pass should feel like the real product, not a stripped-down demo.
                Evaluate answer quality in the hosted mode, then switch the exact same interface to
                your own API when your team is ready.
              </p>
            </div>

            <div className="grid gap-4 lg:min-w-[560px] lg:grid-cols-2">
              {evaluationModes.map((mode) => (
                <div key={mode.title} className="rounded-sm border border-border-subtle bg-bg-primary/82 p-5 shadow-sm">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-[0.76rem] font-medium uppercase tracking-[0.24em] text-text-tertiary">
                        {mode.eyebrow}
                      </p>
                      <h3 className="mt-3 text-[1.6rem] font-semibold tracking-[-0.05em] text-text-primary">
                        {mode.title}
                      </h3>
                    </div>
                    <mode.icon className="mt-1 h-5 w-5 shrink-0 text-accent-600" />
                  </div>
                  <p className="mt-4 text-sm leading-7 text-text-secondary">{mode.description}</p>
                  <div className="mt-5 inline-flex items-center gap-2 text-[0.78rem] font-medium uppercase tracking-[0.22em] text-accent-700">
                    {mode.footnote}
                    <ArrowRightLeft className="h-3.5 w-3.5" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

