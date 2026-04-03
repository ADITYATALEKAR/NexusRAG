'use client'

import { Paperclip, Send } from 'lucide-react'
import { useRef, useState } from 'react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function QueryInput({
  onSubmit,
  onAttach,
  isLoading,
  isUploading = false,
  disabled = false
}: {
  onSubmit: (query: string) => void
  onAttach?: (files: File[]) => Promise<unknown> | unknown
  isLoading?: boolean
  isUploading?: boolean
  disabled?: boolean
}) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

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

  const handleAttach = async (files: File[]) => {
    if (!onAttach || files.length === 0 || disabled || isUploading) {
      return
    }
    await onAttach(files)
  }

  return (
    <div className={cn('surface flex items-end gap-3 p-3 transition-all duration-[var(--duration-normal)] focus-within:border-accent-500 focus-within:ring-2 focus-within:ring-accent-500/10', disabled && 'opacity-70')}>
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        multiple
        accept=".pdf,.docx,.md,.txt,text/plain,text/markdown,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        onChange={(event) => {
          const files = Array.from(event.target.files || [])
          void handleAttach(files)
          event.currentTarget.value = ''
        }}
      />
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="shrink-0"
        aria-label="Attach documents"
        disabled={disabled || !onAttach || isUploading}
        onClick={() => fileInputRef.current?.click()}
      >
        <Paperclip className="h-4 w-4" />
      </Button>
      <textarea
        ref={textareaRef}
        value={value}
        rows={1}
        placeholder={
          disabled
            ? 'Querying is unavailable until this workspace can reach a NexusRAG API...'
            : 'Ask a grounded question about your uploaded knowledge...'
        }
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
