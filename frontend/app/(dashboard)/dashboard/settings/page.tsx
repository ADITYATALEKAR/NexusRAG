'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useTheme } from 'next-themes'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { DEPLOYMENT_TARGET } from '@/lib/public-config'
import { useAppStore } from '@/lib/stores/app-store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Shell } from '@/components/layout/shell'

const llmSchema = z.object({
  llmKey: z.string().min(3, 'API key is required')
})

type LlmFormValues = z.infer<typeof llmSchema>

function maskKey(key: string | null): string {
  if (!key) return ''
  if (key.length <= 8) return '••••••••'
  return key.slice(0, 4) + '••••••••' + key.slice(-4)
}

function detectProvider(key: string): string {
  if (key.startsWith('AIzaSy')) return 'Google Gemini'
  if (key.startsWith('sk-ant-')) return 'Anthropic Claude'
  if (key.startsWith('gsk_')) return 'Groq'
  if (key.startsWith('dsk-') || key.startsWith('dsk_')) return 'DeepSeek'
  if (key.startsWith('sk-')) return 'OpenAI / DeepSeek'
  return 'Auto-detected'
}

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const llmApiKey = useAppStore((state) => state.llmApiKey)
  const setLlmApiKey = useAppStore((state) => state.setLlmApiKey)
  const [llmSaved, setLlmSaved] = useState(false)
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
          Customize your NexusRAG experience — theme, API key, and deployment info.
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
          <div className="rounded-xl border border-success/30 bg-success/5 px-5 py-4">
            <div className="flex items-center justify-between gap-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="inline-block h-2 w-2 rounded-full bg-success" />
                  <span className="text-sm font-semibold text-text-primary">Connected</span>
                  <span className="rounded-md bg-bg-tertiary px-2 py-0.5 text-xs font-medium text-text-secondary">
                    {detectProvider(llmApiKey)}
                  </span>
                </div>
                <code className="text-sm text-text-secondary">{maskKey(llmApiKey)}</code>
              </div>
              <Button
                type="button"
                variant="subtle"
                onClick={() => {
                  setLlmApiKey(null)
                  setLlmSaved(false)
                }}
              >
                Remove
              </Button>
            </div>
            <p className="mt-3 text-xs text-text-tertiary">
              Your key is stored in this browser only and sent directly to the LLM provider. It is
              never saved on the server.
            </p>
          </div>
        ) : null}
        <form className="space-y-4" onSubmit={onSubmitLlm}>
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
            API key saved. You now have unlimited queries using your own key.
          </p>
        ) : null}
      </section>

      <section className="surface space-y-3 p-6">
        <h2 className="text-lg font-semibold text-text-primary">About</h2>
        <div className="space-y-2 text-sm text-text-secondary">
          <p>
            Deployment target: <code className="text-text-primary">{DEPLOYMENT_TARGET}</code>
          </p>
          <p>
            NexusRAG is an enterprise-grade RAG system with multi-provider LLM failover,
            citation-grounded answers, and document intelligence.
          </p>
        </div>
      </section>
    </Shell>
  )
}
