export default function SkillBadge({ skill, count }) {
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
      {skill}
      {count != null && <span className="text-blue-400">×{count}</span>}
    </span>
  )
}
