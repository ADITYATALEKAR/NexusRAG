import { Shell } from '@/components/layout/shell'

const datasets = [
  { name: 'nexusrag_smoke', rows: 12, updated: 'Today' },
  { name: 'enterprise_finance_eval', rows: 84, updated: 'Yesterday' },
  { name: 'retrieval_regression_core', rows: 36, updated: '2 days ago' }
]

export default function AdminDatasetsPage() {
  return (
    <Shell className="space-y-6">
      <div>
        <h1 className="section-title">Datasets</h1>
        <p className="section-copy">Golden sets and benchmark corpora available to the evaluation workflow.</p>
      </div>
      <div className="surface overflow-hidden">
        <table className="w-full border-collapse text-sm">
          <thead className="bg-bg-secondary text-left text-text-tertiary">
            <tr>
              <th className="px-4 py-3 font-medium">Dataset</th>
              <th className="px-4 py-3 font-medium">Rows</th>
              <th className="px-4 py-3 font-medium">Updated</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map((dataset) => (
              <tr key={dataset.name} className="border-t border-border-subtle text-text-primary">
                <td className="px-4 py-3">{dataset.name}</td>
                <td className="px-4 py-3">{dataset.rows}</td>
                <td className="px-4 py-3 text-text-secondary">{dataset.updated}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Shell>
  )
}