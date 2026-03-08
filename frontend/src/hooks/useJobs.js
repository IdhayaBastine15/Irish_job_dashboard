import { useState, useEffect, useCallback } from 'react'
import { jobsApi } from '../api'

export function useJobs(initialFilters = {}) {
  const [jobs, setJobs] = useState([])
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ page: 1, per_page: 20, ...initialFilters })

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await jobsApi.list(filters)
      setJobs(data.jobs)
      setTotal(data.total)
      setPages(data.pages)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [JSON.stringify(filters)])

  useEffect(() => { fetch() }, [fetch])

  return {
    jobs, total, pages, loading, error, filters,
    updateFilters: (f) => setFilters(p => ({ ...p, ...f, page: 1 })),
    setPage: (page) => setFilters(p => ({ ...p, page })),
  }
}
