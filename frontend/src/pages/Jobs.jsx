import { useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useJobs } from '../hooks/useJobs'
import FilterBar from '../components/FilterBar'
import JobList from '../components/JobList'

export default function Jobs() {
  const [searchParams] = useSearchParams()
  const q = searchParams.get('q')

  const { jobs, total, pages, loading, error, filters, updateFilters, setPage } = useJobs(q ? { q } : {})

  useEffect(() => {
    if (q) updateFilters({ q })
  }, [q])

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-800">Browse Jobs</h2>
        <p className="text-sm text-gray-500">Irish job listings from Adzuna with extracted skills</p>
      </div>
      <FilterBar filters={filters} onFilterChange={updateFilters} />
      <JobList jobs={jobs} loading={loading} error={error} total={total} page={filters.page} pages={pages} onPageChange={setPage} />
    </div>
  )
}
