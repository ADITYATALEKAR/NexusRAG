const howItWorks = [
  {
    step: '01',
    title: 'Upload the source material',
    description:
      'Bring PDFs, DOCX files, Markdown, TXT, HTML, CSV, or JSON into one retrieval layer built for repeated enterprise use, not disposable prompting.',
  },
  {
    step: '02',
    title: 'Ask a focused question',
    description:
      'Dense vectors and BM25 work in the same retrieval loop so semantic intent, product names, policy wording, and clause language stay visible together.',
  },
  {
    step: '03',
    title: 'Review the supporting evidence',
    description:
      'NexusRAG returns a readable answer, cited passages, source names, and the evidence context that explains why that answer was chosen.',
  },
]

const decisionSignals = [
  'Hosted mode is designed for quick product evaluation, not throwaway demo copy.',
  'Bring Your Own API keeps the same UI while moving data control and limits into your environment.',
  'The answer surface stays quiet so legal, support, and operations teams can review without interface clutter.',
]

export function Features() {
  return (
    <section id="how-it-works" className="border-b border-border-subtle/70 bg-bg-secondary/34 py-24">
      <div className="mx-auto w-full max-w-[1920px] px-6 lg:px-10 xl:px-12 2xl:px-16">
        <div className="grid gap-10 xl:grid-cols-[minmax(320px,0.72fr)_minmax(0,1.28fr)] xl:items-start">
          <div className="space-y-6">
            <p className="text-sm font-medium uppercase tracking-[0.24em] text-accent-700">
              How it works
            </p>
            <h2 className="max-w-lg text-3xl font-semibold tracking-[-0.055em] text-text-primary md:text-[3.2rem]">
              From private files to cited answers in one clean workflow
            </h2>
            <p className="max-w-xl text-base leading-8 text-text-secondary">
              The first experience should feel immediate and credible. Upload the source material,
              ask a precise question, inspect the cited evidence, and decide whether to stay on the
              hosted path or move into your own deployment.
            </p>

            <div className="surface space-y-4 p-6">
              <p className="text-[0.78rem] font-medium uppercase tracking-[0.24em] text-accent-700">
                Why this flow converts
              </p>
              <div className="space-y-3 text-sm leading-7 text-text-secondary">
                {decisionSignals.map((signal) => (
                  <p key={signal}>{signal}</p>
                ))}
              </div>
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            {howItWorks.map((item) => (
              <div key={item.step} className="surface min-h-[276px] p-7">
                <div className="text-[0.8rem] font-medium uppercase tracking-[0.24em] text-accent-700">
                  {item.step}
                </div>
                <h3 className="mt-4 text-[1.54rem] font-semibold tracking-[-0.05em] text-text-primary">
                  {item.title}
                </h3>
                <p className="mt-4 text-sm leading-7 text-text-secondary">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
