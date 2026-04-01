const signals = [
  { label: 'Uptime SLA', value: '99.9%' },
  { label: 'P95 latency', value: '<200ms' },
  { label: 'Grounded answers', value: 'Cited' }
]

export function TrustSignals() {
  return (
    <section className="py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid gap-6 md:grid-cols-3">
          {signals.map((signal) => (
            <div key={signal.label} className="surface-muted p-8 text-center">
              <p className="text-4xl font-semibold tracking-tight text-text-primary">{signal.value}</p>
              <p className="mt-3 text-sm text-text-secondary">{signal.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}