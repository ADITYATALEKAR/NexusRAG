'use client'

import { useCallback, useMemo, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { FileText, UploadCloud, X } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function UploadZone({ onUpload }: { onUpload: (files: File[]) => Promise<unknown> | unknown }) {
  const [files, setFiles] = useState<File[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((current) => [...current, ...acceptedFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/markdown': ['.md'],
      'text/plain': ['.txt']
    }
  })

  const totalLabel = useMemo(
    () => `${files.length} file${files.length === 1 ? '' : 's'}`,
    [files.length]
  )

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={cn(
          'surface flex min-h-[220px] flex-col items-center justify-center border-2 border-dashed px-6 py-10 text-center transition-colors',
          isDragActive
            ? 'border-accent-500 bg-accent-50/80 dark:bg-accent-500/10'
            : 'border-border-default hover:border-border-strong'
        )}
      >
        <input {...getInputProps()} />
        <div className="rounded-2xl bg-bg-secondary p-4 text-text-secondary">
          <UploadCloud className="h-8 w-8" />
        </div>
        <h3 className="mt-5 text-lg font-semibold text-text-primary">
          Drop files here or click to browse
        </h3>
        <p className="mt-2 max-w-md text-sm leading-6 text-text-secondary">
          VectorCore accepts PDF, DOCX, Markdown, and plain text. Uploads are processed quietly
          in the background with visible progress.
        </p>
      </div>

      {files.length > 0 ? (
        <div className="surface space-y-3 p-4">
          {files.map((file, index) => (
            <div
              key={`${file.name}-${index}`}
              className="flex items-center gap-3 rounded-lg bg-bg-secondary px-3 py-2"
            >
              <FileText className="h-4 w-4 text-text-tertiary" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-text-primary">{file.name}</p>
                <p className="text-xs text-text-tertiary">
                  {Math.max(1, Math.round(file.size / 1024))} KB
                </p>
              </div>
              <button
                type="button"
                className="text-text-tertiary transition-colors hover:text-text-primary"
                onClick={() =>
                  setFiles((current) => current.filter((_, itemIndex) => itemIndex !== index))
                }
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
          <Button
            className="w-full"
            disabled={isSubmitting}
            onClick={async () => {
              setIsSubmitting(true)
              try {
                await onUpload(files)
                setFiles([])
              } finally {
                setIsSubmitting(false)
              }
            }}
          >
            {isSubmitting ? 'Uploading...' : `Upload ${totalLabel}`}
          </Button>
        </div>
      ) : null}
    </div>
  )
}
