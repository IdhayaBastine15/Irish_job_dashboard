import JobCard from './JobCard'

export default function JobList({ jobs, loading, error, total, page, pages, onPageChange }) {
  if (loading) return <div className="flex justify-center py-20 text-gray-400">⏳ Loading jobs...</div>
  if (error) return <div className="flex justify-center py-20 text-red-400">⚠️ {error}</div>
  if (!jobs.length) return <div className="flex justify-center py-20 text-gray-400">🔍 No jobs found</div>

  return (
    <div>
      <p className="text-sm text-gray-500 mb-4">{total.toLocaleString()} jobs found</p>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {jobs.map(job => <JobCard key={job.id} job={job} />)}
      </div>
      {pages > 1 && (
        <div className="flex justify-center gap-2 mt-8">
          <button onClick={() => onPageChange(page - 1)} disabled={page === 1}
            className="px-4 py-2 rounded-lg border border-gray-300 text-sm disabled:opacity-40 hover:bg-gray-50">
            ← Previous
          </button>
          <span className="px-4 py-2 text-sm text-gray-600">Page {page} of {pages}</span>
          <button onClick={() => onPageChange(page + 1)} disabled={page === pages}
            className="px-4 py-2 rounded-lg border border-gray-300 text-sm disabled:opacity-40 hover:bg-gray-50">
            Next →
          </button>
        </div>
      )}
    </div>
  )
}
