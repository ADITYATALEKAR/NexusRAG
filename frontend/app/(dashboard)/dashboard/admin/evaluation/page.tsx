'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { Shell } from '@/components/layout/shell'
import { LoadingBlock } from '@/components/shared/loading'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api'

const schema = z.object({ datasetId: z.string().min(2, 'Dataset id is required') })

type FormValues = z.infer<typeof schema>

export default function AdminEvaluationPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { datasetId: 'vectorcore_smoke' }
  })

  const mutation = useMutation({ mutationFn: (datasetId: string) => api.evaluate(datasetId) })

  return (
    <Shell className="space-y-6">
      <div>
        <h1 className="section-title">Evaluation</h1>
        <p className="section-copy">Trigger quiet, repeatable evaluation runs without leaving the dashboard.</p>
      </div>
      <form className="surface space-y-4 p-6" onSubmit={handleSubmit((values: FormValues) => mutation.mutate(values.datasetId))}>
        <div className="space-y-2">
          <label className="text-sm font-medium text-text-primary">Dataset id</label>
          <Input {...register('datasetId')} />
          {errors.datasetId ? <p className="text-sm text-error">{errors.datasetId.message}</p> : null}
        </div>
        <Button type="submit" disabled={mutation.isPending}>Run evaluation</Button>
      </form>
      {mutation.isPending ? <div className="surface p-6"><LoadingBlock rows={4} /></div> : null}
      {mutation.data ? (
        <div className="surface space-y-3 p-6">
          <h2 className="text-lg font-semibold text-text-primary">Last run</h2>
          <p className="text-sm text-text-secondary">Dataset: {mutation.data.dataset_id}</p>
          <p className="text-sm text-text-secondary">Latency: {mutation.data.avg_latency_ms.toFixed(1)}ms</p>
          <p className="text-sm text-text-secondary">Cost: ${mutation.data.total_cost_usd.toFixed(4)}</p>
        </div>
      ) : null}
      {mutation.error instanceof Error ? <p className="text-sm text-error">{mutation.error.message}</p> : null}
    </Shell>
  )
}
