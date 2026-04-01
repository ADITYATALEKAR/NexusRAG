import Link from 'next/link'

import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'

export default function SignupPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="surface w-full max-w-xl p-8">
        <Logo />
        <div className="mt-8 space-y-4">
          <h1 className="text-2xl font-semibold text-text-primary">Deployment-ready workspace</h1>
          <p className="text-sm text-text-secondary">
            This Cloudflare Pages build does not create accounts in the frontend. For the hosted demo,
            users can enter the workspace directly. If you are operating a protected backend, use the
            operator login flow and provide your own backend URL plus API key.
          </p>
          <div className="rounded-2xl border border-border-subtle bg-bg-secondary p-4 text-sm text-text-secondary">
            For the temporary free-tier stack, the production shape is:
            Cloudflare Pages for the frontend, Koyeb for the FastAPI backend, and Neon pgvector for
            vectors plus metadata.
          </div>
        </div>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <Button asChild className="sm:flex-1">
            <Link href="/dashboard">Open workspace</Link>
          </Button>
          <Button asChild variant="subtle" className="sm:flex-1">
            <Link href="/login">Operator login</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
