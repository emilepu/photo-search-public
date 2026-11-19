import { useEffect, useState } from 'react'
import { t } from '../strings'
import type { Photo } from '../types'

interface Props {
  photo: Photo
  onClose: () => void
}

export default function PhotoDialog({ photo, onClose }: Props) {
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  async function copyPath() {
    try {
      await navigator.clipboard.writeText(photo.path)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      /* clipboard not available (e.g. insecure context): the path is still shown */
    }
  }

  return (
    <div className="backdrop" onClick={onClose}>
      <div
        className="dialog"
        role="dialog"
        aria-modal="true"
        aria-label={t.dialogTitle}
        onClick={e => e.stopPropagation()}
      >
        <img src={photo.thumb_url} alt={photo.folder || t.mainFolder} />

        <p><strong>{t.fullPath}</strong></p>
        <div className="path-row">
          <code>{photo.path}</code>
          <button onClick={copyPath}>{copied ? t.copied : t.copyPath}</button>
        </div>

        {photo.also_found.length > 0 && (
          <>
            <p><strong>{t.alsoFound}</strong></p>
            <ul>
              {photo.also_found.map(p => (
                <li key={p}><code>{p}</code></li>
              ))}
            </ul>
          </>
        )}

        <button className="primary" onClick={onClose}>{t.close}</button>
      </div>
    </div>
  )
}
