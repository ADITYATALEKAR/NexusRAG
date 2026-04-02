import Link from 'next/link'

import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'
import { PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'

const accessOptions = [
  {
    title: 'Hosted free evaluation',
    description: `${PUBLIC_TRIAL_QUERY_LIMIT} shared API questions so anyone can validate the live NexusRAG workflow immediately.`,
    href: '/dashboard',
    label: 'Start free',
  },
  {
    title: 'Bring your own API',
    description:
      'Connect your own NexusRAG API endpoint and key for unlimited usage on your own infrastructure.',
    href: '/login',
    label: 'Use your own API',
  },
]

export default function SignupPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="surface w-full max-w-3xl p-8">
        <Logo />
        <div className="mt-8 space-y-4">
          <h1 className="text-2xl font-semibold text-text-primary">
            Choose how you want to use NexusRAG
          </h1>
          <p className="text-sm leading-6 text-text-secondary">
            The live deployment is already available. Start with the hosted evaluation mode for a
            quick proof of value, or connect your own NexusRAG API for unlimited usage and private
            operations.
          </p>
        </div>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {accessOptions.map((option) => (
            <div key={option.title} className="rounded-2xl border border-border-subtle bg-bg-secondary p-5">
              <h2 className="text-lg font-semibold text-text-primary">{option.title}</h2>
              <p className="mt-3 text-sm leading-6 text-text-secondary">{option.description}</p>
              <Button asChild className="mt-5 w-full">
                <Link href={option.href}>{option.label}</Link>
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
