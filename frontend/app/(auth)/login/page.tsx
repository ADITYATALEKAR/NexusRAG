'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowRight, ChevronDown, Key, Server } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
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

const operatorSchema = z.object({
  apiUrl: z.string().min(1, 'API URL is required'),
  apiKey: z.string().min(3, 'API key is required')
})

const llmSchema = z.object({
  llmKey: z.string().min(3, 'API key is required')
})

type OperatorFormValues = z.infer<typeof operatorSchema>
type LlmFormValues = z.infer<typeof llmSchema>

function detectProvider(key: string): string {
  if (key.startsWith('AIzaSy')) return 'Google Gemini'
  if (key.startsWith('sk-ant-')) return 'Anthropic Claude'
  if (key.startsWith('gsk_')) return 'Groq'
  if (key.startsWith('dsk-') || key.startsWith('dsk_')) return 'DeepSeek'
  if (key.startsWith('sk-')) return 'OpenAI / DeepSeek'
  return 'Auto-detected'
}

export default function LoginPage() {
  const router = useRouter()
  const setOperatorConnection = useAppStore((state) => state.setOperatorConnection)
  const setLlmApiKey = useAppStore((state) => state.setLlmApiKey)
  const [showOperator, setShowOperator] = useState(false)
  const [llmSaved, setLlmSaved] = useState(false)

  const {
    register: registerOperator,
    handleSubmit: handleSubmitOperator,
    formState: { errors: operatorErrors, isSubmitting: operatorSubmitting }
  } = useForm<OperatorFormValues>({
    resolver: zodResolver(operatorSchema),
    defaultValues: { apiUrl: DEFAULT_PUBLIC_BACKEND_URL, apiKey: '' }
  })

  const {
    register: registerLlm,
    handleSubmit: handleSubmitLlm,
    formState: { errors: llmErrors, isSubmitting: llmSubmitting }
  } = useForm<LlmFormValues>({
    resolver: zodResolver(llmSchema),
    defaultValues: { llmKey: '' }
  })

  const onSubmitOperator = handleSubmitOperator(async (values) => {
    setOperatorConnection(values.apiUrl.trim(), values.apiKey.trim())
    router.push('/dashboard')
  })

  const onSubmitLlm = handleSubmitLlm(async (values) => {
    const key = values.llmKey.trim()
    setLlmApiKey(key)
    setLlmSaved(true)
    setTimeout(() => router.push('/dashboard'), 800)
  })

  if (REQUIRE_OPERATOR_LOGIN) {
    return (
      <div className="flex min-h-screen items-center justify-center px-6 py-12">
        <div className="surface w-full max-w-md p-8">
          <Logo />
          <div className="mt-8">
            <h1 className="text-2xl font-semibold text-text-primary">Connect your NexusRAG API</h1>
            <p className="mt-2 text-sm text-text-secondary">
              Enter a NexusRAG API URL and access key to reach your protected deployment.
            </p>
          </div>
          <form className="mt-8 space-y-5" onSubmit={onSubmitOperator}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">NexusRAG API URL</label>
              <Input {...registerOperator('apiUrl')} placeholder="https://your-nexusrag-api.example.com" />
              {operatorErrors.apiUrl ? <p className="text-sm text-error">{operatorErrors.apiUrl.message}</p> : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Access key</label>
              <Input {...registerOperator('apiKey')} type="password" placeholder="nexusrag_live_..." />
              {operatorErrors.apiKey ? <p className="text-sm text-error">{operatorErrors.apiKey.message}</p> : null}
            </div>
            <Button type="submit" className="w-full" disabled={operatorSubmitting}>
              Connect <ArrowRight className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="surface w-full max-w-md p-8">
        <Logo />

        <div className="mt-8">
          <h1 className="text-2xl font-semibold text-text-primary">Get started with NexusRAG</h1>
          <p className="mt-2 text-sm leading-6 text-text-secondary">
            Try the hosted evaluation for free, or paste your own LLM API key for unlimited queries.
          </p>
        </div>

        {PUBLIC_APP_ENABLED ? (
          <div className="mt-8">
            <Button asChild className="w-full" size="lg">
              <Link href="/dashboard">
                Start free evaluation
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <p className="mt-3 text-center text-sm text-text-tertiary">
              {PUBLIC_TRIAL_QUERY_LIMIT} shared queries included &middot; No account required
            </p>
          </div>
        ) : null}

        <div className="mt-8 rounded-2xl border border-border-subtle bg-bg-secondary p-5">
          <div className="flex items-start gap-3">
            <Key className="mt-0.5 h-5 w-5 flex-shrink-0 text-accent-600" />
            <div>
              <h2 className="font-semibold text-text-primary">Paste your LLM API key</h2>
              <p className="mt-1 text-sm leading-6 text-text-secondary">
                For unlimited queries. Supports OpenAI, Google Gemini, Anthropic Claude, DeepSeek, Qwen, and Groq.
              </p>
            </div>
          </div>
          <form className="mt-4 space-y-3" onSubmit={onSubmitLlm}>
            <Input
              {...registerLlm('llmKey')}
              type="password"
              placeholder="Paste any LLM API key (sk-..., AIzaSy..., gsk_...)"
            />
            {llmErrors.llmKey ? <p className="text-sm text-error">{llmErrors.llmKey.message}</p> : null}
            <Button type="submit" className="w-full" disabled={llmSubmitting}>
              Save & enter workspace <ArrowRight className="h-4 w-4" />
            </Button>
          </form>
          {llmSaved ? (
            <p className="mt-3 text-sm text-success">Key saved. Redirecting to workspace...</p>
          ) : null}
          <p className="mt-3 text-xs text-text-tertiary">
            Your key is stored in this browser only and sent directly to the LLM provider. Never saved on the server.
          </p>
        </div>

        <div className="mt-6">
          <button
            type="button"
            className="flex w-full items-center gap-2 text-sm text-text-tertiary transition-colors hover:text-text-secondary"
            onClick={() => setShowOperator(!showOperator)}
          >
            <Server className="h-3.5 w-3.5" />
            Self-hosted NexusRAG backend
            <ChevronDown className={`ml-auto h-3.5 w-3.5 transition-transform ${showOperator ? 'rotate-180' : ''}`} />
          </button>

          {showOperator ? (
            <form className="mt-4 space-y-4 rounded-xl border border-border-subtle bg-bg-secondary p-4" onSubmit={onSubmitOperator}>
              <p className="text-xs text-text-secondary">
                Connect to your own self-hosted NexusRAG API for private deployments.
              </p>
              <div className="space-y-2">
                <label className="text-sm font-medium text-text-primary">API URL</label>
                <Input {...registerOperator('apiUrl')} placeholder="https://your-nexusrag-api.example.com" />
                {operatorErrors.apiUrl ? <p className="text-sm text-error">{operatorErrors.apiUrl.message}</p> : null}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-text-primary">Access key</label>
                <Input {...registerOperator('apiKey')} type="password" placeholder="nexusrag_live_..." />
                {operatorErrors.apiKey ? <p className="text-sm text-error">{operatorErrors.apiKey.message}</p> : null}
              </div>
              <Button type="submit" variant="subtle" className="w-full" disabled={operatorSubmitting}>
                Save API connection <ArrowRight className="h-4 w-4" />
              </Button>
            </form>
          ) : null}
        </div>
      </div>
    </div>
  )
}
