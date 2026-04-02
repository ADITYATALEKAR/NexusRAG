import {
  BarChart3,
  Code2,
  FileText,
  Globe2,
  SearchCheck,
  Shield,
  Zap,
} from 'lucide-react'

const features = [
  {
    icon: FileText,
    title: 'Multi-format ingestion',
    description:
      'PDF, DOCX, Markdown, and text are converted into chunked evidence that stays searchable instead of living in disconnected uploads.',
  },
  {
    icon: SearchCheck,
    title: 'Hybrid retrieval',
    description:
      'Dense vector search and lexical search work together so the system can handle both semantic intent and exact phrasing.',
  },
  {
    icon: Shield,
    title: 'Citation-backed answers',
    description:
      'Answer text is paired with source excerpts, document names, and relevance signals so review happens in context, not on faith.',
  },
  {
    icon: Zap,
    title: 'Fast operator loop',
    description:
      'Upload, ask, inspect, refine, and re-run in one interface built for repeated operational use instead of a one-shot demo prompt.',
  },
  {
    icon: BarChart3,
    title: 'Evaluation-aware foundation',
    description:
      'The platform is designed around retrieval quality, traceability, and observability so teams can improve quality with evidence.',
  },
  {
    icon: Code2,
    title: 'Bring-your-own API path',
    description:
      'Start on the hosted trial, then point the same UI at your own NexusRAG API deployment for unlimited usage and private operations.',
  },
  {
    icon: Globe2,
    title: 'Real deployment story',
    description:
      'This live deployment already runs across Cloudflare Pages, Render, and Neon pgvector, so the architecture is practical, not theoretical.',
  },
]

export function Features() {
  return (
    <section className="bg-bg-secondary py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight text-text-primary">
            Built for teams that need answers they can actually defend
          </h2>
          <p className="mt-4 text-base leading-7 text-text-secondary">
            NexusRAG is designed to reduce follow-up time after the answer arrives. The product
            keeps evidence, architecture, and operational control close to the query instead of
            hiding them behind a generic chat facade.
          </p>
        </div>
        <div className="mt-14 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="surface p-6 transition-all duration-[var(--duration-normal)] hover:-translate-y-0.5 hover:shadow-md"
            >
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-100 text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
                <feature.icon className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-semibold text-text-primary">{feature.title}</h3>
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
