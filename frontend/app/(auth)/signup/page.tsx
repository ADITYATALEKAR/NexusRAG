'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

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
          <h1 className="text-2xl font-semibold text-text-primary">Create workspace</h1>
          <p className="mt-2 text-sm text-text-secondary">Start with API key auth today. OAuth can be layered in later without changing the rest of the interface.</p>
        </div>
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
        <p className="mt-6 text-sm text-text-secondary">
          Already have a workspace? <Link href="/login" className="font-medium text-accent-700">Sign in</Link>
        </p>
      </div>
    </div>
  )
}