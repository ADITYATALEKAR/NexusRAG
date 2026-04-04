const howItWorks = [
  {
    step: '01',
    title: 'Upload the source material',
    description:
      'Bring PDFs, DOCX files, Markdown, TXT, HTML, CSV, or JSON into one retrieval layer designed for repeated operational use.',
  },
  {
    step: '02',
    title: 'Ask a focused question',
    description:
      'Dense vectors and BM25 stay in the same loop so semantic intent and exact language survive retrieval together.',
  },
  {
    step: '03',
    title: 'Review the evidence',
    description:
      'NexusRAG returns a readable answer, cited passages, source names, and the evidence context that explains why it was chosen.',
  },
]

export function Features() {
  return (
    <section id="how-it-works" className="bg-bg-primary py-20">
      <div className="mx-auto w-full max-w-[1920px] px-6 lg:px-8 xl:px-10 2xl:px-12">
        <div className="grid gap-10 xl:grid-cols-2 xl:items-start">
          <div className="space-y-6">
            <p className="text-sm font-medium uppercase tracking-[0.24em] text-accent-700">
              How it works
            </p>
            <h2 className="max-w-[760px] text-balance text-[2.95rem] font-semibold leading-[1.08] tracking-[-0.06em] text-text-primary md:text-[3.7rem]">
              From private files to cited answers in one clean workflow
            </h2>
            <p className="max-w-[700px] text-base leading-8 text-text-secondary">
              Upload the source material, ask a precise question, inspect the cited evidence, and
              decide whether the product fits your team before any rollout effort.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {howItWorks.map((item) => (
              <div key={item.step} className="surface min-h-[278px] p-7">
                <div className="text-[0.8rem] font-medium uppercase tracking-[0.24em] text-accent-700">
                  {item.step}
                </div>
                <h3 className="mt-4 max-w-[240px] text-[1.56rem] font-semibold leading-[1.08] tracking-[-0.05em] text-text-primary">
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
