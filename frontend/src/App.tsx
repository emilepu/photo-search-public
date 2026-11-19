import { useEffect, useState } from 'react'
import { getInfo } from './api'
import PhotoDialog from './components/PhotoDialog'
import PhotoGrid from './components/PhotoGrid'
import SearchForm from './components/SearchForm'
import { t } from './strings'
import type { Info, Photo } from './types'
import { useSearch } from './useSearch'

export default function App() {
  const { params, results, total, loading, error, search, showMore } = useSearch()
  const [selected, setSelected] = useState<Photo | null>(null)
  const [info, setInfo] = useState<Info | null>(null)

  useEffect(() => {
    getInfo().then(setInfo).catch(() => { /* the footer is optional */ })
  }, [])

  return (
    <main>
      <h1>{t.title}</h1>

      <details className="howto">
        <summary>{t.howToTitle}</summary>
        <ol>
          {t.howTo.map(line => <li key={line}>{line}</li>)}
        </ol>
      </details>

      <SearchForm onSearch={search} disabled={loading} />

      {!params && <p className="muted">{t.idle}</p>}
      {loading && results.length === 0 && <p className="muted">{t.searching}</p>}
      {error && <p className="error" role="alert">{error}</p>}
      {params && !loading && !error && total === 0 && <p className="muted">{t.noResults}</p>}

      {params && results.length > 0 && (
        <>
          <PhotoGrid photos={results} showCopies={params.hideDuplicates} onOpen={setSelected} />
          <p className="muted">{t.shown(results.length, total)}</p>
          {results.length < total && (
            <button className="primary" onClick={showMore} disabled={loading}>
              {loading ? t.searching : t.showMore(params.pageSize)}
            </button>
          )}
        </>
      )}

      {info && <footer className="muted">{t.indexed(info.count)}</footer>}

      {selected && <PhotoDialog photo={selected} onClose={() => setSelected(null)} />}
    </main>
  )
}
