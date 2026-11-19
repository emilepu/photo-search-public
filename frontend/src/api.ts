import type { Info, SearchResponse } from './types'

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Server error ${res.status}`)
  return (await res.json()) as T
}

export function searchPhotos(
  query: string,
  hideDuplicates: boolean,
  offset: number,
  limit: number,
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    hide_duplicates: String(hideDuplicates),
    offset: String(offset),
    limit: String(limit),
  })
  return getJson<SearchResponse>(`/api/search?${params}`)
}

export function getInfo(): Promise<Info> {
  return getJson<Info>('/api/info')
}
