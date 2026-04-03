'use client'

import { Menu, Moon, Sun } from 'lucide-react'
import { usePathname } from 'next/navigation'
import { useTheme } from 'next-themes'

import { Logo } from '@/components/shared/logo'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/stores/app-store'

const titles: Record<string, string> = {
  '/dashboard': 'Query workspace',
  '/dashboard/documents': 'Documents',
  '/dashboard/analytics': 'Analytics',
  '/dashboard/settings': 'Settings'
}

export function Header() {
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()
  const setMobileSidebarOpen = useAppStore((state) => state.setMobileSidebarOpen)
  const title = titles[pathname] || 'Workspace'

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border-subtle bg-bg-primary/90 px-4 backdrop-blur md:px-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setMobileSidebarOpen(true)} aria-label="Open navigation">
          <Menu className="h-4 w-4" />
        </Button>
        <div className="flex items-center gap-4">
          <Logo subtitle="by Fundamental Labs" className="shrink-0" />
          <div className="hidden h-8 w-px bg-border-subtle md:block" />
          <div className="hidden md:block">
            <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-text-tertiary">
              {title}
            </p>
            <p className="text-sm text-text-secondary">
              Grounded answers with inline evidence from your uploaded knowledge.
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} aria-label="Toggle theme">
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
      </div>
    </header>
  )
}
