'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { PUBLIC_APP_ENABLED, SUPABASE_AUTH_ENABLED } from '@/lib/public-config'
import { getSupabaseBrowserClient } from '@/lib/supabase/browser'
import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const operatorSchema = z.object({
  workspace: z.string().min(2, 'Workspace name is required'),
  email: z.string().email('Enter a valid work email')
})

const supabaseSchema = z.object({
  workspace: z.string().min(2, 'Display name is required'),
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters')
})

type OperatorValues = z.infer<typeof operatorSchema>
type SupabaseValues = z.infer<typeof supabaseSchema>

export default function SignupPage() {
  const router = useRouter()
  const [message, setMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const operatorForm = useForm<OperatorValues>({
    resolver: zodResolver(operatorSchema)
  })

  const supabaseForm = useForm<SupabaseValues>({
    resolver: zodResolver(supabaseSchema),
    defaultValues: {
      workspace: '',
      email: '',
      password: ''
    }
  })

  const onOperatorSubmit = operatorForm.handleSubmit(async () => {
    router.push('/login')
  })

  const onSupabaseSubmit = supabaseForm.handleSubmit(async (values) => {
    setMessage(null)
    setErrorMessage(null)
    const supabase = getSupabaseBrowserClient()
    const redirectTo = typeof window !== 'undefined' ? `${window.location.origin}/dashboard` : undefined
    const { error } = await supabase.auth.signUp({
      email: values.email,
      password: values.password,
      options: {
        data: {
          display_name: values.workspace
        },
        emailRedirectTo: redirectTo
      }
    })

    if (error) {
      setErrorMessage(error.message)
      return
    }

    setMessage('Account created. If email confirmation is enabled in Supabase, check your inbox before signing in.')
    router.push('/login')
    router.refresh()
  })

  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="surface w-full max-w-md p-8">
        <Logo />
        <div className="mt-8">
          <h1 className="text-2xl font-semibold text-text-primary">
            {SUPABASE_AUTH_ENABLED ? 'Create your account' : PUBLIC_APP_ENABLED ? 'Public workspace access' : 'Create workspace'}
          </h1>
          <p className="mt-2 text-sm text-text-secondary">
            {SUPABASE_AUTH_ENABLED
              ? 'Supabase Auth will manage users for this Vercel deployment. Browser-safe keys stay in the client, while service-role access remains server-only.'
              : PUBLIC_APP_ENABLED
                ? 'This deployment is configured for public access. Visitors can enter the workspace without supplying backend credentials.'
                : 'Start with operator access today. Public access can be layered in later through deployment-managed service credentials.'}
          </p>
        </div>
        {SUPABASE_AUTH_ENABLED ? (
          <form className="mt-8 space-y-5" onSubmit={onSupabaseSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Display name</label>
              <Input {...supabaseForm.register('workspace')} placeholder="Aditya" />
              {supabaseForm.formState.errors.workspace ? <p className="text-sm text-error">{supabaseForm.formState.errors.workspace.message}</p> : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Email</label>
              <Input {...supabaseForm.register('email')} type="email" placeholder="you@example.com" />
              {supabaseForm.formState.errors.email ? <p className="text-sm text-error">{supabaseForm.formState.errors.email.message}</p> : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Password</label>
              <Input {...supabaseForm.register('password')} type="password" placeholder="At least 8 characters" />
              {supabaseForm.formState.errors.password ? <p className="text-sm text-error">{supabaseForm.formState.errors.password.message}</p> : null}
            </div>
            <Button type="submit" className="w-full" disabled={supabaseForm.formState.isSubmitting}>Create account</Button>
          </form>
        ) : PUBLIC_APP_ENABLED ? (
          <div className="mt-8 space-y-5">
            <div className="rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-4 text-sm text-text-secondary">
              For Vercel + Supabase, let the web app use Supabase Auth and server-managed deployment secrets rather than asking users for backend API keys.
            </div>
            <Button asChild className="w-full">
              <Link href="/dashboard">Open the public workspace</Link>
            </Button>
          </div>
        ) : (
          <form className="mt-8 space-y-5" onSubmit={onOperatorSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Workspace name</label>
              <Input {...operatorForm.register('workspace')} placeholder="Acme Research" />
              {operatorForm.formState.errors.workspace ? <p className="text-sm text-error">{operatorForm.formState.errors.workspace.message}</p> : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Work email</label>
              <Input {...operatorForm.register('email')} placeholder="you@company.com" />
              {operatorForm.formState.errors.email ? <p className="text-sm text-error">{operatorForm.formState.errors.email.message}</p> : null}
            </div>
            <Button type="submit" className="w-full" disabled={operatorForm.formState.isSubmitting}>Continue to setup</Button>
          </form>
        )}
        {message ? <p className="mt-4 text-sm text-success">{message}</p> : null}
        {errorMessage ? <p className="mt-4 text-sm text-error">{errorMessage}</p> : null}
        <p className="mt-6 text-sm text-text-secondary">
          Already have a workspace? <Link href="/login" className="font-medium text-accent-700">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
