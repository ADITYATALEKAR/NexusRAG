'use client'

import {
  FileText,
  LayoutPanelLeft,
  LayoutPanelTop,
  LogOut,
  Moon,
  Search,
  Settings,
  Sun,
  X,
} from 'lucide-react'
import { useTheme } from 'next-themes'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect } from 'react'

import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'
import { useScrollActivity } from '@/lib/hooks/use-scroll-activity'
import { PUBLIC_APP_ENABLED, PUBLIC_TRIAL_QUERY_LIMIT } from '@/lib/public-config'
import { useAppStore } from '@/lib/stores/app-store'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/dashboard', icon: Search, label: 'Query' },
  { href: '/dashboard/documents', icon: FileText, label: 'Documents' },
  { href: '/dashboard/analytics', icon: LayoutPanelTop, label: 'Analytics' },
  { href: '/dashboard/settings', icon: Settings, label: 'Settings' },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { theme, setTheme } = useTheme()
  const mobileSidebarOpen = useAppStore((state) => state.mobileSidebarOpen)
  const desktopSidebarCollapsed = useAppStore((state) => state.desktopSidebarCollapsed)
  const operatorApiKey = useAppStore((state) => state.operatorApiKey)
  const publicTrialUsage = useAppStore((state) => state.publicTrialUsage)
  const clearWorkspace = useAppStore((state) => state.clearWorkspace)
  const setMobileSidebarOpen = useAppStore((state) => state.setMobileSidebarOpen)
  const toggleDesktopSidebar = useAppStore((state) => state.toggleDesktopSidebar)
  const usingOwnApi = Boolean(operatorApiKey)
  const trialRemaining = Math.max(PUBLIC_TRIAL_QUERY_LIMIT - publicTrialUsage, 0)
  const navScrollRef = useScrollActivity<HTMLElement>()

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
        className={cn(
          'fixed inset-0 z-30 bg-slate-950/40 transition-opacity md:hidden',
          mobileSidebarOpen ? 'opacity-100' : 'pointer-events-none opacity-0',
        )}
        onClick={() => setMobileSidebarOpen(false)}
      />
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 flex h-screen flex-col border-r border-border-subtle bg-bg-secondary transition-all duration-200',
          mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full',
          desktopSidebarCollapsed ? 'md:w-[88px]' : 'md:w-[280px]',
          'w-[280px] md:translate-x-0',
        )}
      >
        <div
          className={cn(
            'flex h-20 items-center border-b border-border-subtle',
            desktopSidebarCollapsed ? 'justify-between px-2' : 'justify-between px-5',
          )}
        >
          <Logo
            showText={!desktopSidebarCollapsed}
            showSubtitle={!desktopSidebarCollapsed}
            iconSize={38}
            className={desktopSidebarCollapsed ? 'justify-center' : ''}
          />
          <div className={cn('items-center gap-1', desktopSidebarCollapsed ? 'hidden md:flex' : 'flex')}>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="hidden md:inline-flex"
              aria-label={desktopSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              onClick={toggleDesktopSidebar}
            >
              <LayoutPanelLeft className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="md:hidden"
              aria-label="Close navigation"
              onClick={() => setMobileSidebarOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <nav ref={navScrollRef} className="app-scroll flex-1 space-y-6 overflow-y-auto p-3 md:p-4">
          <div className="space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.href}
                href={item.href}
                icon={item.icon}
                label={item.label}
                active={pathname === item.href}
                collapsed={desktopSidebarCollapsed}
                onClick={() => setMobileSidebarOpen(false)}
              />
            ))}
          </div>
        </nav>

        <div className="border-t border-border-subtle p-3 md:p-4">
          <div className={cn('mb-3 flex items-center gap-2', desktopSidebarCollapsed ? 'justify-center' : 'justify-between')}>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label="Toggle theme"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            {!desktopSidebarCollapsed ? (
              <p className="text-xs font-medium uppercase tracking-[0.18em] text-text-tertiary">
                Workspace
              </p>
            ) : null}
          </div>

          {PUBLIC_APP_ENABLED ? (
            desktopSidebarCollapsed ? (
              <div className="flex justify-center">
                <div className="rounded-full bg-bg-tertiary px-2.5 py-1 text-[11px] font-semibold text-text-secondary">
                  {usingOwnApi ? 'BYO' : `${trialRemaining}`}
                </div>
              </div>
            ) : (
              <div className="rounded-2xl bg-bg-tertiary px-3 py-3 text-sm text-text-secondary">
                {usingOwnApi ? (
                  <>
                    <p className="font-medium text-text-primary">Bring Your Own API</p>
                    <p className="mt-1">
                      This browser is connected to your own NexusRAG API with no hosted usage cap.
                    </p>
                  </>
                ) : (
                  <>
                    <p className="font-medium text-text-primary">Hosted evaluation</p>
                    <p className="mt-1">
                      {trialRemaining} of {PUBLIC_TRIAL_QUERY_LIMIT} shared API questions remaining
                      in this browser.
                    </p>
                  </>
                )}
              </div>
            )
          ) : desktopSidebarCollapsed ? (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="w-full"
              aria-label="Sign out"
              onClick={() => {
                clearWorkspace()
                router.push('/login')
              }}
            >
              <LogOut className="h-4 w-4" />
            </Button>
          ) : (
            <button
              type="button"
              className="flex w-full items-center gap-3 rounded-2xl px-3 py-2 text-left text-sm text-text-secondary transition-colors hover:bg-bg-tertiary hover:text-text-primary"
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

function NavLink({
  href,
  icon: Icon,
  label,
  active,
  collapsed,
  onClick,
}: {
  href: string
  icon: typeof Search
  label: string
  active: boolean
  collapsed: boolean
  onClick: () => void
}) {
  return (
    <Link
      href={href}
      title={collapsed ? label : undefined}
      onClick={onClick}
      className={cn(
        'flex items-center rounded-xl px-3 py-2.5 text-sm transition-colors',
        collapsed ? 'justify-center' : 'gap-3',
        active
          ? 'bg-accent-100 text-accent-700 dark:bg-accent-500/15 dark:text-accent-100'
          : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary',
      )}
    >
      <Icon className="h-4 w-4 shrink-0" />
      {collapsed ? <span className="sr-only">{label}</span> : <span>{label}</span>}
    </Link>
  )
}
