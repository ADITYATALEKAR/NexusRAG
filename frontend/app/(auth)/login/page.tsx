'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowRight } from 'lucide-react'
import Link from 'next/link'
import { signIn, useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { DEFAULT_PUBLIC_BACKEND_URL, PUBLIC_APP_ENABLED } from '@/lib/public-config'
import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const schema = z.object({
  apiUrl: z.string().min(1, 'API URL is required'),
  apiKey: z.string().min(3, 'API key is required')
})

type FormValues = z.infer<typeof schema>

export default function LoginPage() {
  const { status } = useSession()
  const router = useRouter()
  const [authError, setAuthError] = useState<string | null>(null)
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      apiUrl: DEFAULT_PUBLIC_BACKEND_URL,
      apiKey: ''
    }
  })

  useEffect(() => {
    if (status === 'authenticated') {
      router.replace('/dashboard')
    }
  }, [router, status])

  const onSubmit = handleSubmit(async (values: FormValues) => {
    setAuthError(null)
    const result = await signIn('credentials', {
      redirect: false,
      apiUrl: values.apiUrl,
      apiKey: values.apiKey
    })
    if (result?.error) {
      setAuthError('Unable to validate the backend URL or API key. Check both values and try again.')
      return
    }
    router.push('/dashboard')
    router.refresh()
  })

  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="surface w-full max-w-md p-8">
        <Logo />
        <div className="mt-8">
          <h1 className="text-2xl font-semibold text-text-primary">Sign in</h1>
          <p className="mt-2 text-sm text-text-secondary">
            {PUBLIC_APP_ENABLED
              ? 'Public access is enabled. Deployment-managed credentials stay on the server, so visitors can enter the workspace without handling API keys.'
              : 'Use operator credentials to connect this workspace to a protected NexusRAG backend.'}
          </p>
        </div>
        {PUBLIC_APP_ENABLED ? (
          <div className="mt-8 space-y-5">
            <div className="rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-4 text-sm text-text-secondary">
              The public app will talk to the backend through secure server-side proxy routes. No end-user API key entry is required.
            </div>
            <Button asChild className="w-full">
              <Link href="/dashboard">
                Enter workspace
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>
        ) : (
          <form className="mt-8 space-y-5" onSubmit={onSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">API URL</label>
              <Input {...register('apiUrl')} placeholder="http://localhost:8000" />
              {errors.apiUrl ? <p className="text-sm text-error">{errors.apiUrl.message}</p> : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">API key</label>
              <Input {...register('apiKey')} type="password" placeholder="rag_live_..." />
              {errors.apiKey ? <p className="text-sm text-error">{errors.apiKey.message}</p> : null}
            </div>
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              Enter workspace
              <ArrowRight className="h-4 w-4" />
            </Button>
            {authError ? <p className="text-sm text-error">{authError}</p> : null}
          </form>
        )}
        <p className="mt-6 text-sm text-text-secondary">
          {PUBLIC_APP_ENABLED ? (
            <>
              Want to self-host?{' '}
              <Link href="/signup" className="font-medium text-accent-700">
                Review deployment setup
              </Link>
            </>
          ) : (
            <>
              New here?{' '}
              <Link href="/signup" className="font-medium text-accent-700">
                Create a workspace
              </Link>
            </>
          )}
        </p>
      </div>
    </div>
  )
}
