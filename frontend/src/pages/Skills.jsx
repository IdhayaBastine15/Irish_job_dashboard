import { useStats } from '../hooks/useStats'
import TopSkills from '../components/Charts/TopSkills'
import SkillBadge from '../components/SkillBadge'

export default function Skills() {
  const { topSkills, loading } = useStats()

  if (loading) return <div className="text-center py-20 text-gray-400">Loading skills data...</div>

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-800">Skill Demand</h2>
        <p className="text-sm text-gray-500">Extracted from job descriptions using spaCy NLP + Irish market skill taxonomy</p>
      </div>

      <TopSkills data={topSkills} />

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">All Skills ({topSkills.length} tracked)</h3>
        <div className="flex flex-wrap gap-2">
          {topSkills.map(s => (
            <SkillBadge key={s.skill} skill={s.skill} count={s.count} />
          ))}
        </div>
      </div>
    </div>
  )
}
