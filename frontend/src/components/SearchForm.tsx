import { useState } from 'react'
import { t } from '../strings'
import type { PageSize, SearchParams } from '../types'

const PAGE_SIZES: PageSize[] = [20, 40, 60]

interface Props {
  onSearch: (params: SearchParams) => void
  disabled?: boolean
}

export default function SearchForm({ onSearch, disabled }: Props) {
  const [query, setQuery] = useState('')
  const [pageSize, setPageSize] = useState<PageSize>(20)
  const [hideDuplicates, setHideDuplicates] = useState(true)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = query.trim()
    if (trimmed) onSearch({ query: trimmed, hideDuplicates, pageSize })
  }

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <label>
        {t.searchLabel}
        <input
          value={query}
          placeholder={t.searchPlaceholder}
          onChange={e => setQuery(e.target.value)}
        />
      </label>

      <div className="options">
        <fieldset>
          <legend>{t.pageSizeLabel}</legend>
          {PAGE_SIZES.map(n => (
            <label key={n} className="inline">
              <input
                type="radio"
                name="pageSize"
                checked={pageSize === n}
                onChange={() => setPageSize(n)}
              />
              {n}
            </label>
          ))}
        </fieldset>

        <label className="inline">
          <input
            type="checkbox"
            checked={hideDuplicates}
            onChange={e => setHideDuplicates(e.target.checked)}
          />
          {t.hideDuplicates}
        </label>
      </div>

      <button type="submit" className="primary" disabled={disabled}>
        {t.searchButton}
      </button>
    </form>
  )
}
