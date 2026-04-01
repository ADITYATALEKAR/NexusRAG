'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useTheme } from 'next-themes'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import {
  DEFAULT_PUBLIC_BACKEND_URL,
  DEPLOYMENT_TARGET,
  PUBLIC_APP_ENABLED
} from '@/lib/public-config'
import { useAppStore } from '@/lib/stores/app-store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Shell } from '@/components/layout/shell'

const schema = z.object({
  apiUrl: z.string().min(1, 'API URL is required'),
  apiKey: z.string().min(3, 'API key is required')
})

type FormValues = z.infer<typeof schema>

export default function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const operatorApiUrl = useAppStore((state) => state.operatorApiUrl)
  const setOperatorConnection = useAppStore((state) => state.setOperatorConnection)
  const [saved, setSaved] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      apiUrl: operatorApiUrl || DEFAULT_PUBLIC_BACKEND_URL,
      apiKey: ''
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

  return (
    <Shell className="space-y-6">
      <div>
        <h1 className="section-title">Settings</h1>
        <p className="section-copy">Tune theme and optional operator connectivity for this temporary deployment.</p>
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
          <h2 className="text-lg font-semibold text-text-primary">Operator backend</h2>
          <p className="mt-1 text-sm text-text-secondary">
            Public demo mode is {PUBLIC_APP_ENABLED ? 'enabled' : 'disabled'} for this build. Use the fields below only if you want to point the app at a protected backend with your own API key.
          </p>
        </div>
        <form className="space-y-5" onSubmit={onSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">API URL</label>
            <Input {...register('apiUrl')} placeholder="https://your-koyeb-service.koyeb.app" />
            {errors.apiUrl ? <p className="text-sm text-error">{errors.apiUrl.message}</p> : null}
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">API key</label>
            <Input {...register('apiKey')} type="password" placeholder="rag_live_..." />
            {errors.apiKey ? <p className="text-sm text-error">{errors.apiKey.message}</p> : null}
          </div>
          <div className="flex flex-wrap gap-3">
            <Button type="submit" disabled={isSubmitting}>
              Save operator connection
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
              Reset to public demo
            </Button>
          </div>
        </form>
        {saved ? <p className="text-sm text-success">Operator connection updated for this browser.</p> : null}
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
