'use client'

import { Bell, Menu, Moon, Sun } from 'lucide-react'
import { usePathname } from 'next/navigation'
import { useTheme } from 'next-themes'

import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/stores/app-store'

const titles: Record<string, string> = {
  '/dashboard': 'Query workspace',
  '/dashboard/documents': 'Documents',
  '/dashboard/analytics': 'Analytics',
  '/dashboard/settings': 'Settings',
  '/dashboard/admin': 'Admin overview',
  '/dashboard/admin/datasets': 'Datasets',
  '/dashboard/admin/evaluation': 'Evaluation'
}

export function Header() {
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()
  const setMobileSidebarOpen = useAppStore((state) => state.setMobileSidebarOpen)

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border-subtle bg-bg-primary/90 px-4 backdrop-blur md:px-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setMobileSidebarOpen(true)} aria-label="Open navigation">
          <Menu className="h-4 w-4" />
        </Button>
        <div>
          <p className="text-xs uppercase tracking-[0.22em] text-text-tertiary">VectorCore</p>
          <h1 className="text-sm font-semibold text-text-primary md:text-base">{titles[pathname] || 'Dashboard'}</h1>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} aria-label="Toggle theme">
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
        <Button variant="ghost" size="icon" aria-label="Notifications">
          <Bell className="h-4 w-4" />
        </Button>
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-accent-100 text-sm font-semibold text-accent-700 dark:bg-accent-500/15 dark:text-accent-100">
          VC
        </div>
      </div>
    </header>
  )
}