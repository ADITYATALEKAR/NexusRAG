'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowRight } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import {
  DEFAULT_PUBLIC_BACKEND_URL,
  PUBLIC_APP_ENABLED,
  PUBLIC_TRIAL_QUERY_LIMIT,
  REQUIRE_OPERATOR_LOGIN
} from '@/lib/public-config'
import { useAppStore } from '@/lib/stores/app-store'
import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const schema = z.object({
  apiUrl: z.string().min(1, 'API URL is required'),
  apiKey: z.string().min(3, 'API key is required')
})

type FormValues = z.infer<typeof schema>

export default function LoginPage() {
  const router = useRouter()
  const setOperatorConnection = useAppStore((state) => state.setOperatorConnection)
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      apiUrl: DEFAULT_PUBLIC_BACKEND_URL,
      apiKey: ''
    }
  })

  const onSubmit = handleSubmit(async (values) => {
    setOperatorConnection(values.apiUrl.trim(), values.apiKey.trim())
    router.push('/dashboard')
  })

  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="surface w-full max-w-md p-8">
        <Logo />
        <div className="mt-8">
          <h1 className="text-2xl font-semibold text-text-primary">
            {REQUIRE_OPERATOR_LOGIN ? 'Connect your NexusRAG API' : 'Bring your own API'}
          </h1>
          <p className="mt-2 text-sm text-text-secondary">
            {REQUIRE_OPERATOR_LOGIN
              ? 'Enter a NexusRAG API URL and access key to reach your protected deployment.'
              : 'The hosted deployment is already live. Use this screen only if you want unlimited usage through your own NexusRAG API endpoint and key.'}
          </p>
        </div>

        {!REQUIRE_OPERATOR_LOGIN && PUBLIC_APP_ENABLED ? (
          <div className="mt-8 space-y-5">
            <div className="rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-4 text-sm text-text-secondary">
              Hosted evaluation is enabled. No browser secret is required for the public deployment,
              and the shared API includes {PUBLIC_TRIAL_QUERY_LIMIT} questions for evaluation.
            </div>
            <Button asChild className="w-full">
              <Link href="/dashboard">
                Start free
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>
        ) : null}

        <form className="mt-8 space-y-5" onSubmit={onSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">NexusRAG API URL</label>
            <Input {...register('apiUrl')} placeholder="https://your-nexusrag-api.example.com" />
            {errors.apiUrl ? <p className="text-sm text-error">{errors.apiUrl.message}</p> : null}
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">Access key</label>
            <Input {...register('apiKey')} type="password" placeholder="nexusrag_live_..." />
            {errors.apiKey ? <p className="text-sm text-error">{errors.apiKey.message}</p> : null}
          </div>
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            Save API connection
            <ArrowRight className="h-4 w-4" />
          </Button>
        </form>

        <p className="mt-6 text-sm text-text-secondary">
          Want the hosted evaluation instead?{' '}
          <Link href="/dashboard" className="font-medium text-accent-700">
            Go straight to the workspace
          </Link>
        </p>
      </div>
    </div>
  )
}
