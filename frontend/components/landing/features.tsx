import {
  BarChart3,
  Code2,
  FileText,
  Globe2,
  RefreshCw,
  SearchCheck,
  Shield,
  Zap,
} from 'lucide-react'

const features = [
  {
    icon: FileText,
    title: 'Eight input formats',
    description:
      'Ingest PDF, DOCX, DOC, TXT, Markdown, HTML, CSV, and JSON. Each file is semantically chunked (512 tokens, 64-token overlap) and indexed for hybrid retrieval — up to 50 MB per file.',
  },
  {
    icon: SearchCheck,
    title: 'Hybrid retrieval pipeline',
    description:
      'Dense vector search and BM25 keyword matching run in parallel. Results are fused (top 50 from each method), reranked to 25, and the best 10 passages are sent to generation.',
  },
  {
    icon: Shield,
    title: 'Citation-backed answers with abstention',
    description:
      'Every response includes inline source references with document names and relevance scores. When evidence is insufficient, the system abstains rather than hallucinating.',
  },
  {
    icon: RefreshCw,
    title: 'Multi-provider failover',
    description:
      'Defaults to GPT-4o for generation, with automatic failover across Claude Sonnet 4, Gemini 1.5 Pro, and Llama 3.1 70B. Configurable per deployment.',
  },
  {
    icon: Zap,
    title: 'Operational workspace',
    description:
      'Upload, query, inspect source passages, refine, and re-query in a single interface. Built for repeated daily use by operations, legal, and support teams — not one-off demos.',
  },
  {
    icon: BarChart3,
    title: 'Retrieval observability',
    description:
      'See which chunks were retrieved, their relevance scores, and how the answer was constructed. The platform includes evaluation and regression tooling to measure quality over time.',
  },
  {
    icon: Code2,
    title: 'Full REST API',
    description:
      'Every capability — ingestion, retrieval, generation, document management — is exposed through a documented API. Build retrieval into your own applications or use the workspace directly.',
  },
  {
    icon: Globe2,
    title: 'Production-deployed, self-hostable',
    description:
      'Already running in production on Cloudflare Pages, Render (FastAPI), and Neon Postgres with pgvector. Clone the public repo and deploy your own instance.',
  },
]

export function Features() {
  return (
    <section id="features" className="bg-bg-secondary py-24">
      <div className="mx-auto max-w-[1440px] px-6">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight text-text-primary">
            What ships out of the box
          </h2>
          <p className="mt-4 text-base leading-7 text-text-secondary">
            End-to-end retrieval pipeline — from document ingestion and hybrid search to
            cited answer generation — in one deployable stack. API-first for developers,
            workspace-ready for end users.
          </p>
        </div>
        <div className="mt-14 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="surface p-6 transition-all duration-[var(--duration-normal)] hover:-translate-y-0.5 hover:shadow-md"
            >
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-100 text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
                <feature.icon className="h-5 w-5" />
              </div>
              <h3 className="text-base font-semibold text-text-primary">{feature.title}</h3>
              <p className="mt-3 text-sm leading-6 text-text-secondary">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
