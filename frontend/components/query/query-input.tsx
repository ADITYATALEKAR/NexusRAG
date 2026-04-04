'use client'

import { Loader2, Paperclip, Send } from 'lucide-react'
import { useRef, useState } from 'react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function QueryInput({
  onSubmit,
  onAttach,
  isLoading,
  isUploading = false,
  disabled = false,
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
    <div
      className={cn(
        'surface flex w-full min-w-0 items-end gap-3 rounded-[8px] border-border-default bg-bg-elevated/98 px-4 py-4 transition-all duration-[var(--duration-normal)] focus-within:border-accent-500 focus-within:ring-2 focus-within:ring-accent-500/10',
        disabled && 'opacity-70',
      )}
    >
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
        className="h-11 w-11 shrink-0 rounded-sm border border-border-subtle bg-bg-secondary"
        aria-label="Attach documents"
        disabled={disabled || !onAttach || isUploading}
        onClick={() => fileInputRef.current?.click()}
      >
        {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Paperclip className="h-4 w-4" />}
      </Button>
      <div className="flex-1">
        <textarea
          ref={textareaRef}
          value={value}
          rows={1}
          placeholder={
            disabled
              ? 'Querying is unavailable until this workspace can reach a NexusRAG API...'
              : 'Ask a grounded question about your uploaded knowledge...'
          }
          className="min-h-[30px] max-h-[180px] w-full resize-none border-0 bg-transparent text-[15px] leading-7 text-text-primary placeholder:text-text-tertiary focus:outline-none disabled:cursor-not-allowed"
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
      </div>
      <Button
        onClick={submit}
        size="icon"
        className="h-12 w-12 rounded-sm"
        disabled={disabled || isLoading || !value.trim()}
        aria-label="Submit query"
      >
        {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
      </Button>
    </div>
  )
}


