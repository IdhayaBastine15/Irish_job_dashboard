import SkillBadge from './SkillBadge'

export default function JobCard({ job }) {
  const contractColors = {
    permanent: 'bg-green-100 text-green-700',
    contract: 'bg-blue-100 text-blue-700',
    temporary: 'bg-orange-100 text-orange-700',
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start gap-3 mb-3">
        <div className="min-w-0">
          <h3 className="font-semibold text-gray-800 leading-snug">{job.title}</h3>
          <p className="text-sm text-gray-500">{job.company}</p>
        </div>
        {job.contract_type && (
          <span className={`text-xs font-medium px-2 py-1 rounded-full shrink-0 ${contractColors[job.contract_type] || 'bg-gray-100 text-gray-600'}`}>
            {job.contract_type}
          </span>
        )}
      </div>

      <div className="flex flex-wrap gap-3 text-sm text-gray-500 mb-3">
        {job.location && <span>📍 {job.location}</span>}
        {job.category && <span>🏷️ {job.category}</span>}
        {job.contract_time && <span>🕐 {job.contract_time?.replace('_', '-')}</span>}
      </div>

      {(job.salary_min || job.salary_max) && (
        <p className="text-sm font-medium text-green-700 mb-3">
          💰 {job.salary_min ? `€${job.salary_min.toLocaleString()}` : ''}
          {job.salary_min && job.salary_max ? ' – ' : ''}
          {job.salary_max ? `€${job.salary_max.toLocaleString()}` : ''}
          {job.salary_predicted && <span className="text-xs text-gray-400 ml-1">(est.)</span>}
        </p>
      )}

      {job.skills?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {job.skills.slice(0, 5).map(s => <SkillBadge key={s} skill={s} />)}
          {job.skills.length > 5 && (
            <span className="text-xs text-gray-400 self-center">+{job.skills.length - 5} more</span>
          )}
        </div>
      )}

      <div className="flex justify-between items-center mt-2 pt-3 border-t border-gray-100">
        <span className="text-xs text-gray-400">
          {job.posted_date ? new Date(job.posted_date).toLocaleDateString('en-IE') : 'Date unknown'}
        </span>
        {job.redirect_url && (
          <a href={job.redirect_url} target="_blank" rel="noopener noreferrer"
            className="text-sm text-green-600 hover:text-green-700 font-medium">
            View on Adzuna →
          </a>
        )}
      </div>
    </div>
  )
}
