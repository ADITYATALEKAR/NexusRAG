'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import type { AuthChangeEvent, Session as SupabaseSession } from '@supabase/supabase-js'
import { ArrowRight } from 'lucide-react'
import Link from 'next/link'
import { signIn, useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import {
  DEFAULT_PUBLIC_BACKEND_URL,
  PUBLIC_APP_ENABLED,
  SUPABASE_AUTH_ENABLED
} from '@/lib/public-config'
import { getSupabaseBrowserClient } from '@/lib/supabase/browser'
import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const credentialsSchema = z.object({
  apiUrl: z.string().min(1, 'API URL is required'),
  apiKey: z.string().min(3, 'API key is required')
})

const supabaseSchema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters')
})

type CredentialsFormValues = z.infer<typeof credentialsSchema>
type SupabaseFormValues = z.infer<typeof supabaseSchema>

export default function LoginPage() {
  const { status } = useSession()
  const router = useRouter()
  const [authError, setAuthError] = useState<string | null>(null)
  const [infoMessage, setInfoMessage] = useState<string | null>(null)

  const credentialsForm = useForm<CredentialsFormValues>({
    resolver: zodResolver(credentialsSchema),
    defaultValues: {
      apiUrl: DEFAULT_PUBLIC_BACKEND_URL,
      apiKey: ''
    }
  })

  const supabaseForm = useForm<SupabaseFormValues>({
    resolver: zodResolver(supabaseSchema),
    defaultValues: {
      email: '',
      password: ''
    }
  })

  useEffect(() => {
    if (!SUPABASE_AUTH_ENABLED && status === 'authenticated') {
      router.replace('/dashboard')
    }
  }, [router, status])

  useEffect(() => {
    if (!SUPABASE_AUTH_ENABLED) {
      return
    }

    const supabase = getSupabaseBrowserClient()

    const syncSession = async () => {
      const result = await supabase.auth.getUser()
      if (result.data.user) {
        router.replace('/dashboard')
      }
    }

    void syncSession()

    const {
      data: { subscription }
    } = supabase.auth.onAuthStateChange(
      (_event: AuthChangeEvent, session: SupabaseSession | null) => {
        if (session?.user) {
          router.replace('/dashboard')
        }
      }
    )

    return () => subscription.unsubscribe()
  }, [router])

  const onCredentialsSubmit = credentialsForm.handleSubmit(async (values) => {
    setAuthError(null)
    setInfoMessage(null)
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

  const onSupabaseSubmit = supabaseForm.handleSubmit(async (values) => {
    setAuthError(null)
    setInfoMessage(null)
    const supabase = getSupabaseBrowserClient()
    const { error } = await supabase.auth.signInWithPassword({
      email: values.email,
      password: values.password
    })

    if (error) {
      setAuthError(error.message)
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
            {SUPABASE_AUTH_ENABLED
              ? 'Sign in with your Supabase-backed account. Secrets stay on the server, and the Vercel app only uses browser-safe keys.'
              : PUBLIC_APP_ENABLED
                ? 'Public access is enabled. Deployment-managed credentials stay on the server, so visitors can enter the workspace without handling API keys.'
                : 'Use operator credentials to connect this workspace to a protected NexusRAG backend.'}
          </p>
        </div>
        {SUPABASE_AUTH_ENABLED ? (
          <form className="mt-8 space-y-5" onSubmit={onSupabaseSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Email</label>
              <Input {...supabaseForm.register('email')} type="email" placeholder="you@example.com" />
              {supabaseForm.formState.errors.email ? (
                <p className="text-sm text-error">{supabaseForm.formState.errors.email.message}</p>
              ) : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Password</label>
              <Input {...supabaseForm.register('password')} type="password" placeholder="At least 8 characters" />
              {supabaseForm.formState.errors.password ? (
                <p className="text-sm text-error">{supabaseForm.formState.errors.password.message}</p>
              ) : null}
            </div>
            <Button type="submit" className="w-full" disabled={supabaseForm.formState.isSubmitting}>
              Enter workspace
              <ArrowRight className="h-4 w-4" />
            </Button>
          </form>
        ) : PUBLIC_APP_ENABLED ? (
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
          <form className="mt-8 space-y-5" onSubmit={onCredentialsSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">API URL</label>
              <Input {...credentialsForm.register('apiUrl')} placeholder="http://localhost:8000" />
              {credentialsForm.formState.errors.apiUrl ? <p className="text-sm text-error">{credentialsForm.formState.errors.apiUrl.message}</p> : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">API key</label>
              <Input {...credentialsForm.register('apiKey')} type="password" placeholder="rag_live_..." />
              {credentialsForm.formState.errors.apiKey ? <p className="text-sm text-error">{credentialsForm.formState.errors.apiKey.message}</p> : null}
            </div>
            <Button type="submit" className="w-full" disabled={credentialsForm.formState.isSubmitting}>
              Enter workspace
              <ArrowRight className="h-4 w-4" />
            </Button>
          </form>
        )}
        {authError ? <p className="mt-4 text-sm text-error">{authError}</p> : null}
        {infoMessage ? <p className="mt-4 text-sm text-success">{infoMessage}</p> : null}
        <p className="mt-6 text-sm text-text-secondary">
          {SUPABASE_AUTH_ENABLED ? (
            <>
              Need an account?{' '}
              <Link href="/signup" className="font-medium text-accent-700">
                Create one
              </Link>
            </>
          ) : PUBLIC_APP_ENABLED ? (
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
