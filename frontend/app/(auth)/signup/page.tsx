'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { PUBLIC_APP_ENABLED } from '@/lib/public-config'
import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const schema = z.object({
  workspace: z.string().min(2, 'Workspace name is required'),
  email: z.string().email('Enter a valid work email')
})

type FormValues = z.infer<typeof schema>

export default function SignupPage() {
  const router = useRouter()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = handleSubmit(async () => {
    router.push('/login')
  })

  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="surface w-full max-w-md p-8">
        <Logo />
        <div className="mt-8">
          <h1 className="text-2xl font-semibold text-text-primary">
            {PUBLIC_APP_ENABLED ? 'Public workspace access' : 'Create workspace'}
          </h1>
          <p className="mt-2 text-sm text-text-secondary">
            {PUBLIC_APP_ENABLED
              ? 'This deployment is configured for public access. Visitors can enter the workspace without supplying backend credentials.'
              : 'Start with operator access today. Public access can be layered in later through deployment-managed service credentials.'}
          </p>
        </div>
        {PUBLIC_APP_ENABLED ? (
          <div className="mt-8 space-y-5">
            <div className="rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-4 text-sm text-text-secondary">
              For Northflank or similar hosting, keep the backend API key in deployment secrets and let the web app proxy requests server-side.
            </div>
            <Button asChild className="w-full">
              <Link href="/dashboard">Open the public workspace</Link>
            </Button>
          </div>
        ) : (
          <form className="mt-8 space-y-5" onSubmit={onSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Workspace name</label>
              <Input {...register('workspace')} placeholder="Acme Research" />
              {errors.workspace ? <p className="text-sm text-error">{errors.workspace.message}</p> : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Work email</label>
              <Input {...register('email')} placeholder="you@company.com" />
              {errors.email ? <p className="text-sm text-error">{errors.email.message}</p> : null}
            </div>
            <Button type="submit" className="w-full" disabled={isSubmitting}>Continue to setup</Button>
          </form>
        )}
        <p className="mt-6 text-sm text-text-secondary">
          Already have a workspace? <Link href="/login" className="font-medium text-accent-700">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
