import { useStats } from '../hooks/useStats'
import StatsCard from '../components/StatsCard'
import JobsByCategory from '../components/Charts/JobsByCategory'
import JobsByLocation from '../components/Charts/JobsByLocation'
import TopSkills from '../components/Charts/TopSkills'
import SalaryRange from '../components/Charts/SalaryRange'

export default function Dashboard() {
  const { overview, byCategory, byCounty, topSkills, salaryDist, loading, error } = useStats()

  if (loading) return <div className="flex justify-center h-64 items-center text-gray-400">Loading dashboard...</div>
  if (error) return <div className="flex justify-center h-64 items-center text-red-400">⚠️ Can't reach backend. Is FastAPI running on port 8000?</div>

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-800">Irish Job Market Overview</h2>
        <p className="text-sm text-gray-500">Live data from Adzuna API · Skill extraction via spaCy · Insights via Claude</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <StatsCard title="Total Jobs" value={overview?.total_jobs?.toLocaleString()} icon="💼" color="green" />
        <StatsCard title="New This Week" value={overview?.new_this_week?.toLocaleString()} icon="🆕" color="blue" />
        <StatsCard title="Avg Salary" value={overview?.avg_salary ? `€${overview.avg_salary.toLocaleString()}` : 'N/A'} icon="💰" color="orange" />
        <StatsCard title="Top County" value={overview?.top_county} icon="📍" color="purple" />
        <StatsCard title="Categories" value={overview?.categories} icon="🏷️" color="green" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <JobsByCategory data={byCategory} />
        <JobsByLocation data={byCounty.slice(0, 12)} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <TopSkills data={topSkills.slice(0, 15)} />
        <SalaryRange data={salaryDist} />
      </div>
    </div>
  )
}
