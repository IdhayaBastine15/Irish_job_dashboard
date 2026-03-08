import { NavLink } from 'react-router-dom'
import clsx from 'clsx'

const nav = [
  { to: '/', label: 'Dashboard', icon: '📊', end: true },
  { to: '/jobs', label: 'Jobs', icon: '💼' },
  { to: '/skills', label: 'Skills', icon: '🧠' },
  { to: '/insights', label: 'AI Insights', icon: '✨' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 bg-white border-r border-gray-200 flex flex-col py-6 shrink-0">
      <nav className="flex-1 px-3 space-y-1">
        {nav.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive ? 'bg-green-50 text-green-700' : 'text-gray-600 hover:bg-gray-100'
              )
            }
          >
            <span>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="px-4 pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-400">Data: Adzuna API</p>
        <p className="text-xs text-gray-400">Insights: Claude API</p>
        <p className="text-xs text-gray-400 mt-1">Synced every 6h</p>
      </div>
    </aside>
  )
}
