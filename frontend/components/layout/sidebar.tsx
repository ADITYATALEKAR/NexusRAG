'use client'

import { FileText, Home, LogOut, Search, Settings, X } from 'lucide-react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect } from 'react'

import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'
import { PUBLIC_APP_ENABLED, PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'
import { useAppStore } from '@/lib/stores/app-store'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/dashboard', icon: Search, label: 'Query' },
  { href: '/dashboard/documents', icon: FileText, label: 'Documents' },
  { href: '/dashboard/analytics', icon: Home, label: 'Analytics' },
  { href: '/dashboard/settings', icon: Settings, label: 'Settings' }
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const mobileSidebarOpen = useAppStore((state) => state.mobileSidebarOpen)
  const operatorApiKey = useAppStore((state) => state.operatorApiKey)
  const publicTrialUsage = useAppStore((state) => state.publicTrialUsage)
  const clearWorkspace = useAppStore((state) => state.clearWorkspace)
  const setMobileSidebarOpen = useAppStore((state) => state.setMobileSidebarOpen)
  const usingOwnApi = Boolean(operatorApiKey)
  const trialRemaining = Math.max(PUBLIC_TRIAL_QUERY_LIMIT - publicTrialUsage, 0)

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setMobileSidebarOpen(false)
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [setMobileSidebarOpen])

  return (
    <>
      <div
        className={cn('fixed inset-0 z-30 bg-slate-950/40 transition-opacity md:hidden', mobileSidebarOpen ? 'opacity-100' : 'pointer-events-none opacity-0')}
        onClick={() => setMobileSidebarOpen(false)}
      />
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-border-subtle bg-bg-secondary transition-transform md:static md:w-64 md:translate-x-0',
          mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-16 items-center justify-between border-b border-border-subtle px-6">
          <Logo />
          <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setMobileSidebarOpen(false)} aria-label="Close navigation">
            <X className="h-4 w-4" />
          </Button>
        </div>

        <nav className="flex-1 space-y-6 overflow-y-auto p-4">
          <div className="space-y-1">
            {navItems.map((item) => (
              <NavLink key={item.href} href={item.href} icon={item.icon} label={item.label} active={pathname === item.href} onClick={() => setMobileSidebarOpen(false)} />
            ))}
          </div>
        </nav>

        <div className="border-t border-border-subtle p-4">
          {PUBLIC_APP_ENABLED ? (
            <div className="rounded-lg bg-bg-tertiary px-3 py-3 text-sm text-text-secondary">
              {usingOwnApi ? (
                <>
                  <p className="font-medium text-text-primary">Bring Your Own API</p>
                  <p className="mt-1">
                    This browser is connected to your own NexusRAG API and is not using the hosted
                    trial limit.
                  </p>
                </>
              ) : (
                <>
                  <p className="font-medium text-text-primary">Hosted evaluation</p>
                  <p className="mt-1">
                    {trialRemaining} of {PUBLIC_TRIAL_QUERY_LIMIT} shared API questions remaining in
                    this browser.
                  </p>
                </>
              )}
            </div>
          ) : (
            <button
              type="button"
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm text-text-secondary transition-colors hover:bg-bg-tertiary hover:text-text-primary"
              onClick={() => {
                clearWorkspace()
                router.push('/login')
              }}
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          )}
        </div>
      </aside>
    </>
  )
}

function NavLink({ href, icon: Icon, label, active, onClick }: { href: string; icon: typeof Search; label: string; active: boolean; onClick: () => void }) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={cn(
        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
        active
          ? 'bg-accent-100 text-accent-700 dark:bg-accent-500/15 dark:text-accent-100'
          : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
      )}
    >
      <Icon className="h-4 w-4" />
      {label}
    </Link>
  )
}
