'use client'

import { Paperclip, Send } from 'lucide-react'
import { useRef, useState } from 'react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function QueryInput({ onSubmit, isLoading, disabled = false }: { onSubmit: (query: string) => void; isLoading?: boolean; disabled?: boolean }) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const submit = () => {
    const normalized = value.trim()
    if (!normalized || isLoading || disabled) {
      return
    }
    onSubmit(normalized)
    setValue('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  return (
    <div className={cn('surface flex items-end gap-3 p-3 transition-all duration-[var(--duration-normal)] focus-within:border-accent-500 focus-within:ring-2 focus-within:ring-accent-500/10', disabled && 'opacity-70')}>
      <Button variant="ghost" size="icon" className="hidden shrink-0 sm:inline-flex" aria-label="Attach context" disabled={disabled}>
        <Paperclip className="h-4 w-4" />
      </Button>
      <textarea
        ref={textareaRef}
        value={value}
        rows={1}
        placeholder={disabled ? 'Connect the external RAG backend to enable querying...' : 'Ask a question about your documents...'}
        className="min-h-[28px] max-h-[180px] flex-1 resize-none border-0 bg-transparent text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none disabled:cursor-not-allowed"
        disabled={disabled}
        onChange={(event) => setValue(event.target.value)}
        onInput={(event) => {
          const target = event.currentTarget
          target.style.height = 'auto'
          target.style.height = `${target.scrollHeight}px`
        }}
        onKeyDown={(event) => {
          if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault()
            submit()
          }
        }}
      />
      <Button onClick={submit} size="icon" disabled={disabled || isLoading || !value.trim()} aria-label="Submit query">
        <Send className="h-4 w-4" />
      </Button>
    </div>
  )
}
