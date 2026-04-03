const architectureLayers = [
  {
    short: '1',
    title: 'Cloudflare Pages',
    role: 'Frontend',
    description:
      'Static Next.js build served at the edge. Sub-second loads globally, zero backend secrets in the browser.',
  },
  {
    short: '2',
    title: 'Render',
    role: 'API server (FastAPI)',
    description:
      'Handles document ingestion, hybrid retrieval, answer generation with multi-provider failover, and usage tracking.',
  },
  {
    short: '3',
    title: 'Neon Postgres + pgvector',
    role: 'Data layer',
    description:
      'Document metadata, 384-dimensional vector embeddings, and retrieval state in managed Postgres. Durable, queryable, inspectable.',
  },
]

const technicalSpecs = [
  { label: 'Chunking', value: '512 tokens, 64-token overlap' },
  { label: 'Dense retrieval', value: 'Top 50, 384-dim vectors' },
  { label: 'Lexical retrieval', value: 'BM25, top 50' },
  { label: 'Fusion + rerank', value: 'Top 25, final top 10' },
  { label: 'Generation', value: 'GPT-4o (temp 0.1, 1024 max)' },
  { label: 'Failover chain', value: 'Claude \u2192 Gemini \u2192 Llama 3.1' },
]

const comparisons = [
  {
    category: 'Source verification',
    nexusrag:
      'Inline citations with document names, chunk positions, and relevance scores on every answer. Abstains when evidence is insufficient.',
    competitors: 'ChatPDF, Vectara',
    generic:
      'Answers arrive as plain text. Source attribution, when present, is limited to document-level references without passage-level tracing.',
  },
  {
    category: 'Retrieval method',
    nexusrag:
      'Hybrid pipeline: dense vector similarity + BM25 keyword matching with fusion and reranking. Handles semantic queries and exact-phrase lookups.',
    competitors: 'PrivateGPT, ChatPDF',
    generic:
      'Single-method retrieval (usually vector-only) that struggles with exact names, numbers, and domain-specific terminology.',
  },
  {
    category: 'Deployment model',
    nexusrag:
      'Hosted evaluation with zero setup, plus a fully self-hostable open-source stack. Same interface, same API, your infrastructure.',
    competitors: 'Danswer/Onyx, Ragie',
    generic:
      'Either cloud-only with no self-hosting path, or self-host-only with no managed evaluation option.',
  },
  {
    category: 'Developer + end-user',
    nexusrag:
      'Full REST API for programmatic access and an end-user workspace in a single product. API-first for developers, workspace-ready for operators.',
    competitors: 'Vectara, Ragie',
    generic:
      'Forces a choice: simple end-user chat app with no API, or developer-only API with no built-in interface.',
  },
]

export function TrustSignals() {
  return (
    <section id="architecture" className="py-24">
      <div className="mx-auto max-w-[1440px] space-y-8 px-6">
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
          <div className="space-y-6">
            <div className="surface space-y-5 p-8">
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
                Architecture
              </p>
              <h2 className="text-3xl font-semibold tracking-tight text-text-primary">
                Three-tier production stack
              </h2>
              <p className="text-sm leading-7 text-text-secondary">
                NexusRAG runs on the same architecture you would deploy in production:
                edge-hosted frontend, dedicated API server, and managed vector-capable
                Postgres. What you evaluate is what you ship.
              </p>
              <div className="rounded-2xl border border-border-subtle bg-bg-secondary p-5">
                <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_24px_minmax(0,1fr)_24px_minmax(0,1fr)] md:items-center">
                  {architectureLayers.map((layer, index) => (
                    <div key={layer.title} className="contents">
                      <div className="rounded-2xl border border-border-subtle bg-bg-primary px-4 py-4">
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent-100 text-sm font-semibold text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
                            {layer.short}
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-text-primary">{layer.title}</p>
                            <p className="text-xs text-text-tertiary">{layer.role}</p>
                          </div>
                        </div>
                      </div>
                      {index < architectureLayers.length - 1 ? (
                        <div className="hidden text-center text-lg text-text-tertiary md:block">-&gt;</div>
                      ) : null}
                    </div>
                  ))}
                </div>
                <p className="mt-4 text-sm leading-6 text-text-secondary">
                  Browser sessions stay on Cloudflare, ingestion and answer generation run on Render,
                  and every document, chunk, and vector lands in Neon for durable retrieval.
                </p>
              </div>
              <div className="grid gap-4">
                {architectureLayers.map((layer) => (
                  <div
                    key={layer.title}
                    className="rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-4"
                  >
                    <div className="flex items-baseline gap-2">
                      <h3 className="text-base font-semibold text-text-primary">{layer.title}</h3>
                      <span className="text-xs font-medium text-text-tertiary">{layer.role}</span>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-text-secondary">
                      {layer.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="surface p-8">
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
                Retrieval defaults
              </p>
              <h3 className="mt-3 text-xl font-semibold tracking-tight text-text-primary">
                Pipeline configuration
              </h3>
              <div className="mt-4 grid grid-cols-2 gap-3">
                {technicalSpecs.map((spec) => (
                  <div
                    key={spec.label}
                    className="rounded-xl border border-border-subtle bg-bg-secondary px-3 py-2.5"
                  >
                    <p className="text-[11px] font-medium uppercase tracking-[0.15em] text-text-tertiary">
                      {spec.label}
                    </p>
                    <p className="mt-1 text-sm font-medium text-text-primary">{spec.value}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="surface space-y-5 p-8">
            <p className="text-sm font-medium uppercase tracking-[0.22em] text-accent-700 dark:text-accent-100">
              NexusRAG vs. alternatives
            </p>
            <h2 className="text-3xl font-semibold tracking-tight text-text-primary">
              How we compare to ChatPDF, Vectara, Danswer, and others
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
                        {row.competitors}
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
