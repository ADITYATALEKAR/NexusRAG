'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useTheme } from 'next-themes'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import {
  DEFAULT_PUBLIC_BACKEND_URL,
  DEPLOYMENT_TARGET,
  PUBLIC_TRIAL_QUERY_LIMIT,
  PUBLIC_APP_ENABLED
} from '@/lib/public-config'
import { useAppStore } from '@/lib/stores/app-store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Shell } from '@/components/layout/shell'

const operatorSchema = z.object({
  apiUrl: z.string().min(1, 'API URL is required'),
  apiKey: z.string().min(3, 'API key is required')
})

const llmSchema = z.object({
  llmKey: z.string().min(3, 'API key is required')
})

type OperatorFormValues = z.infer<typeof operatorSchema>
type LlmFormValues = z.infer<typeof llmSchema>

function maskKey(key: string | null): string {
  if (!key) return ''
  if (key.length <= 8) return '••••••••'
  return key.slice(0, 4) + '••••••••' + key.slice(-4)
}

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const operatorApiUrl = useAppStore((state) => state.operatorApiUrl)
  const llmApiKey = useAppStore((state) => state.llmApiKey)
  const setOperatorConnection = useAppStore((state) => state.setOperatorConnection)
  const setLlmApiKey = useAppStore((state) => state.setLlmApiKey)
  const [saved, setSaved] = useState(false)
  const [llmSaved, setLlmSaved] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<OperatorFormValues>({
    resolver: zodResolver(operatorSchema),
    defaultValues: {
      apiUrl: operatorApiUrl || DEFAULT_PUBLIC_BACKEND_URL,
      apiKey: ''
    }
  })
  const {
    register: registerLlm,
    handleSubmit: handleSubmitLlm,
    reset: resetLlm,
    formState: { errors: llmErrors, isSubmitting: llmIsSubmitting }
  } = useForm<LlmFormValues>({
    resolver: zodResolver(llmSchema),
    defaultValues: {
      llmKey: ''
    }
  })

  const onSubmit = handleSubmit(async (values) => {
    setSaveError(null)
    setSaved(false)
    try {
      setOperatorConnection(values.apiUrl.trim(), values.apiKey.trim())
      reset({ apiUrl: values.apiUrl.trim(), apiKey: '' })
      setSaved(true)
    } catch {
      setSaveError('Unable to update the operator connection.')
    }
  })

  const onSubmitLlm = handleSubmitLlm(async (values) => {
    setLlmSaved(false)
    setLlmApiKey(values.llmKey.trim())
    resetLlm({ llmKey: '' })
    setLlmSaved(true)
  })

  return (
    <Shell className="space-y-6">
      <div>
        <h1 className="section-title">Settings</h1>
        <p className="section-copy">
          Control how this browser connects to NexusRAG, from the hosted evaluation mode to your
          own private API deployment.
        </p>
      </div>

      <section className="surface space-y-5 p-6">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">Appearance</h2>
          <p className="mt-1 text-sm text-text-secondary">Pick the theme used in this browser.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          {['light', 'dark', 'system'].map((option) => (
            <Button
              key={option}
              type="button"
              variant={theme === option ? 'default' : 'subtle'}
              onClick={() => setTheme(option)}
            >
              {option[0].toUpperCase() + option.slice(1)}
            </Button>
          ))}
        </div>
      </section>

      <section className="surface space-y-5 p-6">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">LLM API Key</h2>
          <p className="mt-1 text-sm text-text-secondary">
            Provide your own LLM API key for unlimited queries. Supports OpenAI, Google Gemini,
            Anthropic Claude, DeepSeek, Qwen, and Groq. The key is auto-detected — just paste any
            valid key.
          </p>
        </div>
        {llmApiKey ? (
          <div className="flex items-center gap-3 rounded-xl border border-border-subtle bg-bg-secondary px-4 py-3">
            <span className="text-sm font-medium text-success">Connected</span>
            <code className="text-sm text-text-secondary">{maskKey(llmApiKey)}</code>
            <Button
              type="button"
              variant="subtle"
              className="ml-auto"
              onClick={() => {
                setLlmApiKey(null)
                setLlmSaved(false)
              }}
            >
              Remove
            </Button>
          </div>
        ) : null}
        <form className="space-y-5" onSubmit={onSubmitLlm}>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">API Key</label>
            <Input
              {...registerLlm('llmKey')}
              type="password"
              placeholder="Paste any LLM API key (sk-..., AIzaSy..., gsk_..., etc.)"
            />
            {llmErrors.llmKey ? (
              <p className="text-sm text-error">{llmErrors.llmKey.message}</p>
            ) : null}
          </div>
          <Button type="submit" disabled={llmIsSubmitting}>
            Save API key
          </Button>
        </form>
        {llmSaved ? (
          <p className="text-sm text-success">
            API key saved for this browser session. Your key is auto-detected and will be used for
            all queries.
          </p>
        ) : null}
      </section>

      <section className="surface space-y-5 p-6">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">Bring your own API</h2>
          <p className="mt-1 text-sm text-text-secondary">
            The hosted evaluation mode is {PUBLIC_APP_ENABLED ? 'enabled' : 'disabled'} for this
            build. The public deployment includes {PUBLIC_TRIAL_QUERY_LIMIT} hosted questions. Use
            the fields below if you want unlimited usage on your own NexusRAG API endpoint and key.
          </p>
        </div>
        <form className="space-y-5" onSubmit={onSubmit}>
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
          <div className="flex flex-wrap gap-3">
            <Button type="submit" disabled={isSubmitting}>
              Save API connection
            </Button>
            <Button
              type="button"
              variant="subtle"
              onClick={() => {
                setOperatorConnection(null, null)
                reset({ apiUrl: DEFAULT_PUBLIC_BACKEND_URL, apiKey: '' })
                setSaved(false)
              }}
            >
              Reset to hosted evaluation
            </Button>
          </div>
        </form>
        {saved ? <p className="text-sm text-success">API connection updated for this browser.</p> : null}
        {saveError ? <p className="text-sm text-error">{saveError}</p> : null}
      </section>

      <section className="surface space-y-3 p-6">
        <h2 className="text-lg font-semibold text-text-primary">Deployment target</h2>
        <p className="text-sm text-text-secondary">
          This frontend is configured for <code>{DEPLOYMENT_TARGET}</code>.
        </p>
      </section>
    </Shell>
  )
}
