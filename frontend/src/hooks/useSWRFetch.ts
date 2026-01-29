import useSWR, { SWRConfiguration } from 'swr'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const fetcher = async (url: string) => {
  const res = await fetch(`${API_BASE_URL}${url}`)
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP error ${res.status}`)
  }
  return res.json()
}

export function useSWRFetch<T>(
  endpoint: string | null,
  config?: SWRConfiguration
) {
  return useSWR<T>(endpoint, fetcher, {
    refreshInterval: 5000, // Refresh every 5 seconds for status updates
    ...config,
  })
}
