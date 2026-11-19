import { useCallback, useRef, useState } from 'react'
import { searchPhotos } from './api'
import type { Photo, SearchParams } from './types'

/**
 * Holds everything about the current search: the results so far, the total,
 * loading and error state. `search` starts a new search, `showMore` loads the next page.
 */
export function useSearch() {
  const [params, setParams] = useState<SearchParams | null>(null)
  const [results, setResults] = useState<Photo[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const latestRequest = useRef(0)

  const load = useCallback(async (p: SearchParams, offset: number) => {
    const id = ++latestRequest.current
    setLoading(true)
    setError(null)
    try {
      const data = await searchPhotos(p.query, p.hideDuplicates, offset, p.pageSize)
      if (id !== latestRequest.current) return // a newer search has started: ignore this answer
      setTotal(data.total)
      setResults(prev => (offset === 0 ? data.results : [...prev, ...data.results]))
    } catch (e) {
      if (id !== latestRequest.current) return
      setError(e instanceof Error ? e.message : 'Something went wrong')
    } finally {
      if (id === latestRequest.current) setLoading(false)
    }
  }, [])

  const search = useCallback(
    (p: SearchParams) => {
      setParams(p)
      setResults([])
      setTotal(0)
      void load(p, 0)
    },
    [load],
  )

  const showMore = useCallback(() => {
    if (params) void load(params, results.length)
  }, [params, results.length, load])

  return { params, results, total, loading, error, search, showMore }
}
