import { useState } from 'react'
import { useStats } from '../hooks/useStats'
import InsightPanel from '../components/InsightPanel'

export default function Insights() {
  const { byCategory } = useStats()
  const [selected, setSelected] = useState(null)

  const categories = byCategory.slice(0, 12)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-800">AI Insights</h2>
        <p className="text-sm text-gray-500">Claude-powered analysis of the Irish job market by category</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <p className="text-sm font-medium text-gray-600 mb-3">Select a category to analyse:</p>
        <div className="flex flex-wrap gap-2">
          {categories.map(c => (
            <button
              key={c.category}
              onClick={() => setSelected(c.category)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                selected === c.category
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {c.category} <span className="text-xs opacity-70">({c.count})</span>
            </button>
          ))}
        </div>
      </div>

      {selected && <InsightPanel category={selected} key={selected} />}

      {!selected && (
        <div className="text-center py-12 text-gray-400">
          <p className="text-4xl mb-3">✨</p>
          <p>Select a category above to get a Claude-powered market insight.</p>
        </div>
      )}
    </div>
  )
}
