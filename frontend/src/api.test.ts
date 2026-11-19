import { afterEach, describe, expect, test, vi } from 'vitest'
import { searchPhotos } from './api'

afterEach(() => vi.unstubAllGlobals())

describe('searchPhotos', () => {
  test('sends the query, paging and duplicate setting', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ total: 0, results: [] }) })
    vi.stubGlobal('fetch', fetchMock)

    await searchPhotos('old oak', true, 20, 40)

    const url = new URL(fetchMock.mock.calls[0][0] as string, 'http://x')
    expect(url.pathname).toBe('/api/search')
    expect(url.searchParams.get('q')).toBe('old oak')
    expect(url.searchParams.get('hide_duplicates')).toBe('true')
    expect(url.searchParams.get('offset')).toBe('20')
    expect(url.searchParams.get('limit')).toBe('40')
  })

  test('throws a readable error when the server fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 500 }))
    await expect(searchPhotos('owl', true, 0, 20)).rejects.toThrow('Server error 500')
  })
})
