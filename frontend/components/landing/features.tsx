import { BarChart3, Code2, FileText, Globe2, Shield, Zap } from 'lucide-react'

const features = [
  { icon: FileText, title: 'Multi-format ingestion', description: 'PDF, DOCX, Markdown, HTML. Upload once, query forever.' },
  { icon: Zap, title: 'Sub-second retrieval', description: 'Hybrid search that combines semantic depth with lexical precision.' },
  { icon: Shield, title: 'Citation-backed answers', description: 'Every claim points to source evidence, so teams can trust what they read.' },
  { icon: BarChart3, title: 'Built-in evaluation', description: 'Latency, cost, retrieval quality, and regressions all in one quiet dashboard.' },
  { icon: Code2, title: 'Developer-first', description: 'REST API, CLI, SDK, and proxy routes for secure, same-origin deployments.' },
  { icon: Globe2, title: 'Deploy anywhere', description: 'Cloud, on-prem, or hybrid. Keep your data where your compliance needs it.' }
]

export function Features() {
  return (
    <section className="bg-bg-secondary py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight text-text-primary">Everything you need, nothing you do not</h2>
          <p className="mt-4 text-base leading-7 text-text-secondary">Quiet power for real teams: production-grade search, transparent answers, and operational visibility without the visual noise.</p>
        </div>
        <div className="mt-14 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {features.map((feature) => (
            <div key={feature.title} className="surface p-6 transition-all duration-[var(--duration-normal)] hover:-translate-y-0.5 hover:shadow-md">
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-100 text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
                <feature.icon className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-semibold text-text-primary">{feature.title}</h3>
              <p className="mt-3 text-sm leading-6 text-text-secondary">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}