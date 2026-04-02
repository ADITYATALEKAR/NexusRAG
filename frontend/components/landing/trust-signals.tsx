const architectureLayers = [
  {
    title: 'Cloudflare Pages frontend',
    description:
      'Static Next.js delivery keeps the workspace fast, globally accessible, and free of backend secrets in the browser.',
  },
  {
    title: 'Render-hosted NexusRAG API',
    description:
      'FastAPI handles ingestion, retrieval, answer generation, and usage control for the hosted public experience.',
  },
  {
    title: 'Neon pgvector evidence layer',
    description:
      'Document metadata, vector search, and retrieval state live in managed Postgres so the data plane is durable and inspectable.',
  },
]

const comparisons = [
  {
    category: 'Source transparency',
    nexusrag: 'Inline citations, evidence panel, and source excerpts in the same workspace.',
    generic: 'Answers often arrive as plain text with no clear audit trail back to source chunks.',
  },
  {
    category: 'Operational control',
    nexusrag: 'Hosted evaluation mode plus a direct path to your own NexusRAG API deployment.',
    generic: 'Many demos stop at a shared playground and offer no migration path to controlled usage.',
  },
  {
    category: 'Architecture',
    nexusrag: 'Frontend, backend, and vector store are deployed on distinct real-world services.',
    generic: 'Single-stack prototypes often hide where retrieval, storage, and inference actually happen.',
  },
  {
    category: 'Decision support',
    nexusrag: 'Designed for grounded retrieval and evidence review before action.',
    generic: 'Optimized for impression, not for documentation-heavy workflows that need defensible answers.',
  },
]

export function TrustSignals() {
  return (
    <section className="py-24">
      <div className="mx-auto max-w-6xl space-y-8 px-6">
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
          <div className="surface space-y-5 p-8">
            <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
              Architecture
            </p>
            <h2 className="text-3xl font-semibold tracking-tight text-text-primary">
              Production architecture, not presentation-only polish
            </h2>
            <p className="text-sm leading-7 text-text-secondary">
              The live deployment is already split the way serious teams expect: edge-hosted
              frontend, dedicated backend API, and a managed vector-capable Postgres layer. That
              means the product story, deployment story, and recruiter story all point to the same
              system.
            </p>
            <div className="grid gap-4">
              {architectureLayers.map((layer) => (
                <div
                  key={layer.title}
                  className="rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-4"
                >
                  <h3 className="text-base font-semibold text-text-primary">{layer.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-text-secondary">
                    {layer.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="surface space-y-5 p-8">
            <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
              Why NexusRAG
            </p>
            <h2 className="text-3xl font-semibold tracking-tight text-text-primary">
              Better suited to evidence-heavy work than generic file chat
            </h2>
            <div className="space-y-4">
              {comparisons.map((row) => (
                <div
                  key={row.category}
                  className="rounded-2xl border border-border-subtle bg-bg-secondary p-4"
                >
                  <p className="text-sm font-semibold text-text-primary">{row.category}</p>
                  <div className="mt-3 grid gap-3 md:grid-cols-2">
                    <div className="rounded-xl bg-bg-primary px-4 py-3">
                      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-accent-700 dark:text-accent-100">
                        NexusRAG
                      </p>
                      <p className="mt-2 text-sm leading-6 text-text-secondary">{row.nexusrag}</p>
                    </div>
                    <div className="rounded-xl bg-bg-primary px-4 py-3">
                      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-text-tertiary">
                        Generic alternative
                      </p>
                      <p className="mt-2 text-sm leading-6 text-text-secondary">{row.generic}</p>
                    </div>
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
