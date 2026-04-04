import { Braces, Building2, GitBranchPlus, ShieldCheck } from 'lucide-react'

const reasons = [
  {
    title: 'Plug into your product',
    description:
      'Use NexusRAG as infrastructure inside your own app, not as a closed chat tab with no system-level hooks.',
    icon: GitBranchPlus,
  },
  {
    title: 'Control the retrieval path',
    description:
      'Keep hybrid retrieval, reranking, evidence visibility, and answer grounding inside a pipeline you can actually tune.',
    icon: Braces,
  },
  {
    title: 'Ship grounded AI',
    description:
      'Show citations, preserve review context, and abstain when evidence is thin instead of hiding uncertainty behind polished text.',
    icon: ShieldCheck,
  },
]

const audiences = [
  {
    title: 'Builders and developers',
    description:
      'Teams building AI products who need a controllable retrieval engine, not another black-box assistant.',
  },
  {
    title: 'Teams with internal data',
    description:
      'Startups, operations teams, support orgs, and security-minded groups that need private knowledge plugged into real workflows.',
  },
  {
    title: 'Correctness-critical work',
    description:
      'Anyone who cares about evidence, source visibility, ranking quality, and why the answer was chosen.',
  },
]

const comparison = [
  {
    title: 'Black-box assistants',
    points: [
      'Good for casual document chat',
      'Limited control over retrieval and ranking',
      'Hard to integrate at system level',
      'Evidence and reasoning path stay mostly hidden',
    ],
  },
  {
    title: 'NexusRAG engine',
    points: [
      'Built for grounded product workflows',
      'Hybrid retrieval, reranking, and explicit evidence',
      'Bring your own model, data, and rollout plan',
      'Same workspace from hosted evaluation to private deployment',
    ],
  },
]

export function Positioning() {
  return (
    <section id="why-nexusrag" className="bg-bg-primary">
      <div className="mx-auto w-full max-w-[1920px] px-6 lg:px-8 xl:px-10 2xl:px-12">
        {/* Why teams choose NexusRAG */}
        <div className="border-b border-border-subtle/40 py-20">
          <div className="grid gap-12 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)] xl:items-start">
            <div className="space-y-6">
              <p className="text-[0.72rem] font-medium uppercase tracking-[0.26em] text-accent-700">
                Why teams choose NexusRAG
              </p>
              <h2 className="max-w-[720px] text-balance text-[2.6rem] font-semibold leading-[1.08] tracking-[-0.05em] text-text-primary md:text-[3.4rem]">
                Control, transparency, and retrieval quality in one stack
              </h2>
              <p className="max-w-[580px] text-[1.02rem] leading-[1.8] text-text-secondary">
                NexusRAG is for teams that have outgrown generic document chat. It keeps the
                retrieval path visible, lets you plug the system into real products, and gives
                teams a grounded interface they can trust.
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              {reasons.map((item) => (
                <div
                  key={item.title}
                  className="rounded-2xl bg-bg-secondary/60 p-6"
                >
                  <item.icon className="h-5 w-5 text-accent-600" />
                  <h3 className="mt-5 text-[1.24rem] font-semibold leading-[1.12] tracking-[-0.03em] text-text-primary">
                    {item.title}
                  </h3>
                  <p className="mt-3 text-sm leading-7 text-text-secondary">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Who should use it */}
        <div className="border-b border-border-subtle/40 py-20">
          <div className="grid gap-12 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)] xl:items-start">
            <div className="space-y-6">
              <p className="text-[0.72rem] font-medium uppercase tracking-[0.26em] text-accent-700">
                Who should use it
              </p>
              <h3 className="max-w-[640px] text-balance text-[2.4rem] font-semibold leading-[1.08] tracking-[-0.05em] text-text-primary md:text-[3.1rem]">
                For teams that need more than &ldquo;chat with docs&rdquo;
              </h3>
              <p className="max-w-[580px] text-[1.02rem] leading-[1.8] text-text-secondary">
                The strongest fit is teams saying: &ldquo;ChatGPT is not enough for what we
                are building.&rdquo;
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              {audiences.map((item) => (
                <div
                  key={item.title}
                  className="rounded-2xl bg-bg-secondary/60 p-6"
                >
                  <Building2 className="h-5 w-5 text-accent-600" />
                  <h4 className="mt-5 text-[1.18rem] font-semibold leading-[1.12] tracking-[-0.03em] text-text-primary">
                    {item.title}
                  </h4>
                  <p className="mt-3 text-sm leading-7 text-text-secondary">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Why not just use ChatGPT or Claude? */}
        <div className="py-20">
          <div className="grid gap-12 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)] xl:items-start">
            <div className="space-y-6">
              <p className="text-[0.72rem] font-medium uppercase tracking-[0.26em] text-accent-700">
                Why not just use ChatGPT or Claude?
              </p>
              <h3 className="max-w-[560px] text-balance text-[2.4rem] font-semibold leading-[1.1] tracking-[-0.05em] text-text-primary md:text-[2.85rem]">
                Assistants are helpful. Engines are shippable.
              </h3>
              <p className="max-w-[560px] text-[1.02rem] leading-[1.8] text-text-secondary">
                NexusRAG sits between open-source chaos and closed SaaS tools: easier than
                building from scratch, but far more controllable than a black-box assistant.
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              {comparison.map((column) => (
                <div
                  key={column.title}
                  className="rounded-2xl bg-bg-secondary/60 p-6"
                >
                  <h4 className="text-[1.24rem] font-semibold tracking-[-0.03em] text-text-primary">
                    {column.title}
                  </h4>
                  <ul className="mt-5 space-y-3 text-sm leading-7 text-text-secondary">
                    {column.points.map((point) => (
                      <li key={point} className="flex gap-3">
                        <span className="mt-[11px] h-1.5 w-1.5 shrink-0 rounded-full bg-accent-600" />
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
