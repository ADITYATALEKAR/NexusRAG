const differentiators = [
  {
    title: 'Evidence over impression',
    nexusrag:
      'Inline citations, source file names, and passage-level grounding stay attached to the answer so the reviewer can inspect why it was returned.',
    typical:
      'Many tools give you fluent prose first and treat evidence as a secondary tab, a weak footnote, or a document-level link with no passage context.',
  },
  {
    title: 'Retrieval that handles meaning and exact language',
    nexusrag:
      'Hybrid retrieval keeps dense semantic search and BM25 exact matching in the same pipeline, so clauses, policy names, and numeric references survive retrieval.',
    typical:
      'Vector-only flows often feel good on broad semantic prompts, then miss the exact terms and narrow phrasing that enterprise teams actually care about.',
  },
  {
    title: 'One product for trials, operators, and developers',
    nexusrag:
      'The same stack supports a hosted two-query evaluation, an operator workspace, and a full REST API when teams want to integrate retrieval into their own products.',
    typical:
      'You usually have to choose between a polished demo app for end users or an API-only platform that still needs an internal interface built around it.',
  },
]

const trustPillars = [
  'Public GitHub repository and live cloud deployment',
  'Hosted trial with no account required',
  'Bring Your Own API path for unlimited usage',
  'Open-source, self-hostable deployment model',
]

export function TrustSignals() {
  return (
    <section id="why-nexusrag" className="py-24">
      <div className="mx-auto w-full max-w-[1920px] px-8 lg:px-12 xl:px-16">
        <div className="grid gap-8 xl:grid-cols-[minmax(340px,0.82fr)_minmax(0,1.18fr)]">
          <div className="surface space-y-8 p-8 md:p-10">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
                Why NexusRAG
              </p>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight text-text-primary md:text-4xl">
                Built for teams that need trust, not just speed
              </h2>
              <p className="mt-5 text-base leading-8 text-text-secondary">
                The strongest retrieval products do not just answer quickly. They make it easy to
                understand what grounded the answer, move from a trial to a real deployment, and
                keep the retrieval workflow understandable for both operators and engineers.
              </p>
            </div>

            <div className="space-y-3">
              {trustPillars.map((pillar) => (
                <div
                  key={pillar}
                  className="rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-3 text-sm font-medium text-text-primary"
                >
                  {pillar}
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-5">
            {differentiators.map((item, index) => (
              <div
                key={item.title}
                className="surface grid gap-5 p-7 md:grid-cols-[88px_minmax(0,1fr)_minmax(0,1fr)] md:items-start"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-accent-100 text-lg font-semibold text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
                  0{index + 1}
                </div>
                <div>
                  <p className="text-[11px] font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
                    NexusRAG
                  </p>
                  <h3 className="mt-2 text-xl font-semibold tracking-tight text-text-primary">
                    {item.title}
                  </h3>
                  <p className="mt-3 text-sm leading-7 text-text-secondary">{item.nexusrag}</p>
                </div>
                <div className="rounded-[24px] border border-border-subtle bg-bg-secondary px-5 py-4">
                  <p className="text-[11px] font-medium uppercase tracking-[0.22em] text-text-tertiary">
                    Typical alternative
                  </p>
                  <p className="mt-3 text-sm leading-7 text-text-secondary">{item.typical}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

