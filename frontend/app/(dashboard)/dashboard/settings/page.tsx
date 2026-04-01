'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { signIn, useSession } from 'next-auth/react'
import { useTheme } from 'next-themes'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { DEFAULT_PUBLIC_BACKEND_URL, PUBLIC_APP_ENABLED } from '@/lib/public-config'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Shell } from '@/components/layout/shell'

const schema = z.object({
  apiUrl: z.string().min(1, 'API URL is required'),
  apiKey: z.string().min(3, 'API key is required')
})

type FormValues = z.infer<typeof schema>

export default function SettingsPage() {
  const router = useRouter()
  const { data: session } = useSession()
  const { theme, setTheme } = useTheme()
  const [saveError, setSaveError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)
  const { register, handleSubmit, reset, formState: { errors, isSubmitting, isSubmitSuccessful } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      apiUrl: session?.apiUrl || DEFAULT_PUBLIC_BACKEND_URL,
      apiKey: ''
    }
  })

  useEffect(() => {
    reset({
      apiUrl: session?.apiUrl || DEFAULT_PUBLIC_BACKEND_URL,
      apiKey: ''
    })
  }, [reset, session?.apiUrl])

  const onSubmit = handleSubmit(async (values: FormValues) => {
    setSaveError(null)
    setSaved(false)
    const result = await signIn('credentials', {
      redirect: false,
      apiUrl: values.apiUrl,
      apiKey: values.apiKey
    })
    if (result?.error) {
      setSaveError('Connection update failed. Re-enter a valid API URL and API key.')
      return
    }
    reset({
      apiUrl: values.apiUrl,
      apiKey: ''
    })
    setSaved(true)
    router.refresh()
  })

  return (
    <Shell className="space-y-6">
      <div>
        <h1 className="section-title">Settings</h1>
        <p className="section-copy">Tune API connectivity, auth, and workspace presentation.</p>
      </div>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,520px)_minmax(0,1fr)]">
        {PUBLIC_APP_ENABLED ? (
          <div className="surface space-y-5 p-6">
            <div>
              <h2 className="text-lg font-semibold text-text-primary">Connection</h2>
              <p className="mt-1 text-sm text-text-secondary">
                This deployment is in public mode. Backend connectivity and credentials are managed on the server by your deployment platform.
              </p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Backend URL</label>
              <Input value={session?.apiUrl || DEFAULT_PUBLIC_BACKEND_URL} readOnly />
            </div>
            <div className="rounded-2xl border border-border-subtle bg-bg-secondary px-4 py-4 text-sm text-text-secondary">
              To rotate credentials, update the deployment secret such as <code>BACKEND_SERVICE_API_KEY</code> rather than asking users to re-enter an API key in the browser.
            </div>
          </div>
        ) : (
          <form className="surface space-y-5 p-6" onSubmit={onSubmit}>
            <div>
              <h2 className="text-lg font-semibold text-text-primary">Connection</h2>
              <p className="mt-1 text-sm text-text-secondary">Point the frontend to your NexusRAG backend and refresh the session-bound API key when you want to rotate credentials.</p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">API URL</label>
              <Input {...register('apiUrl')} />
              {errors.apiUrl ? <p className="text-sm text-error">{errors.apiUrl.message}</p> : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">API key</label>
              <Input {...register('apiKey')} type="password" placeholder="Re-enter to update the active session" />
              {errors.apiKey ? <p className="text-sm text-error">{errors.apiKey.message}</p> : null}
            </div>
            <Button type="submit" disabled={isSubmitting}>Save settings</Button>
            {saved || isSubmitSuccessful ? <p className="text-sm text-success">Session updated. New requests will use the refreshed backend connection immediately.</p> : null}
            {saveError ? <p className="text-sm text-error">{saveError}</p> : null}
          </form>
        )}
        <div className="surface space-y-5 p-6">
          <div>
            <h2 className="text-lg font-semibold text-text-primary">Appearance</h2>
            <p className="mt-1 text-sm text-text-secondary">Toggle the calm light and dark themes with the same design tokens.</p>
          </div>
          <div className="flex gap-3">
            <Button variant={theme === 'light' ? 'default' : 'outline'} onClick={() => setTheme('light')}>Light</Button>
            <Button variant={theme === 'dark' ? 'default' : 'outline'} onClick={() => setTheme('dark')}>Dark</Button>
            <Button variant={theme === 'system' ? 'default' : 'outline'} onClick={() => setTheme('system')}>System</Button>
          </div>
        </div>
      </div>
    </Shell>
  )
}
