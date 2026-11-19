// These mirror the JSON the Python API returns (see backend/photosearch/api.py).

export interface Photo {
  id: number
  thumb_url: string
  folder: string          // folder inside the collection; "" means the main folder
  path: string            // full path including collection name and file name
  copies: number          // number of other copies of the same picture
  also_found: string[]    // full paths of those copies
}

export interface SearchResponse {
  total: number
  results: Photo[]
}

export interface Info {
  count: number
  root_name: string
}

export type PageSize = 20 | 40 | 60

export interface SearchParams {
  query: string
  hideDuplicates: boolean
  pageSize: PageSize
}
